import os
from typing import Dict, Any

class Config:
    """配置管理类"""
    
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        config = {}
        
        # OpenAI配置
        config["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")
        config["OPENAI_API_BASE"] = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1/chat/completions")
        config["OPENAI_MODEL"] = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        config["OPENAI_MAX_TOKENS"] = int(os.getenv("OPENAI_MAX_TOKENS", "0")) or None
        
        # Ollama配置
        config["OLLAMA_API_BASE"] = os.getenv("OLLAMA_API_BASE", "http://localhost:11434/api/generate")
        config["OLLAMA_MODEL"] = os.getenv("OLLAMA_MODEL", "llama2")
        
        # DeepSeek配置
        config["DEEPSEEK_API_KEY"] = os.getenv("DEEPSEEK_API_KEY", "")
        config["DEEPSEEK_API_BASE"] = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1/chat/completions")
        config["DEEPSEEK_MODEL"] = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        
        # Qwen配置
        config["QWEN_API_KEY"] = os.getenv("QWEN_API_KEY", "")
        config["QWEN_API_BASE"] = os.getenv("QWEN_API_BASE", "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation")
        config["QWEN_MODEL"] = os.getenv("QWEN_MODEL", "qwen-plus")
        
        # GLM配置
        config["GLM_API_KEY"] = os.getenv("GLM_API_KEY", "")
        config["GLM_API_BASE"] = os.getenv("GLM_API_BASE", "https://open.bigmodel.cn/api/paas/v4/chat/completions")
        config["GLM_MODEL"] = os.getenv("GLM_MODEL", "glm-4")
        
        # 通用配置
        config["TEMPERATURE"] = float(os.getenv("TEMPERATURE", "0.3"))
        config["DEFAULT_MODEL"] = os.getenv("DEFAULT_MODEL", "openai")
        
        # 日志配置
        config["LOG_LEVEL"] = os.getenv("LOG_LEVEL", "INFO")
        config["LOG_FILE"] = os.getenv("LOG_FILE", "logs/translation_agent.log")
        
        # Prometheus配置
        config["PROMETHEUS_PORT"] = int(os.getenv("PROMETHEUS_PORT", "8000"))
        config["ENABLE_METRICS"] = os.getenv("ENABLE_METRICS", "true").lower() == "true"
        
        return config
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        self.config[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self.config.copy()

# 全局配置实例
config = Config()