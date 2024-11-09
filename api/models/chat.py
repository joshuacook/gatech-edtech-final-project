# api/models/chat.py

from typing import Dict, List, Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: str
    messages: Optional[List[Dict[str, str]]] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    message: str
