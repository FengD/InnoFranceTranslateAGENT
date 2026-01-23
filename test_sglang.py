#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple script to test SGLang API connectivity
"""

import os
import logging
from openai import OpenAI

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_sglang_connection():
    """Test SGLang connection directly with OpenAI client"""
    # Get configuration
    api_key = os.getenv("SGLANG_API_KEY", "") or "EMPTY"
    base_url = os.getenv("SGLANG_API_BASE", "http://localhost:30000/v1")
    model = os.getenv("SGLANG_MODEL", "default")
    
    logger.info(f"Testing SGLang connection:")
    logger.info(f"  API Key: {api_key[:5]}... (truncated)")
    logger.info(f"  Base URL: {base_url}")
    logger.info(f"  Model: {model}")
    
    try:
        # Create OpenAI client
        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        # Test the connection
        logger.info("Sending test request...")
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": "Hello, this is a test message. Please respond with 'Success' if you receive this."
                }
            ],
            temperature=0.0,
            max_tokens=50
        )
        
        logger.info(f"Response received:")
        logger.info(f"  Content: {completion.choices[0].message.content}")
        logger.info(f"  Finish reason: {completion.choices[0].finish_reason}")
        logger.info(f"  Usage: {completion.usage}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error connecting to SGLang: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_sglang_connection()
    if success:
        print("SGLang connection test PASSED")
    else:
        print("SGLang connection test FAILED")