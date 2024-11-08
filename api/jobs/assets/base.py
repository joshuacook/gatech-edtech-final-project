# api/jobs/assets/base.py
import logging
import os
from typing import Dict, Optional, Type, TypeVar

from redis import Redis
from rq import Queue
from utils.db_utils import init_mongo, update_asset_status

logger = logging.getLogger(__name__)

T = TypeVar("T", bound="AssetProcessor")


class AssetProcessor:
    """Base class for asset processors"""

    processor_type: str = None  # Override in subclasses

    def __init__(self, file_hash: str):
        self.file_hash = file_hash
        self.db = init_mongo()
        self.asset = self._get_asset()
        self.filestore_base = os.path.join("/app", "filestore")
        self.processed_dir = os.path.join(
            self.filestore_base, "processed", self.file_hash
        )

    @classmethod
    def execute_job(cls, file_hash: str):
        """Static method for job execution"""
        processor = cls(file_hash)
        return processor.process()

    def _get_asset(self):
        """Get asset from database"""
        asset = self.db["raw_assets"].find_one({"file_hash": self.file_hash})
        if not asset:
            raise Exception(f"Asset not found: {self.file_hash}")
        return asset

    def _update_asset(self, update_data: dict):
        """Update asset in database"""
        self.db["raw_assets"].update_one(
            {"file_hash": self.file_hash}, {"$set": update_data}
        )

    def get_raw_file_path(self):
        """Get path to raw file"""
        return os.path.join(
            self.filestore_base,
            "raw",
            f"{self.file_hash}{os.path.splitext(self.asset['original_name'])[1]}",
        )

    @classmethod
    def queue(cls: Type[T], file_hash: str) -> Optional[str]:
        """Queue this processor for execution"""
        if not cls.processor_type:
            raise ValueError(f"processor_type not set for {cls.__name__}")

        try:
            redis_conn = Redis.from_url("redis://redis:6379")
            queue = Queue("default", connection=redis_conn)

            # Queue the job using execute_job method
            job = queue.enqueue(
                f"{cls.__module__}.{cls.__name__}.execute_job",
                args=(file_hash,),
                job_timeout="1h",
                job_id=f"{cls.processor_type}_{file_hash}",
            )

            logger.info(f"Queued {cls.processor_type} processor for {file_hash}")
            return job.id

        except Exception as e:
            logger.error(
                f"Error queueing {cls.processor_type} processor for {file_hash}: {str(e)}"
            )
            return None

    @classmethod
    def queue_all(cls, file_hash: str) -> Dict[str, str]:
        """Queue all processors for an asset"""
        from jobs.assets.images import ImageProcessor
        from jobs.assets.metadata import MetadataProcessor
        from jobs.assets.refined import RefinedProcessor
        from jobs.assets.tables import TableProcessor

        # Queue metadata processor after refined processor
        processors = [
            TableProcessor,
            ImageProcessor,
            RefinedProcessor,
            MetadataProcessor,  # Added metadata processor
        ]
        job_ids = {}

        try:
            for processor in processors:
                if job_id := processor.queue(file_hash):
                    job_ids[processor.processor_type] = job_id

            if job_ids:
                update_asset_status(file_hash, "processing_queued", job_ids=job_ids)

            return job_ids
        except Exception as e:
            logger.error(f"Error queueing processors for {file_hash}: {str(e)}")
            update_asset_status(file_hash, "queue_error", error=str(e))
            raise
