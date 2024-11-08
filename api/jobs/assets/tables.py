# api/jobs/assets/tables.py
import csv
import json
import logging
import os
from typing import Dict, Tuple

from docx import Document
from jobs.assets.base import AssetProcessor
from utils.db_utils import update_asset_status

logger = logging.getLogger(__name__)


class TableProcessor(AssetProcessor):
    """Process tables from DOCX files"""

    processor_type = "tables"

    def process(self):
        """Main processing method"""
        try:
            if (
                self.asset["file_type"]
                != "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ):
                logger.info(
                    f"Asset {self.file_hash} is not a DOCX file, skipping table processing"
                )
                return

            update_asset_status(self.file_hash, "processing_tables")

            doc = Document(self.get_raw_file_path())
            tables_dir = os.path.join(self.processed_dir, "tables")
            table_paths, tables_meta = self._process_tables(doc, tables_dir)

            update_data = {
                "has_tables": len(table_paths) > 0,
                "table_count": len(table_paths),
                "processed_paths.tables": table_paths,
            }
            self._update_asset(update_data)

            update_asset_status(self.file_hash, "tables_complete")

        except Exception as e:
            logger.error(f"Error processing tables for {self.file_hash}: {str(e)}")
            update_asset_status(self.file_hash, "tables_error", str(e))
            raise

    def _extract_table(self, table) -> list[list[str]]:
        """Convert a table to a list of lists"""
        table_data = []
        for row in table.rows:
            row_data = []
            for cell in row.cells:
                text = cell.text.strip()
                row_data.append(text)
            table_data.append(row_data)
        return table_data

    def _process_tables(
        self, doc: Document, tables_dir: str
    ) -> Tuple[Dict[str, str], Dict[str, str]]:
        """Process all tables from document"""
        table_paths = {}
        tables_meta = {}
        os.makedirs(tables_dir, exist_ok=True)

        for i, table in enumerate(doc.tables):
            table_name = f"table_{i}"
            table_data = self._extract_table(table)

            if not table_data or not any(table_data):
                continue

            csv_path = os.path.join(tables_dir, f"{table_name}.csv")
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerows(table_data)

            table_paths[table_name] = csv_path
            tables_meta[table_name] = {
                "num_rows": len(table_data),
                "num_cols": len(table_data[0]) if table_data else 0,
                "headers": table_data[0] if table_data else [],
            }

        meta_path = os.path.join(tables_dir, "tables_meta.json")
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(tables_meta, f, ensure_ascii=False, indent=2)

        return table_paths, tables_meta
