import asyncio
import json
import logging
import os
import time
from typing import Dict

import requests
from fastapi import HTTPException
from processors.base import BaseAssetProcessor
from routers.chat import multimodal_chat_call
from utils import handle_error
from utils.db_utils import update_asset_status

logger = logging.getLogger(__name__)


class ProcessRefined(BaseAssetProcessor):
    def __init__(self):
        super().__init__("refined", "refined")

    async def process_asset(self, file_hash: str, asset: dict, db: dict, span):
        file_path = os.path.join(
            "/app/filestore/raw",
            f"{file_hash}{os.path.splitext(asset['original_name'])[1]}",
        )

        marker_generation = span.generation(
            name="content_processing",
            input=file_path,
            metadata={"file_hash": file_hash, "file_name": asset["original_name"]},
        )

        try:
            if asset["file_type"] == "image/png":
                result = await self._process_image(file_path)
            elif asset["file_type"] == "application/pdf":
                result = await self._process_pdf(file_path, asset, file_hash)
            else:
                result = await self._process_with_marker_api(
                    file_path, asset, headers={"X-Api-Key": os.getenv("MARKER_API_KEY")}
                )

            marker_generation.end(output=result)

            processed_dir = os.path.join("/app/filestore/processed", file_hash)
            os.makedirs(processed_dir, exist_ok=True)

            markdown_path = os.path.join(processed_dir, "content.md")
            with open(markdown_path, "w", encoding="utf-8") as f:
                f.write(result["markdown"])

            meta_path = os.path.join(processed_dir, "meta.json")
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(result["meta"], f, ensure_ascii=False, indent=2)

            update_data = {
                "processed_paths.markdown": markdown_path,
                "processed_paths.meta": meta_path,
                "page_count": result.get("page_count", 1),
                "status": "success",
            }

            if result.get("images"):
                images_dir = os.path.join(processed_dir, "images")
                os.makedirs(images_dir, exist_ok=True)
                image_paths = await self._save_images(result["images"], images_dir)
                update_data["processed_paths.images"] = image_paths
                update_data["has_images"] = True
                update_data["image_count"] = len(image_paths)

            if result.get("tables"):
                tables_dir = os.path.join(processed_dir, "tables")
                os.makedirs(tables_dir, exist_ok=True)
                table_paths = await self._save_tables(result["tables"], tables_dir)
                update_data["processed_paths.tables"] = table_paths
                update_data["has_tables"] = True
                update_data["table_count"] = len(table_paths)

            db["raw_assets"].update_one({"file_hash": file_hash}, {"$set": update_data})

            return result

        except Exception as e:
            error_msg = f"Error in refined processing: {str(e)}"
            handle_error(span, file_hash, error_msg, logger, update_asset_status)
            raise HTTPException(status_code=500, detail=error_msg)

    async def _process_pdf(self, file_path: str, asset: dict, file_hash: str) -> Dict:
        """Process a PDF file using multiple Marker API endpoints"""
        # First get the main content and images using marker endpoint
        marker_result = await self._process_with_marker_api(
            file_path,
            asset,
            headers={"X-Api-Key": os.getenv("MARKER_API_KEY")},
        )
        # Then get table data using table_rec endpoint
        table_result = await self._process_tables(file_path)

        # Combine results
        combined_result = {
            "markdown": marker_result["markdown"],
            "meta": marker_result["meta"],
            "page_count": marker_result["page_count"],
            "images": marker_result.get("images", {}),
            "tables": table_result.get("pages", []),
            "status": "complete",
            "success": True,
        }

        return combined_result

    async def _process_image(self, file_path: str) -> Dict:
        """Process an image file using the chat/with-image endpoint"""
        prompt = """
        Please analyze this image and convert it into well-formatted markdown. If you see:
        
        - Mathematical equations or formulas: Use LaTeX with proper inline (`$...$`) or block (`$$...$$`) delimiters
        - Diagrams or figures: Describe their layout and components clearly
        - Tables: Convert to properly aligned markdown tables
        - Code: Use appropriate markdown code blocks with language specification
        - Handwritten text: Transcribe accurately, preserving any special formatting
        - Scientific notation: Use proper LaTeX notation
        
        Format the output with clear headings, lists, and proper spacing for optimal readability and pandoc compatibility.

        Please return EXACTLY the markdown output only with no formatting, no backticks wrapping the output.
        """
        response = multimodal_chat_call(file_path, prompt)
        message_text = response["message"]
        response_data = {
            "markdown": message_text,
            "meta": {
                "processed_type": "image",
                "processing_method": "claude_vision",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            },
            "page_count": 1,
        }

        return response_data

    async def _process_with_marker_api(
        self, file_path: str, asset: dict, headers: Dict
    ) -> Dict:
        """Process a document using the Marker API"""
        base_url = "https://www.datalab.to/api/v1/marker"

        with open(file_path, "rb") as f:
            files = {
                "file": (asset["original_name"], f, asset["file_type"]),
                "langs": (None, "English"),
                "force_ocr": (None, False),
                "paginate": (None, False),
            }
            response = requests.post(base_url, files=files, headers=headers)

        if not response.ok:
            raise Exception(f"Marker API request failed: {response.text}")

        initial_data = response.json()
        request_check_url = initial_data["request_check_url"]

        # Poll for results
        max_polls = 300
        poll_interval = 2

        for attempt in range(max_polls):
            time.sleep(poll_interval)
            response = requests.get(request_check_url, headers=headers)
            data = response.json()

            if data["status"] == "complete":
                if not data["success"]:
                    raise Exception(f"Marker API processing failed: {data['error']}")
                return data

            if attempt % 10 == 0:
                logger.debug(
                    f"Still waiting for results. Attempt {attempt + 1}/{max_polls}"
                )

        raise Exception(f"Marker API request timed out after {max_polls} attempts")

    async def _save_images(self, images: dict, images_dir: str) -> dict:
        """Save images to disk and return mapping of image names to paths"""
        image_paths = {}
        for name, data in images.items():
            ext = os.path.splitext(name)[1] or ".png"
            path = os.path.join(images_dir, f"{name}{ext}")
            # Convert base64 string to bytes if needed
            if isinstance(data, str):
                import base64

                data = base64.b64decode(data)
            with open(path, "wb") as f:
                f.write(data)
            image_paths[name] = path
        return image_paths

    async def _process_tables(self, file_path: str, max_wait: int = 600) -> Dict:
        """Process PDF tables using table recognition API with exponential backoff"""
        base_url = "https://www.datalab.to/api/v1/tablerec"
        headers = {"X-Api-Key": os.getenv("MARKER_API_KEY")}
        retryable_codes = {
            520,
            429,
            503,
        }  # CloudFlare error, rate limit, service unavailable

        wait = 1
        start = time.time()

        while (time.time() - start) < max_wait:
            try:
                with open(file_path, "rb") as f:
                    files = {"file": f}
                    response = requests.post(base_url, files=files, headers=headers)

                if response.ok:
                    return response.json()

                if response.status_code not in retryable_codes:
                    logger.warning(f"Non-retryable error {response.status_code}")
                    return {
                        "pages": [],
                        "error": f"Table recognition unavailable: {response.status_code}",
                    }

                logger.warning(
                    f"Retryable error {response.status_code}, waiting {wait}s"
                )
                await asyncio.sleep(wait)
                wait = min(wait * 2, 60)

            except Exception as e:
                logger.warning(f"Table recognition error: {str(e)}")
                return {"pages": [], "error": str(e)}

        return {"pages": [], "error": f"Table recognition timed out after {max_wait}s"}
