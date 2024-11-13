# api/routers/assets.py

import json
import logging
import os
import time
from typing import Dict, Optional

from fastapi import APIRouter, Header, HTTPException
from langfuse import Langfuse
from utils.db_utils import init_mongo, update_asset_status
from utils.langfuse_utils import configure_langfuse

from .chat import chat_call

logger = logging.getLogger(__name__)
process_refined_splitting_router = APIRouter()

configure_langfuse()
langfuse = Langfuse()


@process_refined_splitting_router.post("/process_refined_splitting/{file_hash}")
async def process_refined_splitting(
    file_hash: str,
    x_span_id: Optional[str] = Header(None),
    x_run_id: Optional[str] = Header(None),
) -> Dict:
    """Process document content into logical segments"""
    try:
        db = init_mongo()
        if isinstance(db, dict) and "error" in db:
            raise HTTPException(status_code=500, detail=db["error"])

        asset = db["raw_assets"].find_one({"file_hash": file_hash})
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")

        run_id = x_run_id or asset.get("current_run_id")
        if not run_id:
            raise HTTPException(status_code=400, detail="No run_id found for asset")

        trace = langfuse.trace(
            name="asset-processing",
            id=run_id,
            metadata={
                "file_hash": file_hash,
                "file_name": asset["original_name"],
                "file_type": asset["file_type"],
                "file_size": asset["file_size"],
            },
        )

        span = trace.span(
            id=x_span_id,
            name="splitting_processing",
            metadata={"processor_type": "splitting", "run_id": run_id},
        )

        update_asset_status(file_hash, "processing_splitting")
        logger.info(f"Starting content splitting for {file_hash}")

        processed_paths = asset.get("processed_paths", {})
        if not processed_paths or "markdown" not in processed_paths:
            error_msg = "Markdown content not available - need refined content first"
            logger.error(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)

        with open(processed_paths["markdown"], "r") as f:
            file_content = f.read()
            content_length = len(file_content)
            logger.info(f"Document length: {content_length} characters")

        MIN_CHARS_FOR_SPLIT = 24000  # ~6k tokens
        IDEAL_SEGMENT_SIZE = 16000  # ~4k tokens
        MAX_SEGMENT_SIZE = 28000  # ~7k tokens

        if content_length <= MIN_CHARS_FOR_SPLIT:
            logger.info("Document below split threshold - no splitting needed")
            results = {
                "splitRecommendations": {
                    "shouldSplit": False,
                    "confidence": 95,
                    "reasoning": "Document small enough for single-unit processing",
                },
                "documentStats": {
                    "totalLength": {"value": content_length, "unit": "characters"}
                },
            }
            prompt = None
        else:
            prompts_dir = os.path.join("/app", "prompts", "assets")
            with open(os.path.join(prompts_dir, "splitting.txt"), "r") as f:
                prompt_template = f.read()

            prompt = prompt_template + "\n\nDocument Content:\n" + file_content

            generation = span.generation(
                name="splitting_analysis",
                input=prompt,
            )

            response = chat_call(query=prompt, messages=[])

            if "error" in response:
                raise HTTPException(status_code=500, detail=response["error"])

            response_text = response["message"]
            generation.end(output=response_text)

            # Extract JSON from response
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1

            if json_start < 0 or json_end <= json_start:
                raise HTTPException(
                    status_code=500, detail="Could not find JSON in chat response"
                )

            results = json.loads(response_text[json_start:json_end])

        # Validate and adjust split recommendations based on size
        should_split = content_length > MIN_CHARS_FOR_SPLIT
        if should_split and "splitRecommendations" in results:
            splits = results["splitRecommendations"].get("recommendedSplits", [])

            # Validate split sizes
            oversized_splits = []
            total_chars = 0

            for split in splits:
                length = split.get("estimatedLength", {}).get("value", 0)
                if length > MAX_SEGMENT_SIZE:
                    oversized_splits.append(split["suggestedTitle"])
                total_chars += length

            # Add warnings if needed
            if oversized_splits:
                results["splitRecommendations"]["warnings"] = {
                    "oversizedSegments": oversized_splits,
                    "recommendedMaxSize": MAX_SEGMENT_SIZE,
                    "recommendation": "Consider further splitting large segments",
                }

            # Validate total size
            if abs(total_chars - content_length) > content_length * 0.1:
                logger.warning(
                    f"Split size mismatch. Original: {content_length}, "
                    f"Sum of splits: {total_chars}"
                )
                results["splitRecommendations"]["warnings"] = {
                    **results["splitRecommendations"].get("warnings", {}),
                    "sizeMismatch": {
                        "originalSize": content_length,
                        "splitTotalSize": total_chars,
                        "recommendation": "Review split boundaries",
                    },
                }

        # Save results
        processed_dir = os.path.join("/app/filestore/processed", file_hash)
        splitting_path = os.path.join(processed_dir, "splitting.json")
        os.makedirs(os.path.dirname(splitting_path), exist_ok=True)

        with open(splitting_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        # Update asset record
        update_data = {
            "splitting": results,
            "processed_paths.splitting": splitting_path,
            "segment_count": len(
                results.get("splitRecommendations", {}).get("recommendedSplits", [])
            ),
            "should_split": results.get("splitRecommendations", {}).get(
                "shouldSplit", False
            ),
        }

        db["raw_assets"].update_one({"file_hash": file_hash}, {"$set": update_data})

        update_asset_status(file_hash, "splitting_complete")

        span.event(name="splitting_complete", metadata={"results": results})

        return {
            "status": "success",
            "results": results,
            "splitting_path": splitting_path,
        }

    except Exception as e:
        error_msg = f"Error in content splitting: {str(e)}"
        logger.error(error_msg)
        if "span" in locals():
            span.event(
                name="splitting_error", metadata={"error": error_msg}, level="error"
            )
        update_asset_status(file_hash, "splitting_error", error=error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

    finally:
        if "span" in locals():
            span.end()
            time.sleep(0.5)
