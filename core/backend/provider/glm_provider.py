#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time     : 2024/10/28
@Author   : FengD
@File     : glm_provider.py
@brief    : GLM LLM provider implementation
"""

from openai import OpenAI
import os

from .base_llm import BaseLLM
from ..configs.llm_config import LLMConfig, LLMType
from .llm_provider import register_provider
from typing import Union, Optional


@register_provider(LLMType.GLM)
class GLMProvider(BaseLLM):
    """GLM LLM provider implementation"""
    
    def __init__(self, config: LLMConfig):
        """
        Initialize GLM provider
        
        Args:
            config: LLM configuration
        """
        super().__init__(config)
        # If no API key in config, get from environment variables
        if not self._config.api_key:
            self._config.api_key = os.getenv("ZHIPUAI_API_KEY", "")
        
        # Initialize GLM client (OpenAI-compatible)
        self._client = OpenAI(
            api_key=self._config.api_key,
            base_url=self._config.base_url or "https://open.bigmodel.cn/api/paas/v4"
        )
    
    def call_llm(self, prompt: str, images: Optional[Union[str, list[str]]] = None):
        """
        Call GLM API
        
        Args:
            prompt: Prompt
            images: Image data (optional)
            
        Returns:
            Result returned by API
        """
        messages, response_format = self._user_msg(prompt, images)

        request_kwargs = {
            "model": self._config.model or "glm-4",
            "temperature": self._config.temperature,
            "top_p": self._config.top_p,
            "messages": messages,
        }
        if response_format:
            request_kwargs["response_format"] = response_format

        completion = self._client.chat.completions.create(**request_kwargs)
        return completion.choices[0].message.content
        
        
    def _user_msg(self, msg: str, images: Optional[Union[str, list[str]]] = None):
        """
        Construct user message
        
        Args:
            msg: User message text
            images: Image data (optional)
            
        Returns:
            Constructed user message and response format
        """
        messages = []
        if self._config.user_msg:
            messages.append({"role": "system", "content": self._config.user_msg})

        if images:
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": msg},
                    {"type": "image_url", "image_url": {"url": images}},
                ],
            })
        else:
            messages.append({"role": "user", "content": msg})

        response_format = self._config.response_format
        return messages, response_format