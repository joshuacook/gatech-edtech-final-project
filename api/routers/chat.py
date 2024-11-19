import base64
import logging
import os
import re
from typing import Dict, List, Optional, Union

from anthropic import Anthropic
from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

chat_router = APIRouter()

CLIENT = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
)
MODEL_ID = "claude-3-sonnet-20240229"


class ImageContent(BaseModel):
    type: str = "image"
    source: Dict[str, str] = Field(
        ...,
        example={
            "type": "base64",
            "media_type": "image/jpeg",
            "data": "base64_encoded_string",
        },
    )


class TextContent(BaseModel):
    type: str = "text"
    text: str


class Message(BaseModel):
    role: str
    content: Union[str, List[Union[ImageContent, TextContent]]]


class ChatRequest(BaseModel):
    query: Optional[str] = None
    messages: Optional[List[Message]] = None
    expect_json: bool = False


class ChatResponse(BaseModel):
    message: str
    json: Optional[Dict] = None
    error: Optional[str] = None
    raw_content: Optional[str] = None


def extract_json_from_markdown(text: str) -> str:
    """Extract JSON content from markdown code blocks"""
    json_pattern = r"```(?:json)?\n([\s\S]*?)\n```"
    matches = re.findall(json_pattern, text)
    return matches[0] if matches else text


def encode_image_to_base64(image_data: bytes, media_type: str) -> str:
    """Convert image bytes to base64 string"""
    return base64.b64encode(image_data).decode("utf-8")


def chat_call(
    query: Optional[str] = None,
    messages: Optional[List[Message]] = None,
    expect_json: bool = False,
) -> Union[Dict[str, str], Dict[str, Union[str, dict]]]:
    """Make a chat API call with support for multimodal content"""
    if messages is None:
        messages = []

    anthropic_messages = []
    for msg in messages:
        if isinstance(msg.content, str):
            anthropic_messages.append({"role": msg.role, "content": msg.content})
        else:
            # Handle multimodal content
            anthropic_messages.append({"role": msg.role, "content": msg.content})

    if query:
        anthropic_messages.append({"role": "user", "content": query})

    try:
        response = CLIENT.messages.create(
            max_tokens=4096,
            messages=anthropic_messages,
            model=MODEL_ID,
        )

        message_text = response.content[0].text

        if not expect_json:
            return {"message": message_text}

        try:
            cleaned_json = extract_json_from_markdown(message_text)
            import json

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


@chat_router.post("/chat", response_model=ChatResponse)
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
            json=response.get("json"),
            error=response.get("error"),
            raw_content=response.get("raw_content"),
        )
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@chat_router.post("/chat/with-image", response_model=ChatResponse)
async def chat_with_image(
    image: UploadFile = File(...),
    query: str = Form(...),
    previous_messages: str = Form(default="[]"),  # JSON string of previous messages
):
    """Endpoint that handles image upload with the chat message"""
    try:
        # Read and encode the image
        image_data = await image.read()
        media_type = image.content_type or "image/jpeg"
        base64_image = encode_image_to_base64(image_data, media_type)

        # Parse previous messages
        import json

        prev_messages = json.loads(previous_messages)

        # Create the new message with image
        new_message = Message(
            role="user",
            content=[
                ImageContent(
                    source={
                        "type": "base64",
                        "media_type": media_type,
                        "data": base64_image,
                    }
                ),
                TextContent(text=query),
            ],
        )

        # Combine previous messages with new message
        all_messages = [Message(**msg) for msg in prev_messages] + [new_message]

        # Make the API call
        response = chat_call(messages=all_messages)

        if "error" in response:
            raise HTTPException(status_code=500, detail=response["error"])

        return ChatResponse(
            message=response["message"],
            json=response.get("json"),
            error=response.get("error"),
            raw_content=response.get("raw_content"),
        )
    except Exception as e:
        logger.error(f"Chat with image endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
