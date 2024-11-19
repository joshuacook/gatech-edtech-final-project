import logging
import os
from typing import Any, Dict, Optional

from fastapi import APIRouter, Header, HTTPException
from langfuse import Langfuse
from utils.db_utils import init_mongo, update_asset_status
from utils.langfuse_utils import configure_langfuse

logger = logging.getLogger(__name__)


class BaseAssetProcessor:
    def __init__(
        self,
        processor_name: str,
        processor_type: str,
        requires_docx: bool = False,
        required_paths: list[str] = None,
    ):
        self.processor_name = processor_name
        self.processor_type = processor_type
        self.requires_docx = requires_docx
        self.required_paths = required_paths or []
        self.router = APIRouter()

        configure_langfuse()
        self.langfuse = Langfuse()

        self.router.add_api_route(
            f"/process_{processor_name}/{{file_hash}}", self.process, methods=["POST"]
        )

    async def process(
        self,
        file_hash: str,
        x_span_id: Optional[str] = Header(None),
        x_run_id: Optional[str] = Header(None),
    ) -> Dict:
        """Base process method that handles common functionality"""
        span = None
        try:
            db = init_mongo()
            if isinstance(db, dict) and "error" in db:
                raise HTTPException(status_code=500, detail=db["error"])

            asset = db["raw_assets"].find_one({"file_hash": file_hash})
            if not asset:
                raise HTTPException(status_code=404, detail="Asset not found")

            if (
                self.requires_docx
                and asset["file_type"]
                != "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ):
                logger.info(
                    f"Asset {file_hash} is not a DOCX file, skipping {self.processor_name} processing"
                )
                update_asset_status(file_hash, f"{self.processor_name}_skipped")
                return {"status": "skipped", "reason": "not_docx"}

            processed_paths = asset.get("processed_paths", {})
            for path in self.required_paths:
                if path not in processed_paths:
                    error_msg = (
                        f"{path} not available - required for {self.processor_name}"
                    )
                    logger.error(error_msg)
                    raise HTTPException(status_code=400, detail=error_msg)

            run_id = x_run_id or asset.get("current_run_id")
            if not run_id:
                raise HTTPException(status_code=400, detail="No run_id found for asset")

            trace = self.langfuse.trace(
                name="asset-processing",
                id=run_id,
                metadata={
                    "file_hash": file_hash,
                    "file_name": asset["original_name"],
                    "file_type": asset["file_type"],
                    "file_size": asset["file_size"],
                },
            )

            span = trace.span(
                id=x_span_id,
                name=f"{self.processor_name}_processing",
                metadata={"processor_type": self.processor_type, "run_id": run_id},
            )

            update_asset_status(file_hash, f"processing_{self.processor_name}")
            logger.info(f"Starting {self.processor_name} processing for {file_hash}")

            result = await self.process_asset(file_hash, asset, db, span)

            update_asset_status(file_hash, f"{self.processor_name}_complete")
            span.event(
                name=f"{self.processor_name}_complete", metadata={"result": result}
            )

            return result

        except Exception as e:
            error_msg = f"Error in {self.processor_name} processing: {str(e)}"
            logger.error(error_msg)
            if span:
                span.event(
                    name=f"{self.processor_name}_error",
                    metadata={"error": error_msg},
                    level="error",
                )
            update_asset_status(
                file_hash, f"{self.processor_name}_error", error=error_msg
            )
            raise HTTPException(status_code=500, detail=error_msg)

        finally:
            if span:
                span.end()

    async def process_asset(
        self, file_hash: str, asset: Dict[str, Any], db: Any, span: Any
    ) -> Dict[str, Any]:
        """
        Override this method to implement specific processing logic.
        Returns a dictionary of results to be included in the response.
        """
        raise NotImplementedError("Subclasses must implement process_asset")

    def get_processed_dir(self, file_hash: str, *subdirs: str) -> str:
        """Helper to create and return processed directory path"""
        path = os.path.join("/app/filestore/processed", file_hash, *subdirs)
        os.makedirs(path, exist_ok=True)
        return path

    def read_prompt_template(self, prompt_name: str, is_lexeme: bool = False) -> str:
        """Helper to read prompt template file"""
        path_list = ["/app", "prompts", "assets"]
        if is_lexeme:
            path_list.append("lexeme")
        path_list.append(prompt_name)
        prompt_path = os.path.join(*path_list)
        with open(prompt_path, "r") as f:
            return f.read()
