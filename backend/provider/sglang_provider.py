#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time     : 2024/10/28
@Author   : FengD
@File     : sglang_provider.py
@brief    : SGLang LLM provider implementation
"""

from openai import OpenAI
import os

from backend.provider.base_llm import BaseLLM
from backend.configs.llm_config import LLMConfig, LLMType
from backend.provider.llm_provider import register_provider
from typing import Union, Optional


@register_provider(LLMType.SGLANG)
class SGLangProvider(BaseLLM):
    """SGLang LLM provider implementation"""
    
    def __init__(self, config: LLMConfig):
        """
        Initialize SGLang provider
        
        Args:
            config: LLM configuration
        """
        super().__init__(config)
        # If no API key in config, get from environment variables
        if not self._config.api_key:
            self._config.api_key = os.getenv("SGLANG_API_KEY", "")
        
        # Initialize OpenAI client (SGLang uses OpenAI-compatible API)
        # Handle proxies parameter issue with newer versions of openai library
        client_kwargs = {
            "api_key": self._config.api_key or "EMPTY",  # SGLang doesn't require API key
        }
        if self._config.base_url:
            client_kwargs["base_url"] = self._config.base_url
            
        # Debug: Print the config and kwargs
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"SGLangProvider config: {self._config}")
        logger.debug(f"SGLang client kwargs: {client_kwargs}")
        
        # Additional debug info
        logger.debug(f"Base URL being used: {client_kwargs.get('base_url', 'Not set')}")
            
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
            logger.error(f"TypeError when initializing SGLang client: {e}")
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
        Call SGLang API
        
        Args:
            prompt: Prompt
            images: Image data (optional)
            
        Returns:
            Result returned by API
        """
        messages, response_format = self._user_msg(prompt, images)
        
        # Debug: Print the request details
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"Sending request to SGLang API with model: {self._config.model or 'default'}")
        logger.debug(f"Messages: {messages}")
        
        try:
            request_kwargs = {
                "model": self._config.model or "default",
                "temperature": self._config.temperature,
                "top_p": self._config.top_p,
                "messages": messages,
            }
            if response_format:
                request_kwargs["response_format"] = response_format

            completion = self._client.chat.completions.create(**request_kwargs)
            logger.debug(f"Received response from SGLang API: {completion}")
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Error calling SGLang API: {str(e)}")
            raise
        
        
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