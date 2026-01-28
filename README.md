# Translation Agent

A multi-model supported French to Chinese colloquial translation agent, specifically designed for processing multi-speaker audio transcription texts such as podcasts, interviews, and roundtable discussions.

![App screenshot](docs/doc.png)

## 1. Project Structure

```
InnoFranceTranslateAGENT/
├── app/                    # Web application
│   └── main.py            # FastAPI application entry point
├── core/                  # Core algorithm modules
│   ├── translator_agent.py     # Core Agent implementation
│   ├── utils.py               # Utility functions
│   ├── prompt.md              # System prompt
│   └── backend/               # LLM backend implementations
│       ├── configs/           # Configuration classes
│       └── provider/          # Provider implementations
├── config.py              # Configuration management
├── logger.py              # Logging module
├── metrics.py             # Metrics monitoring
├── main.py                # Command line interface
├── requirements.txt       # Dependencies
├── README.md              # This file
├── static/                # Static files (CSS)
├── templates/             # HTML templates
├── test_data/             # Test data samples
└── docs/                  # Documentation
    └── doc.png            # Application screenshot
```

## 2. Features

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

## 3. Installation

```bash
pip install -r requirements.txt
```

## 4. Starting the Service

### 4.1 Method 1: Using Web Service

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Then access `http://localhost:8000` in your browser.

## 5. Usage

### 5.1 Web Interface

After starting the service, visit `http://localhost:8000` in your browser to access the web interface. The interface allows you to:

1. Select different LLM providers (OpenAI, Ollama, Qwen, GLM, DeepSeek, SGLang, VLLM)
2. Specify custom model names
3. Upload JSON files for translation
4. Input text directly for translation
5. View and copy translation results

### 5.2 API Endpoints

#### Translate Text

```bash
# Upload JSON file
curl -X POST http://localhost:8000/translate \
  -F "provider=openai" \
  -F "file=@test_data/sample.json"

# Provide text data directly
curl -X POST http://localhost:8000/translate \
  -F "provider=openai" \
  -F "text_input={\"segments\":[{\"text\":\"Bonjour, comment allez-vous?\",\"speaker\":\"SPEAKER1\"},{\"text\":\"Je vais bien, merci.\",\"speaker\":\"SPEAKER2\"}]}"

# Using SGLang/VLLM service with custom model
curl -X POST http://localhost:8000/translate \
  -F "provider=sglang" \
  -F "model_name=my-custom-model" \
  -F "file=@test_data/sample.json"
```

### 5.3 Command-Line Interface (CLI)

The Translation Agent includes a command-line interface for batch processing:

```bash
# Basic usage - translate input file
python main.py --input test_data/sample.json --provider openai

# Specify output file
python main.py --input test_data/sample.json --output result.txt --provider openai

# Override model name
python main.py --input test_data/sample.json --provider deepseek --model-name deepseek-chat

# Use different provider
python main.py --input test_data/sample.json --provider qwen
```

CLI options:
- `--input`, `-i`: Input file path (JSON or TXT) (required)
- `--output`, `-o`: Output file path (optional, defaults to stdout)
- `--provider`, `-p`: LLM provider to use (openai, ollama, qwen, glm, deepseek, sglang, vllm)
- `--model-name`, `-m`: Specific model name to use (optional)

### 5.4 Using TranslationAgent in Python Code

```python
from core.translator_agent import TranslationAgent
from config import config
from core.backend.configs.llm_config import LLMConfig, LLMType

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

## 6. Input Data Format

The Translation Agent expects input data in the following JSON format:

```json
{
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
```

Each segment contains:
- `text`: The French text to be translated
- `speaker`: Identifier for the speaker (used for maintaining context in multi-speaker conversations)

## 7. Environment Variables

### 7.1 General Configuration

| Variable Name | Default Value | Description |
|---------------|---------------|-------------|
| LOG_LEVEL | "INFO" | Log level |
| LOG_FILE | "logs/translation_agent.log" | Log file path |
| PROMETHEUS_PORT | 8001 | Prometheus metrics port |
| ENABLE_METRICS | "true" | Whether to enable metrics collection |
| INPUT_MAX_TOKENS | 3000 | Approximate max input tokens per request |
| TOKEN_CHAR_RATIO | 4 | Approximate chars-per-token ratio |

### 7.2 OpenAI Configuration

| Variable Name | Default Value | Description |
|---------------|---------------|-------------|
| OPENAI_API_KEY | "" | OpenAI API key |
| OPENAI_API_BASE | "https://api.openai.com/v1" | OpenAI API address |
| OPENAI_MODEL | "gpt-3.5-turbo" | OpenAI model name |

### 7.3 Ollama Configuration

| Variable Name | Default Value | Description |
|---------------|---------------|-------------|
| OLLAMA_API_BASE | "http://localhost:11434/api/generate" | Ollama API address |
| OLLAMA_MODEL | "llama2" | Ollama model name |

### 7.4 DeepSeek Configuration

| Variable Name | Default Value | Description |
|---------------|---------------|-------------|
| DEEPSEEK_API_KEY | "" | DeepSeek API key |
| DEEPSEEK_API_BASE | "https://api.deepseek.com" | DeepSeek API address |
| DEEPSEEK_MODEL | "deepseek-chat" | DeepSeek model name |

### 7.5 Tongyi Qianwen (Qwen) Configuration

| Variable Name | Default Value | Description |
|---------------|---------------|-------------|
| DASHSCOPE_API_KEY | "" | Tongyi Qianwen API key |
| QWEN_API_BASE | "https://dashscope.aliyuncs.com/compatible-mode/v1" | Tongyi Qianwen API address |
| QWEN_MODEL | "qwen-turbo" | Tongyi Qianwen model name |

### 7.6 Zhipu AI (GLM) Configuration

| Variable Name | Default Value | Description |
|---------------|---------------|-------------|
| ZHIPUAI_API_KEY | "" | Zhipu AI API key |
| GLM_API_BASE | "https://open.bigmodel.cn/api/paas/v4" | Zhipu AI API address |
| GLM_MODEL | "glm-4" | Zhipu AI model name |

### 7.7 SGLang Configuration

| Variable Name | Default Value | Description |
|---------------|---------------|-------------|
| SGLANG_API_KEY | "" | SGLang API key |
| SGLANG_API_BASE | "http://localhost:30000/v1" | SGLang API address |
| SGLANG_MODEL | "default" | SGLang model name |

### 7.8 VLLM Configuration

| Variable Name | Default Value | Description |
|---------------|---------------|-------------|
| VLLM_API_KEY | "" | VLLM API key |
| VLLM_API_BASE | "http://localhost:8000/v1" | VLLM API address |
| VLLM_MODEL | "default" | VLLM model name |

## 8. Monitoring Metrics

After starting the application, you can view Prometheus metrics at `http://localhost:8001/metrics`:

- `translation_requests_total`: Number of translation requests
- `translation_duration_seconds`: Translation duration distribution
- `active_translations`: Number of active translations
- `api_errors_total`: Number of API errors

## 9. Development Guide

### 9.1 Adding New Model Support

1. Implement a new provider in the `core/backend/provider/` directory
2. Register the provider in `core/backend/provider/__init__.py`
3. Add the model type to the web interface dropdown in `templates/index.html`

### 9.2 Using SGLang/VLLM

This project supports SGLang and VLLM OpenAI-compatible interfaces. Set the corresponding API base:

```bash
export SGLANG_API_BASE="http://localhost:30000/v1"  # SGLang example
export VLLM_API_BASE="http://localhost:8000/v1"     # VLLM example
```

For scenarios requiring generation length limits, you can set the `OPENAI_MAX_TOKENS` environment variable:

```bash
export OPENAI_MAX_TOKENS=2048
```

### 9.3 Extending Functionality

- Modify `core/prompt.md` to adjust translation rules
- Add new data processing functions in `core/utils.py`
- Add new monitoring metrics in `metrics.py`

## 10. License

MIT License

## 11. Contact

If you have any questions, please submit an Issue or contact the project maintainers.