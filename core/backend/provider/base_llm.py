#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time     : 2024/10/28
@Author   : FengD
@File     : base_llm.py
@brief    : Base class for LLM providers
"""

from abc import ABC, abstractmethod
from typing import Optional, Union
from ..configs.llm_config import LLMConfig

class BaseLLM(ABC):
    """Base class for LLM providers"""
    
    def __init__(self, config: LLMConfig):
        """
        Initialize LLM provider
        
        Args:
            config: LLM configuration
        """
        self._config = config
    
    @abstractmethod
    def call_llm(self, prompt: str, images: Optional[Union[str, list[str]]] = None):
        """
        Call LLM interface
        
        Args:
            prompt: Prompt
            images: Image data (optional)
            
        Returns:
            Result returned by LLM
        """
        pass

    @abstractmethod
    def _user_msg(self, msg: str, images: Optional[Union[str, list[str]]] = None) -> dict[str, Union[str, dict]]:
        """
        Construct user message
        
        Args:
            msg: User message text
            images: Image data (optional)
            
        Returns:
            Constructed user message
        """
        pass
