# api/routers/chat.py

import os

from anthropic import AnthropicBedrock
from fastapi import APIRouter, HTTPException, Request
from models.chat import ChatRequest, ChatResponse

chat_router = APIRouter()


CLIENT = AnthropicBedrock(
    aws_access_key=os.getenv("aws_access_key_id"),
    aws_secret_key=os.getenv("aws_secret_access_key"),
)
MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"


@chat_router.post("/chat", response_model=ChatResponse)
async def chat(request: Request, chat_request: ChatRequest):
    messages = chat_request.messages or []
    response_text = chat_call(messages, chat_request.query)
    if "error" in response_text:
        raise HTTPException(status_code=500, detail=response_text["error"])
    return ChatResponse(message=response_text["message"])


def chat_call(messages: list[dict], query: str):
    messages.append({"role": "user", "content": query})
    try:
        message = CLIENT.messages.create(
            max_tokens=4096,
            messages=messages,
            model=MODEL_ID,
        )
        return {"message": message.content[0].text}
    except Exception as e:
        return {"error": str(e)}
