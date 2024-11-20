import base64
import json
import logging
import os
import re
import tempfile
import time
import traceback
from functools import partial
from typing import Dict, List, Optional, Union

import openai
from anthropic import Anthropic, AnthropicBedrock
from config.chat_config import CURRENT_CLIENT
from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from models.chat import ChatRequest, ChatResponse
from utils.rate_limit_utils import rate_limit

logger = logging.getLogger(__name__)

chat_router = APIRouter()


def extract_json_from_markdown(text: str) -> str:
    """Extract JSON content from markdown code blocks"""
    json_pattern = r"```(?:json)?\n([\s\S]*?)\n```"
    matches = re.findall(json_pattern, text)
    return matches[0] if matches else text


def get_base64_encoded_image(image_path):
    with open(image_path, "rb") as image_file:
        binary_data = image_file.read()
        base_64_encoded_data = base64.b64encode(binary_data)
        base64_string = base_64_encoded_data.decode("utf-8")
        return base64_string


def sanitize_message_for_logging(msg: dict) -> dict:
    """Safely sanitize message for logging by removing large base64 data"""
    msg_copy = msg.copy()
    if isinstance(msg_copy.get("content"), list):
        for content in msg_copy["content"]:
            if content.get("type") == "image" and "source" in content:
                content["source"]["data"] = "<base64_data>"
    return msg_copy


def chat_call(
    query: Optional[str] = None,
    messages: Optional[List[Dict]] = None,
    expect_json: bool = False,
) -> Union[Dict[str, str], Dict[str, Union[str, dict]]]:
    """Unified chat call interface for different clients"""
    max_retries = 5
    base_delay = 1

    for attempt in range(max_retries):
        try:
            return _chat_with_client(query, messages, expect_json)
        except Exception as e:
            time.sleep(base_delay * (2**attempt))
            if "429" not in str(e) or attempt == max_retries - 1:
                raise


def _chat_with_client(
    query: Optional[str] = None,
    messages: Optional[List[Dict]] = None,
    expect_json: bool = False,
):
    """Helper function to route chat requests to the current client"""
    client = CURRENT_CLIENT  # Do not call the module
    try:
        if query:
            messages = [{"role": "user", "content": query}]
        elif messages is None:
            messages = []

        if client == openai:
            # OpenAI API call using the new interface
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=4096,
            )
            message_text = response.choices[0].message.content
        elif isinstance(client, partial) and client.func in [
            Anthropic,
            AnthropicBedrock,
        ]:
            # Anthropic API call
            response = client().messages.create(
                max_tokens=4096,
                messages=messages,
            )
            # Anthropic response parsing
            message_text = response["completion"]
        else:
            raise ValueError("Unsupported client type")

        if not expect_json:
            return {"message": message_text}

        try:
            cleaned_json = extract_json_from_markdown(message_text)
            parsed_json = json.loads(cleaned_json)
            return {"message": message_text, "json": parsed_json}
        except json.JSONDecodeError as e:
            return {
                "message": message_text,
                "error": f"Failed to parse JSON response: {str(e)}",
                "raw_content": cleaned_json,
            }

    except Exception as e:
        logger.error(f"Chat API call failed: {str(e)}")
        return {"error": str(e)}


def multimodal_chat_call(image_path: str, query: str):
    """Multimodal chat using the configured client"""
    client = CURRENT_CLIENT  # Do not call the module
    try:
        # Prepare the image as base64 encoded data
        encoded_image = get_base64_encoded_image(image_path)

        # Prepare the messages payload
        if client == openai:
            # OpenAI's API expects the query and image separately
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": query},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{encoded_image}"
                            },
                        },
                    ],
                }
            ]
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=4096,
            )
            message_text = response.choices[0].message.content
        elif isinstance(client, partial) and client.func in [
            Anthropic,
            AnthropicBedrock,
        ]:
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "data": encoded_image,
                                "media_type": "image/png",
                            },
                        },
                        {"type": "text", "text": query},
                    ],
                }
            ]
            response = client().messages.create(
                max_tokens=4096,
                messages=messages,
            )
            # Anthropic response parsing
            message_text = response["completion"]
        else:
            raise ValueError("Unsupported client type")

        return {"message": message_text}

    except Exception as e:
        logger.error(f"Multimodal chat API call failed: {str(e)}")
        return {"error": str(e)}


@chat_router.post("/chat", response_model=ChatResponse)
@rate_limit(key="chat")
async def chat(request: Request, chat_request: ChatRequest):
    """Standard chat endpoint for text-only messages"""
    try:
        response = chat_call(
            query=chat_request.query,
            messages=chat_request.messages,
            expect_json=chat_request.expect_json,
        )

        if "error" in response:
            raise HTTPException(status_code=500, detail=response["error"])

        return ChatResponse(
            message=response["message"],
            result_json=response.get("json"),
            error=response.get("error"),
            raw_content=response.get("raw_content"),
        )
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@chat_router.post("/chat/with-image", response_model=ChatResponse)
@rate_limit(key="chat_with_image")
async def chat_with_image(
    image: UploadFile = File(...),
    query: str = Form(...),
    previous_messages: str = Form(default="[]"),
):
    """Endpoint that handles image upload with the chat message"""
    try:
        # Read and validate image
        image_data = await image.read()
        if not image_data:
            raise HTTPException(status_code=400, detail="Empty image file")

        # Write to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            temp_file.write(image_data)
            temp_path = temp_file.name

        try:
            response = multimodal_chat_call(temp_path, query)
            message_text = response.content[0].text
            return ChatResponse(message=message_text)

        except Exception as e:
            logger.error(f"Claude API call failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Chat with image endpoint error: {str(e)}\n{traceback.format_exc()}"
        )
        raise HTTPException(status_code=500, detail=str(e))
