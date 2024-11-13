import imghdr
import logging
import os
from typing import Dict

from PIL import Image

logger = logging.getLogger(__name__)


def get_image_technical_metadata(image_name: str, image_path: str) -> Dict:
    """Get technical metadata from image file"""
    try:
        if not os.path.exists(image_path):
            raise ValueError(f"Image file not found: {image_path}")

        file_size = os.path.getsize(image_path)
        file_type = imghdr.what(image_path)

        with Image.open(image_path) as img:
            width, height = img.size
            mode = img.mode
            format = img.format

            metadata = {
                "filename": os.path.basename(image_path),
                "file_size": file_size,
                "file_type": file_type,
                "width": width,
                "height": height,
                "aspect_ratio": round(width / height, 2),
                "color_mode": mode,
                "format": format,
                "dpi": img.info.get("dpi", None),
            }

        return metadata

    except Exception as e:
        logger.error(f"Error getting technical metadata for {image_name}: {str(e)}")
        return None


def format_image_info(technical_metadata: Dict) -> str:
    """Format technical metadata as text for AI analysis"""
    lines = [
        f"Filename: {technical_metadata['filename']}",
        f"Dimensions: {technical_metadata['width']}x{technical_metadata['height']} pixels",
        f"Format: {technical_metadata['format']}",
        f"Color Mode: {technical_metadata['color_mode']}",
        f"File Size: {technical_metadata['file_size']} bytes",
        f"Aspect Ratio: {technical_metadata['aspect_ratio']}",
    ]

    if technical_metadata["dpi"]:
        lines.append(f"DPI: {technical_metadata['dpi']}")

    return "\n".join(lines)
