import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Union

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Pydantic models for implementations
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


# Pydantic models for procedures
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


# Pydantic models for tools
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


operations_router = APIRouter()


def get_db():
    try:
        client = MongoClient(os.getenv("MONGODB_URI", "mongodb://db:27017/"))
        db = client["chelle"]
        client.admin.command("ping")
        logger.debug("Successfully connected to MongoDB")
        return db
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise HTTPException(status_code=500, detail="Database connection failed")


# Implementation endpoints
@operations_router.get("/implementations", response_model=List[Implementation])
async def get_implementations():
    """Get all implementations"""
    try:
        logger.debug("Fetching all implementations")
        db = get_db()
        implementations = list(db["implementations"].find())
        return implementations
    except Exception as e:
        logger.error(f"Error fetching implementations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@operations_router.post("/implementations", response_model=Implementation)
async def create_implementation(implementation: ImplementationCreate):
    """Create a new implementation"""
    try:
        logger.debug(f"Creating implementation: {implementation.name}")
        db = get_db()

        # Check if implementation already exists
        if db["implementations"].find_one({"name": implementation.name}):
            raise HTTPException(status_code=400, detail="Implementation already exists")

        # Verify concept exists
        if not db["concepts"].find_one({"name": implementation.concept}):
            raise HTTPException(
                status_code=400, detail="Referenced concept does not exist"
            )

        implementation_dict = implementation.model_dump()
        implementation_dict["created_at"] = datetime.now().strftime("%Y-%m-%d")

        result = db["implementations"].insert_one(implementation_dict)
        created_implementation = db["implementations"].find_one(
            {"_id": result.inserted_id}
        )
        created_implementation.pop("_id")
        return created_implementation
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error creating implementation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@operations_router.get("/implementations/{name}", response_model=Implementation)
async def get_implementation(name: str):
    """Get a specific implementation"""
    try:
        logger.debug(f"Fetching implementation: {name}")
        db = get_db()
        implementation = db["implementations"].find_one({"name": name})
        if not implementation:
            raise HTTPException(status_code=404, detail="Implementation not found")
        implementation.pop("_id")
        return implementation
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error fetching implementation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Procedure endpoints
@operations_router.get("/procedures", response_model=List[Procedure])
async def get_procedures():
    """Get all procedures"""
    try:
        logger.debug("Fetching all procedures")
        db = get_db()
        procedures = list(db["procedures"].find())
        for proc in procedures:
            proc.pop("_id")
        return procedures
    except Exception as e:
        logger.error(f"Error fetching procedures: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@operations_router.post("/procedures", response_model=Procedure)
async def create_procedure(procedure: ProcedureCreate):
    """Create a new procedure"""
    try:
        logger.debug(f"Creating procedure: {procedure.name}")
        db = get_db()

        if db["procedures"].find_one({"name": procedure.name}):
            raise HTTPException(status_code=400, detail="Procedure already exists")

        if not db["concepts"].find_one({"name": procedure.concept}):
            raise HTTPException(
                status_code=400, detail="Referenced concept does not exist"
            )

        procedure_dict = procedure.model_dump()
        procedure_dict["created_at"] = datetime.now().strftime("%Y-%m-%d")

        result = db["procedures"].insert_one(procedure_dict)
        created_procedure = db["procedures"].find_one({"_id": result.inserted_id})
        created_procedure.pop("_id")
        return created_procedure
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error creating procedure: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Tool endpoints
@operations_router.get("/tools", response_model=List[Tool])
async def get_tools():
    """Get all tools"""
    try:
        logger.debug("Fetching all tools")
        db = get_db()
        tools = list(db["tools"].find())
        for tool in tools:
            tool.pop("_id")
        return tools
    except Exception as e:
        logger.error(f"Error fetching tools: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@operations_router.post("/tools", response_model=Tool)
async def create_tool(tool: ToolCreate):
    """Create a new tool"""
    try:
        logger.debug(f"Creating tool: {tool.name}")
        db = get_db()

        if db["tools"].find_one({"name": tool.name}):
            raise HTTPException(status_code=400, detail="Tool already exists")

        # Verify all referenced concepts exist
        for concept in tool.concepts:
            if not db["concepts"].find_one({"name": concept}):
                raise HTTPException(
                    status_code=400,
                    detail=f"Referenced concept does not exist: {concept}",
                )

        tool_dict = tool.model_dump()
        tool_dict["created_at"] = datetime.now().strftime("%Y-%m-%d")

        result = db["tools"].insert_one(tool_dict)
        created_tool = db["tools"].find_one({"_id": result.inserted_id})
        created_tool.pop("_id")
        return created_tool
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error creating tool: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Get operations by concept
@operations_router.get("/concepts/{concept_name}/operations")
async def get_operations_by_concept(concept_name: str):
    """Get all operational elements related to a specific concept"""
    try:
        logger.debug(f"Fetching operations for concept: {concept_name}")
        db = get_db()

        # Verify concept exists
        if not db["concepts"].find_one({"name": concept_name}):
            raise HTTPException(status_code=404, detail="Concept not found")

        # Get related implementations
        implementations = list(db["implementations"].find({"concept": concept_name}))
        for impl in implementations:
            impl.pop("_id")

        # Get related procedures
        procedures = list(db["procedures"].find({"concept": concept_name}))
        for proc in procedures:
            proc.pop("_id")

        # Get related tools
        tools = list(db["tools"].find({"concepts": concept_name}))
        for tool in tools:
            tool.pop("_id")

        return {
            "implementations": implementations,
            "procedures": procedures,
            "tools": tools,
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error fetching operations for concept: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
