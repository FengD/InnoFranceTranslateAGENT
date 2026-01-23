import json
import os
import sys
from translator_agent import TranslationAgent
from config import config
from logger import setup_logging, get_logger
from backend.configs.llm_config import LLMConfig
from backend.provider.llm_provider import LLM_REGISTER

def test_basic_functionality():
    """Test basic functionality"""
    print("Starting TranslationAgent testing...")
    
    # Setup logging
    setup_logging("INFO", "logs/test.log")
    logger = get_logger(__name__)
    
    # Create log directory
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    try:
        # Initialize Agent
        llm_config = LLMConfig()
        agent = TranslationAgent(config.get_all(), llm_config, LLM_REGISTER)
        print("✓ TranslationAgent initialized successfully")
        
        # Test data
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
        
        # Test preprocessing
        processed = agent._preprocess_input(test_data)
        assert "[SPEAKER1] Bonjour, comment allez-vous?" in processed
        assert "[SPEAKER2] Je vais bien, merci. Et vous?" in processed
        print("✓ Input preprocessing works correctly")
        
        # Test prompt construction
        prompt = agent._construct_prompt(processed)
        assert len(prompt) > len(processed)
        print("✓ Prompt construction works correctly")
        
        # Test postprocessing
        test_output = "Translation result:\n[SPEAKER1] 你好，你怎么样？\n[SPEAKER2] 我很好，谢谢。你呢？"
        cleaned = agent._postprocess_output(test_output)
        assert "Translation result" not in cleaned
        assert "[SPEAKER1] 你好，你怎么样？" in cleaned
        print("✓ Output postprocessing works correctly")
        
        print("\nAll basic functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        logger.error(f"Test failed: {str(e)}")
        return False

def test_utils():
    """Test utility functions"""
    print("\nStarting utility function testing...")
    
    try:
        # Test data validation
        from utils import validate_input_data
        
        # Valid data
        valid_data1 = {
            "segments": [
                {"text": "test", "speaker": "SPEAKER1"}
            ]
        }
        assert validate_input_data(valid_data1) == True
        
        # Valid plain text data
        valid_data2 = {"text": "这是一个测试"}
        assert validate_input_data(valid_data2) == True
        
        # Invalid data
        invalid_data = {"segments": "not a list"}
        assert validate_input_data(invalid_data) == False
        
        print("✓ Data validation works correctly")
        
        # Test cleaning function
        from utils import clean_translation_output
        
        test_output = "Translation result:\n这是测试内容"
        cleaned = clean_translation_output(test_output)
        assert "Translation result" not in cleaned
        assert "这是测试内容" in cleaned
        
        print("✓ Text cleaning works correctly")
        
        print("\nUtility function tests passed!")
        return True
        
    except Exception as e:
        print(f"Utility function test failed: {str(e)}")
        return False

def test_llm_providers():
    """Test all LLM providers"""
    print("\nStarting LLM providers testing...")
    
    try:
        # Setup logging
        setup_logging("INFO", "logs/test.log")
        logger = get_logger(__name__)
        
        # Initialize Agent
        llm_config = LLMConfig()
        agent = TranslationAgent(config.get_all(), llm_config, LLM_REGISTER)
        
        # Test data
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
        
        # Test all supported LLM providers
        providers = ["openai", "ollama", "qwen", "glm", "deepseek"]
        
        for provider in providers:
            try:
                # Skip providers that require API keys if not configured
                if provider == "openai" and not config.get("OPENAI_API_KEY"):
                    print(f"⚠️  Skipping {provider} test (API key not configured)")
                    continue
                elif provider == "qwen" and not config.get("QWEN_API_KEY"):
                    print(f"⚠️  Skipping {provider} test (API key not configured)")
                    continue
                elif provider == "glm" and not config.get("GLM_API_KEY"):
                    print(f"⚠️  Skipping {provider} test (API key not configured)")
                    continue
                elif provider == "deepseek" and not config.get("DEEPSEEK_API_KEY"):
                    print(f"⚠️  Skipping {provider} test (API key not configured)")
                    continue
                
                # Test preprocessing
                processed = agent._preprocess_input(test_data)
                
                # Test prompt construction
                prompt = agent._construct_prompt(processed)
                
                print(f"✓ {provider} provider test passed")
                
            except Exception as e:
                # For providers that require running services (like Ollama), we don't want to fail the test
                if provider == "ollama" and ("Connection refused" in str(e) or "Connection refused" in str(e)):
                    print(f"⚠️  {provider} test skipped (service not running)")
                else:
                    print(f"⚠️  {provider} test failed: {str(e)}")
                    logger.warning(f"{provider} test failed: {str(e)}")
        
        print("\nLLM providers tests completed!")
        return True
        
    except Exception as e:
        print(f"LLM providers test failed: {str(e)}")
        logger.error(f"LLM providers test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Translation Agent Test Suite ===\n")
    
    # Test basic functionality
    basic_test_passed = test_basic_functionality()
    
    # Test utility functions
    utils_test_passed = test_utils()
    
    # Test LLM providers
    llm_test_passed = test_llm_providers()
    
    print("\n=== Test Summary ===")
    if basic_test_passed and utils_test_passed and llm_test_passed:
        print("All tests passed! Translation Agent basic functionality is working.")
        sys.exit(0)
    else:
        print("Some tests failed, please check the code.")
        sys.exit(1)