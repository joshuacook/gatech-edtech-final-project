import hashlib
import os
from datetime import datetime


def format_datetime(dt) -> str:
    """Convert datetime object to ISO format string"""
    if isinstance(dt, datetime):
        return dt.isoformat()
    return dt


def save_file(file_data: bytes, original_filename: str, content_type: str) -> dict:
    """Save uploaded file to disk and return file details"""
    try:
        file_hash = hashlib.sha256(file_data).hexdigest()

        filestore_base = os.path.join("/app", "filestore")
        raw_dir = os.path.join(filestore_base, "raw")
        os.makedirs(raw_dir, exist_ok=True)

        file_extension = os.path.splitext(original_filename)[1]
        stored_filename = f"{file_hash}{file_extension}"
        filepath = os.path.join(raw_dir, stored_filename)

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
        return {"error": str(e)}
