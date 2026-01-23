import argparse
import json
import os
from translator_agent import TranslationAgent
from config import config
from logger import setup_logging, get_logger
from utils import load_input_data, save_output_data
from backend.configs.llm_config import LLMConfig, LLMType
from backend.provider.llm_provider import add_llm_arguments, LLM_REGISTER

def main():
    # Setup logging
    setup_logging(config.get("LOG_LEVEL", "INFO"), config.get("LOG_FILE", "logs/translation_agent.log"))
    logger = get_logger(__name__)
    
    # Create log directory
    log_dir = os.path.dirname(config.get("LOG_FILE", "logs/translation_agent.log"))
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    parser = argparse.ArgumentParser(description='Translation Agent - French to Chinese Colloquial Translation')
    parser.add_argument('--input', '-i', required=True, help='Input file path (JSON or TXT)')
    parser.add_argument('--output', '-o', help='Output file path (optional, defaults to stdout)')
    parser.add_argument('--provider', '-p', default=config.get('DEFAULT_MODEL', 'openai'),
                        choices=['openai', 'ollama', 'qwen', 'glm', 'deepseek', 'sglang', 'vllm'],
                        help='LLM provider to use')
    parser.add_argument('--model-name', '-m', help='Specific model name to use (optional)')
    
    # Add LLM-related arguments
    add_llm_arguments(parser)
    
    args = parser.parse_args()
    
    try:
        # Load input data
        logger.info(f"Loading input data from {args.input}")
        input_data = load_input_data(args.input)
        
        # Create LLM configuration based on provider type
        llm_type = LLMType(args.provider)
        llm_config = LLMConfig.from_args(args, llm_type)
        
        # Debug: Print the LLM config
        logger.info(f"LLM Config: {llm_type} {llm_config}")
        
        # If model name is specified, override the model in config
        if args.model_name:
            llm_config.model = args.model_name
        
        # Initialize Translation Agent
        logger.info(f"Initializing TranslationAgent with provider: {args.provider}")
        agent = TranslationAgent(config.get_all(), llm_config, LLM_REGISTER)
        
        # Execute translation
        logger.info("Starting translation process")
        result = agent.translate(input_data, args.provider)
        
        # Output results
        if args.output:
            save_output_data(result, args.output)
            logger.info(f"Translation result saved to {args.output}")
            print(f"Translation result saved to {args.output}")
        else:
            print(result)
            logger.info("Translation result printed to stdout")
            
    except Exception as e:
        logger.error(f"Translation failed: {str(e)}")
        print(f"Translation failed: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())