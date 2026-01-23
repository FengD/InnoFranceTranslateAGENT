#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time     : 2024/10/28
@Author   : FengD
@File     : openai_provider.py
@brief    : OpenAI LLM provider implementation
"""

from openai import OpenAI
import os

from backend.provider.base_llm import BaseLLM
from backend.configs.llm_config import LLMConfig, LLMType
from backend.provider.llm_provider import register_provider
from typing import Union, Optional

@register_provider(LLMType.OPENAI)
class OpenAIProvider(BaseLLM):
    """OpenAI LLM provider implementation"""
    
    def __init__(self, config: LLMConfig):
        """
        Initialize OpenAI provider
        
        Args:
            config: LLM configuration
        """
        super().__init__(config)
        # If no API key in config, get from environment variables
        if not self._config.api_key:
            self._config.api_key = os.getenv("OPENAI_API_KEY", "")
        
        # Initialize OpenAI client
        # Handle proxies parameter issue with newer versions of openai library
        client_kwargs = {
            "api_key": self._config.api_key or "EMPTY",  # SGLang/VLLM doesn't require API key
        }
        if self._config.base_url:
            client_kwargs["base_url"] = self._config.base_url
            
        # Debug: Print the config and kwargs
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"OpenAIProvider config: {self._config}")
        logger.debug(f"OpenAI client kwargs: {client_kwargs}")
            
        # Clear proxy environment variables to avoid issues with OpenAI client
        original_proxy = os.environ.get('http_proxy')
        original_https_proxy = os.environ.get('https_proxy')
        
        try:
            # Temporarily remove proxy settings
            if 'http_proxy' in os.environ:
                del os.environ['http_proxy']
            if 'https_proxy' in os.environ:
                del os.environ['https_proxy']
                
            # Only pass supported arguments to OpenAI client
            self._client = OpenAI(**client_kwargs)
            
        except TypeError as e:
            # Log the error for debugging
            logger.error(f"TypeError when initializing OpenAI client: {e}")
            # If there's still an issue with parameters, try with minimal args
            if "proxies" in str(e):
                # Retry with only essential parameters
                minimal_kwargs = {"api_key": client_kwargs["api_key"]}
                if "base_url" in client_kwargs:
                    minimal_kwargs["base_url"] = client_kwargs["base_url"]
                self._client = OpenAI(**minimal_kwargs)
            else:
                raise
        finally:
            # Restore proxy settings
            if original_proxy:
                os.environ['http_proxy'] = original_proxy
            if original_https_proxy:
                os.environ['https_proxy'] = original_https_proxy
    
    def call_llm(self, prompt: str, images: Optional[Union[str, list[str]]] = None):
        """
        Call OpenAI API
        
        Args:
            prompt: Prompt
            images: Image data (optional)
            
        Returns:
            Result returned by API
        """
        messages, response_format = self._user_msg(prompt, images)
        
        completion = self._client.chat.completions.create(
            model=self._config.model or "gpt-3.5-turbo",
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
