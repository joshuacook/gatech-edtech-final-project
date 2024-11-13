# api/routers/assets.py

import json
import logging
import os
import time
from typing import Dict, Optional

import requests
from fastapi import APIRouter, Header, HTTPException
from langfuse import Langfuse
from utils import handle_error
from utils.db_utils import init_mongo, update_asset_status
from utils.langfuse_utils import configure_langfuse

logger = logging.getLogger(__name__)
process_refined_router = APIRouter()

configure_langfuse()
langfuse = Langfuse()


@process_refined_router.post("/process_refined/{file_hash}")
async def process_refined(
    file_hash: str,
    x_span_id: Optional[str] = Header(None),
    x_run_id: Optional[str] = Header(None),
) -> Dict:
    """
    Refine a document using Marker API for content extraction and formatting.
    """
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
            name="refined_processing",
            metadata={"processor_type": "refined", "run_id": run_id},
        )

        logger.info(f"Starting document refinement for {file_hash}")
        span.event(name="refinement_started")

        update_asset_status(file_hash, "processing_refined")

        api_key = os.getenv("MARKER_API_KEY")
        base_url = "https://www.datalab.to/api/v1/marker"
        headers = {"X-Api-Key": api_key}

        file_path = os.path.join(
            "/app/filestore/raw",
            f"{file_hash}{os.path.splitext(asset['original_name'])[1]}",
        )

        marker_generation = span.generation(
            name="marker_api_processing",
            input=file_path,
            metadata={"file_hash": file_hash, "file_name": asset["original_name"]},
        )
        try:
            with open(file_path, "rb") as f:
                files = {
                    "file": (asset["original_name"], f, asset["file_type"]),
                    "langs": (None, "English"),
                    "force_ocr": (None, False),
                    "paginate": (None, False),
                }
                response = requests.post(base_url, files=files, headers=headers)

            if not response.ok:
                error_msg = f"Marker API request failed: {response.text}"
                handle_error(span, file_hash, error_msg, logger, update_asset_status)
                raise HTTPException(status_code=response.status_code, detail=error_msg)

            initial_data = response.json()
            marker_generation.event(name="marker_api_initial_response")

            max_polls = 300
            poll_interval = 2
            request_check_url = initial_data["request_check_url"]

            for attempt in range(max_polls):
                time.sleep(poll_interval)
                response = requests.get(request_check_url, headers=headers)
                data = response.json()

                if data["status"] == "complete":
                    if not data["success"]:
                        error_msg = f"Marker processing failed: {data.get('error', 'Unknown error')}"
                        handle_error(
                            marker_generation,
                            file_hash,
                            error_msg,
                            logger,
                            update_asset_status,
                        )
                        raise HTTPException(status_code=500, detail=error_msg)

                    marker_generation.event(name="marker_api_processing_complete")
                    break

                if attempt % 10 == 0:
                    logger.debug(
                        f"Still waiting for results. Attempt {attempt + 1}/{max_polls}"
                    )
                    marker_generation.event(
                        name="marker_api_polling", metadata={"attempt": attempt + 1}
                    )

            if data["status"] != "complete":
                error_msg = f"Marker processing timed out after {max_polls} attempts"
                handle_error(
                    marker_generation, file_hash, error_msg, logger, update_asset_status
                )
                raise HTTPException(status_code=500, detail=error_msg)

        finally:
            marker_generation.end(
                output=data,
            )

        processed_dir = os.path.join("/app/filestore/processed", file_hash)
        os.makedirs(processed_dir, exist_ok=True)

        markdown_path = os.path.join(processed_dir, "content.md")
        with open(markdown_path, "w", encoding="utf-8") as f:
            f.write(data["markdown"])

        meta_path = os.path.join(processed_dir, "meta.json")
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(data["meta"], f, ensure_ascii=False, indent=2)

        update_data = {
            "processed_paths.markdown": markdown_path,
            "processed_paths.meta": meta_path,
            "page_count": data.get("page_count", 1),
            "status": "refined_complete",
        }
        db["raw_assets"].update_one({"file_hash": file_hash}, {"$set": update_data})

        logger.info(f"Successfully refined document {file_hash}")
        span.event(
            name="refinement_complete",
            metadata={
                "markdown_path": markdown_path,
                "meta_path": meta_path,
                "page_count": data.get("page_count", 1),
            },
        )

        return {
            "status": "success",
            "markdown_path": markdown_path,
            "meta_path": meta_path,
            "page_count": data.get("page_count", 1),
        }

    except Exception as e:
        error_msg = f"Error refining document: {str(e)}"
        if "span" in locals():
            handle_error(span, file_hash, error_msg, logger, update_asset_status)
        raise HTTPException(status_code=500, detail=error_msg)

    finally:
        if "span" in locals():
            span.end()
            time.sleep(0.5)
