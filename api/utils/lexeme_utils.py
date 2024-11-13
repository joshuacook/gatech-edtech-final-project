import os
from typing import Dict, List, Set


def get_prompts_for_category(category: str) -> Set[str]:
    """Determine which prompt files to use based on category"""
    CATEGORY_PROMPT_MAP = {
        "Technical Documentation": "technical.txt",
        "Educational/Academic": "academic.txt",
        "Commercial/Business": "business.txt",
        "Legal/Compliance": "legal.txt",
        "Research/Scientific": "research.txt",
        "Administrative/Operational": "administrative.txt",
        "General/Mixed": "general.txt",
    }

    prompts = {"general.txt"}  # Always include general prompt

    if category in CATEGORY_PROMPT_MAP:
        category_prompt = CATEGORY_PROMPT_MAP[category]
        prompts_dir = os.path.join("/app", "prompts", "assets", "lexeme")
        if os.path.exists(os.path.join(prompts_dir, category_prompt)):
            prompts.add(category_prompt)

    return prompts


def merge_lexeme_results(lexemes: List[Dict]) -> List[Dict]:
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

    # Deduplicate lists
    for lexeme in merged.values():
        lexeme["context"] = list(dict.fromkeys(lexeme["context"]))
        lexeme["related_terms"] = list(dict.fromkeys(lexeme["related_terms"]))

    return list(merged.values())
