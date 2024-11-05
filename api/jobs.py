# api/jobs.py

import os
import requests
import base64
from datetime import datetime
from pathlib import Path
import json
from pymongo import MongoClient
import logging
import zipfile
import time
import re
from typing import Dict, Optional

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

def extract_tables_from_markdown(markdown_content: str) -> Dict[str, str]:
    """
    Extract tables from markdown content and convert them to HTML.
    Returns a dictionary of table name to HTML content.
    """
    def convert_markdown_table_to_html(table_str: str, table_index: int) -> Optional[str]:
        """Convert a markdown table string to HTML with styling"""
        # Split the table into lines
        lines = table_str.strip().split('\n')
        if len(lines) < 2:
            return None
            
        # Process header
        header = lines[0]
        headers = [h.strip() for h in header.split('|')[1:-1]]
        
        # Process alignment row
        align_row = lines[1]
        alignments = []
        for align in align_row.split('|')[1:-1]:
            align = align.strip()
            if align.startswith(':') and align.endswith(':'):
                alignments.append('center')
            elif align.endswith(':'):
                alignments.append('right')
            else:
                alignments.append('left')
                
        # Process data rows
        rows = []
        for line in lines[2:]:
            if line.strip():
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                rows.append(cells)
                
        # Generate HTML with styling
        html = [
            '<div style="overflow-x: auto;">',
            '<style>',
            'table { border-collapse: collapse; width: 100%; margin: 1em 0; }',
            'th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }',
            'th { background-color: #f5f5f5; font-weight: bold; }',
            'tr:nth-child(even) { background-color: #f9f9f9; }',
            'tr:hover { background-color: #f5f5f5; }',
            '</style>',
            '<table>',
            '<thead>',
            '<tr>'
        ]
        
        # Add headers
        for i, header in enumerate(headers):
            align = f' style="text-align: {alignments[i]}"' if i < len(alignments) else ''
            html.append(f'<th{align}>{header}</th>')
            
        html.append('</tr>')
        html.append('</thead>')
        html.append('<tbody>')
        
        # Add rows
        for row in rows:
            html.append('<tr>')
            for i, cell in enumerate(row):
                align = f' style="text-align: {alignments[i]}"' if i < len(alignments) else ''
                html.append(f'<td{align}>{cell}</td>')
            html.append('</tr>')
            
        html.append('</tbody>')
        html.append('</table>')
        html.append('</div>')
        
        return '\n'.join(html)

    # Find all markdown tables
    table_pattern = r'(?:\n\n|\A)(\|[^\n]*\|\n\|[-:| ]*\|\n(?:\|[^\n]*\|\n?)*)'
    tables = {}
    matches = re.finditer(table_pattern, markdown_content)
    
    for i, match in enumerate(matches):
        table_str = match.group(1)
        html = convert_markdown_table_to_html(table_str, i)
        if html:
            tables[f'table_{i}'] = html
            
    return tables

def process_tables(asset: dict, file_hash: str, processed_dir: str) -> dict:
    """Process tables by extracting them from markdown content"""
    table_paths = {}
    tables_dir = os.path.join(processed_dir, 'tables')
    os.makedirs(tables_dir, exist_ok=True)

    try:
        # Get the markdown content path
        markdown_path = os.path.join(processed_dir, 'content.md')
        
        if not os.path.exists(markdown_path):
            logger.warning(f"Markdown file not found at {markdown_path}")
            return table_paths
            
        # Read the markdown content
        with open(markdown_path, 'r') as f:
            markdown_content = f.read()
            
        # Extract tables from markdown
        tables = extract_tables_from_markdown(markdown_content)
        
        # Save each table as an HTML file
        for table_name, table_html in tables.items():
            table_path = os.path.join(tables_dir, f"{table_name}.html")
            with open(table_path, 'w') as f:
                f.write(table_html)
            table_paths[table_name] = table_path
            logger.debug(f"Saved table {table_name} to {table_path}")
            
        logger.info(f"Extracted {len(tables)} tables from markdown content")
        
    except Exception as e:
        logger.error(f"Error processing tables from markdown: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
    return table_paths

def save_marker_results(file_hash: str, data: dict, filestore_base: str):
    """Save marker results to appropriate directories and update MongoDB"""
    try:
        db = init_mongo()
        assets = db['raw_assets']
        
        # Get asset details
        asset = assets.find_one({'file_hash': file_hash})
        if not asset:
            raise Exception(f"Asset not found: {file_hash}")
        
        # Create processed directory
        processed_dir = os.path.join(filestore_base, 'processed', file_hash)
        os.makedirs(processed_dir, exist_ok=True)
        
        # Save markdown content
        markdown_path = os.path.join(processed_dir, 'content.md')
        with open(markdown_path, 'w') as f:
            f.write(data['markdown'])
        
        # Process images
        images_dir = os.path.join(processed_dir, 'images')
        os.makedirs(images_dir, exist_ok=True)
        
        image_paths = {}
        
        if asset['file_type'] == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            try:
                doc = zipfile.ZipFile(asset['file_path'])
                for file in doc.filelist:
                    if file.filename.startswith('word/media/'):
                        hq_filename = f"hq_{os.path.basename(file.filename)}"
                        hq_path = os.path.join(images_dir, hq_filename)
                        with open(hq_path, 'wb') as f:
                            f.write(doc.read(file.filename))
                        image_paths[hq_filename] = hq_path
                doc.close()
            except Exception as e:
                logger.error(f"Error extracting high quality images from DOCX: {str(e)}")
        
        # Process tables using markdown extraction
        table_paths = process_tables(asset, file_hash, processed_dir)
        
        # Save metadata
        meta_path = os.path.join(processed_dir, 'meta.json')
        with open(meta_path, 'w') as f:
            json.dump(data['meta'], f)
        
        # Update the asset record with all processing results
        assets.update_one(
            {'file_hash': file_hash},
            {
                '$set': {
                    'processed': True,
                    'processed_paths': {
                        'markdown': markdown_path,
                        'images': image_paths,
                        'tables': table_paths,
                        'meta': meta_path
                    },
                    'page_count': data.get('page_count', 1),
                    'has_images': len(image_paths) > 0,
                    'image_count': len(image_paths),
                    'has_tables': len(table_paths) > 0,
                    'table_count': len(table_paths),
                    'processing_details': {
                        'completion_time': datetime.now().isoformat(),
                        'extracted_pages': data.get('page_count', 1),
                        'extracted_images': len(image_paths),
                        'extracted_tables': len(table_paths)
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