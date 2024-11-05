# api/routers/chat.py

from typing import Dict, List, Optional

from anthropic import AnthropicBedrock
from fastapi import APIRouter
from pydantic import BaseModel

chat_router = APIRouter()
client = AnthropicBedrock(aws_region="us-east-1")
MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"


class ChatRequest(BaseModel):
    query: str
    messages: Optional[List[Dict[str, str]]] = None


class ChatResponse(BaseModel):
    message: str


@chat_router.get("/chat")
async def chat(request: ChatRequest):
    if request.messages is None:
        request.messages = []

    request.messages.append({"role": "user", "content": [{"text": request.query}]})

    response = client.converse(
        modelId=MODEL_ID,
        messages=request.messages,
        inferenceConfig={
            "maxTokens": 2048,
            "stopSequences": ["\n\nHuman:"],
            "temperature": 0.5,
            "topP": 1,
        },
    )
    response_text = response["output"]["message"]["content"][0]["text"]
    return ChatResponse(message=response_text)
