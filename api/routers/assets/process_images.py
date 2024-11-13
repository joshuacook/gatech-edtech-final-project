# api/routers/assets.py

import hashlib
import logging
import os
import zipfile
from typing import Dict, Optional

from fastapi import APIRouter, Header, HTTPException
from langfuse import Langfuse
from utils.db_utils import init_mongo, update_asset_status
from utils.langfuse_utils import configure_langfuse

logger = logging.getLogger(__name__)
process_images_router = APIRouter()

configure_langfuse()
langfuse = Langfuse()


@process_images_router.post("/process_images/{file_hash}")
async def process_images(
    file_hash: str,
    x_span_id: Optional[str] = Header(None),
    x_run_id: Optional[str] = Header(None),
) -> Dict:
    """Process images from a DOCX file"""
    try:
        db = init_mongo()
        if isinstance(db, dict) and "error" in db:
            raise HTTPException(status_code=500, detail=db["error"])

        asset = db["raw_assets"].find_one({"file_hash": file_hash})
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")

        if (
            asset["file_type"]
            != "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ):
            logger.info(
                f"Asset {file_hash} is not a DOCX file, skipping image processing"
            )
            update_asset_status(file_hash, "images_skipped")
            return {"status": "skipped", "reason": "not_docx"}

        run_id = x_run_id or asset.get("current_run_id")
        if not run_id:
            raise HTTPException(status_code=400, detail="No run_id found for asset")

        trace = langfuse.trace(
            name="asset-processing",
            id=run_id,
            metadata={
                "file_hash": file_hash,
                "file_name": asset["original_name"],
                "file_type": asset["file_type"],
                "file_size": asset["file_size"],
            },
        )

        span = trace.span(
            id=x_span_id,
            name="image_processing",
            metadata={"processor_type": "images", "run_id": run_id},
        )

        update_asset_status(file_hash, "processing_images")
        logger.info(f"Starting image processing for {file_hash}")

        # Create images directory
        processed_dir = os.path.join("/app/filestore/processed", file_hash)
        images_dir = os.path.join(processed_dir, "images")
        os.makedirs(images_dir, exist_ok=True)

        # Process images
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

        # Update asset record
        update_data = {
            "has_images": len(image_paths) > 0,
            "image_count": len(image_paths),
            "processed_paths.images": image_paths,
        }
        db["raw_assets"].update_one({"file_hash": file_hash}, {"$set": update_data})

        logger.info(f"Completed image processing for {file_hash}")
        update_asset_status(file_hash, "images_complete")

        span.event(
            name="image_processing_complete",
            metadata={"image_count": len(image_paths)},
        )

        return {
            "status": "success",
            "image_count": len(image_paths),
            "image_paths": image_paths,
        }

    except Exception as e:
        error_msg = f"Error processing images: {str(e)}"
        if "span" in locals():
            span.event(
                name="image_processing_error",
                metadata={"error": error_msg},
                level="error",
            )
        update_asset_status(file_hash, "images_error", error=error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

    finally:
        if "span" in locals():
            span.end()
