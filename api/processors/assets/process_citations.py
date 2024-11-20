import json
from datetime import datetime

from processors.base import BaseAssetProcessor
from routers.chat import chat_call


class ProcessCitations(BaseAssetProcessor):
    def __init__(self):
        super().__init__("citations", "citations")
        self.required_paths = ["markdown", "metadata"]

    async def process_asset(self, file_hash: str, asset: dict, db: dict, span):
        citations_collection = db["citations"]

        lexemes = asset.get("lexemes", [])
        with open(asset["processed_paths"]["markdown"], "r") as f:
            processed_content = f.read()
        with open(asset["processed_paths"]["metadata"], "r") as f:
            metadata = json.load(f)

        citations_results = {}
        for lexeme in lexemes:
            citations = self._extract_and_validate_citations(
                lexeme["term"], processed_content, metadata, file_hash, span
            )

            if citations["valid_citations"]:
                citations_collection.update_one(
                    {"lexeme": lexeme["term"]},
                    {
                        "$set": {
                            "lexeme": lexeme["term"],
                            f"citations.{file_hash}": citations["valid_citations"],
                            "last_updated": datetime.now(),
                        },
                        "$addToSet": {"documents": file_hash},
                    },
                    upsert=True,
                )

                citations_results[lexeme["term"]] = {
                    "valid_count": len(citations["valid_citations"]),
                    "issues_count": len(citations["issues"]),
                }

            if citations["issues"]:
                span.event(
                    name="citation_issues",
                    metadata={"lexeme": lexeme["term"], "issues": citations["issues"]},
                )

        return {"status": "success", "citations": citations_results}

    def _extract_and_validate_citations(
        self, lexeme, content, metadata, file_hash, span
    ):
        extraction_data = {
            "lexeme": lexeme,
            "metadata": metadata,
            "documents": {"processed": content, "original": None, "metadata": metadata},
        }

        extraction_generation = span.generation(
            name="citation_extraction", metadata={"lexeme": lexeme}
        )

        extraction_response = self._get_citations(extraction_data)
        extraction_generation.end(output=extraction_response)

        valid_citations = []
        validation_issues = []

        validation_generation = span.generation(
            name="citation_validation", metadata={"lexeme": lexeme}
        )

        for citation in extraction_response["citations"]:
            validation = self._validate_citation(citation, content, metadata)

            if validation["verified"]:
                if validation["recommendations"].get("correctedQuote"):
                    citation["quote"] = validation["recommendations"]["correctedQuote"]
                citation["source_document"] = file_hash
                citation["extraction_date"] = datetime.now().isoformat()
                valid_citations.append(citation)
            else:
                validation_issues.append(
                    {
                        "citation": citation,
                        "validation": validation,
                        "reason": validation["status"],
                    }
                )

        validation_generation.end(
            output={
                "valid_count": len(valid_citations),
                "issues_count": len(validation_issues),
            }
        )

        return {"valid_citations": valid_citations, "issues": validation_issues}

    def _get_citations(self, data):
        prompt = self.read_prompt_template("citation/extraction.txt")
        response = chat_call(
            query=prompt + "\n\nInput:\n" + json.dumps(data), expect_json=True
        )

        # Handle both response formats
        if "json" in response:
            return response["json"]
        else:
            # Parse JSON from message text
            return json.loads(response["message"])

    def _validate_citation(self, citation, content, metadata):
        validation_data = {
            "citation": {"quote": citation["quote"], "location": citation["location"]},
            "documents": {"processed": content, "original": None, "metadata": metadata},
        }
        prompt = self.read_prompt_template("citation/verification.txt")
        response = chat_call(
            query=prompt + "\n\nInput:\n" + json.dumps(validation_data),
            expect_json=True,
        )

        # Handle response formats
        if "json" in response:
            validation = response["json"]
        else:
            validation = json.loads(response["message"])

        # Ensure required fields exist
        return {
            "verified": validation.get("verified", False),
            "status": validation.get("status", "Unknown"),
            "recommendations": validation.get("recommendations", {}),
        }
