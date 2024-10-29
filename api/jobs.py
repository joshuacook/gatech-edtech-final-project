# api/jobs.py

import os
from pathlib import Path

def touch_file(file_id):
    """
    Create an empty file with the file_id as name
    """
    file_path = Path('/app/filestore') / f"{file_id}.txt"
    file_path.touch()
    return str(file_path)