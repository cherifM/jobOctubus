import logging
import sys
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler

def setup_logging(log_level: str = "INFO", log_dir: str = "logs"):
    """Configure structured logging for the application"""
    
    # Create logs directory if it doesn't exist
    Path(log_dir).mkdir(exist_ok=True)
    
    # Create formatters
    file_formatter = logging.Formatter(
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "module": "%(name)s", '
        '"function": "%(funcName)s", "line": %(lineno)d, "message": "%(message)s"}'
    )
    
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    root_logger.handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        filename=f"{log_dir}/joboctubus.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    
    # Error file handler
    error_handler = RotatingFileHandler(
        filename=f"{log_dir}/joboctubus_errors.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    error_handler.setFormatter(file_formatter)
    error_handler.setLevel(logging.ERROR)
    root_logger.addHandler(error_handler)
    
    # Suppress noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    return root_logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module"""
    return logging.getLogger(name)