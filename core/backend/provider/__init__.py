#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time     : 2024/10/28
@Author   : FengD
@File     : __init__.py
"""

from importlib import import_module


_PROVIDERS = [
    ("OpenAIProvider", ".openai_provider"),
    ("OllamaProvider", ".ollama_provider"),
    ("QwenProvider", ".qwen_provider"),
    ("GLMProvider", ".glm_provider"),
    ("DeepSeekProvider", ".deepseek_provider"),
    ("SGLangProvider", ".sglang_provider"),
    ("VLLMProvider", ".vllm_provider"),
]

__all__ = []

for name, module_path in _PROVIDERS:
    try:
        module = import_module(module_path, package=__name__)
        globals()[name] = getattr(module, name)
        __all__.append(name)
    except Exception:
        continue
