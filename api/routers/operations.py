import logging
from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException
from models.operations import (Implementation, ImplementationCreate, Procedure,
                               ProcedureCreate, Tool, ToolCreate)
from services.database import get_db

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


operations_router = APIRouter()


@operations_router.get("/implementations", response_model=List[Implementation])
async def get_implementations():
    """Get all implementations"""
    try:
        logger.debug("Fetching all implementations")
        db = get_db()
        if isinstance(db, dict) and "error" in db:
            raise HTTPException(status_code=500, detail=db["error"])
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
        if isinstance(db, dict) and "error" in db:
            raise HTTPException(status_code=500, detail=db["error"])

        if db["implementations"].find_one({"name": implementation.name}):
            raise HTTPException(status_code=400, detail="Implementation already exists")

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
        if isinstance(db, dict) and "error" in db:
            raise HTTPException(status_code=500, detail=db["error"])
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


@operations_router.get("/procedures", response_model=List[Procedure])
async def get_procedures():
    """Get all procedures"""
    try:
        logger.debug("Fetching all procedures")
        db = get_db()
        if isinstance(db, dict) and "error" in db:
            raise HTTPException(status_code=500, detail=db["error"])
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
        if isinstance(db, dict) and "error" in db:
            raise HTTPException(status_code=500, detail=db["error"])

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


@operations_router.get("/tools", response_model=List[Tool])
async def get_tools():
    """Get all tools"""
    try:
        logger.debug("Fetching all tools")
        db = get_db()
        if isinstance(db, dict) and "error" in db:
            raise HTTPException(status_code=500, detail=db["error"])
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
        if isinstance(db, dict) and "error" in db:
            raise HTTPException(status_code=500, detail=db["error"])

        if db["tools"].find_one({"name": tool.name}):
            raise HTTPException(status_code=400, detail="Tool already exists")

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


@operations_router.get("/concepts/{concept_name}/operations")
async def get_operations_by_concept(concept_name: str):
    """Get all operational elements related to a specific concept"""
    try:
        logger.debug(f"Fetching operations for concept: {concept_name}")
        db = get_db()
        if isinstance(db, dict) and "error" in db:
            raise HTTPException(status_code=500, detail=db["error"])

        if not db["concepts"].find_one({"name": concept_name}):
            raise HTTPException(status_code=404, detail="Concept not found")

        implementations = list(db["implementations"].find({"concept": concept_name}))
        for impl in implementations:
            impl.pop("_id")

        procedures = list(db["procedures"].find({"concept": concept_name}))
        for proc in procedures:
            proc.pop("_id")

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
