# api/routers/chat.py

import os

from anthropic import AnthropicBedrock
from fastapi import APIRouter, Request
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
    messages.append({"role": "user", "content": chat_request.query})

    message = CLIENT.messages.create(
        max_tokens=1024,
        messages=messages,
        model=MODEL_ID,
    )
    response_text = message.content[0].text

    return ChatResponse(message=response_text)
