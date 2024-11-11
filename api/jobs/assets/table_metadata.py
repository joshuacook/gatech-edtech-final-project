# jobs/assets/table_metadata.py
import json
import logging
import os

import requests
from jobs.assets.base import AssetProcessor
from utils.db_utils import update_asset_status

logger = logging.getLogger(__name__)


class TableMetadataProcessor(AssetProcessor):
    """Process metadata for extracted tables using AI analysis"""

    processor_type = "table_metadata"
    dependencies = ["tables"]

    def __init__(self, file_hash: str):
        super().__init__(file_hash)

    def process(self):
        """Main processing method"""
        try:
            update_asset_status(self.file_hash, "processing_table_metadata")
            logger.info(f"Starting table metadata processing for {self.file_hash}")

            processed_paths = self.asset.get("processed_paths", {})
            tables = processed_paths.get("tables", {})

            if not tables:
                logger.info(f"No tables found for {self.file_hash}, skipping metadata")
                update_asset_status(self.file_hash, "table_metadata_skipped")
                return True

            table_metadata = {}

            prompts_dir = os.path.join("/app", "prompts", "assets", "table")
            with open(os.path.join(prompts_dir, "metadata.txt"), "r") as f:
                prompt_template = f.read()

            for table_name, paths in tables.items():
                try:
                    csv_path = paths.get("csv")
                    if not csv_path or not os.path.exists(csv_path):
                        continue

                    with open(csv_path, "r", encoding="utf-8") as f:
                        table_content = f.read()

                    prompt = f"{prompt_template}\n\nTable Content:\n{table_content}"

                    response = requests.post(
                        "http://api:8000/chat", json={"query": prompt, "messages": []}
                    )

                    if not response.ok:
                        raise Exception(f"Chat API error: {response.status_code}")

                    chat_response = response.json()
                    response_text = chat_response["message"]

                    json_start = response_text.find("{")
                    json_end = response_text.rfind("}") + 1

                    if json_start < 0 or json_end <= json_start:
                        raise Exception("Could not find JSON in chat response")

                    metadata = json.loads(response_text[json_start:json_end])
                    table_metadata[table_name] = metadata

                except Exception as e:
                    logger.error(f"Error processing table {table_name}: {str(e)}")
                    continue

            if table_metadata:
                metadata_path = os.path.join(
                    self.processed_dir, "tables", "table_metadata.json"
                )
                os.makedirs(os.path.dirname(metadata_path), exist_ok=True)

                with open(metadata_path, "w", encoding="utf-8") as f:
                    json.dump(table_metadata, f, ensure_ascii=False, indent=2)

                update_data = {
                    "processed_paths.table_metadata": metadata_path,
                    "table_metadata": table_metadata,  # Store in document for easy access
                }
                self._update_asset(update_data)

            logger.info(f"Completed table metadata processing for {self.file_hash}")
            update_asset_status(self.file_hash, "table_metadata_complete")
            return True

        except Exception as e:
            logger.error(
                f"Error processing table metadata for {self.file_hash}: {str(e)}"
            )
            update_asset_status(self.file_hash, "table_metadata_error", str(e))
            raise
