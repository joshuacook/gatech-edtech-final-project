from typing import Dict, List, Optional, Union

from pydantic import BaseModel


class ImplementationDetail(BaseModel):
    key: str
    value: str


class ImplementationCreate(BaseModel):
    name: str
    type: str
    description: str
    details: Dict[str, str]
    concept: str
    status: str


class ImplementationUpdate(BaseModel):
    type: Optional[str] = None
    description: Optional[str] = None
    details: Optional[Dict[str, str]] = None
    concept: Optional[str] = None
    status: Optional[str] = None


class Implementation(ImplementationCreate):
    created_at: str


class ProcedureStep(BaseModel):
    order: int
    description: str
    expected_duration: str


class ProcedureCreate(BaseModel):
    name: str
    description: str
    steps: List[ProcedureStep]
    concept: str
    status: str


class ProcedureUpdate(BaseModel):
    description: Optional[str] = None
    steps: Optional[List[ProcedureStep]] = None
    concept: Optional[str] = None
    status: Optional[str] = None


class Procedure(ProcedureCreate):
    created_at: str


class ToolCreate(BaseModel):
    name: str
    purpose: str
    type: str
    concepts: List[str]
    integration_details: Optional[Dict[str, Union[str, List[str]]]] = None
    status: str


class ToolUpdate(BaseModel):
    purpose: Optional[str] = None
    type: Optional[str] = None
    concepts: Optional[List[str]] = None
    integration_details: Optional[Dict[str, Union[str, List[str]]]] = None
    status: Optional[str] = None


class Tool(ToolCreate):
    created_at: str
