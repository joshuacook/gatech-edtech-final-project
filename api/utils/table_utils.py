from typing import Dict

from models.files import TablePaths


def convert_table_paths(table_data: Dict) -> Dict[str, TablePaths]:
    """Convert raw table data to proper TablePaths objects"""
    converted = {}
    for table_name, paths in table_data.items():
        if isinstance(paths, dict) and "csv" in paths and "html" in paths:
            converted[table_name] = TablePaths(csv=paths["csv"], html=paths["html"])
    return converted
