# api/jobs/assets/splitting.py
import json
import logging
import os

from jobs.assets.base import AssetProcessor
from utils.db_utils import update_asset_status
from utils.generative_utils import make_generative_call

logger = logging.getLogger(__name__)


class SplittingProcessor(AssetProcessor):
    """Process asset content into logical segments using semantic analysis"""

    processor_type = "splitting"
    dependencies = ["refined"]

    MIN_CHARS_FOR_SPLIT = 24000  # ~6k tokens
    IDEAL_SEGMENT_SIZE = 16000  # ~4k tokens
    MAX_SEGMENT_SIZE = 28000  # ~7k tokens

    def __init__(self, file_hash: str):
        super().__init__(file_hash)

    def process(self, span):
        """Main processing method"""
        try:
            update_asset_status(self.file_hash, "processing_splitting")
            logger.info(f"Starting content splitting for {self.file_hash}")

            processed_paths = self.asset.get("processed_paths", {})
            if not processed_paths or "markdown" not in processed_paths:
                error_msg = "Markdown content not available - need to wait for refined processor"
                logger.error(error_msg)
                raise Exception(error_msg)

            with open(processed_paths["markdown"], "r") as f:
                file_content = f.read()
                content_length = len(file_content)
                logger.info(f"Document length: {content_length} characters")

            if content_length <= self.MIN_CHARS_FOR_SPLIT:
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
                prompts_dir = os.path.join("/app", "prompts", "assets")
                with open(os.path.join(prompts_dir, "splitting.txt"), "r") as f:
                    prompt_template = f.read()

                prompt = prompt_template + "\n\nDocument Content:\n" + file_content
                generation = span.generation(
                    name="splitting metadata",
                    input=prompt,
                )
                response_text = make_generative_call(prompt)
                generation.end(
                    output=response_text,
                )

                results = self._extract_and_validate_json(response_text)

            validated_results = self._validate_split_recommendation(
                content_length, results
            )
            standardized_results = self._standardize_results(validated_results)

            splitting_path = os.path.join(self.processed_dir, "splitting.json")
            with open(splitting_path, "w", encoding="utf-8") as f:
                json.dump(standardized_results, f, ensure_ascii=False, indent=2)

            update_data = {
                "splitting": standardized_results,
                "processed_paths.splitting": splitting_path,
                "segment_count": len(standardized_results.get("segments", [])),
                "should_split": standardized_results.get(
                    "splitRecommendations", {}
                ).get("shouldSplit", False),
            }
            self._update_asset(update_data)

            logger.info(f"Completed content splitting for {self.file_hash}")
            update_asset_status(self.file_hash, "splitting_complete")

            input_data = {
                "content_length": content_length,
                "split_threshold": self.MIN_CHARS_FOR_SPLIT,
            }

            if prompt:
                input_data["prompt"] = prompt

            self.trace_output(
                span=span,
                input=input_data,
                output=standardized_results,
            )
            return True

        except Exception as e:
            logger.error(f"Error in content splitting for {self.file_hash}: {str(e)}")
            update_asset_status(self.file_hash, "splitting_error", str(e))
            raise

    def _extract_and_validate_json(self, text: str) -> dict:
        """Extract and validate JSON with detailed error reporting"""
        try:
            start_idx = text.find("{")
            if start_idx == -1:
                raise ValueError("No JSON object found in response")

            brace_count = 0
            in_string = False
            escape_next = False

            for i in range(start_idx, len(text)):
                char = text[i]

                if char == "\\" and not escape_next:
                    escape_next = True
                    continue

                if char == '"' and not escape_next:
                    in_string = not in_string

                if not in_string:
                    if char == "{":
                        brace_count += 1
                    elif char == "}":
                        brace_count -= 1
                        if brace_count == 0:
                            json_str = text[start_idx : i + 1]
                            break

                escape_next = False

            if brace_count != 0:
                raise ValueError("Unbalanced braces in JSON")

            result = json.loads(json_str)

            if not isinstance(result, dict):
                raise ValueError("Parsed JSON is not an object")
            if "splitRecommendations" not in result and "segments" not in result:
                raise ValueError("Missing required splitting information")
            if not isinstance(result["segments"], list):
                raise ValueError("'segments' is not an array")

            return result

        except Exception as e:
            logger.error(f"JSON extraction failed: {str(e)}")
            logger.debug(f"Full text:\n{text}")
            raise json.JSONDecodeError(
                str(e), text, 0
            )  # Ensure we raise JSONDecodeError for retry

    def _standardize_results(self, results: dict) -> dict:
        """Convert different result formats to a standardized format"""
        if "segments" in results:
            return results

        return {"summary": results.get("summary", ""), "segments": []}

    def _validate_split_recommendation(
        self, content_length: int, results: dict
    ) -> dict:
        """
        Validate and potentially override split recommendations based on document size.

        Args:
            content_length: Length of the document in characters
            results: Original split recommendations

        Returns:
            Modified results dict with size-appropriate recommendations
        """
        should_split = content_length > self.MIN_CHARS_FOR_SPLIT

        if not should_split:
            logger.info(
                f"Document length ({content_length} chars) below split threshold "
                f"({self.MIN_CHARS_FOR_SPLIT} chars). No splitting needed."
            )
            return {
                "summary": results.get("summary", ""),
                "documentStats": {
                    "totalLength": {"value": content_length, "unit": "characters"}
                },
                "splitRecommendations": {
                    "shouldSplit": False,
                    "confidence": 95,
                    "reasoning": f"Document length ({content_length} chars) is below the minimum threshold "
                    f"({self.MIN_CHARS_FOR_SPLIT} chars) for splitting. Document can be processed "
                    "as a single unit within typical LLM context windows.",
                },
            }

        # If we get here, the document is large enough to potentially need splitting
        if "splitRecommendations" in results:
            splits = results["splitRecommendations"].get("recommendedSplits", [])

            # Validate each proposed split size
            total_chars = 0
            oversized_splits = []

            for split in splits:
                length = split.get("estimatedLength", {}).get("value", 0)
                if length > self.MAX_SEGMENT_SIZE:
                    oversized_splits.append(split["suggestedTitle"])
                total_chars += length

            # Add warnings if splits aren't size-optimized
            if oversized_splits:
                results["splitRecommendations"]["warnings"] = {
                    "oversizedSegments": oversized_splits,
                    "recommendedMaxSize": self.MAX_SEGMENT_SIZE,
                    "recommendation": "Consider further splitting large segments for optimal processing",
                }

            # Validate total size matches original content
            if (
                abs(total_chars - content_length) > content_length * 0.1
            ):  # 10% tolerance
                logger.warning(
                    f"Split size mismatch. Original: {content_length}, "
                    f"Sum of splits: {total_chars}"
                )
                results["splitRecommendations"]["warnings"] = {
                    **results["splitRecommendations"].get("warnings", {}),
                    "sizeMismatch": {
                        "originalSize": content_length,
                        "splitTotalSize": total_chars,
                        "recommendation": "Review split boundaries for potential content loss",
                    },
                }

        return results
