# api/routers/assets.py

import json
import logging
import os
from typing import Dict, Optional

from fastapi import APIRouter, Header, HTTPException
from langfuse import Langfuse
from utils.db_utils import init_mongo, update_asset_status
from utils.image_utils import format_image_info, get_image_technical_metadata
from utils.langfuse_utils import configure_langfuse

from .chat import chat_call

logger = logging.getLogger(__name__)
process_image_metadata_router = APIRouter()

configure_langfuse()
langfuse = Langfuse()


@process_image_metadata_router.post("/process_image_metadata/{file_hash}")
async def process_image_metadata(
    file_hash: str,
    x_span_id: Optional[str] = Header(None),
    x_run_id: Optional[str] = Header(None),
) -> Dict:
    """Process metadata for extracted images"""
    try:
        db = init_mongo()
        if isinstance(db, dict) and "error" in db:
            raise HTTPException(status_code=500, detail=db["error"])

        asset = db["raw_assets"].find_one({"file_hash": file_hash})
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")

        processed_paths = asset.get("processed_paths", {})
        images = processed_paths.get("images", {})

        if not images:
            logger.info(f"No images found for {file_hash}, skipping metadata")
            update_asset_status(file_hash, "image_metadata_skipped")
            return {"status": "skipped", "reason": "no_images"}

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
            name="image_metadata_processing",
            metadata={"processor_type": "image_metadata", "run_id": run_id},
        )

        update_asset_status(file_hash, "processing_image_metadata")
        logger.info(f"Starting image metadata processing for {file_hash}")

        # Read prompt template
        prompts_dir = os.path.join("/app", "prompts", "assets", "image")
        with open(os.path.join(prompts_dir, "metadata.txt"), "r") as f:
            prompt_template = f.read()

        image_metadata = {}

        for image_name, image_path in images.items():
            try:
                # Get technical metadata
                technical_metadata = get_image_technical_metadata(
                    image_name, image_path
                )
                if not technical_metadata:
                    continue

                # Convert image info to text description
                image_description = format_image_info(technical_metadata)
                prompt = f"{prompt_template}\n\nImage Information:\n{image_description}"

                response = chat_call(query=prompt, messages=[])

                if "error" in response:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Chat API error for image {image_name} with error: {response['error']}",
                    )

                response_text = response["message"]
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1

                if json_start < 0 or json_end <= json_start:
                    logger.error(
                        f"Could not find JSON in chat response for image {image_name}"
                    )
                    continue

                ai_metadata = json.loads(response_text[json_start:json_end])
                image_metadata[image_name] = {
                    "technical": technical_metadata,
                    "analysis": ai_metadata,
                }

            except Exception as e:
                logger.error(f"Error processing image {image_name}: {str(e)}")
                continue

        if image_metadata:
            metadata_path = os.path.join(
                "/app/filestore/processed", file_hash, "images", "image_metadata.json"
            )
            os.makedirs(os.path.dirname(metadata_path), exist_ok=True)

            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(image_metadata, f, ensure_ascii=False, indent=2)

            update_data = {
                "processed_paths.image_metadata": metadata_path,
                "image_metadata": image_metadata,
            }
            db["raw_assets"].update_one({"file_hash": file_hash}, {"$set": update_data})

        update_asset_status(file_hash, "image_metadata_complete")
        span.event(
            name="image_metadata_complete",
            metadata={"image_count": len(image_metadata)},
        )

        return {
            "status": "success",
            "image_metadata": image_metadata,
            "image_count": len(image_metadata),
        }

    except Exception as e:
        error_msg = f"Error processing image metadata: {str(e)}"
        if "span" in locals():
            span.event(
                name="image_metadata_error",
                metadata={"error": error_msg},
                level="error",
            )
        update_asset_status(file_hash, "image_metadata_error", error=error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

    finally:
        if "span" in locals():
            span.end()
