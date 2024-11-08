# api/worker.py

import os
import logging
import redis
from rq import Connection, Queue, Worker

from utils.logging_utils import configure_logging
# Configure logging
logging_level = os.getenv("LOG_LEVEL", "INFO")
configure_logging(logging_level)

# Get the redis connection
redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
conn = redis.from_url(redis_url)

if __name__ == "__main__":
    with Connection(conn):
        worker = Worker(
            logging_level=logging_level,
            queues=['default']
        )
        worker.work()