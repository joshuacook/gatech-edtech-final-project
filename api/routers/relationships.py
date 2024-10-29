from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel
from datetime import datetime
from pymongo import MongoClient
import os
import logging
import networkx as nx

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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

relationships_router = APIRouter()

def get_db():
    try:
        client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://db:27017/'))
        db = client['chelle']
        client.admin.command('ping')
        logger.debug("Successfully connected to MongoDB")
        return db
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise HTTPException(status_code=500, detail="Database connection failed")

@relationships_router.get("/relationships", response_model=List[Relationship])
async def get_relationships():
    """Get all relationships"""
    try:
        logger.debug("Attempting to fetch relationships from MongoDB")
        db = get_db()
        relationships_collection = db['relationships']
        
        relationships = []
        for rel in relationships_collection.find():
            relationship_dict = {
                "source": rel["source"],
                "target": rel["target"],
                "type": rel["type"],
                "connection_type": rel.get("connection_type"),
                "strength": rel["strength"],
                "created_at": rel["created_at"]
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
        logger.debug(f"Attempting to create relationship between {relationship.source} and {relationship.target}")
        db = get_db()
        relationships_collection = db['relationships']
        
        # Check if relationship already exists
        existing = relationships_collection.find_one({
            "$or": [
                {"source": relationship.source, "target": relationship.target},
                {"source": relationship.target, "target": relationship.source}
            ]
        })
        if existing:
            raise HTTPException(status_code=400, detail="Relationship already exists")
        
        relationship_dict = relationship.model_dump()
        relationship_dict["created_at"] = datetime.now().strftime('%Y-%m-%d')
        
        result = relationships_collection.insert_one(relationship_dict)
        logger.debug(f"Created relationship with ID: {result.inserted_id}")
        
        created_relationship = relationships_collection.find_one({"_id": result.inserted_id})
        created_relationship.pop('_id')
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
        relationships_collection = db['relationships']
        
        relationships = list(relationships_collection.find())
        
        if not relationships:
            return RelationshipMetrics(
                total_relationships=0,
                average_strength=0.0,
                network_density=0.0
            )
        
        # Create networkx graph
        G = nx.Graph()
        for rel in relationships:
            G.add_edge(rel['source'], rel['target'], weight=rel['strength'])
        
        # Calculate metrics
        total = len(relationships)
        avg_strength = sum(rel['strength'] for rel in relationships) / total
        density = nx.density(G)
        
        return RelationshipMetrics(
            total_relationships=total,
            average_strength=avg_strength,
            network_density=density
        )
        
    except Exception as e:
        logger.error(f"Error calculating metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@relationships_router.put("/relationships/{source}/{target}", response_model=Relationship)
async def update_relationship(source: str, target: str, relationship: RelationshipUpdate):
    """Update a relationship"""
    try:
        logger.debug(f"Attempting to update relationship between {source} and {target}")
        db = get_db()
        relationships_collection = db['relationships']
        
        update_data = {k: v for k, v in relationship.model_dump().items() if v is not None}
        if not update_data:
            raise HTTPException(status_code=400, detail="No valid update data provided")
        
        result = relationships_collection.update_one(
            {"$or": [
                {"source": source, "target": target},
                {"source": target, "target": source}
            ]},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Relationship not found")
        
        updated_relationship = relationships_collection.find_one({
            "$or": [
                {"source": source, "target": target},
                {"source": target, "target": source}
            ]
        })
        updated_relationship.pop('_id')
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
        relationships_collection = db['relationships']
        
        result = relationships_collection.delete_one({
            "$or": [
                {"source": source, "target": target},
                {"source": target, "target": source}
            ]
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Relationship not found")
        
        return {"message": "Relationship deleted successfully"}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error deleting relationship: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))