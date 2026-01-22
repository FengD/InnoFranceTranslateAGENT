import argparse
import json
import os
from translator_agent import TranslationAgent
from config import config
from logger import setup_logging, get_logger
from utils import load_input_data, save_output_data

def main():
    # 设置日志
    setup_logging(config.get("LOG_LEVEL", "INFO"), config.get("LOG_FILE", "logs/translation_agent.log"))
    logger = get_logger(__name__)
    
    # 创建日志目录
    log_dir = os.path.dirname(config.get("LOG_FILE", "logs/translation_agent.log"))
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    parser = argparse.ArgumentParser(description='翻译Agent - 法语到中文口语翻译')
    parser.add_argument('--input', '-i', required=True, help='输入文件路径（JSON或TXT）')
    parser.add_argument('--output', '-o', help='输出文件路径（可选，默认为stdout）')
    parser.add_argument('--model', '-m', default=config.get('DEFAULT_MODEL', 'openai'), 
                        choices=['openai', 'ollama', 'deepseek', 'qwen', 'glm'],
                        help='使用的模型类型')
    
    args = parser.parse_args()
    
    try:
        # 加载输入数据
        logger.info(f"Loading input data from {args.input}")
        input_data = load_input_data(args.input)
        
        # 初始化翻译Agent
        logger.info(f"Initializing TranslationAgent with model: {args.model}")
        agent = TranslationAgent(config.get_all())
        
        # 执行翻译
        logger.info("Starting translation process")
        result = agent.translate(input_data, args.model)
        
        # 输出结果
        if args.output:
            save_output_data(result, args.output)
            logger.info(f"Translation result saved to {args.output}")
            print(f"翻译结果已保存到 {args.output}")
        else:
            print(result)
            logger.info("Translation result printed to stdout")
            
    except Exception as e:
        logger.error(f"Translation failed: {str(e)}")
        print(f"翻译失败: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())