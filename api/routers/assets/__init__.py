# api/routers/assets.py

import logging

from fastapi import APIRouter
from langfuse import Langfuse
from utils.langfuse_utils import configure_langfuse

from .process_image_metadata import process_image_metadata_router
from .process_images import process_images_router
from .process_lexemes import process_lexemes_router
from .process_refined import process_refined_router
from .process_refined_metadata import process_refined_metadata_router
from .process_refined_splitting_metadata import \
    process_refined_splitting_router
from .process_table_metadata import process_table_metadata_router
from .process_tables import process_tables_router

logger = logging.getLogger(__name__)
assets_router = APIRouter(prefix="/assets")

configure_langfuse()
langfuse = Langfuse()

assets_router.include_router(process_image_metadata_router)
assets_router.include_router(process_images_router)
assets_router.include_router(process_lexemes_router)
assets_router.include_router(process_refined_metadata_router)
assets_router.include_router(process_refined_router)
assets_router.include_router(process_refined_splitting_router)
assets_router.include_router(process_table_metadata_router)
assets_router.include_router(process_tables_router)
