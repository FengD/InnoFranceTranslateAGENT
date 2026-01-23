from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import json
import os
from translator_agent import TranslationAgent
from config import config
from logger import setup_logging, get_logger
from utils import load_input_data, validate_input_data
from backend.configs.llm_config import LLMConfig, LLMType
from backend.provider.llm_provider import LLM_REGISTER
import uvicorn

# Setup logging
setup_logging(config.get("LOG_LEVEL", "INFO"), config.get("LOG_FILE", "logs/web_app.log"))
logger = get_logger(__name__)

app = FastAPI(title="Translation Agent API", version="1.0.0")
templates = Jinja2Templates(directory="templates")

# Initialize translation agent
# Use default configuration, will be updated per request
llm_config = LLMConfig()
agent = TranslationAgent(config.get_all(), llm_config, LLM_REGISTER)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Homepage"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/translate")
async def translate(
    request: Request,
    model_type: str = Form(default=config.get('DEFAULT_MODEL', 'openai')),
    file: UploadFile = File(None),
    text_input: str = Form(None)
):
    """Handle translation requests"""
    try:
        # Get input data
        input_data = None
        if file and file.filename != '':
            # Handle file upload
            content = await file.read()
            if file.filename.endswith('.json'):
                input_data = json.loads(content.decode('utf-8'))
            else:
                # Handle text files
                input_data = {"text": content.decode('utf-8')}
        elif text_input and text_input.strip():
            # Handle direct text input
            try:
                # Try to parse as JSON
                input_data = json.loads(text_input.strip())
            except json.JSONDecodeError:
                # Handle as plain text
                input_data = {"text": text_input.strip()}
        else:
            return JSONResponse(content={"error": "Please provide input data"}, status_code=400)
        
        # Validate input data
        if not validate_input_data(input_data):
            return JSONResponse(content={"error": "Input data format is incorrect"}, status_code=400)
        
        # Create LLM configuration based on model type and request
        llm_type = LLMType(model_type)
        # Create a new agent instance with proper configuration for this request
        request_llm_config = LLMConfig.from_args(type('Args', (), config.get_all())(), llm_type)
        request_agent = TranslationAgent(config.get_all(), request_llm_config, LLM_REGISTER)
        
        # Execute translation
        result = request_agent.translate(input_data, model_type)
        
        return JSONResponse(content={
            "success": True,
            "result": result,
            "model_type": model_type
        })
        
    except Exception as e:
        logger.error(f"Error occurred during translation: {str(e)}")
        return JSONResponse(content={"error": f"Translation failed: {str(e)}"}, status_code=500)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(content={"status": "healthy"}, status_code=200)

@app.exception_handler(413)
async def too_large(request: Request, exc: Exception):
    """File too large error handler"""
    return JSONResponse(content={"error": "File size exceeds limit (maximum 16MB)"}, status_code=413)

if __name__ == '__main__':
    # Create log directory
    log_dir = os.path.dirname(config.get("LOG_FILE", "logs/web_app.log"))
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create templates directory
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Run the application
    uvicorn.run(
        "web_app:app",
        host='0.0.0.0',
        port=5000,
        reload=config.get("DEBUG", False)
    )