import os
from typing import Dict, Any

class Config:
    """Configuration management class"""
    
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration"""
        config = {}
        
        # OpenAI configuration
        config["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")
        config["OPENAI_API_BASE"] = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1/chat/completions")
        config["OPENAI_MODEL"] = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        config["OPENAI_MAX_TOKENS"] = int(os.getenv("OPENAI_MAX_TOKENS", "0")) or None
        
        # Ollama configuration
        config["OLLAMA_API_BASE"] = os.getenv("OLLAMA_API_BASE", "http://localhost:11434/api/generate")
        config["OLLAMA_MODEL"] = os.getenv("OLLAMA_MODEL", "llama2")
        
        # DeepSeek configuration
        config["DEEPSEEK_API_KEY"] = os.getenv("DEEPSEEK_API_KEY", "")
        config["DEEPSEEK_API_BASE"] = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1/chat/completions")
        config["DEEPSEEK_MODEL"] = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        
        # Qwen configuration
        config["QWEN_API_KEY"] = os.getenv("QWEN_API_KEY", "")
        config["QWEN_API_BASE"] = os.getenv("QWEN_API_BASE", "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation")
        config["QWEN_MODEL"] = os.getenv("QWEN_MODEL", "qwen-plus")
        
        # GLM configuration
        config["GLM_API_KEY"] = os.getenv("GLM_API_KEY", "")
        config["GLM_API_BASE"] = os.getenv("GLM_API_BASE", "https://open.bigmodel.cn/api/paas/v4/chat/completions")
        config["GLM_MODEL"] = os.getenv("GLM_MODEL", "glm-4")
        
        # SGLang configuration
        config["SGLANG_API_KEY"] = os.getenv("SGLANG_API_KEY", "")
        config["SGLANG_API_BASE"] = os.getenv("SGLANG_API_BASE", "http://localhost:30000/v1")
        config["SGLANG_MODEL"] = os.getenv("SGLANG_MODEL", "default")
        
        # VLLM configuration
        config["VLLM_API_KEY"] = os.getenv("VLLM_API_KEY", "")
        config["VLLM_API_BASE"] = os.getenv("VLLM_API_BASE", "http://localhost:8000/v1")
        config["VLLM_MODEL"] = os.getenv("VLLM_MODEL", "default")
        
        # General configuration
        config["TEMPERATURE"] = float(os.getenv("TEMPERATURE", "0.3"))
        config["DEFAULT_MODEL"] = os.getenv("DEFAULT_MODEL", "openai")
        
        # Logging configuration
        config["LOG_LEVEL"] = os.getenv("LOG_LEVEL", "INFO")
        config["LOG_FILE"] = os.getenv("LOG_FILE", "logs/translation_agent.log")
        
        # Prometheus configuration
        config["PROMETHEUS_PORT"] = int(os.getenv("PROMETHEUS_PORT", "8000"))
        config["ENABLE_METRICS"] = os.getenv("ENABLE_METRICS", "true").lower() == "true"
        
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