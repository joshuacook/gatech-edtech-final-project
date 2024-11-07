# init_script.py

import os
import requests
from pathlib import Path
from time import sleep
from pymongo import MongoClient

SAMPLE_FILE = "hb-roadmap.docx"

def wait_for_services():
    """Wait for MongoDB and API to be ready"""
    # Wait for MongoDB
    max_attempts = 30
    attempt = 0
    client = MongoClient("mongodb://db:27017/")
    
    while attempt < max_attempts:
        try:
            client.admin.command('ping')
            print("MongoDB is ready!")
            break
        except Exception as e:
            print(f"Waiting for MongoDB... (Attempt {attempt + 1}/{max_attempts})")
            sleep(2)
            attempt += 1
    
    # Wait for API
    attempt = 0
    while attempt < max_attempts:
        try:
            response = requests.get("http://api:8000/")
            if response.status_code == 200:
                print("API is ready!")
                break
        except Exception:
            print(f"Waiting for API... (Attempt {attempt + 1}/{max_attempts})")
            sleep(2)
            attempt += 1

def upload_fixture_file():
    """Upload the fixture DOCX file to the API"""
    fixture_path = f"/app/fixtures/{SAMPLE_FILE}"
    
    if not os.path.exists(fixture_path):
        print(f"Error: Fixture file not found at {fixture_path}")
        return
    
    try:
        with open(fixture_path, "rb") as f:
            files = {
                "file": (
                    "sample.docx", 
                    f, 
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            }
            response = requests.post("http://api:8000/upload", files=files)
            
        if response.status_code == 200:
            print("Fixture file uploaded successfully!")
            print(response.json())
        else:
            print(f"Failed to upload file: {response.text}")
            
    except Exception as e:
        print(f"Error uploading file: {str(e)}")

if __name__ == "__main__":
    print("Starting initialization script...")
    wait_for_services()
    upload_fixture_file()
    print("Initialization complete!")