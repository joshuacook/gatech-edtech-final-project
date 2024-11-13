# api/routers/chat.py

import logging
import os
import re
from typing import Dict, Union

from anthropic import AnthropicBedrock
from fastapi import APIRouter, HTTPException, Request
from models.chat import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

chat_router = APIRouter()

CLIENT = AnthropicBedrock(
    aws_access_key=os.getenv("aws_access_key_id"),
    aws_secret_key=os.getenv("aws_secret_access_key"),
)
MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"


def extract_json_from_markdown(text: str) -> str:
    """Extract JSON content from markdown code blocks"""
    logger.debug(
        f"Attempting to extract JSON from: {text[:200]}..."
    )  # Log first 200 chars

    json_pattern = r"```(?:json)?\n([\s\S]*?)\n```"
    matches = re.findall(json_pattern, text)

    if matches:
        logger.debug(f"Found JSON in markdown. First match: {matches[0][:200]}...")
        return matches[0]

    logger.debug("No JSON markdown blocks found, returning original text")
    return text


def chat_call(
    query: str, messages: list[dict] = None, expect_json: bool = False
) -> Union[Dict[str, str], Dict[str, Union[str, dict]]]:
    """
    Make a chat API call with optional JSON response handling.
    """
    if messages is None:
        messages = []
    messages.append({"role": "user", "content": query})

    try:
        logger.debug("Making API call to Anthropic...")
        response = CLIENT.messages.create(
            max_tokens=4096,
            messages=messages,
            model=MODEL_ID,
        )

        message_text = response.content[0].text
        logger.debug(
            f"Received response: {message_text[:200]}..."
        )  # Log first 200 chars

        if not expect_json:
            logger.debug("JSON parsing not requested, returning raw message")
            return {"message": message_text}

        # Handle JSON parsing if requested
        try:
            logger.debug("Attempting to parse JSON response")
            cleaned_json = extract_json_from_markdown(message_text)
            import json

            parsed_json = json.loads(cleaned_json)
            logger.debug("Successfully parsed JSON")
            return {"message": message_text, "json": parsed_json}
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {str(e)}")
            logger.error(
                f"Failed content: {cleaned_json[:200]}..."
            )  # Log problematic content
            return {
                "message": message_text,
                "error": f"Failed to parse JSON response: {str(e)}",
                "raw_content": cleaned_json,
            }

    except Exception as e:
        logger.error(f"Chat API call failed: {str(e)}")
        return {"error": str(e)}


@chat_router.post("/chat", response_model=ChatResponse)
async def chat(request: Request, chat_request: ChatRequest):
    messages = chat_request.messages or []
    response_text = chat_call(messages=messages, query=chat_request.query)
    if "error" in response_text:
        raise HTTPException(status_code=500, detail=response_text["error"])
    return ChatResponse(message=response_text["message"])
