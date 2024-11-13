# jobs/assets/base.py

import logging
import time
from datetime import datetime
from typing import Dict, Optional, TypeVar

import requests
from langfuse import Langfuse
from redis import Redis
from rq import Queue, get_current_job
from rq.job import Job
from utils.db_utils import init_mongo, update_asset_status

logger = logging.getLogger(__name__)

T = TypeVar("T", bound="AssetProcessor")


class AssetProcessor:
    """Base class for asset processors with simplified API-based processing"""

    # Registry of all processor types and their dependencies
    PROCESSOR_REGISTRY = {
        "tables": [],
        "images": [],
        "refined": [],
        "refined_metadata": ["refined"],
        "refined_splitting": ["refined"],
        "lexemes": ["refined", "refined_metadata"],
    }

    def __init__(self, file_hash: str, processor_type: str):
        self.file_hash = file_hash
        self.processor_type = processor_type
        self.db = init_mongo()
        self.asset = self._get_asset()
        self.redis_conn = Redis.from_url("redis://redis:6379")
        self.queue = Queue("default", connection=self.redis_conn)

        self.run_id = self.asset.get("current_run_id")
        if not self.run_id:
            raise ValueError(f"No run_id found for asset {file_hash}")

        self.trace = Langfuse().trace(
            name="asset-processing",
            id=self.run_id,
            metadata={
                "file_hash": file_hash,
                "file_name": self.asset["original_name"],
                "file_type": self.asset["file_type"],
                "file_size": self.asset["file_size"],
            },
        )

    @classmethod
    def execute_job(cls, file_hash: str, processor_type: str, run_id: str):
        """Execute a processing job"""
        processor = cls(file_hash, processor_type)
        current_job = get_current_job(connection=processor.redis_conn)
        span = None

        try:
            span = processor.trace.span(
                name=f"{processor_type}_processing",
                metadata={
                    "processor_type": processor_type,
                    "dependencies": cls.PROCESSOR_REGISTRY[processor_type],
                    "job_id": current_job.id if current_job else None,
                },
            )

            # Make API call to appropriate endpoint
            headers = {"X-Span-ID": span.id, "X-Run-ID": run_id}
            response = requests.post(
                f"http://api:8000/assets/process_{processor_type}/{file_hash}",
                headers=headers,
            )

            if not response.ok:
                raise Exception(
                    f"Processing API call failed with status {response.status_code}"
                )

            result = response.json()

            # Explicitly mark job as finished
            if current_job:
                current_job.meta["status"] = "finished"
                current_job.save_meta()
                current_job.set_status("finished")

            # Queue dependent jobs
            processor.queue_dependent_jobs(run_id)

            span.event(
                name=f"{processor_type}_completed",
                metadata={
                    "result": result,
                    "job_id": current_job.id if current_job else None,
                },
            )

            return True

        except Exception as e:
            error_msg = f"Error in {processor_type} processor: {str(e)}"
            logger.error(error_msg)

            if current_job:
                try:
                    current_job.meta["status"] = "failed"
                    current_job.meta["error"] = str(e)
                    current_job.save_meta()
                    current_job.set_status("failed")
                except Exception as job_error:
                    logger.error(f"Error updating job status: {str(job_error)}")

            if span:
                try:
                    span.event(
                        name=f"{processor_type}_error",
                        metadata={
                            "error": str(e),
                            "job_id": current_job.id if current_job else None,
                        },
                        level="error",
                    )
                except Exception as span_error:
                    logger.error(f"Error recording span event: {str(span_error)}")

            raise

        finally:
            if span:
                try:
                    span.end()
                except Exception as span_error:
                    logger.error(f"Error ending span: {str(span_error)}")
            time.sleep(0.5)

    def queue_dependent_jobs(self, run_id: str):
        """Queue jobs that depend on this processor"""
        try:
            # Find processors that list this one as a dependency
            direct_dependents = [
                proc_type
                for proc_type, deps in self.PROCESSOR_REGISTRY.items()
                if self.processor_type in deps
            ]

            logger.info(
                f"Processor {self.processor_type} completed - checking {len(direct_dependents)} "
                f"direct dependents"
            )

            # Check dependencies for each dependent processor
            for dependent_type in direct_dependents:
                self._queue_if_dependencies_met(dependent_type, run_id)

        except Exception as e:
            logger.error(f"Error queueing dependent jobs: {str(e)}")

    def _queue_if_dependencies_met(self, processor_type: str, run_id: str):
        """Queue a processor if all its dependencies are completed"""
        try:
            dependencies = self.PROCESSOR_REGISTRY[processor_type]
            logger.debug(
                f"Checking dependencies for {processor_type}: needs {dependencies}"
            )

            # Check status of each dependency
            all_deps_complete = True
            dependency_status = {}

            for dep in dependencies:
                dep_job_id = f"{dep}_{self.file_hash}"
                try:
                    dep_job = Job.fetch(dep_job_id, connection=self.redis_conn)

                    if not dep_job:
                        logger.debug(f"Dependency job {dep_job_id} not found")
                        dependency_status[dep] = "missing"
                        all_deps_complete = False
                        continue

                    status = dep_job.get_status()
                    meta_status = dep_job.meta.get("status")

                    if status == "finished" and meta_status == "finished":
                        dependency_status[dep] = "finished"
                    else:
                        dependency_status[dep] = f"status={status}, meta={meta_status}"
                        all_deps_complete = False
                        logger.debug(
                            f"Dependency {dep} not ready: status={status}, meta={meta_status}"
                        )

                except Exception as e:
                    logger.error(f"Error checking dependency {dep}: {str(e)}")
                    dependency_status[dep] = f"error: {str(e)}"
                    all_deps_complete = False

            # Log comprehensive dependency status
            logger.info(
                f"Dependency check for {processor_type}: "
                f"complete={all_deps_complete}, "
                f"statuses={dependency_status}"
            )

            # If all dependencies complete, queue the processor
            if all_deps_complete:
                job_id = self.queue_processor(processor_type, run_id)
                logger.info(
                    f"Queued {processor_type} (job_id={job_id}) after all dependencies completed"
                )
            else:
                logger.debug(
                    f"Not queueing {processor_type} - waiting for dependencies: {dependency_status}"
                )

        except Exception as e:
            logger.error(f"Error checking dependencies for {processor_type}: {str(e)}")

    def queue_processor(self, processor_type: str, run_id: str) -> Optional[str]:
        """Queue a processor for execution"""
        try:
            job_id = f"{processor_type}_{self.file_hash}"

            # Check if job already exists
            try:
                existing_job = Job.fetch(job_id, connection=self.redis_conn)
                if existing_job and existing_job.get_status() != "failed":
                    logger.info(
                        f"Job {job_id} already exists with status {existing_job.get_status()}"
                    )
                    return existing_job.id
            except Exception as e:
                # Job doesn't exist or other error - proceed with creating new job
                logger.debug(f"No existing job found for {job_id}: {str(e)}")
                pass

            # Queue the job
            job = self.queue.enqueue(
                f"{self.__class__.__module__}.{self.__class__.__name__}.execute_job",
                args=(self.file_hash, processor_type, run_id),
                job_timeout="1h",
                job_id=job_id,
                meta={"status": "queued"},
                result_ttl=86400,  # Keep results for 24 hours
            )

            logger.info(
                f"Queued {processor_type} processor for {self.file_hash} with job_id={job.id}"
            )
            return job.id

        except Exception as e:
            logger.error(
                f"Error queueing {processor_type} processor for {self.file_hash}: {str(e)}"
            )
            return None

    @classmethod
    def queue_initial_processors(cls, file_hash: str) -> Dict[str, str]:
        """Queue processors with no dependencies"""
        try:
            run_id = f"asset-{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

            trace = Langfuse().trace(
                name="asset-processing",
                id=run_id,
                metadata={
                    "run_id": run_id,
                    "file_hash": file_hash,
                    "timestamp": datetime.now().isoformat(),
                },
            )

            db = init_mongo()
            db["raw_assets"].update_one(
                {"file_hash": file_hash}, {"$set": {"current_run_id": run_id}}
            )

            # Get processors with no dependencies
            initial_processors = [
                p_type for p_type, deps in cls.PROCESSOR_REGISTRY.items() if not deps
            ]

            processor = cls(file_hash, "initial")
            job_ids = {}

            trace.event(
                name="processing_start",
                metadata={"initial_processors": initial_processors},
            )

            for proc_type in initial_processors:
                if job_id := processor.queue_processor(proc_type, run_id):
                    job_ids[proc_type] = job_id

            if job_ids:
                update_asset_status(file_hash, "processing_queued", job_ids=job_ids)

            return job_ids

        except Exception as e:
            logger.error(f"Error queueing initial processors for {file_hash}: {str(e)}")
            if "trace" in locals():
                trace.event(name="queue_error", metadata={"error": str(e)})
            update_asset_status(file_hash, "queue_error", error=str(e))
            raise

    def _get_asset(self):
        """Get asset from database"""
        asset = self.db["raw_assets"].find_one({"file_hash": self.file_hash})
        if not asset:
            raise Exception(f"Asset not found: {self.file_hash}")
        return asset
