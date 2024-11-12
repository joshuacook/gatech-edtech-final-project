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

    def __init__(self, file_hash: str):
        super().__init__(file_hash)

    def process(self, span):
        """Main processing method"""
        try:
            update_asset_status(self.file_hash, "processing_splitting")
            logger.info(f"Starting content splitting for {self.file_hash}")

            # Get the processed markdown content
            processed_paths = self.asset.get("processed_paths", {})
            if not processed_paths or "markdown" not in processed_paths:
                error_msg = "Markdown content not available - need to wait for refined processor"
                logger.error(error_msg)
                raise Exception(error_msg)

            # Read the prompt template
            prompts_dir = os.path.join("/app", "prompts", "assets")
            with open(os.path.join(prompts_dir, "splitting.txt"), "r") as f:
                prompt_template = f.read()

            # Read the processed content
            with open(processed_paths["markdown"], "r") as f:
                file_content = f.read()
                logger.debug(
                    f"Read {len(file_content)} characters from processed content"
                )

            # Prepare and make the generative call
            prompt = prompt_template + "\n\nDocument Content:\n" + file_content
            generation = span.generation(
                name="splitting metadata",
                input=prompt,
            )
            response_text = make_generative_call(prompt)
            generation.end(
                output=response_text,
            )

            logger.debug(f"Raw chat API response:\n{response_text}")

            # Extract and validate JSON
            splitting_results = self._extract_and_validate_json(response_text)
            logger.info(
                f"Successfully parsed splitting results with {len(splitting_results.get('segments', []))} segments"
            )

            # Save splitting results to a file
            splitting_path = os.path.join(self.processed_dir, "splitting.json")
            with open(splitting_path, "w", encoding="utf-8") as f:
                json.dump(splitting_results, f, ensure_ascii=False, indent=2)

            # Update asset with splitting results and path
            update_data = {
                "splitting": splitting_results,
                "processed_paths.splitting": splitting_path,
                "segment_count": len(splitting_results.get("segments", [])),
            }
            self._update_asset(update_data)

            logger.info(f"Completed content splitting for {self.file_hash}")
            update_asset_status(self.file_hash, "splitting_complete")

            self.trace_output(
                span=span,
                input={"prompt": prompt},
                output={"splitting_results": splitting_results},
            )
            return True

        except Exception as e:
            logger.error(f"Error in content splitting for {self.file_hash}: {str(e)}")
            update_asset_status(self.file_hash, "splitting_error", str(e))
            raise

    def _extract_and_validate_json(self, text: str) -> dict:
        """Extract and validate JSON with detailed error reporting"""
        try:
            # Find the first { and last }
            start_idx = text.find("{")
            if start_idx == -1:
                raise ValueError("No JSON object found in response")

            # Track nested braces to find the proper closing brace
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

            # Try to parse the JSON
            result = json.loads(json_str)

            # Validate expected structure
            if not isinstance(result, dict):
                raise ValueError("Parsed JSON is not an object")
            if "segments" not in result:
                raise ValueError("Missing required 'segments' key")
            if not isinstance(result["segments"], list):
                raise ValueError("'segments' is not an array")

            return result

        except Exception as e:
            logger.error(f"JSON extraction failed: {str(e)}")
            logger.debug(f"Full text:\n{text}")
            raise json.JSONDecodeError(
                str(e), text, 0
            )  # Ensure we raise JSONDecodeError for retry
