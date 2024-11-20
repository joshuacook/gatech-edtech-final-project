# api/models/chat.py
from typing import Dict, List, Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: Optional[str] = None
    messages: Optional[List[Dict[str, str]]] = None
    expect_json: bool = False
    session_id: Optional[str] = None
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    message: str
    result_json: Optional[Dict] = None
    error: Optional[str] = None
    raw_content: Optional[str] = None
