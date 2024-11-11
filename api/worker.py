# api/worker.py

import logging
import os

import redis
from langfuse import Langfuse
from rq import Connection, Worker
from utils.logging_utils import configure_logging

logging_level = os.getenv("LOG_LEVEL", "INFO")
logger = logging.getLogger(__name__)
configure_logging(logging_level)

redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
conn = redis.from_url(redis_url)

langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
)


class LangfuseWorker(Worker):
    """Custom worker class that ensures Langfuse connection is flushed on shutdown"""

    def shutdown(self):
        """Ensure all Langfuse events are sent before shutdown"""
        try:
            langfuse.flush()
        except Exception as e:
            logger.error(f"Error flushing Langfuse events: {e}")
        finally:
            super().shutdown()


if __name__ == "__main__":
    with Connection(conn):
        worker = LangfuseWorker(logging_level=logging_level, queues=["default"])
        worker.work()
