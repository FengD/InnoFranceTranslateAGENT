# Translation Agent

A multi-model supported French to Chinese colloquial translation agent, specifically designed for processing multi-speaker audio transcription texts such as podcasts, interviews, and roundtable discussions.

## Features

- Support for multiple large language model APIs:
  - OpenAI (GPT series)
  - Ollama (locally deployed models)
  - DeepSeek
  - Tongyi Qianwen (Qwen)
  - Zhipu AI (GLM)
  - SGLang/VLLM (high-performance inference services compatible with OpenAI API)
- Web interface testing platform
- Comprehensive logging and structured logs
- Prometheus metrics monitoring
- Professional translation standard-compliant post-processing

## System Requirements

- Python 3.8+
- pip package manager

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd translate_agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables (optional):
```bash
export OPENAI_API_KEY="your-openai-api-key"
export DEEPSEEK_API_KEY="your-deepseek-api-key"
export QWEN_API_KEY="your-qwen-api-key"
export GLM_API_KEY="your-glm-api-key"
```

## Usage

### Starting the Web Application

```bash
python web_app.py
```

Then access `http://localhost:5000` in your browser

### Using the Translation Agent Directly

```bash
# Command line usage
python main.py --input test_data/sample.json --output result.txt --provider openai

# Or without specifying output to print to stdout
python main.py --input test_data/sample.json --provider openai

# Override model name when needed
python main.py --input test_data/sample.json --provider deepseek --model-name deepseek-chat
```

### Using TranslationAgent in Python Code

```python
from translator_agent import TranslationAgent
from config import config
from backend.configs.llm_config import LLMConfig, LLMType

# Prepare input data
input_data = {
    "segments": [
        {
            "text": "Bonjour, comment allez-vous?",
            "speaker": "SPEAKER1"
        },
        {
            "text": "Je vais bien, merci.",
            "speaker": "SPEAKER2"
        }
    ]
}

# Initialize Agent with specific model configuration
llm_config = LLMConfig.from_args(type('Args', (), config.get_all())(), LLMType.OPENAI)
agent = TranslationAgent(config.get_all(), llm_config)

# Execute translation
result = agent.translate(input_data, model_type="openai")
print(result)
```

## Configuration

### Environment Variables

| Variable Name | Default Value | Description |
|---------------|---------------|-------------|
| OPENAI_API_KEY | "" | OpenAI API key |
| OPENAI_API_BASE | "https://api.openai.com/v1" | OpenAI API address |
| OPENAI_MODEL | "gpt-3.5-turbo" | OpenAI model name |
| OLLAMA_API_BASE | "http://localhost:11434/api/generate" | Ollama API address |
| OLLAMA_MODEL | "llama2" | Ollama model name |
| DEEPSEEK_API_KEY | "" | DeepSeek API key |
| DEEPSEEK_API_BASE | "https://api.deepseek.com" | DeepSeek API address |
| DEEPSEEK_MODEL | "deepseek-chat" | DeepSeek model name |
| QWEN_API_KEY | "" | Tongyi Qianwen API key |
| QWEN_API_BASE | "https://dashscope.aliyuncs.com/compatible-mode/v1" | Tongyi Qianwen API address |
| QWEN_MODEL | "qwen-turbo" | Tongyi Qianwen model name |
| GLM_API_KEY | "" | Zhipu AI API key |
| GLM_API_BASE | "https://open.bigmodel.cn/api/paas/v4" | Zhipu AI API address |
| GLM_MODEL | "glm-4" | Zhipu AI model name |
| TEMPERATURE | 0.3 | Model temperature parameter |
| OPENAI_MAX_TOKENS | None | Maximum generated tokens (for SGLang/VLLM, etc.) |
| INPUT_MAX_TOKENS | 3000 | Approximate max input tokens per request |
| TOKEN_CHAR_RATIO | 4 | Approximate chars-per-token ratio |
| SGLANG_API_BASE | "http://localhost:30000/v1" | SGLang API address |
| SGLANG_MODEL | "default" | SGLang model name |
| VLLM_API_BASE | "http://localhost:8000/v1" | VLLM API address |
| VLLM_MODEL | "default" | VLLM model name |
| DEFAULT_MODEL | "openai" | Default provider |
| LOG_LEVEL | "INFO" | Log level |
| LOG_FILE | "logs/translation_agent.log" | Log file path |
| PROMETHEUS_PORT | 8000 | Prometheus metrics port |
| ENABLE_METRICS | "true" | Whether to enable metrics collection |

## Monitoring Metrics

After starting the application, you can view Prometheus metrics at `http://localhost:8000/metrics`:

- `translation_requests_total`: Number of translation requests
- `translation_duration_seconds`: Translation duration distribution
- `active_translations`: Number of active translations
- `api_errors_total`: Number of API errors

## Project Structure

```
translate_agent/
├── translator_agent.py     # Core Agent implementation
├── config.py              # Configuration management
├── logger.py              # Logging module
├── metrics.py             # Metrics monitoring
├── web_app.py             # Web application
├── main.py                # Command line interface
├── utils.py               # Utility functions
├── prompt.md              # System prompt
├── test_json.md           # Test data
├── test_agent.py          # Unit tests
├── requirements.txt       # Dependencies
├── README.md              # English documentation
├── README_zh.md           # Chinese documentation
├── ARCHITECTURE.md        # Architecture design documentation
└── templates/
    └── index.html         # Web interface template
```

## Development Guide

### Adding New Model Support

1. Implement a new provider in the `backend/provider/` directory
2. Register the provider in `backend/provider/__init__.py`
3. Add the model type to the web interface dropdown in `templates/index.html`

### Using SGLang/VLLM

This project now supports SGLang and VLLM OpenAI-compatible interfaces. Use their own provider flags and set the corresponding API base:

```bash
export SGLANG_API_BASE="http://localhost:30000/v1"  # SGLang example
export VLLM_API_BASE="http://localhost:8000/v1"     # VLLM example
```

For scenarios requiring generation length limits, you can set the `OPENAI_MAX_TOKENS` environment variable:

```bash
export OPENAI_MAX_TOKENS=2048
```

### Using curl to Call the API Directly

You can also use curl commands to directly call the translation service API:

```bash
# Using JSON file as input
curl -X POST http://localhost:5000/translate \
  -F "model_type=openai" \
  -F "file=@test_data/sample.json"

# Using text data as input
curl -X POST http://localhost:5000/translate \
  -F "model_type=openai" \
  -F "text_input={\"segments\":[{\"text\":\"Bonjour, comment allez-vous?\",\"speaker\":\"SPEAKER1\"},{\"text\":\"Je vais bien, merci.\",\"speaker\":\"SPEAKER2\"}]}"

# Using SGLang/VLLM service
curl -X POST http://localhost:5000/translate \
  -F "model_type=openai" \
  -F "file=@test_data/sample.json" \
  -H "X-API-Key: your-sglang-vllm-api-key"  # If API key is required
```

Note: When using SGLang or VLLM, make sure you have correctly configured the matching `SGLANG_API_BASE` or `VLLM_API_BASE` environment variable.

### Extending Functionality

- Modify `prompt.md` to adjust translation rules
- Add new data processing functions in `utils.py`
- Add new monitoring metrics in `metrics.py`

## License

MIT License

## Contact

If you have any questions, please submit an Issue or contact the project maintainers.