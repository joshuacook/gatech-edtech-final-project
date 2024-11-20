import json
import logging
import os

from fastapi import HTTPException
from processors.base import BaseAssetProcessor
from routers.chat import chat_call

logger = logging.getLogger(__name__)


class ProcessRefinedMetadata(BaseAssetProcessor):
    def __init__(self):
        super().__init__("refined_metadata", "refined_metadata")
        self.required_paths = ["markdown"]

    async def process_asset(self, file_hash: str, asset: dict, db: dict, span):
        try:
            prompt_template = self.read_prompt_template("metadata.txt")
            processed_paths = asset.get("processed_paths", {})

            with open(processed_paths["markdown"], "r") as f:
                file_content = f.read()

            prompt = prompt_template + "\n\nDocument Content:\n" + file_content

            generation = span.generation(name="metadata_generation", input=prompt)
            response = chat_call(query=prompt, expect_json=True)
            generation.end(output=response)

            if "error" in response:
                raise HTTPException(status_code=500, detail=response["error"])

            if not response.get("message"):
                raise HTTPException(
                    status_code=500, detail="Empty response from chat API"
                )

            try:
                # First try to parse the raw message
                metadata = json.loads(response["message"])
            except json.JSONDecodeError:
                # If that fails, try to extract JSON from markdown
                import re

                json_pattern = r"```(?:json)?\n([\s\S]*?)\n```"
                matches = re.findall(json_pattern, response["message"])
                if not matches:
                    raise HTTPException(
                        status_code=500, detail="No valid JSON found in response"
                    )
                metadata = json.loads(matches[0])

            metadata_path = os.path.join(
                "/app/filestore/processed", file_hash, "metadata.json"
            )
            os.makedirs(os.path.dirname(metadata_path), exist_ok=True)

            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            update_data = {
                "metadata": metadata,
                "processed_paths.metadata": metadata_path,
            }
            db["raw_assets"].update_one({"file_hash": file_hash}, {"$set": update_data})

            return {"status": "success", "metadata": metadata}

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            logger.debug(f"Response content: {response.get('message', 'No message')}")
            raise HTTPException(
                status_code=500, detail=f"Failed to parse metadata: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Metadata processing error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
