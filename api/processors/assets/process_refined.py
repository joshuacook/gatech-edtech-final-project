import json
import logging
import os
import time

import requests
from fastapi import HTTPException
from processors.base import BaseAssetProcessor
from utils import handle_error
from utils.db_utils import update_asset_status

logger = logging.getLogger(__name__)


class ProcessRefined(BaseAssetProcessor):
    def __init__(self):
        super().__init__("refined", "refined")

    async def process_asset(self, file_hash: str, asset: dict, db: dict, span):
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
                        error_msg = f"Marker API request failed: {data['error']}"
                        handle_error(
                            span, file_hash, error_msg, logger, update_asset_status
                        )
                        raise HTTPException(status_code=400, detail=error_msg)

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
                error_msg = f"Marker API request timed out after {max_polls} attempts"
                handle_error(span, file_hash, error_msg, logger, update_asset_status)
                raise HTTPException(status_code=500, detail=error_msg)

        except Exception as e:
            error_msg = f"Error in refined processing: {str(e)}"
            handle_error(span, file_hash, error_msg, logger, update_asset_status)
            raise HTTPException(status_code=500, detail=error_msg)

        finally:
            marker_generation.end(output=data)

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
            "status": "success",
        }
        db["raw_assets"].update_one({"file_hash": file_hash}, {"$set": update_data})

        return data
