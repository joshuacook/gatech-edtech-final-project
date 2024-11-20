# api/utils/generative_utils.py
import functools
import json
import logging
from typing import Callable, TypeVar

import requests

logger = logging.getLogger(__name__)

T = TypeVar("T")


def retry_on_json_error(max_attempts: int = 3):
    """
    Decorator to retry generative calls on JSON parsing failures.
    Tracks attempts in the provided span's metadata.

    Args:
        max_attempts (int): Maximum number of attempts to make

    Returns:
        Callable: Decorated function that will retry on JSON parsing failures

    Example:
        @retry_on_json_error(max_attempts=3)
        def process(self, span):
            # Function that makes generative calls and parses JSON
            ...
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(self, span, *args, **kwargs) -> T:
            last_error = None
            attempts = []

            for attempt in range(max_attempts):
                try:
                    attempt = attempt + 1
                    span.event(name=f"Generation Attempt {attempt}/{max_attempts}")
                    logger.info(f"Generation attempt {attempt}/{max_attempts}")
                    result = func(self, span, *args, **kwargs)

                    return result

                except json.JSONDecodeError as e:
                    last_error = e
                    error_context = (
                        f"Error at line {e.lineno}, column {e.colno}: {e.msg}"
                    )
                    error_msg = (
                        f"JSON parsing failed on attempt {attempt}: {error_context}"
                    )
                    logger.warning(error_msg)

                    # Log failed attempt with detailed context
                    attempts.append(
                        {
                            "attempt": attempt,
                            "status": "failed",
                            "error": str(e),
                            "error_type": "json_decode",
                            "error_context": error_context,
                            "processor": self.processor_type,
                        }
                    )

                    if attempt < max_attempts:
                        logger.info(
                            f"Retrying generation (attempt {attempt + 1}/{max_attempts})"
                        )
                    else:
                        span.event(name="Generation Failed")
                        raise Exception(
                            f"Failed to generate valid JSON after {max_attempts} attempts: {error_context}"
                        ) from e

            # Should never reach here due to raise in loop, but just in case
            raise last_error

        return wrapper

    return decorator


def make_generative_call(prompt: str, endpoint: str = "http://nginx:80/chat") -> str:
    """
    Make a generative call to the chat API with standardized error handling.

    Args:
        prompt (str): The prompt to send to the model
        endpoint (str): The API endpoint to call (defaults to internal chat endpoint)

    Returns:
        str: The model's response text

    Raises:
        Exception: If the API call fails or returns an error
    """
    try:
        response = requests.post(endpoint, json={"query": prompt, "messages": []})

        if not response.ok:
            error_msg = f"Chat API error: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)

        return response.json()["message"]

    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        raise Exception(f"Failed to make API call: {str(e)}") from e
