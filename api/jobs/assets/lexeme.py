# api/jobs/assets/lexeme.py

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Set

from jobs.assets.base import AssetProcessor
from utils.db_utils import update_asset_status
from utils.generative_utils import make_generative_call

logger = logging.getLogger(__name__)


class LexemeProcessor(AssetProcessor):
    """Process lexemes from refined assets using category-specific and general prompts"""

    processor_type = "lexemes"
    dependencies = ["refined", "metadata"]

    CATEGORY_PROMPT_MAP = {
        "Technical Documentation": "technical.txt",
        "Educational/Academic": "academic.txt",
        "Commercial/Business": "business.txt",
        "Legal/Compliance": "legal.txt",
        "Research/Scientific": "research.txt",
        "Administrative/Operational": "administrative.txt",
        "General/Mixed": "general.txt",
    }

    def __init__(self, file_hash: str):
        super().__init__(file_hash)
        self.prompts_dir = os.path.join("/app", "prompts", "assets", "lexeme")

    def process(self, span):
        """Main processing method"""
        try:
            update_asset_status(self.file_hash, "processing_lexemes")
            logger.info(f"Starting lexeme processing for {self.file_hash}")

            content = self._get_document_content()

            category = self._get_document_category()
            prompts_to_run = self._get_prompts_for_category(category)

            all_lexemes = []
            for prompt_file in prompts_to_run:
                prompt_lexemes = self._process_with_prompt(prompt_file, content, span)
                all_lexemes.extend(prompt_lexemes)

            merged_lexemes = self._merge_lexeme_results(all_lexemes)

            self._save_lexeme_results(merged_lexemes)

            logger.info(f"Completed lexeme processing for {self.file_hash}")
            update_asset_status(self.file_hash, "lexemes_complete")

            self.trace_output(
                span=span,
                input={"category": category, "prompts_used": prompts_to_run},
                output={"lexeme_count": len(merged_lexemes)},
            )
            return True

        except Exception as e:
            logger.error(f"Error processing lexemes for {self.file_hash}: {str(e)}")
            update_asset_status(self.file_hash, "lexemes_error", str(e))
            raise

    def _get_document_category(self) -> str:
        """Extract primary category from metadata"""
        metadata = self.asset.get("metadata", {})
        doc_metadata = metadata.get("documentMetadata", {})
        primary_type = doc_metadata.get("primaryType", {})

        category = primary_type.get("category")
        if not category:
            logger.warning(
                f"No category found for {self.file_hash}, defaulting to General/Mixed"
            )
            return "General/Mixed"

        return category

    def _get_prompts_for_category(self, category: str) -> Set[str]:
        """Determine which prompt files to use based on category"""
        prompts = {"general.txt"}  # Always include general prompt

        if category in self.CATEGORY_PROMPT_MAP:
            category_prompt = self.CATEGORY_PROMPT_MAP[category]
            if os.path.exists(os.path.join(self.prompts_dir, category_prompt)):
                prompts.add(category_prompt)
            else:
                logger.warning(
                    f"Prompt file {category_prompt} not found for category {category}"
                )

        return prompts

    def _get_document_content(self) -> str:
        """Get the refined document content"""
        processed_paths = self.asset.get("processed_paths", {})
        if not processed_paths or "markdown" not in processed_paths:
            raise Exception("Refined content not available")

        with open(processed_paths["markdown"], "r") as f:
            return f.read()

    def _process_with_prompt(self, prompt_file: str, content: str, span) -> List[Dict]:
        """Process content with a specific prompt file"""
        try:
            prompt_path = os.path.join(self.prompts_dir, prompt_file)
            with open(prompt_path, "r") as f:
                prompt_template = f.read()

            prompt = f"{prompt_template}\n\nDocument Content:\n{content}"

            generation = span.generation(
                f"lexeme_extraction_{prompt_file}", input=prompt
            )
            response = make_generative_call(prompt)
            lexemes = self._parse_lexemes(response)

            generation.end(
                output=response,
                metadata={"prompt_file": prompt_file, "lexeme_count": len(lexemes)},
            )

            return lexemes

        except Exception as e:
            logger.error(f"Error processing with prompt {prompt_file}: {str(e)}")
            raise

    def _merge_lexeme_results(self, lexemes: List[Dict]) -> List[Dict]:
        """Merge and deduplicate lexemes from multiple prompts"""
        merged = {}

        for lexeme in lexemes:
            term = lexeme["term"].lower().strip()

            if term in merged:
                existing = merged[term]
                existing["frequency"] += lexeme.get("frequency", 1)
                existing["context"].extend(lexeme.get("context", []))
                existing["related_terms"].extend(lexeme.get("related_terms", []))

                if lexeme.get("confidence", 0) > existing["confidence"]:
                    existing["confidence"] = lexeme["confidence"]
            else:
                merged[term] = {
                    "term": term,
                    "frequency": lexeme.get("frequency", 1),
                    "context": lexeme.get("context", []),
                    "related_terms": lexeme.get("related_terms", []),
                    "confidence": lexeme.get("confidence", 1.0),
                }

        for lexeme in merged.values():
            lexeme["context"] = list(dict.fromkeys(lexeme["context"]))
            lexeme["related_terms"] = list(dict.fromkeys(lexeme["related_terms"]))

        return list(merged.values())

    def _save_lexeme_results(self, lexemes: List[Dict]):
        """Save processed lexemes"""
        lexemes_path = os.path.join(self.processed_dir, "lexemes.json")
        os.makedirs(os.path.dirname(lexemes_path), exist_ok=True)

        with open(lexemes_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "lexemes": lexemes,
                    "metadata": {
                        "count": len(lexemes),
                        "processed_at": datetime.now().isoformat(),
                        "asset_id": self.file_hash,
                    },
                },
                f,
                ensure_ascii=False,
                indent=2,
            )

        update_data = {
            "processed_paths.lexemes": lexemes_path,
            "lexemes": lexemes,
            "lexeme_count": len(lexemes),
        }
        self._update_asset(update_data)
