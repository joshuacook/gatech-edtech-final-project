import base64
import logging
import os
import re
from typing import Dict, List, Optional, Union
import traceback
import tempfile
from io import BytesIO
from PIL import Image as PILImage

from anthropic import Anthropic
from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

chat_router = APIRouter()

CLIENT = Anthropic()
MODEL_ID = "claude-3-5-sonnet-latest"




class ChatRequest(BaseModel):
    query: Optional[str] = None
    messages: Optional[List[Dict]] = None
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

def get_base64_encoded_image(image_path):
    with open(image_path, "rb") as image_file:
        binary_data = image_file.read()
        base_64_encoded_data = base64.b64encode(binary_data)
        base64_string = base_64_encoded_data.decode('utf-8')
        return base64_string

def sanitize_message_for_logging(msg: dict) -> dict:
    """Safely sanitize message for logging by removing large base64 data"""
    msg_copy = msg.copy()
    if isinstance(msg_copy.get('content'), list):
        for content in msg_copy['content']:
            if content.get('type') == 'image' and 'source' in content:
                # Handle the correct path to the base64 data
                content['source']['data'] = '<base64_data>'
    return msg_copy


def chat_call(
    query: Optional[str] = None,
    messages: Optional[List[Dict]] = None,
    expect_json: bool = False,
) -> Union[Dict[str, str], Dict[str, Union[str, dict]]]:
    """Make a chat API call for text-only messages"""
    try:
        # Handle either query or messages
        if query:
            messages = [{"role": "user", "content": query}]
        elif messages is None:
            messages = []

        response = CLIENT.messages.create(
            max_tokens=4096,
            messages=messages,
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
        logger.error(f"Chat API call failed: {str(e)}\n{traceback.format_exc()}")
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
    previous_messages: str = Form(default="[]"),
):
    """Endpoint that handles image upload with the chat message"""
    try:
        # Read and validate image
        image_data = await image.read()
        if not image_data:
            raise HTTPException(status_code=400, detail="Empty image file")
        
        # Write to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            temp_file.write(image_data)
            temp_path = temp_file.name

        try:
            # Create message list
            message_list = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": get_base64_encoded_image(temp_path)
                            }
                        },
                        {
                            "type": "text",
                            "text": query
                        }
                    ]
                }
            ]

            # Make the API call
            response = CLIENT.messages.create(
                model=MODEL_ID,
                max_tokens=2048,
                messages=message_list
            )
            
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
        logger.error(f"Chat with image endpoint error: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))