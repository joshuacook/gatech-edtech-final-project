# api/models/concepts.py

from typing import List, Optional

from pydantic import BaseModel


class ConceptCreate(BaseModel):
    name: str
    definition: str
    citations: List[str]
    synonyms: List[str]
    understanding_level: str


class ConceptUpdate(BaseModel):
    definition: Optional[str] = None
    citations: Optional[List[str]] = None
    synonyms: Optional[List[str]] = None
    understanding_level: Optional[str] = None


class Concept(BaseModel):
    name: str
    definition: str
    citations: List[str]
    synonyms: List[str]
    understanding_level: str
    created_at: str
