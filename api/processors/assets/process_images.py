import hashlib
import logging
import os
import zipfile
from typing import Any, Dict

from processors.base import BaseAssetProcessor

logger = logging.getLogger(__name__)


class ProcessImages(BaseAssetProcessor):
    def __init__(self):
        super().__init__(
            processor_name="images", processor_type="images", requires_docx=True
        )

    async def process_asset(
        self, file_hash: str, asset: Dict[str, Any], db: Any, span: Any
    ) -> Dict[str, Any]:
        processed_dir = self.get_processed_dir(file_hash)
        images_dir = os.path.join(processed_dir, "images")
        os.makedirs(images_dir, exist_ok=True)

        image_paths = {}
        valid_extensions = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp"}

        with zipfile.ZipFile(
            os.path.join("/app/filestore/raw", f"{file_hash}.docx")
        ) as doc_zip:
            media_files = [f for f in doc_zip.namelist() if f.startswith("word/media/")]

            for file_path in media_files:
                _, ext = os.path.splitext(file_path.lower())
                if ext not in valid_extensions:
                    continue

                image_data = doc_zip.read(file_path)
                image_hash = hashlib.md5(image_data).hexdigest()
                unique_filename = f"{image_hash}{ext}"
                image_path = os.path.join(images_dir, unique_filename)

                if not os.path.exists(image_path):
                    with open(image_path, "wb") as f:
                        f.write(image_data)

                original_name = os.path.basename(file_path)
                image_paths[original_name] = image_path

        update_data = {
            "has_images": len(image_paths) > 0,
            "image_count": len(image_paths),
            "processed_paths.images": image_paths,
        }
        db["raw_assets"].update_one({"file_hash": file_hash}, {"$set": update_data})

        return {
            "status": "success",
            "image_count": len(image_paths),
        }
