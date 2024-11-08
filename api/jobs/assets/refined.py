# api/jobs/assets/refined.py
import json
import logging
import os
import time

import requests
from jobs.assets.base import AssetProcessor
from langfuse.decorators import langfuse_context, observe
from utils.db_utils import update_asset_status

logger = logging.getLogger(__name__)


class RefinedProcessor(AssetProcessor):
    """Process files with Marker API for refined content"""

    processor_type = "refined"
    dependencies = []

    def __init__(self, file_hash: str):
        super().__init__(file_hash)
        self.api_key = os.getenv("MARKER_API_KEY")
        self.base_url = "https://www.datalab.to/api/v1/marker"
        self.headers = {"X-Api-Key": self.api_key}

    @observe(name="asset_processor_refined")
    def process(self):
        """Main processing method"""
        try:
            update_asset_status(self.file_hash, "processing_refined")
            logger.info(f"Starting refined processing for {self.file_hash}")

            # Update observation with input info
            langfuse_context.update_current_observation(
                input={
                    "file_hash": self.file_hash,
                    "file_name": self.asset["original_name"],
                    "file_type": self.asset["file_type"],
                }
            )

            # Process with Marker
            initial_data = self._process_file()
            data = self._poll_results(initial_data["request_check_url"])

            langfuse_context.update_current_observation(
                output={
                    "markdown": data["markdown"][:1000],  # First 1000 chars for logging
                    "page_count": data.get("page_count", 1),
                }
            )

            # Save results
            markdown_path = os.path.join(self.processed_dir, "content.md")
            os.makedirs(os.path.dirname(markdown_path), exist_ok=True)

            with open(markdown_path, "w", encoding="utf-8") as f:
                f.write(data["markdown"])

            meta_path = os.path.join(self.processed_dir, "meta.json")
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(data["meta"], f, ensure_ascii=False, indent=2)

            # Update asset record with processed paths
            update_data = {
                "processed_paths.markdown": markdown_path,
                "processed_paths.meta": meta_path,
                "page_count": data.get("page_count", 1),
            }
            self._update_asset(update_data)

            logger.info(f"Completed refined processing for {self.file_hash}")
            update_asset_status(self.file_hash, "refined_complete")

            return True

        except Exception as e:
            logger.error(
                f"Error processing refined content for {self.file_hash}: {str(e)}"
            )
            langfuse_context.update_current_observation(
                level="ERROR", metadata={"error": str(e)}
            )
            update_asset_status(self.file_hash, "refined_error", str(e))
            raise

    def _process_file(self):
        """Send file to Marker API"""
        logger.debug(f"Sending file {self.file_hash} to Marker API")

        try:
            with open(self.get_raw_file_path(), "rb") as f:
                files = {
                    "file": (self.asset["original_name"], f, self.asset["file_type"]),
                    "langs": (None, "English"),
                    "force_ocr": (None, False),
                    "paginate": (None, False),
                }
                response = requests.post(
                    self.base_url, files=files, headers=self.headers
                )

            if not response.ok:
                error_msg = f"Marker API request failed: {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)

            return response.json()

        except Exception as e:
            logger.error(f"Error in _process_file: {str(e)}")
            raise

    def _poll_results(
        self, request_check_url: str, max_polls: int = 300, poll_interval: int = 2
    ):
        """Poll for results from Marker API"""
        logger.debug(f"Starting to poll results for {self.file_hash}")

        for attempt in range(max_polls):
            try:
                time.sleep(poll_interval)
                response = requests.get(request_check_url, headers=self.headers)
                data = response.json()

                if data["status"] == "complete":
                    if data["success"]:
                        logger.info(
                            f"Successfully retrieved results for {self.file_hash}"
                        )
                        return data
                    else:
                        error_msg = f"Marker processing failed: {data.get('error', 'Unknown error')}"
                        logger.error(error_msg)
                        raise Exception(error_msg)

                if attempt % 10 == 0:  # Log progress every 10 attempts
                    logger.debug(
                        f"Still waiting for results. Attempt {attempt + 1}/{max_polls}"
                    )

            except Exception as e:
                logger.error(f"Error polling results: {str(e)}")
                raise

        error_msg = f"Marker processing timed out after {max_polls} attempts"
        logger.error(error_msg)
        raise Exception(error_msg)
