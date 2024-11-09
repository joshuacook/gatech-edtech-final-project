import logging
from datetime import datetime
from typing import List

import networkx as nx
from fastapi import APIRouter, HTTPException
from models.relationships import (Relationship, RelationshipCreate,
                                  RelationshipMetrics, RelationshipUpdate)
from services.database import get_db

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


relationships_router = APIRouter()


@relationships_router.get("/relationships", response_model=List[Relationship])
async def get_relationships():
    """Get all relationships"""
    try:
        logger.debug("Attempting to fetch relationships from MongoDB")
        db = get_db()
        if isinstance(db, dict) and "error" in db:
            raise HTTPException(status_code=500, detail=db["error"])
        relationships_collection = db["relationships"]

        relationships = []
        for rel in relationships_collection.find():
            relationship_dict = {
                "source": rel["source"],
                "target": rel["target"],
                "type": rel["type"],
                "connection_type": rel.get("connection_type"),
                "strength": rel["strength"],
                "created_at": rel["created_at"],
            }
            relationships.append(relationship_dict)

        logger.debug(f"Returning {len(relationships)} relationships")
        return relationships

    except Exception as e:
        logger.error(f"Error fetching relationships: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@relationships_router.post("/relationships", response_model=Relationship)
async def create_relationship(relationship: RelationshipCreate):
    """Create a new relationship"""
    try:
        logger.debug(
            f"Attempting to create relationship between {relationship.source} and {relationship.target}"
        )
        db = get_db()
        if isinstance(db, dict) and "error" in db:
            raise HTTPException(status_code=500, detail=db["error"])
        relationships_collection = db["relationships"]

        existing = relationships_collection.find_one(
            {
                "$or": [
                    {"source": relationship.source, "target": relationship.target},
                    {"source": relationship.target, "target": relationship.source},
                ]
            }
        )
        if existing:
            raise HTTPException(status_code=400, detail="Relationship already exists")

        relationship_dict = relationship.model_dump()
        relationship_dict["created_at"] = datetime.now().strftime("%Y-%m-%d")

        result = relationships_collection.insert_one(relationship_dict)
        logger.debug(f"Created relationship with ID: {result.inserted_id}")

        created_relationship = relationships_collection.find_one(
            {"_id": result.inserted_id}
        )
        created_relationship.pop("_id")
        return created_relationship

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error creating relationship: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@relationships_router.get("/relationships/metrics", response_model=RelationshipMetrics)
async def get_relationship_metrics():
    """Get relationship network metrics"""
    try:
        logger.debug("Calculating relationship metrics")
        db = get_db()
        if isinstance(db, dict) and "error" in db:
            raise HTTPException(status_code=500, detail=db["error"])
        relationships_collection = db["relationships"]

        relationships = list(relationships_collection.find())

        if not relationships:
            return RelationshipMetrics(
                total_relationships=0, average_strength=0.0, network_density=0.0
            )

        G = nx.Graph()
        for rel in relationships:
            G.add_edge(rel["source"], rel["target"], weight=rel["strength"])

        total = len(relationships)
        avg_strength = sum(rel["strength"] for rel in relationships) / total
        density = nx.density(G)

        return RelationshipMetrics(
            total_relationships=total,
            average_strength=avg_strength,
            network_density=density,
        )

    except Exception as e:
        logger.error(f"Error calculating metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@relationships_router.put(
    "/relationships/{source}/{target}", response_model=Relationship
)
async def update_relationship(
    source: str, target: str, relationship: RelationshipUpdate
):
    """Update a relationship"""
    try:
        logger.debug(f"Attempting to update relationship between {source} and {target}")
        db = get_db()
        if isinstance(db, dict) and "error" in db:
            raise HTTPException(status_code=500, detail=db["error"])
        relationships_collection = db["relationships"]

        update_data = {
            k: v for k, v in relationship.model_dump().items() if v is not None
        }
        if not update_data:
            raise HTTPException(status_code=400, detail="No valid update data provided")

        result = relationships_collection.update_one(
            {
                "$or": [
                    {"source": source, "target": target},
                    {"source": target, "target": source},
                ]
            },
            {"$set": update_data},
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Relationship not found")

        updated_relationship = relationships_collection.find_one(
            {
                "$or": [
                    {"source": source, "target": target},
                    {"source": target, "target": source},
                ]
            }
        )
        updated_relationship.pop("_id")
        return updated_relationship

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error updating relationship: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@relationships_router.delete("/relationships/{source}/{target}")
async def delete_relationship(source: str, target: str):
    """Delete a relationship"""
    try:
        logger.debug(f"Attempting to delete relationship between {source} and {target}")
        db = get_db()
        if isinstance(db, dict) and "error" in db:
            raise HTTPException(status_code=500, detail=db["error"])
        relationships_collection = db["relationships"]

        result = relationships_collection.delete_one(
            {
                "$or": [
                    {"source": source, "target": target},
                    {"source": target, "target": source},
                ]
            }
        )

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Relationship not found")

        return {"message": "Relationship deleted successfully"}

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error deleting relationship: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
