import json
import logging
import re

from fastapi import HTTPException
from processors.base import BaseAssetProcessor
from routers.chat import chat_call
from utils.lexeme_utils import get_prompts_for_category, merge_lexeme_results

logger = logging.getLogger(__name__)


class ProcessLexemes(BaseAssetProcessor):
    def __init__(self):
        super().__init__("lexemes", "lexemes")
        self.required_paths = ["markdown", "metadata"]

    def _parse_chat_response(self, response, prompt_file):
        """Helper method to safely parse chat API response"""
        logger.debug(f"Raw response for {prompt_file}: {response}")

        if not isinstance(response, dict):
            logger.error(f"Invalid response type for {prompt_file}: {type(response)}")
            raise ValueError(f"Expected dict response, got {type(response)}")

        message = response.get("message")
        if not message:
            logger.error(f"No message in response for {prompt_file}")
            raise ValueError("Empty message in response")

        # Try parsing as direct JSON first
        try:
            result = json.loads(message)
            if isinstance(result, dict) and "lexemes" in result:
                return result
        except json.JSONDecodeError:
            pass

        # Try extracting from markdown
        json_pattern = r"```(?:json)?\s*\n([\s\S]*?)\n```"
        matches = re.findall(json_pattern, message)

        if not matches:
            logger.error(f"No JSON code blocks found in message for {prompt_file}")
            raise ValueError("No JSON content found in response")

        for match in matches:
            try:
                result = json.loads(match.strip())
                if isinstance(result, dict) and "lexemes" in result:
                    return result
            except json.JSONDecodeError:
                continue

        raise ValueError("No valid lexeme data found in response")

    async def process_asset(self, file_hash: str, asset: dict, db: dict, span):
        errors = []
        all_lexemes = []

        try:
            with open(asset["processed_paths"]["markdown"], "r") as f:
                content = f.read()

            category = (
                asset.get("metadata", {})
                .get("documentMetadata", {})
                .get("primaryType", {})
                .get("category", "General/Mixed")
            )

            prompts_to_run = get_prompts_for_category(category)
            logger.info(
                f"Processing {len(prompts_to_run)} prompts for category {category}"
            )

            for prompt_file in prompts_to_run:
                try:
                    prompt = (
                        self.read_prompt_template(prompt_file, is_lexeme=True)
                        + "\n\nDocument Content:\n"
                        + content
                    )

                    generation = span.generation(
                        name=f"lexeme_generation_{prompt_file}",
                        input={"prompt_file": prompt_file},
                    )

                    response = chat_call(query=prompt, expect_json=True)
                    generation.end(output={"status": "completed"})

                    if "error" in response:
                        error_msg = (
                            f"Chat API error for {prompt_file}: {response['error']}"
                        )
                        logger.error(error_msg)
                        errors.append(error_msg)
                        continue

                    parsed_data = self._parse_chat_response(response, prompt_file)
                    prompt_lexemes = parsed_data.get("lexemes", [])

                    if prompt_lexemes:
                        all_lexemes.extend(prompt_lexemes)
                        logger.info(
                            f"Extracted {len(prompt_lexemes)} lexemes from {prompt_file}"
                        )
                    else:
                        logger.warning(
                            f"No lexemes found in response for {prompt_file}"
                        )

                except Exception as e:
                    error_msg = f"Error processing {prompt_file}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    continue

            if not all_lexemes:
                error_details = "; ".join(errors) if errors else "No lexemes found"
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to extract any valid lexemes: {error_details}",
                )

            merged_lexemes = merge_lexeme_results(all_lexemes)

            update_data = {
                "lexemes": merged_lexemes,
                "lexeme_count": len(merged_lexemes),
                "processing_errors": errors if errors else None,
            }

            db["raw_assets"].update_one({"file_hash": file_hash}, {"$set": update_data})

            return {
                "status": "success",
                "lexeme_count": len(merged_lexemes),
                "errors": errors if errors else None,
            }

        except Exception as e:
            logger.error(f"Lexeme processing failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
