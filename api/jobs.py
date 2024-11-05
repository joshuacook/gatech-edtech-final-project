# api/jobs.py

import csv
import json
import logging
import os
import time
import zipfile
from datetime import datetime
from typing import Dict, Tuple

import requests
from docx import Document
from docx.table import Table
from pymongo import MongoClient

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def init_mongo():
    """Initialize MongoDB connection"""
    client = MongoClient(os.getenv("MONGODB_URI"))
    return client["chelle"]


def update_asset_status(file_hash: str, status: str, error: str = None):
    """Update asset status in database"""
    db = init_mongo()
    assets = db["raw_assets"]

    update_data = {"status": status}
    if error:
        update_data["error"] = error
    if status == "complete":
        update_data["processed_date"] = datetime.now()

    assets.update_one({"file_hash": file_hash}, {"$set": update_data})
    logger.debug(f"Updated status for {file_hash} to {status}")


def extract_table_from_docx(table: Table) -> list[list[str]]:
    """Convert a docx table to a list of lists (rows and cells)"""
    table_data = []

    for row in table.rows:
        row_data = []
        for cell in row.cells:
            # Get cell text and clean it
            text = cell.text.strip()
            # Handle potential cell merging by duplicating content
            # We'll handle the merging during presentation
            row_data.append(text)
        table_data.append(row_data)

    return table_data


def process_docx_content(
    file_path: str, processed_dir: str
) -> Tuple[Dict[str, str], Dict[str, str]]:
    """Extract tables and images from a DOCX file"""
    doc = Document(file_path)

    # Process tables
    table_paths = {}
    tables_dir = os.path.join(processed_dir, "tables")
    os.makedirs(tables_dir, exist_ok=True)

    # Also save a tables.json file with table metadata
    tables_meta = {}

    for i, table in enumerate(doc.tables):
        table_name = f"table_{i}"
        table_data = extract_table_from_docx(table)

        # Skip empty tables
        if not table_data or not any(table_data):
            continue

        # Save as CSV
        csv_path = os.path.join(tables_dir, f"{table_name}.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(table_data)

        # Store path
        table_paths[table_name] = csv_path

        # Store metadata about the table
        tables_meta[table_name] = {
            "num_rows": len(table_data),
            "num_cols": len(table_data[0]) if table_data else 0,
            "headers": table_data[0] if table_data else [],
        }

    # Save table metadata
    meta_path = os.path.join(tables_dir, "tables_meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(tables_meta, f, ensure_ascii=False, indent=2)

    # Process images
    image_paths = {}
    try:
        images_dir = os.path.join(processed_dir, "images")
        os.makedirs(images_dir, exist_ok=True)

        with zipfile.ZipFile(file_path) as doc_zip:
            for file in doc_zip.filelist:
                if file.filename.startswith("word/media/"):
                    filename = os.path.basename(file.filename)
                    image_path = os.path.join(images_dir, filename)
                    with open(image_path, "wb") as f:
                        f.write(doc_zip.read(file.filename))
                    image_paths[filename] = image_path
    except Exception as e:
        logger.error(f"Error extracting images from DOCX: {str(e)}")

    return table_paths, image_paths


def save_marker_results(file_hash: str, data: dict, filestore_base: str):
    """Save marker results to appropriate directories and update MongoDB"""
    try:
        db = init_mongo()
        assets = db["raw_assets"]

        # Get asset details
        asset = assets.find_one({"file_hash": file_hash})
        if not asset:
            raise Exception(f"Asset not found: {file_hash}")

        # Create processed directory
        processed_dir = os.path.join(filestore_base, "processed", file_hash)
        os.makedirs(processed_dir, exist_ok=True)

        # Save markdown content
        markdown_path = os.path.join(processed_dir, "content.md")
        with open(markdown_path, "w") as f:
            f.write(data["markdown"])

        # Initialize empty paths
        table_paths = {}
        image_paths = {}

        # Process DOCX files for tables and images
        if (
            asset["file_type"]
            == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ):
            table_paths, image_paths = process_docx_content(
                asset["file_path"], processed_dir
            )

        # Save metadata
        meta_path = os.path.join(processed_dir, "meta.json")
        with open(meta_path, "w") as f:
            json.dump(data["meta"], f)

        # Update the asset record with all processing results
        assets.update_one(
            {"file_hash": file_hash},
            {
                "$set": {
                    "processed": True,
                    "processed_paths": {
                        "markdown": markdown_path,
                        "images": image_paths,
                        "tables": table_paths,
                        "meta": meta_path,
                    },
                    "page_count": data.get("page_count", 1),
                    "has_images": len(image_paths) > 0,
                    "image_count": len(image_paths),
                    "has_tables": len(table_paths) > 0,
                    "table_count": len(table_paths),
                    "processing_details": {
                        "completion_time": datetime.now().isoformat(),
                        "extracted_pages": data.get("page_count", 1),
                        "extracted_images": len(image_paths),
                        "extracted_tables": len(table_paths),
                    },
                }
            },
        )

        # Update status to complete
        update_asset_status(file_hash, "complete")
        logger.info(f"Successfully processed file {file_hash}")

    except Exception as e:
        logger.error(f"Error saving marker results: {str(e)}")
        update_asset_status(file_hash, "error", str(e))
        raise


def process_with_marker(file_hash: str):
    """Process a file with the Marker API"""
    try:
        logger.info(f"Starting processing for file {file_hash}")

        # Update status to processing
        update_asset_status(file_hash, "processing")

        db = init_mongo()
        assets = db["raw_assets"]

        asset = assets.find_one({"file_hash": file_hash})
        if not asset:
            raise Exception(f"Asset not found: {file_hash}")

        filestore_base = os.path.join("/app", "filestore")
        raw_file_path = os.path.join(
            filestore_base,
            "raw",
            f"{file_hash}{os.path.splitext(asset['original_name'])[1]}",
        )

        # Call Marker API
        url = "https://www.datalab.to/api/v1/marker"
        headers = {"X-Api-Key": os.getenv("MARKER_API_KEY")}

        with open(raw_file_path, "rb") as f:
            files = {
                "file": (asset["original_name"], f, asset["file_type"]),
                "langs": (None, "English"),
                "force_ocr": (None, False),
                "paginate": (None, False),
            }
            response = requests.post(url, files=files, headers=headers)

        if not response.ok:
            raise Exception(f"Marker API request failed: {response.text}")

        initial_data = response.json()
        request_check_url = initial_data["request_check_url"]

        # Poll for results
        max_polls = 300  # 10 minutes at 2 second intervals
        poll_interval = 2

        for _ in range(max_polls):
            time.sleep(poll_interval)

            response = requests.get(request_check_url, headers=headers)
            data = response.json()

            if data["status"] == "complete":
                if data["success"]:
                    save_marker_results(file_hash, data, filestore_base)
                    return True
                else:
                    raise Exception(f"Marker processing failed: {data['error']}")

        raise Exception("Marker processing timed out")

    except Exception as e:
        logger.error(f"Error in process_with_marker: {str(e)}")
        update_asset_status(file_hash, "error", str(e))
        raise
