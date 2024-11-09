# jobs/assets/image_metadata.py
import imghdr
import json
import logging
import os
from typing import Dict

import requests
from jobs.assets.base import AssetProcessor
from PIL import Image
from utils.db_utils import update_asset_status

logger = logging.getLogger(__name__)


class ImageMetadataProcessor(AssetProcessor):
    """Process metadata for extracted images using AI analysis"""

    processor_type = "image_metadata"
    dependencies = ["images"]  # Depends on image extraction

    def __init__(self, file_hash: str):
        super().__init__(file_hash)

    def process(self):
        """Main processing method"""
        try:
            update_asset_status(self.file_hash, "processing_image_metadata")
            logger.info(f"Starting image metadata processing for {self.file_hash}")

            # Check if there are any images
            processed_paths = self.asset.get("processed_paths", {})
            images = processed_paths.get("images", {})

            if not images:
                logger.info(f"No images found for {self.file_hash}, skipping metadata")
                update_asset_status(self.file_hash, "image_metadata_skipped")
                return True

            # Read the prompt template
            prompts_dir = os.path.join("/app", "prompts", "assets", "image")
            with open(os.path.join(prompts_dir, "metadata.txt"), "r") as f:
                prompt_template = f.read()

            image_metadata = {}

            # Process each image
            for image_name, image_path in images.items():
                try:
                    # Get technical metadata
                    technical_metadata = self._get_technical_metadata(
                        image_name, image_path
                    )
                    if not technical_metadata:
                        continue

                    # Convert image info to text description for AI analysis
                    image_description = self._format_image_info(technical_metadata)

                    # Prepare prompt
                    prompt = (
                        f"{prompt_template}\n\nImage Information:\n{image_description}"
                    )

                    # Call chat API for analysis
                    response = requests.post(
                        "http://api:8000/chat", json={"query": prompt, "messages": []}
                    )

                    if not response.ok:
                        raise Exception(f"Chat API error: {response.status_code}")

                    # Parse response
                    chat_response = response.json()
                    response_text = chat_response["message"]

                    # Extract JSON from response
                    json_start = response_text.find("{")
                    json_end = response_text.rfind("}") + 1

                    if json_start < 0 or json_end <= json_start:
                        raise Exception("Could not find JSON in chat response")

                    ai_metadata = json.loads(response_text[json_start:json_end])

                    # Combine technical and AI metadata
                    image_metadata[image_name] = {
                        "technical": technical_metadata,
                        "analysis": ai_metadata,
                    }

                except Exception as e:
                    logger.error(f"Error processing image {image_name}: {str(e)}")
                    continue

            # Save metadata
            if image_metadata:
                metadata_path = os.path.join(
                    self.processed_dir, "images", "image_metadata.json"
                )
                os.makedirs(os.path.dirname(metadata_path), exist_ok=True)

                with open(metadata_path, "w", encoding="utf-8") as f:
                    json.dump(image_metadata, f, ensure_ascii=False, indent=2)

                # Update asset record
                update_data = {
                    "processed_paths.image_metadata": metadata_path,
                    "image_metadata": image_metadata,  # Store in document for easy access
                }
                self._update_asset(update_data)

            logger.info(f"Completed image metadata processing for {self.file_hash}")
            update_asset_status(self.file_hash, "image_metadata_complete")
            return True

        except Exception as e:
            logger.error(
                f"Error processing image metadata for {self.file_hash}: {str(e)}"
            )
            update_asset_status(self.file_hash, "image_metadata_error", str(e))
            raise

    def _get_technical_metadata(self, image_name: str, image_path: str) -> Dict:
        """Get technical metadata from image file"""
        try:
            if not os.path.exists(image_path):
                raise ValueError(f"Image file not found: {image_path}")

            # Get basic file info
            file_size = os.path.getsize(image_path)
            file_type = imghdr.what(image_path)

            # Get image properties using PIL
            with Image.open(image_path) as img:
                width, height = img.size
                mode = img.mode
                format = img.format

                metadata = {
                    "filename": os.path.basename(image_path),
                    "file_size": file_size,
                    "file_type": file_type,
                    "width": width,
                    "height": height,
                    "aspect_ratio": round(width / height, 2),
                    "color_mode": mode,
                    "format": format,
                    "dpi": img.info.get("dpi", None),
                }

            return metadata

        except Exception as e:
            logger.error(f"Error getting technical metadata for {image_name}: {str(e)}")
            return None

    def _format_image_info(self, technical_metadata: Dict) -> str:
        """Format technical metadata as text for AI analysis"""
        lines = [
            f"Filename: {technical_metadata['filename']}",
            f"Dimensions: {technical_metadata['width']}x{technical_metadata['height']} pixels",
            f"Format: {technical_metadata['format']}",
            f"Color Mode: {technical_metadata['color_mode']}",
            f"File Size: {technical_metadata['file_size']} bytes",
            f"Aspect Ratio: {technical_metadata['aspect_ratio']}",
        ]
        if technical_metadata["dpi"]:
            lines.append(f"DPI: {technical_metadata['dpi']}")

        return "\n".join(lines)
