import json
import logging
import os
import requests
import time
from typing import Dict, Any, Optional
from logger import get_logger
from metrics import MetricsCollector

logger = get_logger(__name__)

class TranslationAgent:
    def __init__(self, config: Dict[str, Any]):
        """
        初始化翻译Agent
        
        Args:
            config: 配置字典，包含API密钥和其他设置
        """
        self.config = config
        self.metrics = MetricsCollector()
        self.prompt_template = self._load_prompt()
        
    def _load_prompt(self) -> str:
        """加载系统提示词"""
        try:
            with open('prompt.md', 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.error("未找到prompt.md文件")
            return ""
    
    def translate(self, input_data: Dict[str, Any], model_type: str = "openai") -> str:
        """
        执行翻译任务
        
        Args:
            input_data: 输入的JSON数据
            model_type: 使用的模型类型
            
        Returns:
            翻译结果
        """
        start_time = time.time()
        try:
            # 预处理输入数据
            processed_input = self._preprocess_input(input_data)
            
            # 构造Prompt
            prompt = self._construct_prompt(processed_input)
            
            # 调用指定的模型API
            translation_result = self._call_model_api(prompt, model_type)
            
            # 后处理结果
            final_result = self._postprocess_output(translation_result)
            
            # 记录成功指标
            duration = time.time() - start_time
            self.metrics.record_translation_success(model_type, duration)
            
            return final_result
            
        except Exception as e:
            # 记录失败指标
            duration = time.time() - start_time
            self.metrics.record_translation_failure(model_type, duration)
            logger.error(f"翻译过程中发生错误: {str(e)}")
            raise
    
    def _preprocess_input(self, input_data: Dict[str, Any]) -> str:
        """
        预处理输入数据
        
        Args:
            input_data: 原始输入数据
            
        Returns:
            处理后的文本
        """
        if "segments" in input_data:
            # 处理JSON格式的segments
            segments_text = []
            for segment in input_data["segments"]:
                speaker = segment.get("speaker", "UNKNOWN")
                text = segment.get("text", "")
                segments_text.append(f"[{speaker}] {text}")
            return "\n".join(segments_text)
        else:
            # 处理纯文本
            return str(input_data)
    
    def _construct_prompt(self, input_text: str) -> str:
        """
        构造完整的Prompt
        
        Args:
            input_text: 输入文本
            
        Returns:
            完整的Prompt
        """
        return f"{self.prompt_template}\n\n请翻译以下内容：\n{input_text}"
    
    def _call_model_api(self, prompt: str, model_type: str) -> str:
        """
        调用指定的模型API
        
        Args:
            prompt: 发送给模型的Prompt
            model_type: 模型类型
            
        Returns:
            模型返回的结果
        """
        if model_type == "openai":
            return self._call_openai_api(prompt)
        elif model_type == "ollama":
            return self._call_ollama_api(prompt)
        elif model_type == "deepseek":
            return self._call_deepseek_api(prompt)
        elif model_type == "qwen":
            return self._call_qwen_api(prompt)
        elif model_type == "glm":
            return self._call_glm_api(prompt)
        else:
            raise ValueError(f"不支持的模型类型: {model_type}")
    
    def _call_openai_api(self, prompt: str) -> str:
        """调用OpenAI API (兼容SGLang/VLLM)"""
        api_key = self.config.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("缺少OpenAI API密钥")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # 构建请求数据
        data = {
            "model": self.config.get("OPENAI_MODEL", "gpt-3.5-turbo"),
            "messages": [
                {"role": "system", "content": "你是一个专业的法中口语翻译与对话整理编辑"},
                {"role": "user", "content": prompt}
            ],
            "temperature": self.config.get("TEMPERATURE", 0.3)
        }
        
        # 添加可选参数
        max_tokens = self.config.get("OPENAI_MAX_TOKENS")
        if max_tokens:
            data["max_tokens"] = max_tokens
            
        # 获取API URL
        url = self.config.get("OPENAI_API_BASE", "https://api.openai.com/v1/chat/completions")
        
        # 发送请求
        try:
            response = requests.post(url, headers=headers, json=data, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            
            # 处理不同的响应格式 (兼容SGLang/VLLM)
            if "choices" in result and len(result["choices"]) > 0:
                # 标准OpenAI格式
                choice = result["choices"][0]
                if "message" in choice and "content" in choice["message"]:
                    return choice["message"]["content"]
                elif "text" in choice:
                    return choice["text"]
            elif "data" in result and "choices" in result["data"] and len(result["data"]["choices"]) > 0:
                # 某些VLLM实现的格式
                choice = result["data"]["choices"][0]
                if "text" in choice:
                    return choice["text"]
                elif "message" in choice and "content" in choice["message"]:
                    return choice["message"]["content"]
            elif "text" in result:
                # 简单文本响应
                return result["text"]
            elif "generated_text" in result:
                # 某些SGLang实现的格式
                return result["generated_text"]
                
            # 如果以上都不匹配，抛出异常
            raise ValueError(f"无法解析API响应: {result}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenAI API请求失败: {str(e)}")
            raise
    
    def _call_ollama_api(self, prompt: str) -> str:
        """调用Ollama API"""
        model = self.config.get("OLLAMA_MODEL", "llama2")
        url = self.config.get("OLLAMA_API_BASE", "http://localhost:11434/api/generate")
        
        data = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        result = response.json()
        return result["response"]
    
    def _call_deepseek_api(self, prompt: str) -> str:
        """调用DeepSeek API"""
        api_key = self.config.get("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("缺少DeepSeek API密钥")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.config.get("DEEPSEEK_MODEL", "deepseek-chat"),
            "messages": [
                {"role": "system", "content": "你是一个专业的法中口语翻译与对话整理编辑"},
                {"role": "user", "content": prompt}
            ],
            "temperature": self.config.get("TEMPERATURE", 0.3)
        }
        
        url = self.config.get("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1/chat/completions")
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    def _call_qwen_api(self, prompt: str) -> str:
        """调用Qwen API"""
        api_key = self.config.get("QWEN_API_KEY")
        if not api_key:
            raise ValueError("缺少Qwen API密钥")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.config.get("QWEN_MODEL", "qwen-plus"),
            "input": {
                "messages": [
                    {"role": "system", "content": "你是一个专业的法中口语翻译与对话整理编辑"},
                    {"role": "user", "content": prompt}
                ]
            },
            "parameters": {
                "temperature": self.config.get("TEMPERATURE", 0.3)
            }
        }
        
        url = self.config.get("QWEN_API_BASE", "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation")
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        return result["output"]["text"]
    
    def _call_glm_api(self, prompt: str) -> str:
        """调用GLM API"""
        api_key = self.config.get("GLM_API_KEY")
        if not api_key:
            raise ValueError("缺少GLM API密钥")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.config.get("GLM_MODEL", "glm-4"),
            "messages": [
                {"role": "system", "content": "你是一个专业的法中口语翻译与对话整理编辑"},
                {"role": "user", "content": prompt}
            ],
            "temperature": self.config.get("TEMPERATURE", 0.3),
            "do_sample": True
        }
        
        url = self.config.get("GLM_API_BASE", "https://open.bigmodel.cn/api/paas/v4/chat/completions")
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    def _postprocess_output(self, output: str) -> str:
        """
        后处理输出结果
        
        Args:
            output: 模型原始输出
            
        Returns:
            处理后的结果
        """
        # 移除可能的额外说明文字
        lines = output.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # 跳过空行和只包含说明的文字
            if line.strip() and not line.startswith("翻译结果") and not line.startswith("以下是"):
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)