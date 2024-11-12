# api/jobs/assets/metadata.py
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
    dependencies = ["refined"]

    def __init__(self, file_hash: str):
        super().__init__(file_hash)

    def process(self, span):
        """Extract metadata from processed content"""
        try:
            update_asset_status(self.file_hash, "processing_metadata")
            logger.info(f"Starting metadata extraction for {self.file_hash}")

            # Get the processed markdown content
            processed_paths = self.asset.get("processed_paths", {})
            if not processed_paths or "markdown" not in processed_paths:
                error_msg = "Markdown content not available - need to wait for refined processor"
                logger.error(error_msg)
                raise Exception(error_msg)

            # Read the prompt template
            prompts_dir = os.path.join("/app", "prompts", "assets")
            with open(os.path.join(prompts_dir, "metadata.txt"), "r") as f:
                prompt_template = f.read()

            # Read the processed content
            with open(processed_paths["markdown"], "r") as f:
                file_content = f.read()
                logger.debug(
                    f"Read {len(file_content)} characters from processed content"
                )

            # Prepare the prompt
            prompt = prompt_template + "\n\nDocument Content:\n" + file_content

            # Call the chat API
            logger.debug("Calling chat API for metadata extraction")
            response = requests.post(
                "http://api:8000/chat", json={"query": prompt, "messages": []}
            )

            if not response.ok:
                error_msg = f"Chat API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)

            # Parse the response
            chat_response = response.json()
            response_text = chat_response["message"]
            logger.info(f"Chat API response: {response_text}")

            # Extract JSON from response
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1

            if json_start < 0 or json_end <= json_start:
                error_msg = "Could not find JSON in chat response"
                logger.error(error_msg)
                raise Exception(error_msg)

            json_str = response_text[json_start:json_end]

            try:
                metadata = json.loads(json_str)
                logger.info(f"Metadata extracted: {metadata}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse metadata JSON: {str(e)}")
                logger.debug(f"Attempted to parse: {json_str}")
                raise

            # Save metadata to a file
            metadata_path = os.path.join(self.processed_dir, "metadata.json")
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            # Update asset with metadata and path
            update_data = {
                "metadata": metadata,
                "processed_paths.metadata": metadata_path,
            }
            self._update_asset(update_data)

            logger.info(f"Completed metadata extraction for {self.file_hash}")
            update_asset_status(self.file_hash, "metadata_complete")
            self.trace_output(
                span=span,
                input={"prompt": prompt},
                output={"metadata": metadata},
            )
            return True

        except Exception as e:
            logger.error(f"Error extracting metadata for {self.file_hash}: {str(e)}")
            update_asset_status(self.file_hash, "metadata_error", str(e))
            raise

    def _extract_json_safely(self, text: str) -> dict:
        """Safely extract and parse JSON from text"""
        try:
            # Find the first { and last }
            json_start = text.find("{")
            json_end = text.rfind("}") + 1

            if json_start < 0 or json_end <= json_start:
                raise ValueError("No JSON object found in text")

            json_str = text[json_start:json_end]

            # Try to parse the JSON
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                # If direct parsing fails, try to clean the string
                cleaned_str = json_str.replace("\n", " ").replace("\r", "")
                return json.loads(cleaned_str)

        except Exception as e:
            logger.error(f"JSON extraction failed: {str(e)}")
            logger.debug(f"Problematic text: {text[:500]}...")  # Log first 500 chars
            raise
