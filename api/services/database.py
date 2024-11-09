import os

from pymongo import MongoClient


def get_db():
    try:
        client = MongoClient(os.getenv("MONGODB_URI", "mongodb://db:27017/"))
        db = client["chelle"]
        client.admin.command("ping")
        return db
    except Exception as e:
        return {"error": str(e)}
