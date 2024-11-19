# api/routers/files.py
import json
import logging
import os
from datetime import datetime
from typing import List

from bson import ObjectId
from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse as FastAPIFileResponse
from jobs.assets.base import AssetProcessor
from models.files import FileDetailResponse, FileResponse, ProcessedPaths
from services.database import get_db
from utils import format_datetime, save_file
from utils.table_utils import convert_table_paths

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


files_router = APIRouter()


@files_router.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...)):
    try:
        allowed_types = {
            "application/pdf": ".pdf",
            "image/png": ".png",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
        }
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.content_type}. Supported types are: {', '.join(allowed_types.keys())}",
            )

        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext != allowed_types[file.content_type]:
            raise HTTPException(
                status_code=400,
                detail=f"File extension '{file_ext}' does not match content type '{file.content_type}'",
            )
        file_content = await file.read()
        file_details = save_file(file_content, file.filename, file.content_type)
        if "error" in file_details:
            raise HTTPException(status_code=500, detail=file_details["error"])

        db = get_db()
        if isinstance(db, dict) and "error" in db:
            raise HTTPException(status_code=500, detail=db["error"])
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
        logger.info(file_details)

        AssetProcessor.queue_initial_processors(file_details["file_hash"])

        return FileResponse(
            id=str(result.inserted_id),
            name=file_details["original_name"],
            size=file_details["file_size"],
            type=file_details["file_type"],
            status="processing_queued",
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
        if isinstance(db, dict) and "error" in db:
            raise HTTPException(status_code=500, detail=db["error"])
        raw_assets = db["raw_assets"]

        count = raw_assets.count_documents({})
        logger.debug(f"Found {count} documents in raw_assets")

        files = []
        cursor = raw_assets.find().sort("upload_date", -1)

        for asset in cursor:
            try:
                logger.debug(
                    f"Processing asset: {asset.get('original_name', 'unknown')}"
                )

                asset_id = str(asset["_id"])

                upload_date = format_datetime(asset["upload_date"])
                processed_date = (
                    format_datetime(asset.get("processed_date"))
                    if asset.get("processed_date")
                    else None
                )

                processed_paths = asset.get("processed_paths", {})
                if not isinstance(processed_paths, dict):
                    processed_paths = {}

                tables = processed_paths.get("tables", {})
                converted_tables = convert_table_paths(tables)

                paths = ProcessedPaths(
                    markdown=processed_paths.get("markdown", ""),
                    images=processed_paths.get("images", {}),
                    tables=converted_tables,
                    meta=processed_paths.get("meta", ""),
                    metadata=processed_paths.get("metadata", ""),
                )
                metadata = asset.get("metadata")
                if metadata:
                    logger.debug(f"Found metadata for {asset_id}: {metadata}")

                file_response = FileResponse(
                    id=asset_id,
                    name=asset["original_name"],
                    size=asset["file_size"],
                    type=asset["file_type"],
                    status=asset.get("status", "unknown"),
                    upload_date=upload_date,
                    processed_date=processed_date,
                    error=asset.get("error"),
                    processed_paths=paths,
                    has_images=bool(asset.get("has_images", False)),
                    image_count=asset.get("image_count", 0),
                    has_tables=bool(asset.get("has_tables", False)),
                    table_count=asset.get("table_count", 0),
                    metadata=metadata,
                )

                logger.debug(f"Created FileResponse for {asset_id}")
                files.append(file_response)

            except Exception as e:
                logger.error(f"Error processing file record: {str(e)}", exc_info=True)
                continue

        logger.debug(f"Returning {len(files)} files")
        return files

    except Exception as e:
        logger.error(f"Error listing files: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def get_file_details(file_id: str):
    """Get detailed information about a specific file"""
    try:
        logger.debug(f"Fetching details for file: {file_id}")
        db = get_db()
        if isinstance(db, dict) and "error" in db:
            raise HTTPException(status_code=500, detail=db["error"])
        raw_assets = db["raw_assets"]

        try:
            obj_id = ObjectId(file_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid file ID format")

        asset = raw_assets.find_one({"_id": obj_id})
        if not asset:
            raise HTTPException(status_code=404, detail="File not found")

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
async def get_file_content(request: Request, file_id: str):
    try:
        db = get_db()
        if isinstance(db, dict) and "error" in db:
            raise HTTPException(status_code=500, detail=db["error"])
        raw_assets = db["raw_assets"]

        asset = raw_assets.find_one({"_id": ObjectId(file_id)})
        if not asset:
            raise HTTPException(status_code=404, detail="File not found")

        processed_paths = asset.get("processed_paths", {})
        if not processed_paths or "markdown" not in processed_paths:
            logger.error(
                f"File {file_id} missing processed content. Status: {asset.get('status')}, Paths: {processed_paths}"
            )
            raise HTTPException(
                status_code=400,
                detail=f"Content not ready. Current status: {asset.get('status', 'unknown')}",
            )

        markdown_path = processed_paths["markdown"]
        if not os.path.exists(markdown_path):
            logger.error(f"Markdown file missing at {markdown_path}")
            raise HTTPException(
                status_code=500, detail="Content file not found on disk"
            )

        content_parts = []

        with open(markdown_path, "r") as f:
            markdown_content = f.read()
            content_parts.append({"type": "text", "text": markdown_content})

        for image_name, image_path in processed_paths.get("images", {}).items():
            content_parts.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"/api/files/{file_id}/images/{image_name}"},
                }
            )

        return {"content": markdown_content}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


logger = logging.getLogger(__name__)


@files_router.get("/files/{file_id}/tables/metadata")
async def get_file_tables_metadata(file_id: str):
    """Get metadata for all tables in a file"""
    try:
        logger.debug(f"Fetching table metadata for file {file_id}")
        db = get_db()
        if isinstance(db, dict) and "error" in db:
            raise HTTPException(status_code=500, detail=db["error"])
        raw_assets = db["raw_assets"]

        asset = raw_assets.find_one({"_id": ObjectId(file_id)})
        if not asset:
            logger.error(f"File not found: {file_id}")
            raise HTTPException(status_code=404, detail="File not found")

        processed_paths = asset.get("processed_paths", {})
        tables = processed_paths.get("tables", {})

        if not tables:
            logger.debug(f"No tables found for file {file_id}")
            raise HTTPException(status_code=404, detail="No tables found for this file")

        first_table = next(iter(tables.values()))
        if isinstance(first_table, dict) and "csv" in first_table:
            csv_path = first_table["csv"]
            tables_dir = os.path.dirname(csv_path)
        else:
            logger.error(f"Invalid table path structure: {first_table}")
            raise HTTPException(status_code=500, detail="Invalid table path structure")

        meta_path = os.path.join(tables_dir, "tables_meta.json")
        logger.debug(f"Looking for metadata at: {meta_path}")

        if not os.path.exists(meta_path):
            logger.error(f"Metadata file not found at {meta_path}")
            raise HTTPException(status_code=404, detail="Table metadata not found")

        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
                logger.debug(f"Successfully loaded metadata for {len(metadata)} tables")

                logger.debug(f"Metadata structure: {json.dumps(metadata, indent=2)}")

                return metadata
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing metadata JSON: {str(e)}")
            raise HTTPException(status_code=500, detail="Error reading table metadata")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving table metadata: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@files_router.get("/files/{file_id}/tables/{table_name}")
async def get_file_table(file_id: str, table_name: str):
    """Get a specific table's content"""
    try:
        logger.debug(f"Fetching table {table_name} for file {file_id}")
        db = get_db()
        if isinstance(db, dict) and "error" in db:
            raise HTTPException(status_code=500, detail=db["error"])
        raw_assets = db["raw_assets"]

        asset = raw_assets.find_one({"_id": ObjectId(file_id)})
        if not asset:
            logger.error(f"File not found: {file_id}")
            raise HTTPException(status_code=404, detail="File not found")

        processed_paths = asset.get("processed_paths", {})
        tables = processed_paths.get("tables", {})

        if not tables:
            logger.error(f"No tables found for file {file_id}")
            raise HTTPException(status_code=404, detail="No tables found for this file")

        if table_name not in tables:
            logger.error(f"Table {table_name} not found in file {file_id}")
            raise HTTPException(status_code=404, detail="Table not found")

        table_paths = tables[table_name]
        if not isinstance(table_paths, dict) or "csv" not in table_paths:
            logger.error(f"Invalid table path structure: {table_paths}")
            raise HTTPException(status_code=500, detail="Invalid table path structure")

        csv_path = table_paths["csv"]

        if not os.path.exists(csv_path):
            logger.error(f"CSV file not found at {csv_path}")
            raise HTTPException(status_code=404, detail="Table file not found")

        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                content = f.read()
                logger.debug(f"Successfully read table content ({len(content)} bytes)")
                return {"content": content}
        except Exception as e:
            logger.error(f"Error reading CSV file: {str(e)}")
            raise HTTPException(status_code=500, detail="Error reading table content")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving table: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@files_router.get("/files/{file_id}/images/{image_name}")
async def get_file_image(file_id: str, image_name: str):
    """Get a specific image from a file"""
    try:
        db = get_db()
        if isinstance(db, dict) and "error" in db:
            raise HTTPException(status_code=500, detail=db["error"])
        raw_assets = db["raw_assets"]

        from bson import ObjectId

        asset = raw_assets.find_one({"_id": ObjectId(file_id)})
        if not asset:
            raise HTTPException(status_code=404, detail="File not found")

        if not asset.get("processed_paths", {}).get("images", {}):
            raise HTTPException(status_code=404, detail="No images found for this file")

        images = asset["processed_paths"]["images"]
        if image_name not in images:
            raise HTTPException(status_code=404, detail="Image not found")

        image_path = images[image_name]

        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="Image file not found")

        return FastAPIFileResponse(image_path)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
