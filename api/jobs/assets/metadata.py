# jobs/assets/metadata.py
import json
import logging
import os

import requests
from jobs.assets.base import AssetProcessor
from utils.db_utils import update_asset_status

logger = logging.getLogger(__name__)


class MetadataProcessor(AssetProcessor):
    """Extract metadata from document content using Chat API"""

    processor_type = "metadata"

    def process(self):
        try:
            update_asset_status(self.file_hash, "processing_metadata")

            # Get the processed markdown content
            processed_paths = self.asset.get("processed_paths", {})
            if not processed_paths or "markdown" not in processed_paths:
                raise Exception(
                    "Markdown content not available - need to wait for refined processor"
                )

            # Read the prompt template
            prompts_dir = os.path.join("/app", "prompts", "assets")
            with open(os.path.join(prompts_dir, "metadata.txt"), "r") as f:
                prompt_template = f.read()

            # Read the file content
            with open(processed_paths["markdown"], "r") as f:
                file_content = f.read()

            # Prepare the prompt
            prompt = prompt_template + "\n\nDocument Content:\n" + file_content

            # Call the chat API
            response = requests.post(
                "http://api:8000/chat", json={"query": prompt, "messages": []}
            )

            if not response.ok:
                raise Exception(
                    f"Chat API error: {response.status_code} - {response.text}"
                )

            # Parse the response
            chat_response = response.json()
            response_text = chat_response["message"]

            # Extract JSON from response
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1

            if json_start < 0 or json_end <= json_start:
                raise Exception("Could not find JSON in chat response")

            json_str = response_text[json_start:json_end]
            metadata = json.loads(json_str)

            # Update asset with metadata
            self._update_asset({"metadata": metadata})

            update_asset_status(self.file_hash, "metadata_complete")

        except Exception as e:
            logger.error(f"Error extracting metadata for {self.file_hash}: {str(e)}")
            update_asset_status(self.file_hash, "metadata_error", str(e))
            raise
