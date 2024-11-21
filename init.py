import os
from time import sleep

import requests
from pymongo import MongoClient

# Define all sample files to upload
SAMPLE_FILES = {
    # "hb-roadmap.docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "notes-1.png": "image/png",
    # "syllabus.pdf": "application/pdf",
}


def wait_for_services():
    """Wait for MongoDB and API to be ready"""
    # Wait for MongoDB
    max_attempts = 30
    attempt = 0
    client = MongoClient("mongodb://db:27017/")

    while attempt < max_attempts:
        try:
            client.admin.command("ping")
            print("MongoDB is ready!")
            break
        except Exception:
            print(f"Waiting for MongoDB... (Attempt {attempt + 1}/{max_attempts})")
            sleep(2)
            attempt += 1

    # Wait for API
    attempt = 0
    while attempt < max_attempts:
        try:
            response = requests.get("http://nginx:80")
            if response.status_code == 200:
                print("API is ready!")
                break
        except Exception:
            print(f"Waiting for API... (Attempt {attempt + 1}/{max_attempts})")
            sleep(2)
            attempt += 1


def upload_fixture_files():
    """Upload all fixture files to the API"""
    for filename, mime_type in SAMPLE_FILES.items():
        fixture_path = f"/app/fixtures/{filename}"

        if not os.path.exists(fixture_path):
            print(f"Error: Fixture file not found at {fixture_path}")
            continue

        try:
            with open(fixture_path, "rb") as f:
                files = {
                    "file": (
                        filename,
                        f,
                        mime_type,
                    )
                }
                print(f"Uploading {filename}...")
                response = requests.post("http://nginx:80/upload", files=files)

            if response.status_code == 200:
                print(f"Successfully uploaded {filename}!")
                print(response.json())
            else:
                print(f"Failed to upload {filename}: {response.text}")

        except Exception as e:
            print(f"Error uploading {filename}: {str(e)}")


if __name__ == "__main__":
    print("Starting initialization script...")
    wait_for_services()
    upload_fixture_files()
    print("Initialization complete!")
