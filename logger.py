import logging
import os
from datetime import datetime
from typing import Any

def setup_logging(log_level: str = "INFO", log_file: str = "translation_agent.log") -> None:
    """
    设置日志配置
    
    Args:
        log_level: 日志级别
        log_file: 日志文件路径
    """
    # 创建日志目录（如果不存在）
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 配置根日志记录器
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
    获取命名的日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        配置好的日志记录器
    """
    return logging.getLogger(name)

class StructuredLogger:
    """结构化日志记录器"""
    
    def __init__(self, name: str):
        self.logger = get_logger(name)
    
    def info(self, message: str, **kwargs: Any) -> None:
        """记录INFO级别日志"""
        if kwargs:
            extra_info = " ".join([f"{k}={v}" for k, v in kwargs.items()])
            self.logger.info(f"{message} | {extra_info}")
        else:
            self.logger.info(message)
    
    def error(self, message: str, **kwargs: Any) -> None:
        """记录ERROR级别日志"""
        if kwargs:
            extra_info = " ".join([f"{k}={v}" for k, v in kwargs.items()])
            self.logger.error(f"{message} | {extra_info}")
        else:
            self.logger.error(message)
    
    def warning(self, message: str, **kwargs: Any) -> None:
        """记录WARNING级别日志"""
        if kwargs:
            extra_info = " ".join([f"{k}={v}" for k, v in kwargs.items()])
            self.logger.warning(f"{message} | {extra_info}")
        else:
            self.logger.warning(message)
    
    def debug(self, message: str, **kwargs: Any) -> None:
        """记录DEBUG级别日志"""
        if kwargs:
            extra_info = " ".join([f"{k}={v}" for k, v in kwargs.items()])
            self.logger.debug(f"{message} | {extra_info}")
        else:
            self.logger.debug(message)