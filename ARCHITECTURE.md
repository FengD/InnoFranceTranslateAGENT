# 翻译Agent架构设计

## 概述
翻译Agent是一个能够处理多说话人法语转中文翻译的智能体，支持多种大语言模型API，并提供完整的监控和日志功能。

## 核心组件

### 1. Agent核心模块 (`translator_agent.py`)
- 支持多种大模型API调用
- 处理输入数据解析
- 应用翻译规则和后处理

### 2. 配置管理模块 (`config.py`)
- 管理各种API密钥和配置参数
- 支持环境变量和配置文件

### 3. 日志模块 (`logger.py`)
- 结构化日志记录
- 支持不同级别日志输出

### 4. 指标监控模块 (`metrics.py`)
- Prometheus指标收集
- 性能监控和统计

### 5. Web应用模块 (`web_app.py`)
- FastAPI Web界面
- 文件上传和结果展示

### 6. 工具模块 (`utils.py`)
- 数据处理辅助函数
- 格式转换工具

## 目录结构
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

## API支持列表
1. Ollama API
2. OpenAI API
3. DeepSeek API
4. Qwen API
5. GLM API

## 功能流程
1. 用户通过Web界面或直接调用上传JSON/TXT文件
2. Agent解析输入数据
3. 根据配置选择合适的API
4. 构造Prompt并调用API
5. 处理返回结果并按规则后处理
6. 返回最终翻译结果
7. 记录日志和指标