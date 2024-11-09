# api/jobs/assets/base.py
import json
import logging
import os
from typing import Dict, List, Optional, Set, Type, TypeVar

from redis import Redis
from rq import Queue, get_current_job
from rq.job import Job
from utils.db_utils import init_mongo, update_asset_status

logger = logging.getLogger(__name__)

T = TypeVar("T", bound="AssetProcessor")


class AssetProcessor:
    """Base class for asset processors with dependency management and chaining"""

    processor_type: str = None  # Override in subclasses
    dependencies: List[str] = []  # List of processor types this processor depends on

    def __init__(self, file_hash: str):
        self.file_hash = file_hash
        self.db = init_mongo()
        self.asset = self._get_asset()
        self.filestore_base = os.path.join("/app", "filestore")
        self.processed_dir = os.path.join(
            self.filestore_base, "processed", self.file_hash
        )
        self.redis_conn = Redis.from_url("redis://redis:6379")
        self.queue = Queue("default", connection=self.redis_conn)

    def process(self):
        """
        Main processing method to be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement process()")

    @classmethod
    def execute_job(cls, file_hash: str):
        """Static method for job execution"""
        processor = cls(file_hash)
        try:
            result = processor.process()

            # Mark current job as finished in Redis
            current_job = get_current_job(connection=processor.redis_conn)
            if current_job:
                current_job.set_status("finished")

            # After job is marked as finished, queue dependent jobs
            processor.queue_dependent_jobs()

            return result
        except Exception as e:
            logger.error(f"Error in {cls.processor_type} processor: {str(e)}")
            raise

    def queue_dependent_jobs(self):
        """Queue jobs that DIRECTLY depend on this processor"""
        current_job = get_current_job(connection=self.redis_conn)
        if not current_job:
            return

        try:
            # Get only processors that list this processor type as a direct dependency
            registry = self.get_processor_registry()
            direct_dependents = [
                p_class
                for p_class in registry.values()
                if self.processor_type in p_class.dependencies
            ]

            logger.info(
                f"Processor {self.processor_type} completed - checking {len(direct_dependents)} "
                f"direct dependents"
            )

            # Check dependencies only for processors that directly depend on this one
            for processor_class in direct_dependents:
                self._queue_if_dependencies_met(processor_class)

        except Exception as e:
            logger.error(f"Error queueing dependent jobs: {str(e)}")

    def _queue_if_dependencies_met(self, processor_class):
        """Queue a processor if all its dependencies are completed"""
        try:
            # Log the check
            logger.debug(
                f"Checking dependencies for {processor_class.processor_type}: "
                f"needs {processor_class.dependencies}"
            )

            # Track status of each dependency
            dependency_status = {}
            all_deps_complete = True

            for dep in processor_class.dependencies:
                dep_job_id = f"{dep}_{self.file_hash}"
                try:
                    dep_job = Job.fetch(dep_job_id, connection=self.redis_conn)
                    # Check if job exists and is finished
                    if dep_job and dep_job.get_status() == "finished":
                        dependency_status[dep] = "finished"
                    else:
                        status = dep_job.get_status() if dep_job else "missing"
                        dependency_status[dep] = status
                        all_deps_complete = False
                        logger.debug(f"Dependency {dep} not ready: status={status}")

                except Exception as e:
                    logger.error(f"Error checking dependency {dep}: {str(e)}")
                    dependency_status[dep] = "error"
                    all_deps_complete = False

            # Log the full dependency status
            logger.info(
                f"Dependency status for {processor_class.processor_type}: "
                f"{json.dumps(dependency_status, indent=2)}"
            )

            # If all dependencies are complete, queue the processor
            if all_deps_complete:
                processor_class.queue(self.file_hash)
                logger.info(
                    f"Queued {processor_class.processor_type} after all dependencies completed: "
                    f"{processor_class.dependencies}"
                )
            else:
                logger.debug(
                    f"Not queueing {processor_class.processor_type} - "
                    f"waiting for dependencies: {dependency_status}"
                )

        except Exception as e:
            logger.error(
                f"Error checking dependencies for {processor_class.processor_type}: {str(e)}"
            )

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
    def get_processor_registry(cls) -> Dict[str, Type["AssetProcessor"]]:
        """Get registry of all processor types"""
        from jobs.assets.image_metadata import ImageMetadataProcessor
        from jobs.assets.images import ImageProcessor
        from jobs.assets.metadata import MetadataProcessor
        from jobs.assets.refined import RefinedProcessor
        from jobs.assets.table_metadata import TableMetadataProcessor
        from jobs.assets.tables import TableProcessor

        return {
            "tables": TableProcessor,
            "images": ImageProcessor,
            "refined": RefinedProcessor,
            "metadata": MetadataProcessor,
            "table_metadata": TableMetadataProcessor,
            "image_metadata": ImageMetadataProcessor,
        }

    @classmethod
    def validate_dependencies(cls) -> bool:
        """Validate that all declared dependencies exist and don't form cycles"""
        registry = cls.get_processor_registry()

        # Check all dependencies exist
        for dep in cls.dependencies:
            if dep not in registry:
                raise ValueError(f"Invalid dependency '{dep}' in {cls.__name__}")

        # Check for circular dependencies
        def get_all_deps(processor_type: str, seen: Set[str] = None) -> Set[str]:
            if seen is None:
                seen = set()

            if processor_type in seen:
                raise ValueError(
                    f"Circular dependency detected involving {processor_type}"
                )

            seen.add(processor_type)
            processor_class = registry[processor_type]

            for dep in processor_class.dependencies:
                get_all_deps(dep, seen)

            return seen

        # Validate no circular dependencies
        try:
            get_all_deps(cls.processor_type)
        except ValueError as e:
            raise ValueError(f"Dependency validation failed: {str(e)}")

        return True

    @classmethod
    def queue(cls: Type[T], file_hash: str) -> Optional[str]:
        """Queue this processor for execution"""
        if not cls.processor_type:
            raise ValueError(f"processor_type not set for {cls.__name__}")

        try:
            cls.validate_dependencies()

            redis_conn = Redis.from_url("redis://redis:6379")
            queue = Queue("default", connection=redis_conn)

            # Queue the job
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
    def get_initial_processors(cls) -> List[Type["AssetProcessor"]]:
        """Get processors with no dependencies"""
        return [
            p_class
            for p_class in cls.get_processor_registry().values()
            if not p_class.dependencies
        ]

    @classmethod
    def queue_all(cls, file_hash: str) -> Dict[str, str]:
        """Queue initial processors - others will be queued automatically"""
        try:
            # Only queue processors with no dependencies
            initial_processors = cls.get_initial_processors()
            job_ids = {}

            for processor in initial_processors:
                if job_id := processor.queue(file_hash):
                    job_ids[processor.processor_type] = job_id

            if job_ids:
                update_asset_status(file_hash, "processing_queued", job_ids=job_ids)

            return job_ids

        except Exception as e:
            logger.error(f"Error queueing processors for {file_hash}: {str(e)}")
            update_asset_status(file_hash, "queue_error", error=str(e))
            raise
