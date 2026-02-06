import json
import logging
import os
import requests
import time
from pathlib import Path
from typing import Dict, Any, Optional
from logger import get_logger
from metrics import MetricsCollector
from core.backend.configs.llm_config import LLMConfig, LLMType
from core.backend.provider.base_llm import BaseLLM
from core.backend.provider.llm_provider import LLMProvider

logger = get_logger(__name__)

class TranslationAgent:
    def __init__(
        self,
        config: Dict[str, Any],
        llm_config: LLMConfig,
        llm_register: LLMProvider,
        prompt_type: str = "translate",
        prompt_path: Optional[str] = None,
    ):
        """
        Initialize Translation Agent
        
        Args:
            config: Configuration dictionary containing API keys and other settings
            llm_config: LLM configuration
            llm_register: LLM provider registry
        """
        self.config = config
        self.llm_config = llm_config
        self.llm_register = llm_register
        self.metrics = MetricsCollector()
        self.prompt_type = prompt_type
        self.prompt_path = prompt_path
        self.prompt_template = self._load_prompt()
        
    def _resolve_prompt_path(self) -> Path:
        base_dir = Path(__file__).resolve().parent
        if self.prompt_path:
            path = Path(self.prompt_path)
            if not path.is_absolute():
                path = base_dir / path
            return path
        prompt_name = f"{self.prompt_type}.md" if self.prompt_type else "translate.md"
        return base_dir / prompt_name

    def _load_prompt(self) -> str:
        """Load system prompt"""
        try:
            prompt_path = self._resolve_prompt_path()
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            logger.error("prompt file not found")
            return ""
    
    def translate(self, input_data: Dict[str, Any], model_type: str = "openai") -> str:
        """
        Execute translation task
        
        Args:
            input_data: Input JSON data
            model_type: Model type to use
            
        Returns:
            Translation result
        """
        start_time = time.time()
        try:
            # Preprocess input data
            processed_input = self._preprocess_input(input_data)
            
            # Split input to avoid exceeding token limits
            if self.prompt_type == "summary":
                input_chunks = [processed_input]
            else:
                input_chunks = self._split_input_by_tokens(processed_input)

            # Call specified model API for each chunk
            results = []
            for chunk in input_chunks:
                prompt = self._construct_prompt(chunk)
                translation_result = self._call_model_api(prompt, model_type)
                results.append(self._postprocess_output(translation_result))

            if self.prompt_type == "summary" and len(results) > 1:
                combined = " ".join([r for r in results if r.strip()])
                final_prompt = self._construct_prompt(combined)
                final_output = self._call_model_api(final_prompt, model_type)
                final_result = self._normalize_summary_output(
                    self._postprocess_output(final_output)
                )
            else:
                final_result = "\n".join([r for r in results if r.strip()])
                if self.prompt_type == "summary":
                    final_result = self._normalize_summary_output(final_result)
            
            # Record success metrics
            duration = time.time() - start_time
            self.metrics.record_translation_success(model_type, duration)
            
            return final_result
            
        except Exception as e:
            # Record failure metrics
            duration = time.time() - start_time
            self.metrics.record_translation_failure(model_type, duration)
            logger.error(f"Error occurred during translation: {str(e)}")
            raise
    
    def _preprocess_input(self, input_data: Dict[str, Any]) -> str:
        """
        Preprocess input data
        
        Args:
            input_data: Raw input data
            
        Returns:
            Processed text
        """
        if "segments" in input_data:
            # Process JSON format segments
            segments_text = []
            for segment in input_data["segments"]:
                speaker = segment.get("speaker", "UNKNOWN")
                text = segment.get("text", "")
                segments_text.append(f"[{speaker}] {text}")
            return "\n".join(segments_text)
        else:
            # Process plain text
            return str(input_data)
    
    def _construct_prompt(self, input_text: str) -> str:
        """
        Construct complete prompt
        
        Args:
            input_text: Input text
            
        Returns:
            Complete prompt
        """
        prefix = self._prompt_prefix()
        return f"{prefix}{input_text}"

    def _prompt_prefix(self) -> str:
        prefix_map = {
            "translate": "Please translate the following content:\n",
            "summary": "Please summarize the following content:\n",
            "check": "Please check and format the following content:\n",
        }
        return prefix_map.get(self.prompt_type, "Please process the following content:\n")

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count using a simple character ratio heuristic."""
        ratio = self.config.get("TOKEN_CHAR_RATIO", 4)
        try:
            ratio = float(ratio)
        except (TypeError, ValueError):
            ratio = 4
        if ratio <= 0:
            ratio = 4
        return max(1, int(len(text) / ratio))

    def _split_input_by_tokens(self, input_text: str) -> list[str]:
        """Split long input into chunks based on approximate token count."""
        max_tokens = self.config.get("INPUT_MAX_TOKENS", 3000)
        try:
            max_tokens = int(max_tokens)
        except (TypeError, ValueError):
            max_tokens = 3000
        if max_tokens <= 0:
            return [input_text]

        system_tokens = self._estimate_tokens(self.prompt_template)
        overhead_tokens = self._estimate_tokens(self._prompt_prefix())
        available_tokens = max(max_tokens - system_tokens - overhead_tokens, 200)

        if self._estimate_tokens(input_text) <= available_tokens:
            return [input_text]

        lines = input_text.splitlines()
        chunks: list[str] = []
        current: list[str] = []
        current_tokens = 0

        def flush_current():
            nonlocal current, current_tokens
            if current:
                chunks.append("\n".join(current))
                current = []
                current_tokens = 0

        try:
            ratio = float(self.config.get("TOKEN_CHAR_RATIO", 4))
        except (TypeError, ValueError):
            ratio = 4
        if ratio <= 0:
            ratio = 4
        max_chars = max(int(available_tokens * ratio), 200)

        for line in lines:
            line_tokens = self._estimate_tokens(line)
            if line_tokens > available_tokens:
                flush_current()
                for i in range(0, len(line), max_chars):
                    chunks.append(line[i:i + max_chars])
                continue

            projected = current_tokens + line_tokens + (1 if current else 0)
            if projected > available_tokens:
                flush_current()

            current.append(line)
            current_tokens = current_tokens + line_tokens + (1 if current_tokens > 0 else 0)

        flush_current()
        return chunks
    
    def _call_model_api(self, prompt: str, model_type: str) -> str:
        """
        Call specified model API
        
        Args:
            prompt: Prompt sent to the model
            model_type: Model type
            
        Returns:
            Result returned by the model
        """
        # Create LLM instance based on model type
        llm_type = LLMType(model_type)
        # Use the llm_config passed to the agent if available, otherwise create from config
        if hasattr(self, 'llm_config') and self.llm_config.api_type == llm_type:
            llm_config = self.llm_config
        else:
            llm_config = LLMConfig.from_args(type('Args', (), self.config)(), llm_type)
        llm_config.user_msg = self.prompt_template
        llm: BaseLLM = self.llm_register.create_llm_instance(llm_config)
        
        # Call LLM
        return llm.call_llm(prompt)
    
    def _postprocess_output(self, output: str) -> str:
        """
        Post-process output results
        
        Args:
            output: Raw output from the model
            
        Returns:
            Processed results
        """
        # Remove possible extra explanatory text
        lines = output.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip empty lines and lines containing only explanations
            if line.strip() and not line.startswith("Translation result") and not line.startswith("The following is"):
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)

    def _normalize_summary_output(self, output: str) -> str:
        """Force summary output into a single paragraph."""
        normalized = " ".join(output.replace("\r", "\n").split())
        return normalized.strip()