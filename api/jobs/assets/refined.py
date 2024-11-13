# api/jobs/assets/refined.py

import logging

import requests
from jobs.assets.base import AssetProcessor

logger = logging.getLogger(__name__)


class RefinedProcessor(AssetProcessor):
    """Process files with Marker API for refined content"""

    processor_type = "refined"
    dependencies = []

    def __init__(self, file_hash: str):
        super().__init__(file_hash)

    def process(self, span):
        """Main processing method"""
        # Simply call the refine endpoint and verify success
        headers = {"X-Span-ID": span.id}
        response = requests.post(
            f"http://api:8000/assets/refine/{self.file_hash}", headers=headers
        )

        if not response.ok:
            raise Exception(
                f"Refine API call failed with status {response.status_code}"
            )

        return True
