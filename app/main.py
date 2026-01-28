import json
import os
import time
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from config import config
from logger import setup_logging, get_logger
from core.translator_agent import TranslationAgent
from core.utils import validate_input_data
from core.backend.configs.llm_config import LLMConfig, LLMType
from core.backend.provider.llm_provider import LLM_REGISTER


APP_DIR = Path(__file__).resolve().parent
BASE_DIR = APP_DIR.parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

setup_logging(config.get("LOG_LEVEL", "INFO"), os.getenv("WEB_LOG_FILE", "logs/web_app.log"))
logger = get_logger("translation_api")

app = FastAPI(title="Translation Agent API", version="1.0.0")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def _build_agent(provider: str, model_name: Optional[str], prompt_type: str) -> TranslationAgent:
    llm_type = LLMType(provider)
    llm_config = LLMConfig.from_args(type("Args", (), config.get_all())(), llm_type)
    if model_name:
        llm_config.model = model_name
    return TranslationAgent(
        config.get_all(),
        llm_config,
        LLM_REGISTER,
        prompt_type=prompt_type,
    )


async def _parse_input(file: UploadFile | None, text_input: Optional[str]) -> dict:
    if file and file.filename:
        content = await file.read()
        if file.filename.lower().endswith(".json"):
            try:
                return json.loads(content.decode("utf-8"))
            except json.JSONDecodeError as exc:
                raise HTTPException(status_code=400, detail="Invalid JSON file") from exc
        return {"text": content.decode("utf-8")}

    if text_input and text_input.strip():
        payload = text_input.strip()
        try:
            return json.loads(payload)
        except json.JSONDecodeError:
            return {"text": payload}

    raise HTTPException(status_code=400, detail="Please provide input data")


@app.middleware("http")
async def request_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or uuid.uuid4().hex
    request.state.request_id = request_id
    start = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception as exc:
        duration_ms = int((time.perf_counter() - start) * 1000)
        logger.exception(
            "request.error",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "duration_ms": duration_ms,
                "error": str(exc),
            },
        )
        raise

    duration_ms = int((time.perf_counter() - start) * 1000)
    logger.info(
        "request.end",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "duration_ms": duration_ms,
            "status_code": response.status_code,
        },
    )
    response.headers["X-Request-Id"] = request_id
    return response


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/translate")
async def translate(
    request: Request,
    provider: str = Form(default=config.get("DEFAULT_MODEL", "openai")),
    model_name: str = Form(default=None),
    prompt_type: str = Form(default="translate"),
    file: UploadFile = File(None),
    text_input: str = Form(None),
):
    try:
        input_data = await _parse_input(file, text_input)
        if not validate_input_data(input_data):
            raise HTTPException(status_code=400, detail="Input data format is incorrect")

        request_agent = _build_agent(provider, model_name, prompt_type)
        result = request_agent.translate(input_data, provider)

        return JSONResponse(
            content={
                "success": True,
                "result": result,
                "provider": provider,
                "model_name": model_name or request_agent.llm_config.model,
                "prompt_type": prompt_type,
            }
        )
    except ValueError as exc:
        logger.warning("translation.validation_error", extra={"error": str(exc)})
        raise HTTPException(status_code=400, detail=str(exc))
    except HTTPException as exc:
        logger.warning("translation.bad_request", extra={"error": exc.detail})
        raise
    except Exception as exc:
        logger.exception("translation.failed", extra={"error": str(exc)})
        return JSONResponse(content={"error": f"Translation failed: {str(exc)}"}, status_code=500)


@app.get("/api/health")
async def health_check(request: Request):
    return JSONResponse(
        content={"status": "healthy", "request_id": getattr(request.state, "request_id", None)},
        status_code=200,
    )


@app.exception_handler(413)
async def too_large(request: Request, exc: Exception):
    return JSONResponse(content={"error": "File size exceeds limit (maximum 16MB)"}, status_code=413)
