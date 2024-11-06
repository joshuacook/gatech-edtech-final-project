from functools import wraps
from typing import Optional

from fastapi import Request
from langfuse.decorators import langfuse_context, observe


def configure_langfuse():
    """Configure global Langfuse settings"""
    langfuse_context.configure(
        debug=True  # Enables detailed logging
    )


def get_trace_metadata(request: Optional[Request] = None):
    """Extract useful metadata from the request"""
    metadata = {}

    if request:
        metadata.update(
            {
                "path": str(request.url.path),
                "method": request.method,
                "client_host": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            }
        )

    return metadata


def fastapi_observe(**decorator_kwargs):
    """
    Custom decorator that combines FastAPI dependency injection with Langfuse tracing.
    Automatically captures request metadata and handles async functions.
    """

    def decorator(func):
        # Apply the Langfuse decorator first
        observed_func = observe(**decorator_kwargs)(func)

        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request object if present in kwargs
            request = kwargs.get("request")

            if request and isinstance(request, Request):
                # Update trace with request metadata
                metadata = get_trace_metadata(request)
                langfuse_context.update_current_trace(metadata=metadata)

            return await observed_func(*args, **kwargs)

        return wrapper

    return decorator


def score_generation(name: str, score: float, comment: Optional[str] = None):
    """Helper to score generations with standardized names"""
    langfuse_context.score_current_observation(name=name, value=score, comment=comment)


def add_file_metadata(file_details: dict):
    """Add file processing metadata to current trace"""
    langfuse_context.update_current_observation(
        metadata={
            "file_name": file_details.get("original_name"),
            "file_type": file_details.get("file_type"),
            "file_size": file_details.get("file_size"),
            "file_hash": file_details.get("file_hash"),
        }
    )
