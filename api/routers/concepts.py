import logging
import os
from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException
from models.concepts import Concept, ConceptCreate, ConceptUpdate
from pymongo import MongoClient

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


concepts_router = APIRouter()


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


@concepts_router.get("/concepts", response_model=List[Concept])
async def get_concepts():
    """Get all concepts"""
    try:
        logger.debug("Attempting to fetch concepts from MongoDB")
        db = get_db()
        concepts_collection = db["concepts"]

        count = concepts_collection.count_documents({})
        logger.debug(f"Found {count} concepts in database")

        concepts = []
        for concept in concepts_collection.find():
            logger.debug(f"Processing concept: {concept.get('name', 'unknown')}")
            concept_dict = {
                "name": concept["name"],
                "definition": concept["definition"],
                "citations": concept["citations"],
                "synonyms": concept["synonyms"],
                "understanding_level": concept["understanding_level"],
                "created_at": concept["created_at"],
            }
            concepts.append(concept_dict)

        logger.debug(f"Returning {len(concepts)} concepts")
        return concepts

    except Exception as e:
        logger.error(f"Error fetching concepts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@concepts_router.post("/concepts", response_model=Concept)
async def create_concept(concept: ConceptCreate):
    """Create a new concept"""
    try:
        logger.debug(f"Attempting to create concept: {concept.name}")
        db = get_db()
        concepts_collection = db["concepts"]

        if concepts_collection.find_one({"name": concept.name}):
            raise HTTPException(status_code=400, detail="Concept already exists")

        concept_dict = concept.model_dump()
        concept_dict["created_at"] = datetime.now().strftime("%Y-%m-%d")

        result = concepts_collection.insert_one(concept_dict)
        logger.debug(f"Created concept with ID: {result.inserted_id}")

        created_concept = concepts_collection.find_one({"_id": result.inserted_id})
        created_concept.pop("_id")
        return created_concept

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error creating concept: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@concepts_router.get("/concepts/{name}", response_model=Concept)
async def get_concept(name: str):
    """Get a specific concept by name"""
    try:
        logger.debug(f"Attempting to fetch concept: {name}")
        db = get_db()
        concepts_collection = db["concepts"]

        concept = concepts_collection.find_one({"name": name})
        if not concept:
            raise HTTPException(status_code=404, detail="Concept not found")

        concept.pop("_id")
        return concept

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error fetching concept: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@concepts_router.put("/concepts/{name}", response_model=Concept)
async def update_concept(name: str, concept_update: ConceptUpdate):
    """Update a concept"""
    try:
        logger.debug(f"Attempting to update concept: {name}")
        db = get_db()
        concepts_collection = db["concepts"]

        update_data = {
            k: v for k, v in concept_update.model_dump().items() if v is not None
        }
        if not update_data:
            raise HTTPException(status_code=400, detail="No valid update data provided")

        result = concepts_collection.update_one({"name": name}, {"$set": update_data})

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Concept not found")

        updated_concept = concepts_collection.find_one({"name": name})
        updated_concept.pop("_id")
        return updated_concept

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error updating concept: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@concepts_router.delete("/concepts/{name}")
async def delete_concept(name: str):
    """Delete a concept"""
    try:
        logger.debug(f"Attempting to delete concept: {name}")
        db = get_db()
        concepts_collection = db["concepts"]

        result = concepts_collection.delete_one({"name": name})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Concept not found")

        return {"message": "Concept deleted successfully"}

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error deleting concept: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
