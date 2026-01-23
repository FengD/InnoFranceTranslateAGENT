#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time     : 2024/10/28
@Author   : FengD
@File     : deepseek_provider.py
@brief    : DeepSeek LLM provider implementation
"""

from openai import OpenAI
import os

from backend.provider.base_llm import BaseLLM
from backend.configs.llm_config import LLMConfig, LLMType
from backend.provider.llm_provider import register_provider
from typing import Union, Optional


@register_provider(LLMType.DEEPSEEK)
class DeepSeekProvider(BaseLLM):
    """DeepSeek LLM provider implementation"""
    
    def __init__(self, config: LLMConfig):
        """
        Initialize DeepSeek provider
        
        Args:
            config: LLM configuration
        """
        super().__init__(config)
        # If no API key in config, get from environment variables
        if not self._config.api_key:
            self._config.api_key = os.getenv("DEEPSEEK_API_KEY", "")
        
        # Initialize DeepSeek client
        self._client = OpenAI(
            api_key=self._config.api_key, 
            base_url=self._config.base_url or "https://api.deepseek.com/v1/chat/completions"
        )
    
    def call_llm(self, prompt: str, images: Optional[Union[str, list[str]]] = None):
        """
        Call DeepSeek API
        
        Args:
            prompt: Prompt
            images: Image data (optional)
            
        Returns:
            Result returned by API
        """
        messages, response_format = self._user_msg(prompt, images)
        
        completion = self._client.chat.completions.create(
            model=self._config.model or "deepseek-chat",
            temperature=self._config.temperature,
            top_p=self._config.top_p,
            messages=messages,
            response_format=response_format
        )
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
        messages = [{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": msg
                }
            ],
        }]
        
        # If there is image data, add it to the message
        if images:
            messages[0]["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": images,
                }
            })

        # Define response format
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "translation_result",
                "schema": {
                    "type": "object",
                    "properties": {
                        "translated_text": {
                            "description": "The translated text",
                            "type": "string"
                        },
                        "explanation": {
                            "description": "Explanation of the translation",
                            "type": "string"
                        }
                    },
                    "required": ["translated_text"],
                    "additionalProperties": False
                }
            }
        }
        
        return messages, response_format