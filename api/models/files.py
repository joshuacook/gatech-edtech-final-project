# api/models/files.py

from typing import Dict, List, Optional

from pydantic import BaseModel


class TablePaths(BaseModel):
    csv: str
    html: str


class TableMetadataResponse(BaseModel):
    num_rows: int
    num_cols: int
    headers: List[str]
    empty_cells: int
    total_cells: int


class ProcessedPaths(BaseModel):
    markdown: str = ""
    images: Dict[str, str] = {}
    tables: Dict[str, TablePaths] = {}
    meta: str = ""
    metadata: Optional[str] = ""


class FileResponse(BaseModel):
    id: str
    name: str
    size: int
    type: str
    status: str
    upload_date: str
    processed_date: Optional[str] = None
    error: Optional[str] = None
    processed_paths: Optional[ProcessedPaths] = None
    has_images: bool = False
    image_count: int = 0
    has_tables: bool = False
    table_count: int = 0
    metadata: Optional[dict] = None
    file_path: Optional[str] = None


class FileDetailResponse(FileResponse):
    preview: Optional[str] = None
    processing_details: Optional[dict] = None
