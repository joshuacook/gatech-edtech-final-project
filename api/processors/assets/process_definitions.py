import json
from datetime import datetime

from processors.base import BaseAssetProcessor
from routers.chat import chat_call


class ProcessDefinitions(BaseAssetProcessor):
    def __init__(self):
        super().__init__("definitions", "definitions")
        self.required_paths = ["markdown", "metadata"]

    async def process_asset(self, file_hash: str, asset: dict, db: dict, span):
        existing_citations = self._get_existing_citations(
            db, asset.get("citations", {})
        )

        definitions = {}
        concepts_collection = db["concepts"]

        for lexeme, citations_by_doc in existing_citations.items():
            all_citations = [
                c for doc_citations in citations_by_doc.values() for c in doc_citations
            ]

            input_data = {
                "lexeme": lexeme,
                "citations": all_citations,
                "domainContext": asset.get("metadata", {})
                .get("documentMetadata", {})
                .get("domain", ""),
            }

            definition_response = self._generate_definition(input_data)
            definitions[lexeme] = definition_response

            concept_data = {
                "name": lexeme,
                "definition": definition_response["definition"]["primaryStatement"],
                "citations": [c["quote"] for c in all_citations],
                "synonyms": [],
                "understanding_level": "Practical",
                "created_at": datetime.now().strftime("%Y-%m-%d"),
            }

            concepts_collection.update_one(
                {"name": lexeme}, {"$set": concept_data}, upsert=True
            )

        db["raw_assets"].update_one(
            {"file_hash": file_hash}, {"$set": {"definitions": definitions}}
        )

        return {"status": "success", "definition_count": len(definitions)}

    def _get_existing_citations(self, db, current_citations):
        citations_by_lexeme = {}

        docs_with_citations = db["raw_assets"].find(
            {"citations": {"$exists": True}}, {"file_hash": 1, "citations": 1}
        )

        for doc in docs_with_citations:
            for lexeme, citations in doc["citations"].items():
                if lexeme not in citations_by_lexeme:
                    citations_by_lexeme[lexeme] = {}
                citations_by_lexeme[lexeme][doc["file_hash"]] = citations

        return citations_by_lexeme

    def _generate_definition(self, data):
        prompt = self.read_prompt_template("concept/definition.txt")
        response = chat_call(
            query=prompt + "\n\nInput:\n" + json.dumps(data), expect_json=True
        )
        return response
