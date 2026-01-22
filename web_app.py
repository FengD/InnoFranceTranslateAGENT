from flask import Flask, request, render_template, jsonify, redirect, url_for
import json
import os
from translator_agent import TranslationAgent
from config import config
from logger import setup_logging, get_logger
from utils import load_input_data, validate_input_data

# 设置日志
setup_logging(config.get("LOG_LEVEL", "INFO"), config.get("LOG_FILE", "logs/web_app.log"))
logger = get_logger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 最大16MB文件

# 初始化翻译Agent
agent = TranslationAgent(config.get_all())

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate():
    """处理翻译请求"""
    try:
        # 获取模型类型
        model_type = request.form.get('model_type', config.get('DEFAULT_MODEL', 'openai'))
        
        # 获取输入数据
        input_data = None
        if 'file' in request.files and request.files['file'].filename != '':
            # 处理文件上传
            file = request.files['file']
            if file.filename.endswith('.json'):
                input_data = json.load(file)
            else:
                # 处理文本文件
                content = file.read().decode('utf-8')
                input_data = {"text": content}
        elif 'text_input' in request.form and request.form['text_input'].strip():
            # 处理直接文本输入
            text_input = request.form['text_input'].strip()
            try:
                # 尝试解析为JSON
                input_data = json.loads(text_input)
            except json.JSONDecodeError:
                # 作为纯文本处理
                input_data = {"text": text_input}
        else:
            return jsonify({"error": "请提供输入数据"}), 400
        
        # 验证输入数据
        if not validate_input_data(input_data):
            return jsonify({"error": "输入数据格式不正确"}), 400
        
        # 执行翻译
        result = agent.translate(input_data, model_type)
        
        return jsonify({
            "success": True,
            "result": result,
            "model_type": model_type
        })
        
    except Exception as e:
        logger.error(f"翻译过程中发生错误: {str(e)}")
        return jsonify({"error": f"翻译失败: {str(e)}"}), 500

@app.route('/health')
def health_check():
    """健康检查端点"""
    return jsonify({"status": "healthy"}), 200

@app.errorhandler(413)
def too_large(e):
    """文件过大错误处理"""
    return jsonify({"error": "文件大小超过限制（最大16MB）"}), 413

if __name__ == '__main__':
    # 创建日志目录
    log_dir = os.path.dirname(config.get("LOG_FILE", "logs/web_app.log"))
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 创建templates目录
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=config.get("DEBUG", False)
    )