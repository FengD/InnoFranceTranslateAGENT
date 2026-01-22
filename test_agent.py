import json
import os
import sys
from translator_agent import TranslationAgent
from config import config
from logger import setup_logging, get_logger

def test_basic_functionality():
    """测试基本功能"""
    print("开始测试翻译Agent...")
    
    # 设置日志
    setup_logging("INFO", "logs/test.log")
    logger = get_logger(__name__)
    
    # 创建日志目录
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    try:
        # 初始化Agent
        agent = TranslationAgent(config.get_all())
        print("✓ TranslationAgent初始化成功")
        
        # 测试数据
        test_data = {
            "segments": [
                {
                    "text": "Bonjour, comment allez-vous?",
                    "speaker": "SPEAKER1"
                },
                {
                    "text": "Je vais bien, merci. Et vous?",
                    "speaker": "SPEAKER2"
                }
            ]
        }
        
        # 测试预处理
        processed = agent._preprocess_input(test_data)
        assert "[SPEAKER1] Bonjour, comment allez-vous?" in processed
        assert "[SPEAKER2] Je vais bien, merci. Et vous?" in processed
        print("✓ 输入预处理功能正常")
        
        # 测试Prompt构造
        prompt = agent._construct_prompt(processed)
        assert len(prompt) > len(processed)
        print("✓ Prompt构造功能正常")
        
        # 测试后处理
        test_output = "翻译结果：\n[SPEAKER1] 你好，你怎么样？\n[SPEAKER2] 我很好，谢谢。你呢？"
        cleaned = agent._postprocess_output(test_output)
        assert "翻译结果" not in cleaned
        assert "[SPEAKER1] 你好，你怎么样？" in cleaned
        print("✓ 输出后处理功能正常")
        
        print("\n所有基本功能测试通过！")
        return True
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        logger.error(f"Test failed: {str(e)}")
        return False

def test_utils():
    """测试工具函数"""
    print("\n开始测试工具函数...")
    
    try:
        # 测试数据验证
        from utils import validate_input_data
        
        # 有效数据
        valid_data1 = {
            "segments": [
                {"text": "test", "speaker": "SPEAKER1"}
            ]
        }
        assert validate_input_data(valid_data1) == True
        
        # 有效纯文本数据
        valid_data2 = {"text": "这是一个测试"}
        assert validate_input_data(valid_data2) == True
        
        # 无效数据
        invalid_data = {"segments": "not a list"}
        assert validate_input_data(invalid_data) == False
        
        print("✓ 数据验证功能正常")
        
        # 测试清理函数
        from utils import clean_translation_output
        
        test_output = "翻译结果：\n这是测试内容"
        cleaned = clean_translation_output(test_output)
        assert "翻译结果" not in cleaned
        assert "这是测试内容" in cleaned
        
        print("✓ 文本清理功能正常")
        
        print("\n工具函数测试通过！")
        return True
        
    except Exception as e:
        print(f"工具函数测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== 翻译Agent测试套件 ===\n")
    
    # 测试基本功能
    basic_test_passed = test_basic_functionality()
    
    # 测试工具函数
    utils_test_passed = test_utils()
    
    print("\n=== 测试总结 ===")
    if basic_test_passed and utils_test_passed:
        print("所有测试通过！翻译Agent基本功能正常。")
        sys.exit(0)
    else:
        print("部分测试失败，请检查代码。")
        sys.exit(1)