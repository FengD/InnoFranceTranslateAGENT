#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time     : 2024/10/28
@Author   : FengD
@File     : ollama_provider.py
@brief    : Ollama LLM provider implementation
"""

from typing import Union, Optional
import requests
import os
from backend.configs.llm_config import LLMType, LLMConfig
from backend.provider.base_llm import BaseLLM
from backend.provider.llm_provider import register_provider


@register_provider(LLMType.OLLAMA)
class OllamaProvider(BaseLLM):
    """Ollama LLM provider implementation"""

    def __init__(self, config: LLMConfig):
        """
        Initialize Ollama provider
        
        Args:
            config: LLM configuration
        """
        super().__init__(config)
        # If no base_url in config, get from environment variables
        if not self._config.base_url:
            self._config.base_url = os.environ.get("OLLAMA_API_BASE", "http://localhost:11434/api/generate")

    def call_llm(self, prompt: str, images: Optional[Union[str, list[str]]] = None):
        """
        Call Ollama API
        
        Args:
            prompt: Prompt
            images: Image data (optional)
            
        Returns:
            Result returned by API
        """
        system_prefix = f"{self._config.user_msg}\n\n" if self._config.user_msg else ""
        payload = {
            "model": self._config.model or "llama2",
            "prompt": f"{system_prefix}{prompt}",
            "stream": False,
            "format": "json",
            "options": {
                "temperature": self._config.temperature,
                "top_p": self._config.top_p
            }
        }
        
        response = requests.post(self._config.base_url, json=payload)

        # Process response
        if response.status_code == 200:
            return response.json()["response"]
        else:
            raise Exception(f"Ollama API request failed with status code {response.status_code}: {response.text}")

    def _user_msg(self, msg: str, images: Optional[Union[str, list[str]]] = None) -> dict[str, Union[str, dict]]:
        """
        Construct user message
        
        Args:
            msg: User message text
            images: Image data (optional)
            
        Returns:
            Constructed user message
        """
        return {"role": "user", "content": msg}
