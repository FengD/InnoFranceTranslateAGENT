from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time
from typing import Dict, Any
from logger import get_logger
from config import config

logger = get_logger(__name__)

class MetricsCollector:
    """Metrics collector"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MetricsCollector, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            # Initialize metrics
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
            
            # Start Prometheus HTTP server using configured port
            prometheus_port = config.get("PROMETHEUS_PORT", 8001)
            try:
                start_http_server(prometheus_port)
                logger.info(f"Prometheus metrics server started on port {prometheus_port}")
            except Exception as e:
                logger.error(f"Failed to start Prometheus metrics server: {e}")
            
            self._initialized = True
    
    def record_translation_success(self, model_type: str, duration: float) -> None:
        """
        Record translation success metrics
        
        Args:
            model_type: Model type
            duration: Translation duration (seconds)
        """
        self.translation_requests_total.labels(model_type=model_type, status='success').inc()
        self.translation_duration_seconds.labels(model_type=model_type).observe(duration)
        logger.info(f"Translation success recorded for {model_type} in {duration:.2f}s")
    
    def record_translation_failure(self, model_type: str, duration: float) -> None:
        """
        Record translation failure metrics
        
        Args:
            model_type: Model type
            duration: Translation duration (seconds)
        """
        self.translation_requests_total.labels(model_type=model_type, status='failure').inc()
        self.translation_duration_seconds.labels(model_type=model_type).observe(duration)
        logger.error(f"Translation failure recorded for {model_type} in {duration:.2f}s")
    
    def record_active_translation_start(self, model_type: str) -> None:
        """
        Record start of active translation
        
        Args:
            model_type: Model type
        """
        self.active_translations.labels(model_type=model_type).inc()
        logger.debug(f"Active translation started for {model_type}")
    
    def record_active_translation_end(self, model_type: str) -> None:
        """
        Record end of active translation
        
        Args:
            model_type: Model type
        """
        self.active_translations.labels(model_type=model_type).dec()
        logger.debug(f"Active translation ended for {model_type}")
    
    def record_api_error(self, model_type: str, error_type: str) -> None:
        """
        Record API error
        
        Args:
            model_type: Model type
            error_type: Error type
        """
        self.api_errors_total.labels(model_type=model_type, error_type=error_type).inc()
        logger.error(f"API error recorded for {model_type}: {error_type}")

# Global metrics collector instance
metrics_collector = MetricsCollector()