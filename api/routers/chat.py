# api/routers/chat.py

import os
from typing import Dict, List, Optional

from anthropic import AnthropicBedrock
from fastapi import APIRouter, Request
from langfuse.decorators import langfuse_context
from pydantic import BaseModel
from utils.langfuse_utils import fastapi_observe, score_generation

chat_router = APIRouter()


client = AnthropicBedrock(
    aws_access_key=os.getenv("aws_access_key_id"),
    aws_secret_key=os.getenv("aws_secret_access_key"),
)
MODEL_ID = "claude-3-5-sonnet-20241022"


class ChatRequest(BaseModel):
    query: str
    messages: Optional[List[Dict[str, str]]] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    message: str


@chat_router.post("/chat", response_model=ChatResponse)
@fastapi_observe(as_type="generation")
async def chat(request: Request, chat_request: ChatRequest):
    # Update trace with session and user info if provided
    if chat_request.session_id or chat_request.user_id:
        langfuse_context.update_current_trace(
            session_id=chat_request.session_id, user_id=chat_request.user_id
        )

    # Prepare messages
    messages = chat_request.messages or []
    messages.append({"role": "user", "content": chat_request.query})

    # Update observation with input
    langfuse_context.update_current_observation(
        input=messages,
        metadata={
            "model": MODEL_ID,
            "max_tokens": 2048,
            "temperature": 0.5,
        },
    )

    # Call the client
    message = client.messages.create(
        max_tokens=1024,
        messages=messages,
        model="anthropic.claude-3-sonnet-20240229-v1:0",
    )

    # Ensure response_text is a string
    response_text = message.content[0].text

    # Update observation with output and usage
    input_tokens = message.usage.input_tokens
    output_tokens = message.usage.output_tokens

    langfuse_context.update_current_observation(
        output=response_text,
        usage={
            "total_tokens": input_tokens + output_tokens,
            "prompt_tokens": input_tokens,
            "completion_tokens": output_tokens,
        },
    )

    # Example automatic scoring based on response length
    if len(response_text) > 50:  # Simple example metric
        score_generation(
            name="response_length",
            score=1.0,
            comment="Response meets minimum length requirement",
        )
    else:
        score_generation(
            name="response_length",
            score=0.5,
            comment="Response is shorter than desired",
        )

    return ChatResponse(message=response_text)
