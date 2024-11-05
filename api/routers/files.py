# api/routers/files.py

import hashlib
import json
import logging
import os
from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse as FastAPIFileResponse
from pydantic import BaseModel
from pymongo import MongoClient
from redis import Redis
from rq import Queue

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class ProcessedPaths(BaseModel):
    markdown: str
    images: dict[str, str] = {}
    tables: dict[str, str] = {}
    meta: str


class FileResponse(BaseModel):
    id: str
    name: str
    size: int
    type: str
    status: str
    upload_date: str
    processed_date: Optional[str] = None
    error: Optional[str] = None
    processed_paths: Optional[ProcessedPaths] = None
    has_images: bool = False
    image_count: int = 0
    has_tables: bool = False
    table_count: int = 0


class FileDetailResponse(FileResponse):
    preview: Optional[str] = None
    processing_details: Optional[dict] = None


files_router = APIRouter()


def format_datetime(dt) -> str:
    """Convert datetime object to ISO format string"""
    if isinstance(dt, datetime):
        return dt.isoformat()
    return dt


# Initialize MongoDB connection
def get_db():
    try:
        client = MongoClient(os.getenv("MONGODB_URI", "mongodb://db:27017/"))
        db = client["chelle"]
        client.admin.command("ping")
        logger.debug("Successfully connected to MongoDB")
        return db
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise HTTPException(status_code=500, detail="Database connection failed")


# Initialize Redis connection
def get_redis_queue():
    try:
        redis_conn = Redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379"))
        return Queue("default", connection=redis_conn)
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {str(e)}")
        raise HTTPException(status_code=500, detail="Redis connection failed")


def save_file(file_data: bytes, original_filename: str, content_type: str) -> dict:
    """Save uploaded file to disk and return file details"""
    try:
        # Generate file hash
        file_hash = hashlib.sha256(file_data).hexdigest()

        # Create filestore directory structure
        filestore_base = os.path.join("/app", "filestore")
        raw_dir = os.path.join(filestore_base, "raw")
        os.makedirs(raw_dir, exist_ok=True)

        # Determine file extension and create filepath
        file_extension = os.path.splitext(original_filename)[1]
        stored_filename = f"{file_hash}{file_extension}"
        filepath = os.path.join(raw_dir, stored_filename)

        # Save file
        with open(filepath, "wb") as f:
            f.write(file_data)

        return {
            "file_hash": file_hash,
            "original_name": original_filename,
            "stored_name": stored_filename,
            "file_path": filepath,
            "file_type": content_type,
            "file_size": len(file_data),
        }
    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save file")


@files_router.post("/upload", response_model=FileResponse)
async def upload_file(file: UploadFile = File(...)):
    """Handle file upload and queue processing job"""
    try:
        logger.debug(f"Processing upload for file: {file.filename}")

        # Read file content
        file_content = await file.read()

        # Save file to disk
        file_details = save_file(file_content, file.filename, file.content_type)

        # Create database record
        db = get_db()
        raw_assets = db["raw_assets"]

        asset_record = {
            "original_name": file_details["original_name"],
            "stored_name": file_details["stored_name"],
            "file_path": file_details["file_path"],
            "file_hash": file_details["file_hash"],
            "file_type": file_details["file_type"],
            "file_size": file_details["file_size"],
            "upload_date": datetime.now(),
            "status": "uploaded",
            "processed": False,
        }

        result = raw_assets.insert_one(asset_record)

        # Queue processing job
        queue = get_redis_queue()
        job = queue.enqueue(
            "jobs.process_with_marker", file_details["file_hash"], job_timeout="1h"
        )

        logger.debug(f"Created job {job.id} for file {file_details['file_hash']}")

        # Update record with job ID
        raw_assets.update_one({"_id": result.inserted_id}, {"$set": {"job_id": job.id}})

        return FileResponse(
            id=str(result.inserted_id),
            name=file_details["original_name"],
            size=file_details["file_size"],
            type=file_details["file_type"],
            status="uploaded",
            upload_date=datetime.now().isoformat(),
        )

    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@files_router.get("/files", response_model=List[FileResponse])
async def list_files():
    """Get list of all files"""
    try:
        logger.debug("Fetching file list")
        db = get_db()
        raw_assets = db["raw_assets"]

        files = []
        for asset in raw_assets.find().sort("upload_date", -1):
            try:
                # Convert MongoDB ObjectId to string
                asset_id = str(asset["_id"])

                # Format dates
                upload_date = format_datetime(asset["upload_date"])
                processed_date = (
                    format_datetime(asset.get("processed_date"))
                    if asset.get("processed_date")
                    else None
                )

                # Get image information
                processed_paths = asset.get("processed_paths", {})
                images = processed_paths.get("images", {})

                # Create response object
                file_response = FileResponse(
                    id=asset_id,
                    name=asset["original_name"],
                    size=asset["file_size"],
                    type=asset["file_type"],
                    status=asset.get("status", "unknown"),
                    upload_date=upload_date,
                    processed_date=processed_date,
                    error=asset.get("error"),
                    processed_paths=ProcessedPaths(
                        markdown=processed_paths.get("markdown", ""),
                        images=images,
                        tables=processed_paths.get("tables", {}),
                        meta=processed_paths.get("meta", ""),
                    )
                    if processed_paths
                    else None,
                    has_images=len(images) > 0,
                    image_count=len(images),
                    has_tables=bool(processed_paths.get("tables")),
                    table_count=len(processed_paths.get("tables", {}))
                    if processed_paths
                    else 0,
                )
                files.append(file_response)

                logger.debug(f"Processed file record: {asset_id}")

            except Exception as e:
                logger.error(f"Error processing file record: {str(e)}")
                continue

        logger.debug(f"Returning {len(files)} files")
        return files

    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) @ files_router.get(
            "/files/{file_id}", response_model=FileDetailResponse
        )


async def get_file_details(file_id: str):
    """Get detailed information about a specific file"""
    try:
        logger.debug(f"Fetching details for file: {file_id}")
        db = get_db()
        raw_assets = db["raw_assets"]

        # Convert string ID to ObjectId for MongoDB query
        try:
            obj_id = ObjectId(file_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid file ID format")

        asset = raw_assets.find_one({"_id": obj_id})
        if not asset:
            raise HTTPException(status_code=404, detail="File not found")

        # Get preview content if file is processed
        preview = None
        if asset.get("processed", False) and "processed_paths" in asset:
            try:
                with open(asset["processed_paths"]["markdown"], "r") as f:
                    preview = f.read(1000)  # First 1000 characters as preview
            except Exception as e:
                logger.error(f"Error reading preview: {str(e)}")

        return FileDetailResponse(
            id=str(asset["_id"]),
            name=asset["original_name"],
            size=asset["file_size"],
            type=asset["file_type"],
            status=asset.get("status", "unknown"),
            upload_date=format_datetime(asset["upload_date"]),
            processed_date=format_datetime(asset.get("processed_date"))
            if asset.get("processed_date")
            else None,
            error=asset.get("error"),
            preview=preview,
            processing_details=asset.get("processing_details"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@files_router.get("/files/{file_id}/content")
async def get_file_content(file_id: str):
    """Get the content of a processed file"""
    try:
        db = get_db()
        raw_assets = db["raw_assets"]

        asset = raw_assets.find_one({"_id": ObjectId(file_id)})
        if not asset:
            raise HTTPException(status_code=404, detail="File not found")

        if not asset.get("processed", False) or "processed_paths" not in asset:
            raise HTTPException(status_code=400, detail="File content not available")

        try:
            with open(asset["processed_paths"]["markdown"], "r") as f:
                content = f.read()
            return {"content": content}
        except Exception as e:
            logger.error(f"Error reading content: {str(e)}")
            raise HTTPException(status_code=500, detail="Error reading file content")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@files_router.get("/files/{file_id}/tables/metadata")
async def get_file_tables_metadata(file_id: str):
    """Get metadata for all tables in a file"""
    try:
        db = get_db()
        raw_assets = db["raw_assets"]

        asset = raw_assets.find_one({"_id": ObjectId(file_id)})
        if not asset:
            raise HTTPException(status_code=404, detail="File not found")

        if not asset.get("processed_paths", {}).get("tables", {}):
            raise HTTPException(status_code=404, detail="No tables found for this file")

        tables_dir = os.path.dirname(
            list(asset["processed_paths"]["tables"].values())[0]
        )
        meta_path = os.path.join(tables_dir, "tables_meta.json")

        if not os.path.exists(meta_path):
            raise HTTPException(status_code=404, detail="Table metadata not found")

        with open(meta_path, "r", encoding="utf-8") as f:
            return json.load(f)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving table metadata: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@files_router.get("/files/{file_id}/tables/{table_name}")
async def get_file_table(file_id: str, table_name: str):
    """Get a specific table from a file"""
    try:
        db = get_db()
        raw_assets = db["raw_assets"]

        asset = raw_assets.find_one({"_id": ObjectId(file_id)})
        if not asset:
            raise HTTPException(status_code=404, detail="File not found")

        if not asset.get("processed_paths", {}).get("tables", {}):
            raise HTTPException(status_code=404, detail="No tables found for this file")

        tables = asset["processed_paths"]["tables"]
        if table_name not in tables:
            raise HTTPException(status_code=404, detail="Table not found")

        table_path = tables[table_name]

        # Read and return the HTML content
        with open(table_path, "r") as f:
            table_content = f.read()

        return {"content": table_content}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving table: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@files_router.delete("/files/{file_id}")
async def delete_file(file_id: str):
    """Delete a file and its processed contents"""
    try:
        logger.debug(f"Attempting to delete file: {file_id}")
        db = get_db()
        raw_assets = db["raw_assets"]

        # Get file details
        asset = raw_assets.find_one({"_id": ObjectId(file_id)})
        if not asset:
            raise HTTPException(status_code=404, detail="File not found")

        # Delete raw file
        raw_file_path = os.path.join("/app", "filestore", "raw", asset["stored_name"])
        if os.path.exists(raw_file_path):
            os.remove(raw_file_path)

        # Delete processed files if they exist
        if asset.get("processed_paths"):
            processed_dir = os.path.dirname(asset["processed_paths"]["markdown"])
            if os.path.exists(processed_dir):
                import shutil

                shutil.rmtree(processed_dir)

        # Delete database record
        raw_assets.delete_one({"_id": ObjectId(file_id)})

        return {"message": "File deleted successfully"}

    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@files_router.get("/files/{file_id}/images/{image_name}")
async def get_file_image(file_id: str, image_name: str):
    """Get a specific image from a file"""
    try:
        db = get_db()
        raw_assets = db["raw_assets"]

        # Find the asset
        from bson import ObjectId

        asset = raw_assets.find_one({"_id": ObjectId(file_id)})
        if not asset:
            raise HTTPException(status_code=404, detail="File not found")

        # Check if file has processed images
        if not asset.get("processed_paths", {}).get("images", {}):
            raise HTTPException(status_code=404, detail="No images found for this file")

        # Get the image path
        images = asset["processed_paths"]["images"]
        if image_name not in images:
            raise HTTPException(status_code=404, detail="Image not found")

        image_path = images[image_name]

        # Verify file exists
        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="Image file not found")

        return FastAPIFileResponse(image_path)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
