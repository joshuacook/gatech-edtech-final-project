# api/worker.py

import os

import redis
from rq import Connection, Queue, Worker

redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
conn = redis.from_url(redis_url)

if __name__ == "__main__":
    with Connection(conn):
        worker = Worker([Queue("default")])
        worker.work()
