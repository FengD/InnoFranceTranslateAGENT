import json
import logging
import os
import requests
import time
from typing import Dict, Any, Optional
from logger import get_logger
from metrics import MetricsCollector
from backend.configs.llm_config import LLMConfig, LLMType
from backend.provider.base_llm import BaseLLM
from backend.provider.llm_provider import LLMProvider

logger = get_logger(__name__)

class TranslationAgent:
    def __init__(self, config: Dict[str, Any], llm_config: LLMConfig, llm_register: LLMProvider):
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
        self.prompt_template = self._load_prompt()
        
    def _load_prompt(self) -> str:
        """Load system prompt"""
        try:
            with open('prompt.md', 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.error("prompt.md file not found")
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
            
            # Construct prompt
            prompt = self._construct_prompt(processed_input)
            
            # Call specified model API
            translation_result = self._call_model_api(prompt, model_type)
            
            # Post-process results
            final_result = self._postprocess_output(translation_result)
            
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
        return f"{self.prompt_template}\n\nPlease translate the following content:\n{input_text}"
    
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