# 翻译Agent

一个多模型支持的法语到中文口语翻译智能体，专门用于处理播客、访谈、圆桌讨论等多说话人语音转写文本。

## 功能特性

- 支持多种大语言模型API：
  - OpenAI (GPT系列)
  - Ollama (本地部署模型)
  - DeepSeek
  - 通义千问 (Qwen)
  - 智谱清言 (GLM)
  - SGLang/VLLM (兼容OpenAI API的高性能推理服务)
- Web界面测试平台
- 完整的日志记录和结构化日志
- Prometheus指标监控
- 符合专业翻译规范的后处理

## 系统要求

- Python 3.8+
- pip包管理器

## 安装

1. 克隆仓库：
```bash
git clone <repository-url>
cd translate_agent
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量（可选）：
```bash
export OPENAI_API_KEY="your-openai-api-key"
export DEEPSEEK_API_KEY="your-deepseek-api-key"
export QWEN_API_KEY="your-qwen-api-key"
export GLM_API_KEY="your-glm-api-key"
```

## 使用方法

### 启动Web应用

```bash
python web_app.py
```

然后在浏览器中访问 `http://localhost:5000`

### 直接使用翻译Agent

```python
from translator_agent import TranslationAgent
from config import config

# 初始化Agent
agent = TranslationAgent(config.get_all())

# 准备输入数据
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

# 执行翻译
result = agent.translate(input_data, model_type="openai")
print(result)
```

## 配置说明

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| OPENAI_API_KEY | "" | OpenAI API密钥 |
| OPENAI_API_BASE | "https://api.openai.com/v1/chat/completions" | OpenAI API地址 |
| OPENAI_MODEL | "gpt-3.5-turbo" | OpenAI模型名称 |
| OLLAMA_API_BASE | "http://localhost:11434/api/generate" | Ollama API地址 |
| OLLAMA_MODEL | "llama2" | Ollama模型名称 |
| DEEPSEEK_API_KEY | "" | DeepSeek API密钥 |
| DEEPSEEK_API_BASE | "https://api.deepseek.com/v1/chat/completions" | DeepSeek API地址 |
| DEEPSEEK_MODEL | "deepseek-chat" | DeepSeek模型名称 |
| QWEN_API_KEY | "" | 通义千问API密钥 |
| QWEN_API_BASE | "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation" | 通义千问API地址 |
| QWEN_MODEL | "qwen-plus" | 通义千问模型名称 |
| GLM_API_KEY | "" | 智谱清言API密钥 |
| GLM_API_BASE | "https://open.bigmodel.cn/api/paas/v4/chat/completions" | 智谱清言API地址 |
| GLM_MODEL | "glm-4" | 智谱清言模型名称 |
| TEMPERATURE | 0.3 | 模型温度参数 |
| OPENAI_MAX_TOKENS | None | 最大生成token数（适用于SGLang/VLLM等） |
| DEFAULT_MODEL | "openai" | 默认模型 |
| LOG_LEVEL | "INFO" | 日志级别 |
| LOG_FILE | "logs/translation_agent.log" | 日志文件路径 |
| PROMETHEUS_PORT | 8000 | Prometheus指标端口 |
| ENABLE_METRICS | "true" | 是否启用指标收集 |

## 监控指标

启动应用后，可以通过访问 `http://localhost:8000/metrics` 查看Prometheus指标：

- `translation_requests_total`：翻译请求数量
- `translation_duration_seconds`：翻译耗时分布
- `active_translations`：活跃翻译数量
- `api_errors_total`：API错误数量

## 项目结构

```
translate_agent/
├── translator_agent.py     # 核心Agent实现
├── config.py              # 配置管理
├── logger.py              # 日志模块
├── metrics.py             # 指标监控
├── web_app.py             # Web应用
├── utils.py               # 工具函数
├── prompt.md              # 系统提示词
├── test_json.md           # 测试数据
├── test_agent.py          # 单元测试
├── requirements.txt       # 依赖包
├── README.md              # 说明文档
├── ARCHITECTURE.md        # 架构设计文档
└── templates/
    └── index.html         # Web界面模板
```

## 开发指南

### 添加新的模型支持

1. 在 `translator_agent.py` 中的 `_call_model_api` 方法中添加新的条件分支
2. 实现对应的 `_call_{model_name}_api` 方法
3. 在 `web_app.py` 的模型选择下拉框中添加新选项

### 使用SGLang/VLLM

本项目现已支持SGLang和VLLM提供的兼容OpenAI API的接口。只需将 `OPENAI_API_BASE` 环境变量指向您的SGLang/VLLM服务地址即可：

```bash
export OPENAI_API_BASE="http://localhost:30000/v1/chat/completions"  # SGLang示例
export OPENAI_API_BASE="http://localhost:8000/v1/completions"        # VLLM示例
```

对于需要限制生成长度的场景，可以设置 `OPENAI_MAX_TOKENS` 环境变量：

```bash
export OPENAI_MAX_TOKENS=2048
```

### 使用curl直接调用API

您也可以使用curl命令直接调用翻译服务API：

```bash
# 使用JSON文件作为输入
curl -X POST http://localhost:5000/translate \
  -F "model_type=openai" \
  -F "file=@test_data/sample.json"

# 使用文本数据作为输入
curl -X POST http://localhost:5000/translate \
  -F "model_type=openai" \
  -F "text_input={\"segments\":[{\"text\":\"Bonjour, comment allez-vous?\",\"speaker\":\"SPEAKER1\"},{\"text\":\"Je vais bien, merci.\",\"speaker\":\"SPEAKER2\"}]}"

# 使用SGLang/VLLM服务
curl -X POST http://localhost:5000/translate \
  -F "model_type=openai" \
  -F "file=@test_data/sample.json" \
  -H "X-API-Key: your-sglang-vllm-api-key"  # 如果需要API密钥
```

注意：当使用SGLang或VLLM时，请确保已正确配置 `OPENAI_API_BASE` 环境变量指向相应的服务地址。

### 扩展功能

- 修改 `prompt.md` 来调整翻译规则
- 在 `utils.py` 中添加新的数据处理函数
- 在 `metrics.py` 中添加新的监控指标

## 许可证

MIT License

## 联系方式

如有问题，请提交Issue或联系项目维护者。