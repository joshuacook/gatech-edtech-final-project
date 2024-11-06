# api/routers/chat.py

from typing import Dict, List, Optional

from anthropic import AnthropicBedrock
from fastapi import APIRouter, Request
from langfuse.decorators import langfuse_context
from pydantic import BaseModel
from utils.langfuse_utils import fastapi_observe, score_generation

chat_router = APIRouter()
client = AnthropicBedrock(aws_region="us-east-1")
MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"


class ChatRequest(BaseModel):
    query: str
    messages: Optional[List[Dict[str, str]]] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    message: str


@chat_router.get("/chat")
@fastapi_observe(as_type="generation")
async def chat(request: Request, chat_request: ChatRequest):
    # Update trace with session and user info if provided
    if chat_request.session_id or chat_request.user_id:
        langfuse_context.update_current_trace(
            session_id=chat_request.session_id, user_id=chat_request.user_id
        )

    messages = chat_request.messages or []
    messages.append({"role": "user", "content": [{"text": chat_request.query}]})

    # Update observation with input
    langfuse_context.update_current_observation(
        input=messages,
        metadata={
            "model": MODEL_ID,
            "max_tokens": 2048,
            "temperature": 0.5,
            "top_p": 1,
        },
    )

    response = client.converse(
        modelId=MODEL_ID,
        messages=messages,
        inferenceConfig={
            "maxTokens": 2048,
            "stopSequences": ["\n\nHuman:"],
            "temperature": 0.5,
            "topP": 1,
        },
    )

    response_text = response["output"]["message"]["content"][0]["text"]

    # Update observation with output and usage
    langfuse_context.update_current_observation(
        output=response_text,
        usage={
            "total_tokens": response.get("usage", {}).get("total_tokens", 0),
            "prompt_tokens": response.get("usage", {}).get("prompt_tokens", 0),
            "completion_tokens": response.get("usage", {}).get("completion_tokens", 0),
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
