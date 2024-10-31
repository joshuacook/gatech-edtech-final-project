# api/routers/files.py

from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import os
import hashlib
from redis import Redis
from rq import Queue
import logging
from pymongo import MongoClient
from bson import ObjectId
import json

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class FileResponse(BaseModel):
    id: str
    name: str
    size: int
    type: str
    status: str
    upload_date: str
    processed_date: Optional[str] = None
    error: Optional[str] = None

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
        client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://db:27017/'))
        db = client['chelle']
        client.admin.command('ping')
        logger.debug("Successfully connected to MongoDB")
        return db
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise HTTPException(status_code=500, detail="Database connection failed")

# Initialize Redis connection
def get_redis_queue():
    try:
        redis_conn = Redis.from_url(os.getenv('REDIS_URL', 'redis://redis:6379'))
        return Queue('default', connection=redis_conn)
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {str(e)}")
        raise HTTPException(status_code=500, detail="Redis connection failed")

def save_file(file_data: bytes, original_filename: str, content_type: str) -> dict:
    """Save uploaded file to disk and return file details"""
    try:
        # Generate file hash
        file_hash = hashlib.sha256(file_data).hexdigest()
        
        # Create filestore directory structure
        filestore_base = os.path.join('/app', 'filestore')
        raw_dir = os.path.join(filestore_base, 'raw')
        os.makedirs(raw_dir, exist_ok=True)
        
        # Determine file extension and create filepath
        file_extension = os.path.splitext(original_filename)[1]
        stored_filename = f"{file_hash}{file_extension}"
        filepath = os.path.join(raw_dir, stored_filename)
        
        # Save file
        with open(filepath, 'wb') as f:
            f.write(file_data)
        
        return {
            'file_hash': file_hash,
            'original_name': original_filename,
            'stored_name': stored_filename,
            'file_path': filepath,
            'file_type': content_type,
            'file_size': len(file_data)
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
        raw_assets = db['raw_assets']
        
        asset_record = {
            'original_name': file_details['original_name'],
            'stored_name': file_details['stored_name'],
            'file_path': file_details['file_path'],
            'file_hash': file_details['file_hash'],
            'file_type': file_details['file_type'],
            'file_size': file_details['file_size'],
            'upload_date': datetime.now(),
            'status': 'uploaded',
            'processed': False
        }
        
        result = raw_assets.insert_one(asset_record)
        
        # Queue processing job
        queue = get_redis_queue()
        job = queue.enqueue(
            'jobs.process_with_marker',
            file_details['file_hash'],
            job_timeout='1h'
        )
        
        logger.debug(f"Created job {job.id} for file {file_details['file_hash']}")
        
        # Update record with job ID
        raw_assets.update_one(
            {'_id': result.inserted_id},
            {'$set': {'job_id': job.id}}
        )
        
        return FileResponse(
            id=str(result.inserted_id),
            name=file_details['original_name'],
            size=file_details['file_size'],
            type=file_details['file_type'],
            status='uploaded',
            upload_date=datetime.now().isoformat()
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
        raw_assets = db['raw_assets']
        
        files = []
        for asset in raw_assets.find().sort('upload_date', -1):
            try:
                # Convert MongoDB ObjectId to string
                asset_id = str(asset['_id'])
                
                # Format dates
                upload_date = format_datetime(asset['upload_date'])
                processed_date = format_datetime(asset.get('processed_date')) if asset.get('processed_date') else None
                
                # Create response object
                file_response = FileResponse(
                    id=asset_id,
                    name=asset['original_name'],
                    size=asset['file_size'],
                    type=asset['file_type'],
                    status=asset.get('status', 'unknown'),
                    upload_date=upload_date,
                    processed_date=processed_date,
                    error=asset.get('error')
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
        raise HTTPException(status_code=500, detail=str(e))

@files_router.get("/files/{file_id}", response_model=FileDetailResponse)
async def get_file_details(file_id: str):
    """Get detailed information about a specific file"""
    try:
        logger.debug(f"Fetching details for file: {file_id}")
        db = get_db()
        raw_assets = db['raw_assets']
        
        # Convert string ID to ObjectId for MongoDB query
        try:
            obj_id = ObjectId(file_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid file ID format")
        
        asset = raw_assets.find_one({'_id': obj_id})
        if not asset:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Get preview content if file is processed
        preview = None
        if asset.get('processed', False) and 'processed_paths' in asset:
            try:
                with open(asset['processed_paths']['markdown'], 'r') as f:
                    preview = f.read(1000)  # First 1000 characters as preview
            except Exception as e:
                logger.error(f"Error reading preview: {str(e)}")
        
        return FileDetailResponse(
            id=str(asset['_id']),
            name=asset['original_name'],
            size=asset['file_size'],
            type=asset['file_type'],
            status=asset.get('status', 'unknown'),
            upload_date=format_datetime(asset['upload_date']),
            processed_date=format_datetime(asset.get('processed_date')) if asset.get('processed_date') else None,
            error=asset.get('error'),
            preview=preview,
            processing_details=asset.get('processing_details')
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
        raw_assets = db['raw_assets']
        
        asset = raw_assets.find_one({'_id': ObjectId(file_id)})
        if not asset:
            raise HTTPException(status_code=404, detail="File not found")
            
        if not asset.get('processed', False) or 'processed_paths' not in asset:
            raise HTTPException(status_code=400, detail="File content not available")
            
        try:
            with open(asset['processed_paths']['markdown'], 'r') as f:
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

@files_router.get("/files/{file_id}/metadata")
async def get_file_metadata(file_id: str):
    """Get the metadata for a processed file"""
    try:
        db = get_db()
        raw_assets = db['raw_assets']
        
        asset = raw_assets.find_one({'_id': ObjectId(file_id)})
        if not asset:
            raise HTTPException(status_code=404, detail="File not found")
            
        if not asset.get('processed', False) or 'processed_paths' not in asset:
            raise HTTPException(status_code=400, detail="File metadata not available")
            
        try:
            with open(asset['processed_paths']['meta'], 'r') as f:
                metadata = json.load(f)
            return metadata
        except Exception as e:
            logger.error(f"Error reading metadata: {str(e)}")
            raise HTTPException(status_code=500, detail="Error reading metadata")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting metadata: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))