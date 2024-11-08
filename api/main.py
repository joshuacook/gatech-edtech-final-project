# api/main.py

import logging
import os

import fastapi
from fastapi.middleware.cors import CORSMiddleware
from routers.chat import chat_router
from routers.concepts import concepts_router
from routers.files import files_router
from routers.operations import operations_router
from routers.relationships import relationships_router
from utils.langfuse_utils import configure_langfuse
from utils.logging_utils import configure_logging

# Create logger for this module
logger = logging.getLogger(__name__)

app = fastapi.FastAPI()


# Configure logging on startup
@app.on_event("startup")
async def startup_event():
    configure_langfuse()
    # Set initial logging level from environment variable
    initial_level = os.getenv("LOG_LEVEL", "INFO")
    result = configure_logging(initial_level)
    logger.info(result)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Hello World"}


app.include_router(chat_router)
app.include_router(concepts_router)
app.include_router(files_router)
app.include_router(operations_router)
app.include_router(relationships_router)
