import json
import logging

from fastapi import HTTPException
from processors.base import BaseAssetProcessor
from routers.chat import chat_call

logger = logging.getLogger(__name__)


class ProcessRefinedSplitting(BaseAssetProcessor):
    def __init__(self):
        super().__init__("refined_splitting", "refined_splitting")
        self.required_paths = ["markdown"]

    async def process_asset(self, file_hash: str, asset: dict, db: dict, span):
        MIN_CHARS_FOR_SPLIT = 24000  # ~6k tokens
        MAX_SEGMENT_SIZE = 28000  # ~7k tokens

        processed_paths = asset.get("processed_paths", {})
        with open(processed_paths["markdown"], "r") as f:
            file_content = f.read()
            content_length = len(file_content)
            logger.info(f"Document length: {content_length} characters")

        if content_length <= MIN_CHARS_FOR_SPLIT:
            logger.info("Document below split threshold - no splitting needed")
            results = {
                "splitRecommendations": {
                    "shouldSplit": False,
                    "confidence": 95,
                    "reasoning": "Document small enough for single-unit processing",
                },
                "documentStats": {
                    "totalLength": {"value": content_length, "unit": "characters"}
                },
            }
            prompt = None
        else:
            prompt = (
                self.read_prompt_template("splitting")
                + "\n\nDocument Content:\n"
                + file_content
            )
            generation = span.generation(name="splitting_analysis", input=prompt)
            response = chat_call(query=prompt, expect_json=True)
            generation.end(output=response)

            if "error" in response:
                raise HTTPException(status_code=500, detail=response["error"])

            results = json.loads(response["message"])

        should_split = content_length > MIN_CHARS_FOR_SPLIT
        if should_split:
            splits = results["splitRecommendations"].get("recommendedSplits", [])

            oversized_splits = []
            total_chars = 0

            for split in splits:
                length = split.get("estimatedLength", {}).get("value", 0)
                if length > MAX_SEGMENT_SIZE:
                    oversized_splits.append(split["suggestedTitle"])
                total_chars += length

            if oversized_splits:
                results["splitRecommendations"]["warnings"] = {
                    "oversizedSegments": oversized_splits,
                    "recommendedMaxSize": MAX_SEGMENT_SIZE,
                    "recommendation": "Consider further splitting large segments",
                }

            if abs(total_chars - content_length) > content_length * 0.1:
                logger.warning(
                    f"Split size mismatch. Original: {content_length}, "
                    f"Sum of splits: {total_chars}"
                )
                results["splitRecommendations"]["warnings"] = {
                    "sizeMismatch": {
                        "originalSize": content_length,
                        "splitTotalSize": total_chars,
                        "recommendation": "Review split boundaries",
                    },
                }
        else:
            splits = []

        update_data = {
            "splitting": results,
            "segment_count": len(splits),
            "should_split": should_split,
        }
        db["raw_assets"].update_one({"file_hash": file_hash}, {"$set": update_data})

        return {"status": "success", "splitting": results}
