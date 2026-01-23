import os
from typing import Dict, Any

class Config:
    """Configuration management class"""
    
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration"""
        config = {}
        
        # Logging configuration
        config["LOG_LEVEL"] = os.getenv("LOG_LEVEL", "INFO")
        config["LOG_FILE"] = os.getenv("LOG_FILE", "logs/translation_agent.log")
        
        # Prometheus configuration
        config["PROMETHEUS_PORT"] = int(os.getenv("PROMETHEUS_PORT", "8000"))
        config["ENABLE_METRICS"] = os.getenv("ENABLE_METRICS", "true").lower() == "true"

        # Input chunking configuration (approximate tokens)
        config["INPUT_MAX_TOKENS"] = int(os.getenv("INPUT_MAX_TOKENS", "3000"))
        config["TOKEN_CHAR_RATIO"] = float(os.getenv("TOKEN_CHAR_RATIO", "4"))
        
        return config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self.config[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configurations"""
        return self.config.copy()

# Global configuration instance
config = Config()