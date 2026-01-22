from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time
from typing import Dict, Any
from logger import get_logger

logger = get_logger(__name__)

class MetricsCollector:
    """指标收集器"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MetricsCollector, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            # 初始化指标
            self.translation_requests_total = Counter(
                'translation_requests_total',
                'Total number of translation requests',
                ['model_type', 'status']
            )
            
            self.translation_duration_seconds = Histogram(
                'translation_duration_seconds',
                'Translation request duration in seconds',
                ['model_type']
            )
            
            self.active_translations = Gauge(
                'active_translations',
                'Number of active translations',
                ['model_type']
            )
            
            self.api_errors_total = Counter(
                'api_errors_total',
                'Total number of API errors',
                ['model_type', 'error_type']
            )
            
            # 启动Prometheus HTTP服务器
            try:
                start_http_server(8000)
                logger.info("Prometheus metrics server started on port 8000")
            except Exception as e:
                logger.error(f"Failed to start Prometheus metrics server: {e}")
            
            self._initialized = True
    
    def record_translation_success(self, model_type: str, duration: float) -> None:
        """
        记录翻译成功指标
        
        Args:
            model_type: 模型类型
            duration: 翻译耗时（秒）
        """
        self.translation_requests_total.labels(model_type=model_type, status='success').inc()
        self.translation_duration_seconds.labels(model_type=model_type).observe(duration)
        logger.info(f"Translation success recorded for {model_type} in {duration:.2f}s")
    
    def record_translation_failure(self, model_type: str, duration: float) -> None:
        """
        记录翻译失败指标
        
        Args:
            model_type: 模型类型
            duration: 翻译耗时（秒）
        """
        self.translation_requests_total.labels(model_type=model_type, status='failure').inc()
        self.translation_duration_seconds.labels(model_type=model_type).observe(duration)
        logger.error(f"Translation failure recorded for {model_type} in {duration:.2f}s")
    
    def record_active_translation_start(self, model_type: str) -> None:
        """
        记录开始活跃翻译
        
        Args:
            model_type: 模型类型
        """
        self.active_translations.labels(model_type=model_type).inc()
        logger.debug(f"Active translation started for {model_type}")
    
    def record_active_translation_end(self, model_type: str) -> None:
        """
        记录结束活跃翻译
        
        Args:
            model_type: 模型类型
        """
        self.active_translations.labels(model_type=model_type).dec()
        logger.debug(f"Active translation ended for {model_type}")
    
    def record_api_error(self, model_type: str, error_type: str) -> None:
        """
        记录API错误
        
        Args:
            model_type: 模型类型
            error_type: 错误类型
        """
        self.api_errors_total.labels(model_type=model_type, error_type=error_type).inc()
        logger.error(f"API error recorded for {model_type}: {error_type}")

# 全局指标收集器实例
metrics_collector = MetricsCollector()