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
process_table_metadata_router = APIRouter()

configure_langfuse()
langfuse = Langfuse()


@process_table_metadata_router.post("/process_table_metadata/{file_hash}")
async def process_table_metadata(
    file_hash: str,
    x_span_id: Optional[str] = Header(None),
    x_run_id: Optional[str] = Header(None),
) -> Dict:
    """Process metadata for extracted tables"""
    try:
        db = init_mongo()
        if isinstance(db, dict) and "error" in db:
            raise HTTPException(status_code=500, detail=db["error"])

        asset = db["raw_assets"].find_one({"file_hash": file_hash})
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")

        processed_paths = asset.get("processed_paths", {})
        tables = processed_paths.get("tables", {})

        if not tables:
            logger.info(f"No tables found for {file_hash}, skipping metadata")
            update_asset_status(file_hash, "table_metadata_skipped")
            return {"status": "skipped", "reason": "no_tables"}

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
            name="table_metadata_processing",
            metadata={"processor_type": "table_metadata", "run_id": run_id},
        )

        update_asset_status(file_hash, "processing_table_metadata")
        logger.info(f"Starting table metadata processing for {file_hash}")

        # Read the prompt template
        prompts_dir = os.path.join("/app", "prompts", "assets", "table")
        with open(os.path.join(prompts_dir, "metadata.txt"), "r") as f:
            prompt_template = f.read()

        table_metadata = {}

        for table_name, paths in tables.items():
            csv_path = paths.get("csv")
            if not csv_path or not os.path.exists(csv_path):
                continue

            with open(csv_path, "r", encoding="utf-8") as f:
                table_content = f.read()

            prompt = f"{prompt_template}\n\nTable Content:\n{table_content}"
            response = chat_call(query=prompt, messages=[])

            if "error" in response:
                raise HTTPException(
                    status_code=500,
                    detail=f"Chat API error for table {table_name}",
                )

            response_text = response["message"]
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1

            if json_start < 0 or json_end <= json_start:
                logger.error(
                    f"Could not find JSON in chat response for table {table_name}"
                )
                continue

            metadata = json.loads(response_text[json_start:json_end])
            table_metadata[table_name] = metadata

        if table_metadata:
            metadata_path = os.path.join(
                "/app/filestore/processed", file_hash, "tables", "table_metadata.json"
            )
            os.makedirs(os.path.dirname(metadata_path), exist_ok=True)

            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(table_metadata, f, ensure_ascii=False, indent=2)

            update_data = {
                "processed_paths.table_metadata": metadata_path,
                "table_metadata": table_metadata,
            }
            db["raw_assets"].update_one({"file_hash": file_hash}, {"$set": update_data})

        update_asset_status(file_hash, "table_metadata_complete")
        span.event(
            name="table_metadata_complete",
            metadata={"table_count": len(table_metadata)},
        )

        return {
            "status": "success",
            "table_metadata": table_metadata,
            "table_count": len(table_metadata),
        }

    except Exception as e:
        error_msg = f"Error processing table metadata: {str(e)}"
        if "span" in locals():
            span.event(
                name="table_metadata_error",
                metadata={"error": error_msg},
                level="error",
            )
        update_asset_status(file_hash, "table_metadata_error", error=error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

    finally:
        if "span" in locals():
            span.end()
