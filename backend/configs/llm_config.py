#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time     : 2024/10/28
@Author   : FengD
@File     : llm_config.py
@brief    : used to define the useful parameters of a LLM Config
"""

from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
import argparse
import os
import logging
logger = logging.getLogger(__name__)

class LLMType(Enum):
    OPENAI = "openai"
    OLLAMA = "ollama"
    QWEN = "qwen"
    GLM = "glm"
    DEEPSEEK = "deepseek"
    SGLANG = "sglang"
    VLLM = "vllm"
    
    def __missing__(self, key):
        raise ValueError(f"{key} is not a valid llm type")


@dataclass
class LLMConfig:
    """LLM configuration base class"""
    api_key: str = ""
    api_type: LLMType = LLMType.OPENAI
    base_url: str = ""
    api_version: Optional[str] = None
    model: Optional[str] = None
    response_format: Optional[object] = None
    user_msg: str = ""
    temperature: float = 0.0
    top_p: float = 0.9
    
def arg_or_env(args, arg_name: str, env_name: str, default=None):
    """
    Priority:
    1. Command line argument (if not None)
    2. Environment variable
    3. Default value
    """
    value = getattr(args, arg_name, None)
    if value is not None:
        return value
    return os.getenv(env_name, default)


@dataclass
class LLMConfig:
    """LLM configuration base class"""
    api_key: str = ""
    api_type: 'LLMType' = None
    base_url: str = ""
    api_version: Optional[str] = None
    model: Optional[str] = None
    response_format: Optional[object] = None
    user_msg: str = ""
    temperature: float = 0.0
    top_p: float = 0.9

    @classmethod
    def from_args(cls, args: argparse.Namespace, llm_type: 'LLMType') -> 'LLMConfig':
        """Create configuration from command line arguments"""
        config = cls(api_type=llm_type)

        if llm_type == LLMType.OPENAI:
            config.api_key = arg_or_env(
                args, 'openai_api_key', 'OPENAI_API_KEY', ""
            )
            config.base_url = arg_or_env(
                args, 'openai_api_base', 'OPENAI_API_BASE',
                "https://api.openai.com/v1/chat/completions"
            )
            config.model = arg_or_env(
                args, 'openai_model', 'OPENAI_MODEL', "gpt-3.5-turbo"
            )

        elif llm_type == LLMType.OLLAMA:
            config.base_url = arg_or_env(
                args, 'ollama_api_base', 'OLLAMA_API_BASE',
                "http://localhost:11434/api/generate"
            )
            config.model = arg_or_env(
                args, 'ollama_model', 'OLLAMA_MODEL', "llama2"
            )

        elif llm_type == LLMType.QWEN:
            config.api_key = arg_or_env(
                args, 'qwen_api_key', 'DASHSCOPE_API_KEY', ""
            )
            config.base_url = arg_or_env(
                args, 'qwen_api_base', 'QWEN_API_BASE',
                "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
            )
            config.model = arg_or_env(
                args, 'qwen_model', 'QWEN_MODEL', "qwen-turbo"
            )

        elif llm_type == LLMType.GLM:
            config.api_key = arg_or_env(
                args, 'glm_api_key', 'ZHIPUAI_API_KEY', ""
            )
            config.base_url = arg_or_env(
                args, 'glm_api_base', 'GLM_API_BASE',
                "https://open.bigmodel.cn/api/paas/v4/chat/completions"
            )
            config.model = arg_or_env(
                args, 'glm_model', 'GLM_MODEL', "glm-4"
            )

        elif llm_type == LLMType.DEEPSEEK:
            config.api_key = arg_or_env(
                args, 'deepseek_api_key', 'DEEPSEEK_API_KEY', ""
            )
            config.base_url = arg_or_env(
                args, 'deepseek_api_base', 'DEEPSEEK_API_BASE',
                "https://api.deepseek.com/v1/chat/completions"
            )
            config.model = arg_or_env(
                args, 'deepseek_model', 'DEEPSEEK_MODEL', "deepseek-chat"
            )

        elif llm_type == LLMType.SGLANG:
            config.api_key = arg_or_env(
                args, 'sglang_api_key', 'SGLANG_API_KEY', ""
            )
            config.base_url = arg_or_env(
                args, 'sglang_api_base', 'SGLANG_API_BASE',
                "http://localhost:30000/v1"
            )
            config.model = arg_or_env(
                args, 'sglang_model', 'SGLANG_MODEL', "default"
            )

            logger.info(
                f"SGLANG config - api_key: {config.api_key}, "
                f"base_url: {config.base_url}, model: {config.model}"
            )

        elif llm_type == LLMType.VLLM:
            config.api_key = arg_or_env(
                args, 'vllm_api_key', 'VLLM_API_KEY', ""
            )
            config.base_url = arg_or_env(
                args, 'vllm_api_base', 'VLLM_API_BASE',
                "http://localhost:8000/v1"
            )
            config.model = arg_or_env(
                args, 'vllm_model', 'VLLM_MODEL', "default"
            )

            logger.info(
                f"VLLM config - api_key: {config.api_key}, "
                f"base_url: {config.base_url}, model: {config.model}"
            )

        return config

    
    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        """Add command line arguments"""
        # OpenAI related parameters
        parser.add_argument('--openai-api-key', help='OpenAI API Key')
        parser.add_argument('--openai-api-base', help='OpenAI API Base URL')
        parser.add_argument('--openai-model', help='OpenAI Model Name')
        
        # Ollama related parameters
        parser.add_argument('--ollama-api-base', help='Ollama API Base URL')
        parser.add_argument('--ollama-model', help='Ollama Model Name')
        
        # Qwen related parameters
        parser.add_argument('--qwen-api-key', help='Qwen API Key')
        parser.add_argument('--qwen-api-base', help='Qwen API Base URL')
        parser.add_argument('--qwen-model', help='Qwen Model Name')
        
        # GLM related parameters
        parser.add_argument('--glm-api-key', help='GLM API Key')
        parser.add_argument('--glm-api-base', help='GLM API Base URL')
        parser.add_argument('--glm-model', help='GLM Model Name')
        
        # DeepSeek related parameters
        parser.add_argument('--deepseek-api-key', help='DeepSeek API Key')
        parser.add_argument('--deepseek-api-base', help='DeepSeek API Base URL')
        parser.add_argument('--deepseek-model', help='DeepSeek Model Name')
        
        # SGLang related parameters
        parser.add_argument('--sglang-api-key', help='SGLang API Key')
        parser.add_argument('--sglang-api-base', help='SGLang API Base URL')
        parser.add_argument('--sglang-model', help='SGLang Model Name')
        
        # VLLM related parameters
        parser.add_argument('--vllm-api-key', help='VLLM API Key')
        parser.add_argument('--vllm-api-base', help='VLLM API Base URL')
        parser.add_argument('--vllm-model', help='VLLM Model Name')
