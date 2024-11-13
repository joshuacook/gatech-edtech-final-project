import json

from fastapi import HTTPException
from processors.base import BaseAssetProcessor
from routers.chat import chat_call
from utils.lexeme_utils import get_prompts_for_category, merge_lexeme_results


class ProcessLexemes(BaseAssetProcessor):
    def __init__(self):
        super().__init__("lexemes", "lexemes")
        self.required_paths = ["markdown", "metadata"]

    async def process_asset(self, file_hash: str, asset: dict, db: dict, span):
        with open(asset["processed_paths"]["markdown"], "r") as f:
            content = f.read()

        category = (
            asset.get("metadata", {})
            .get("documentMetadata", {})
            .get("primaryType", {})
            .get("category", "General/Mixed")
        )
        prompts_to_run = get_prompts_for_category(category)
        all_lexemes = []

        for prompt_file in prompts_to_run:
            prompt = (
                self.read_prompt_template(prompt_file, is_lexeme=True)
                + "\n\nDocument Content:\n"
                + content
            )
            prompt_generation = span.generation(
                name=f"lexeme_generation_{prompt_file}", input=prompt
            )
            response = chat_call(query=prompt)
            prompt_generation.end(output=response)

            if "error" in response:
                raise HTTPException(status_code=500, detail=response["error"])

            response_text = response["message"]
            prompt_lexemes = json.loads(response_text)["lexemes"]
            all_lexemes.extend(prompt_lexemes)

        merged_lexemes = merge_lexeme_results(all_lexemes)
        update_data = {
            "lexemes": merged_lexemes,
            "lexeme_count": len(merged_lexemes),
        }
        db["raw_assets"].update_one({"file_hash": file_hash}, {"$set": update_data})

        return {"status": "success", "lexemes": merged_lexemes}
