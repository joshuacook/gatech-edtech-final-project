from typing import Optional

from pydantic import BaseModel


class RelationshipCreate(BaseModel):
    source: str
    target: str
    type: str
    connection_type: Optional[str] = None
    strength: float


class RelationshipUpdate(BaseModel):
    type: Optional[str] = None
    connection_type: Optional[str] = None
    strength: Optional[float] = None


class Relationship(BaseModel):
    source: str
    target: str
    type: str
    connection_type: Optional[str]
    strength: float
    created_at: str


class RelationshipMetrics(BaseModel):
    total_relationships: int
    average_strength: float
    network_density: float
