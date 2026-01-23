#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time     : 2024/10/28
@Author   : FengD
@File     : llm_provider.py
@Brief    : registry and getter of the llm provider
"""

from backend.configs.llm_config import LLMConfig, LLMType
from backend.provider.base_llm import BaseLLM
import argparse

class LLMProvider:
    """LLM provider registry"""
    
    def __init__(self):
        self.providers = {}

    def register(self, key, provider_cls):
        """Register LLM provider"""
        self.providers[key] = provider_cls

    def get_provider(self, enum: LLMType):
        """Get provider instance by enum"""
        return self.providers.get(enum)

    def create_llm_instance(self, config: LLMConfig) -> BaseLLM:
        """Create LLM instance"""
        provider_cls = self.providers.get(config.api_type)
        if not provider_cls:
            raise ValueError(f"Unsupported LLM type: {config.api_type}")
        return provider_cls(config)


def register_provider(key):
    """Decorator for registering providers"""
    def decorator(cls):
        if key:
            LLM_REGISTER.register(key, cls)
        return cls
    return decorator


# Registry instance
LLM_REGISTER = LLMProvider()


def add_llm_arguments(parser: argparse.ArgumentParser) -> None:
    """Add LLM-related command line arguments"""
    LLMConfig.add_arguments(parser)