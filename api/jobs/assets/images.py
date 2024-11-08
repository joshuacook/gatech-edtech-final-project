# api/jobs/assets/images.py
import logging
import os
import zipfile
from typing import Dict

from jobs.assets.base import AssetProcessor
from utils.db_utils import update_asset_status

logger = logging.getLogger(__name__)


class ImageProcessor(AssetProcessor):
    """Process images from DOCX files"""

    processor_type = "images"

    def process(self):
        """Main processing method"""
        try:
            if (
                self.asset["file_type"]
                != "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ):
                logger.info(
                    f"Asset {self.file_hash} is not a DOCX file, skipping image processing"
                )
                return

            update_asset_status(self.file_hash, "processing_images")

            images_dir = os.path.join(self.processed_dir, "images")
            image_paths = self._process_images(images_dir)

            update_data = {
                "has_images": len(image_paths) > 0,
                "image_count": len(image_paths),
                "processed_paths.images": image_paths,
            }
            self._update_asset(update_data)

            update_asset_status(self.file_hash, "images_complete")

        except Exception as e:
            logger.error(f"Error processing images for {self.file_hash}: {str(e)}")
            update_asset_status(self.file_hash, "images_error", str(e))
            raise

    def _process_images(self, images_dir: str) -> Dict[str, str]:
        """Extract and save images from DOCX"""
        image_paths = {}
        os.makedirs(images_dir, exist_ok=True)

        try:
            with zipfile.ZipFile(self.get_raw_file_path()) as doc_zip:
                logger.debug(f"Files in DOCX: {doc_zip.namelist()}")

                for file in doc_zip.filelist:
                    if file.filename.startswith("word/media/"):
                        try:
                            filename = os.path.basename(file.filename)
                            image_path = os.path.join(images_dir, filename)

                            image_data = doc_zip.read(file.filename)
                            with open(image_path, "wb") as f:
                                f.write(image_data)

                            image_paths[filename] = image_path
                            logger.debug(f"Successfully saved image: {filename}")

                        except Exception as img_error:
                            logger.error(
                                f"Error processing image {file.filename}: {str(img_error)}"
                            )
                            continue
        except Exception as e:
            logger.error(f"Error extracting images from DOCX: {str(e)}")

        return image_paths
