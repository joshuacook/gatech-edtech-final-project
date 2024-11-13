# api/routers/assets.py

import json
import logging
import os
from datetime import datetime
from typing import Dict, Optional

from fastapi import APIRouter, Header, HTTPException
from langfuse import Langfuse
from utils.db_utils import init_mongo, update_asset_status
from utils.langfuse_utils import configure_langfuse
from utils.lexeme_utils import get_prompts_for_category, merge_lexeme_results

from .chat import chat_call

logger = logging.getLogger(__name__)
process_lexemes_router = APIRouter()

configure_langfuse()
langfuse = Langfuse()


@process_lexemes_router.post("/process_lexemes/{file_hash}")
async def process_lexemes(
    file_hash: str,
    x_span_id: Optional[str] = Header(None),
    x_run_id: Optional[str] = Header(None),
) -> Dict:
    """Extract lexemes from document content"""
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
            name="lexeme_processing",
            metadata={"processor_type": "lexemes", "run_id": run_id},
        )

        update_asset_status(file_hash, "processing_lexemes")
        logger.info(f"Starting lexeme processing for {file_hash}")

        # Get the content and metadata
        processed_paths = asset.get("processed_paths", {})
        if not processed_paths or "markdown" not in processed_paths:
            raise HTTPException(
                status_code=400, detail="Markdown content not available"
            )

        with open(processed_paths["markdown"], "r") as f:
            content = f.read()

        category = (
            asset.get("metadata", {})
            .get("documentMetadata", {})
            .get("primaryType", {})
            .get("category", "General/Mixed")
        )
        prompts_to_run = get_prompts_for_category(category)
        all_lexemes = []

        for prompt_file in prompts_to_run:
            try:
                prompt_path = os.path.join(
                    "/app", "prompts", "assets", "lexeme", prompt_file
                )
                with open(prompt_path, "r") as f:
                    prompt_template = f.read()

                prompt = f"{prompt_template}\n\nDocument Content:\n{content}"

                generation = span.generation(
                    name=f"lexeme_extraction_{prompt_file}",
                    input=prompt,
                )

                response = chat_call(query=prompt, messages=[])

                if "error" in response:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Chat API error for prompt {prompt_file} with error: {response['error']}",
                    )

                response_text = response["message"]
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1

                if json_start < 0 or json_end <= json_start:
                    raise ValueError(
                        f"Could not find JSON in chat response for prompt {prompt_file}"
                    )

                prompt_lexemes = json.loads(response_text[json_start:json_end])[
                    "lexemes"
                ]
                all_lexemes.extend(prompt_lexemes)

                generation.end(
                    output=response_text,
                    metadata={
                        "prompt_file": prompt_file,
                        "lexeme_count": len(prompt_lexemes),
                    },
                )

            except Exception as e:
                logger.error(f"Error processing with prompt {prompt_file}: {str(e)}")
                continue

        # Merge and deduplicate lexemes
        merged_lexemes = merge_lexeme_results(all_lexemes)

        # Save results
        lexemes_path = os.path.join(
            "/app/filestore/processed", file_hash, "lexemes.json"
        )
        os.makedirs(os.path.dirname(lexemes_path), exist_ok=True)

        lexeme_data = {
            "lexemes": merged_lexemes,
            "metadata": {
                "count": len(merged_lexemes),
                "processed_at": datetime.now().isoformat(),
                "asset_id": file_hash,
            },
        }

        with open(lexemes_path, "w", encoding="utf-8") as f:
            json.dump(lexeme_data, f, ensure_ascii=False, indent=2)

        # Update asset
        update_data = {
            "processed_paths.lexemes": lexemes_path,
            "lexemes": merged_lexemes,
            "lexeme_count": len(merged_lexemes),
        }
        db["raw_assets"].update_one({"file_hash": file_hash}, {"$set": update_data})

        update_asset_status(file_hash, "lexemes_complete")
        span.event(
            name="lexemes_complete", metadata={"lexeme_count": len(merged_lexemes)}
        )

        return {
            "status": "success",
            "lexeme_count": len(merged_lexemes),
            "lexemes": merged_lexemes,
        }

    except Exception as e:
        error_msg = f"Error processing lexemes: {str(e)}"
        if "span" in locals():
            span.event(
                name="lexemes_error", metadata={"error": error_msg}, level="error"
            )
        update_asset_status(file_hash, "lexemes_error", error=error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

    finally:
        if "span" in locals():
            span.end()
