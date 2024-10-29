# api/jobs.py

import os
import requests
import base64
from datetime import datetime
from pathlib import Path
import json
from pymongo import MongoClient
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def init_mongo():
    """Initialize MongoDB connection"""
    client = MongoClient(os.getenv('MONGODB_URI'))
    return client['chelle']

def update_asset_status(file_hash: str, status: str, error: str = None):
    """Update asset status in database"""
    db = init_mongo()
    assets = db['raw_assets']
    
    update_data = {'status': status}
    if error:
        update_data['error'] = error
    if status == 'complete':
        update_data['processed_date'] = datetime.now()
    
    assets.update_one(
        {'file_hash': file_hash},
        {'$set': update_data}
    )
    logger.debug(f"Updated status for {file_hash} to {status}")

def save_marker_results(file_hash: str, data: dict, filestore_base: str):
    """Save marker results to appropriate directories and update MongoDB"""
    try:
        db = init_mongo()
        assets = db['raw_assets']
        
        processed_dir = os.path.join(filestore_base, 'processed', file_hash)
        os.makedirs(processed_dir, exist_ok=True)
        
        markdown_path = os.path.join(processed_dir, 'content.md')
        with open(markdown_path, 'w') as f:
            f.write(data['markdown'])
        
        images_dir = os.path.join(processed_dir, 'images')
        os.makedirs(images_dir, exist_ok=True)
        
        image_paths = {}
        for filename, image_data in data.get('images', {}).items():
            image_path = os.path.join(images_dir, filename)
            with open(image_path, 'wb') as f:
                f.write(base64.b64decode(image_data))
            image_paths[filename] = image_path
        
        meta_path = os.path.join(processed_dir, 'meta.json')
        with open(meta_path, 'w') as f:
            json.dump(data['meta'], f)
        
        # Update the asset record with processing results
        assets.update_one(
            {'file_hash': file_hash},
            {
                '$set': {
                    'processed': True,
                    'processed_paths': {
                        'markdown': markdown_path,
                        'images': image_paths,
                        'meta': meta_path
                    },
                    'page_count': data.get('page_count', 1),
                    'processing_details': {
                        'completion_time': datetime.now().isoformat(),
                        'extracted_pages': data.get('page_count', 1),
                        'extracted_images': len(image_paths)
                    }
                }
            }
        )
        
        # Update status to complete
        update_asset_status(file_hash, 'complete')
        logger.info(f"Successfully processed file {file_hash}")
        
    except Exception as e:
        logger.error(f"Error saving marker results: {str(e)}")
        update_asset_status(file_hash, 'error', str(e))
        raise

def process_with_marker(file_hash: str):
    """Process a file with the Marker API"""
    try:
        logger.info(f"Starting processing for file {file_hash}")
        
        # Update status to processing
        update_asset_status(file_hash, 'processing')
        
        db = init_mongo()
        assets = db['raw_assets']
        
        asset = assets.find_one({'file_hash': file_hash})
        if not asset:
            raise Exception(f"Asset not found: {file_hash}")
        
        filestore_base = os.path.join('/app', 'filestore')
        raw_file_path = os.path.join(
            filestore_base,
            'raw',
            f"{file_hash}{os.path.splitext(asset['original_name'])[1]}"
        )
        
        # Call Marker API
        url = "https://www.datalab.to/api/v1/marker"
        headers = {"X-Api-Key": os.getenv('MARKER_API_KEY')}
        
        with open(raw_file_path, 'rb') as f:
            files = {
                'file': (asset['original_name'], f, asset['file_type']),
                'langs': (None, "English"),
                'force_ocr': (None, False),
                'paginate': (None, False)
            }
            response = requests.post(url, files=files, headers=headers)
        
        if not response.ok:
            raise Exception(f"Marker API request failed: {response.text}")
        
        initial_data = response.json()
        request_check_url = initial_data['request_check_url']
        
        # Poll for results
        max_polls = 300  # 10 minutes at 2 second intervals
        poll_interval = 2
        
        for _ in range(max_polls):
            import time
            time.sleep(poll_interval)
            
            response = requests.get(request_check_url, headers=headers)
            data = response.json()
            
            if data['status'] == 'complete':
                if data['success']:
                    save_marker_results(file_hash, data, filestore_base)
                    return True
                else:
                    raise Exception(f"Marker processing failed: {data['error']}")
        
        raise Exception("Marker processing timed out")
        
    except Exception as e:
        logger.error(f"Error in process_with_marker: {str(e)}")
        update_asset_status(file_hash, 'error', str(e))
        raise