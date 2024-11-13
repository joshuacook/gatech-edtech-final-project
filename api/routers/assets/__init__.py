# api/routers/assets/__init__.py

import logging

from fastapi import APIRouter
from langfuse import Langfuse
from processors.assets.process_images import ProcessImages
from processors.assets.process_lexemes import ProcessLexemes
from processors.assets.process_refined import ProcessRefined
from processors.assets.process_refined_metadata import ProcessRefinedMetadata
from processors.assets.process_refined_splitting import ProcessRefinedSplitting
from processors.assets.process_tables import ProcessTables
from utils.langfuse_utils import configure_langfuse

logger = logging.getLogger(__name__)

# Create main router
assets_router = APIRouter(prefix="/assets")

# Configure Langfuse
configure_langfuse()
langfuse = Langfuse()

# Initialize processors
processors = [
    ProcessRefined(),
    ProcessLexemes(),
    ProcessTables(),
    ProcessImages(),
    ProcessRefinedMetadata(),
    ProcessRefinedSplitting(),
]

# Include each processor's router
for processor in processors:
    assets_router.include_router(processor.router)
