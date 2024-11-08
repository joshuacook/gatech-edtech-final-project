# api/jobs/assets/images.py
import hashlib
import logging
import os
import zipfile
from typing import Dict

from jobs.assets.base import AssetProcessor
from langfuse.decorators import observe
from utils.db_utils import update_asset_status

logger = logging.getLogger(__name__)


class ImageProcessor(AssetProcessor):
    """Process images from DOCX files"""

    processor_type = "images"
    dependencies = []

    # Allowed image extensions
    VALID_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp"}

    def __init__(self, file_hash: str):
        super().__init__(file_hash)

    @observe(name="asset_processor_images")
    def process(self):
        """Main processing method"""
        try:
            # Check if file is a DOCX
            if (
                self.asset["file_type"]
                != "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ):
                logger.info(
                    f"Asset {self.file_hash} is not a DOCX file, skipping image processing"
                )
                update_asset_status(self.file_hash, "images_skipped")
                return True

            update_asset_status(self.file_hash, "processing_images")
            logger.info(f"Starting image processing for {self.file_hash}")

            # Create images directory
            images_dir = os.path.join(self.processed_dir, "images")
            os.makedirs(images_dir, exist_ok=True)

            # Process images
            image_paths = self._process_images(images_dir)

            # Update asset record
            update_data = {
                "has_images": len(image_paths) > 0,
                "image_count": len(image_paths),
                "processed_paths.images": image_paths,
            }
            self._update_asset(update_data)

            logger.info(
                f"Completed image processing for {self.file_hash}: found {len(image_paths)} images"
            )
            update_asset_status(self.file_hash, "images_complete")

            return True

        except Exception as e:
            logger.error(f"Error processing images for {self.file_hash}: {str(e)}")
            update_asset_status(self.file_hash, "images_error", str(e))
            raise

    def _process_images(self, images_dir: str) -> Dict[str, str]:
        """Extract and save images from DOCX"""
        image_paths = {}

        try:
            with zipfile.ZipFile(self.get_raw_file_path()) as doc_zip:
                media_files = [
                    f for f in doc_zip.namelist() if f.startswith("word/media/")
                ]
                logger.debug(f"Found {len(media_files)} media files in DOCX")

                for file_path in media_files:
                    try:
                        # Process each media file
                        image_info = self._process_single_image(
                            doc_zip, file_path, images_dir
                        )
                        if image_info:
                            image_paths.update(image_info)

                    except Exception as img_error:
                        logger.error(
                            f"Error processing image {file_path}: {str(img_error)}"
                        )
                        continue

            # Generate and save image metadata
            if image_paths:
                self._save_image_metadata(images_dir, image_paths)

            return image_paths

        except Exception as e:
            logger.error(f"Error extracting images from DOCX: {str(e)}")
            raise

    def _process_single_image(
        self, doc_zip: zipfile.ZipFile, file_path: str, images_dir: str
    ) -> Dict[str, str]:
        """Process a single image from the DOCX file"""
        try:
            # Get file extension and check if it's a valid image
            _, ext = os.path.splitext(file_path.lower())
            if ext not in self.VALID_IMAGE_EXTENSIONS:
                logger.debug(f"Skipping non-image file: {file_path}")
                return None

            # Read image data
            image_data = doc_zip.read(file_path)

            # Generate a hash of the image content
            image_hash = hashlib.md5(image_data).hexdigest()

            # Create a unique filename using the hash and original extension
            unique_filename = f"{image_hash}{ext}"
            image_path = os.path.join(images_dir, unique_filename)

            # Save the image if it doesn't already exist
            if not os.path.exists(image_path):
                with open(image_path, "wb") as f:
                    f.write(image_data)
                logger.debug(f"Saved new image: {unique_filename}")
            else:
                logger.debug(f"Image already exists: {unique_filename}")

            # Create and return image info
            original_name = os.path.basename(file_path)
            return {original_name: image_path}

        except Exception as e:
            logger.error(f"Error processing single image {file_path}: {str(e)}")
            return None

    def _save_image_metadata(self, images_dir: str, image_paths: Dict[str, str]):
        """Save metadata about processed images"""
        try:
            metadata = {
                name: {
                    "path": path,
                    "size": os.path.getsize(path),
                    "filename": os.path.basename(path),
                }
                for name, path in image_paths.items()
            }

            metadata_path = os.path.join(images_dir, "images_meta.json")
            with open(metadata_path, "w", encoding="utf-8") as f:
                import json

                json.dump(metadata, f, ensure_ascii=False, indent=2)

            logger.debug(f"Saved image metadata to {metadata_path}")

        except Exception as e:
            logger.error(f"Error saving image metadata: {str(e)}")
            # Don't raise - this is not critical

    def _validate_image(self, image_path: str) -> bool:
        """Validate that the file is actually an image"""
        try:
            # You could add additional validation here, such as:
            # - File signature checking
            # - Image library validation (e.g., using Pillow)
            # - Size limits
            # - Format-specific validation

            # Basic size check
            size = os.path.getsize(image_path)
            if size == 0:
                logger.warning(f"Empty image file detected: {image_path}")
                return False

            if size > 50 * 1024 * 1024:  # 50MB limit
                logger.warning(f"Image too large: {image_path}")
                return False

            return True

        except Exception as e:
            logger.error(f"Error validating image {image_path}: {str(e)}")
            return False

    def cleanup(self):
        """Clean up any temporary files if needed"""
        try:
            # Add any cleanup logic here
            pass
        except Exception as e:
            logger.error(f"Error in cleanup: {str(e)}")
