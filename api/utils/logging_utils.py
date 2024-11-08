import logging
from typing import Optional

def configure_logging(level: Optional[str] = None):
    """Configure global logging level with validation"""
    if level:
        try:
            numeric_level = getattr(logging, level.upper(), None)
            if not isinstance(numeric_level, int):
                raise ValueError(f'Invalid log level: {level}')
            
            # Configure root logger
            logging.basicConfig(
                level=numeric_level,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.StreamHandler(),
                    logging.FileHandler("app.log")
                ]
            )
            
            # Explicitly set levels for specific loggers
            loggers_to_configure = [
                'asyncio',
                'fastapi',
                'langfuse',
                'rq.worker',
                'urllib3',
            ]

            for key in logging.Logger.manager.loggerDict:
                if key.startswith('pymongo'):
                    logging.getLogger(key).setLevel(logging.WARNING)
            
            for logger_name in loggers_to_configure:
                specific_logger = logging.getLogger(logger_name)
                specific_logger.setLevel(logging.WARNING)
            
            return f"Global logging level set to {level}"
            
        except Exception as e:
            return f"Failed to configure logging: {str(e)}"
