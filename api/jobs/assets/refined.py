# api/jobs/assets/refined.py
import json
import logging
import os
import time

import requests
from jobs.assets.base import AssetProcessor
from utils.db_utils import update_asset_status

logger = logging.getLogger(__name__)


class RefinedProcessor(AssetProcessor):
    """Process files with Marker API for refined content"""

    processor_type = "refined"

    def __init__(self, file_hash: str):
        super().__init__(file_hash)
        self.api_key = os.getenv("MARKER_API_KEY")
        self.base_url = "https://www.datalab.to/api/v1/marker"
        self.headers = {"X-Api-Key": self.api_key}

    def process(self):
        """Main processing method"""
        try:
            update_asset_status(self.file_hash, "processing_refined")

            # Process with Marker
            initial_data = self._process_file()
            data = self._poll_results(initial_data["request_check_url"])

            # Save results
            markdown_path = os.path.join(self.processed_dir, "content.md")
            os.makedirs(os.path.dirname(markdown_path), exist_ok=True)

            with open(markdown_path, "w", encoding="utf-8") as f:
                f.write(data["markdown"])

            meta_path = os.path.join(self.processed_dir, "meta.json")
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(data["meta"], f, ensure_ascii=False, indent=2)

            update_data = {
                "processed_paths.markdown": markdown_path,
                "processed_paths.meta": meta_path,
                "page_count": data.get("page_count", 1),
            }
            self._update_asset(update_data)

            update_asset_status(self.file_hash, "refined_complete")

        except Exception as e:
            logger.error(
                f"Error processing refined content for {self.file_hash}: {str(e)}"
            )
            update_asset_status(self.file_hash, "refined_error", str(e))
            raise

    def _process_file(self):
        """Send file to Marker API"""
        with open(self.get_raw_file_path(), "rb") as f:
            files = {
                "file": (self.asset["original_name"], f, self.asset["file_type"]),
                "langs": (None, "English"),
                "force_ocr": (None, False),
                "paginate": (None, False),
            }
            response = requests.post(self.base_url, files=files, headers=self.headers)

        if not response.ok:
            raise Exception(f"Marker API request failed: {response.text}")

        return response.json()

    def _poll_results(
        self, request_check_url: str, max_polls: int = 300, poll_interval: int = 2
    ):
        """Poll for results from Marker API"""
        for _ in range(max_polls):
            time.sleep(poll_interval)
            response = requests.get(request_check_url, headers=self.headers)
            data = response.json()

            if data["status"] == "complete":
                if data["success"]:
                    return data
                else:
                    raise Exception(f"Marker processing failed: {data['error']}")

        raise Exception("Marker processing timed out")
