import logging
import os
from datetime import datetime
from typing import Any

def setup_logging(log_level: str = "INFO", log_file: str = "translation_agent.log") -> None:
    """
    Set up logging configuration
    
    Args:
        log_level: Log level
        log_file: Log file path
    """
    # Create log directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def get_logger(name: str) -> logging.Logger:
    """
    Get named logger
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger
    """
    return logging.getLogger(name)

class StructuredLogger:
    """Structured logger"""
    
    def __init__(self, name: str):
        self.logger = get_logger(name)
    
    def info(self, message: str, **kwargs: Any) -> None:
        """Log INFO level message"""
        if kwargs:
            extra_info = " ".join([f"{k}={v}" for k, v in kwargs.items()])
            self.logger.info(f"{message} | {extra_info}")
        else:
            self.logger.info(message)
    
    def error(self, message: str, **kwargs: Any) -> None:
        """Log ERROR level message"""
        if kwargs:
            extra_info = " ".join([f"{k}={v}" for k, v in kwargs.items()])
            self.logger.error(f"{message} | {extra_info}")
        else:
            self.logger.error(message)
    
    def warning(self, message: str, **kwargs: Any) -> None:
        """Log WARNING level message"""
        if kwargs:
            extra_info = " ".join([f"{k}={v}" for k, v in kwargs.items()])
            self.logger.warning(f"{message} | {extra_info}")
        else:
            self.logger.warning(message)
    
    def debug(self, message: str, **kwargs: Any) -> None:
        """Log DEBUG level message"""
        if kwargs:
            extra_info = " ".join([f"{k}={v}" for k, v in kwargs.items()])
            self.logger.debug(f"{message} | {extra_info}")
        else:
            self.logger.debug(message)