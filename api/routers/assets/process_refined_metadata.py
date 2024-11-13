# api/routers/assets.py

import json
import logging
import os
from typing import Dict, Optional

from fastapi import APIRouter, Header, HTTPException
from langfuse import Langfuse
from utils.db_utils import init_mongo, update_asset_status
from utils.langfuse_utils import configure_langfuse

from .chat import chat_call

logger = logging.getLogger(__name__)
process_refined_metadata_router = APIRouter()

configure_langfuse()
langfuse = Langfuse()


@process_refined_metadata_router.post("/process_refined_metadata/{file_hash}")
async def process_refined_metadata(
    file_hash: str,
    x_span_id: Optional[str] = Header(None),
    x_run_id: Optional[str] = Header(None),
) -> Dict:
    """Extract metadata from document content"""
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
            name="metadata_processing",
            metadata={"processor_type": "metadata", "run_id": run_id},
        )

        update_asset_status(file_hash, "processing_metadata")
        logger.info(f"Starting metadata extraction for {file_hash}")

        # Get the processed markdown content
        processed_paths = asset.get("processed_paths", {})
        if not processed_paths or "markdown" not in processed_paths:
            raise HTTPException(
                status_code=400, detail="Markdown content not available"
            )

        # Read the prompt template
        prompts_dir = os.path.join("/app", "prompts", "assets")
        with open(os.path.join(prompts_dir, "metadata.txt"), "r") as f:
            prompt_template = f.read()

        # Read the processed content
        with open(processed_paths["markdown"], "r") as f:
            file_content = f.read()

        # Prepare and make the chat API call
        prompt = prompt_template + "\n\nDocument Content:\n" + file_content
        response = chat_call(query=prompt, messages=[])

        if "error" in response:
            raise HTTPException(status_code=500, detail=response["error"])

        response_text = response["message"]
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1

        if json_start < 0 or json_end <= json_start:
            raise HTTPException(
                status_code=500, detail="Could not find JSON in chat response"
            )

        metadata = json.loads(response_text[json_start:json_end])

        metadata_path = os.path.join(
            "/app/filestore/processed", file_hash, "metadata.json"
        )
        os.makedirs(os.path.dirname(metadata_path), exist_ok=True)

        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        # Update asset
        update_data = {
            "metadata": metadata,
            "processed_paths.metadata": metadata_path,
        }
        db["raw_assets"].update_one({"file_hash": file_hash}, {"$set": update_data})

        update_asset_status(file_hash, "metadata_complete")
        span.event(name="metadata_complete", metadata={"metadata_path": metadata_path})

        return {
            "status": "success",
            "metadata": metadata,
            "metadata_path": metadata_path,
        }

    except Exception as e:
        error_msg = f"Error extracting metadata: {str(e)}"
        if "span" in locals():
            span.event(
                name="metadata_error", metadata={"error": error_msg}, level="error"
            )
        update_asset_status(file_hash, "metadata_error", error=error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

    finally:
        if "span" in locals():
            span.end()
