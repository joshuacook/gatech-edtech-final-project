# api/utils/db_utils.py

import logging
import os
from datetime import datetime

from pymongo import MongoClient

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def init_mongo():
    """Initialize MongoDB connection"""
    client = MongoClient(os.getenv("MONGODB_URI"))
    return client["chelle"]


def update_asset_status(
    file_hash: str, status: str, error: str = None, job_ids: dict = None
):
    """Update asset status in database"""
    db = init_mongo()
    assets = db["raw_assets"]

    update_data = {"status": status}
    if error:
        update_data["error"] = error
    if status == "complete":
        update_data["processed_date"] = datetime.now()
    if job_ids:
        update_data["job_ids"] = job_ids

    assets.update_one({"file_hash": file_hash}, {"$set": update_data})
    logger.info(f"Updated status for {file_hash} to {status}")
