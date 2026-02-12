"""
MCP server for Translation Agent.
"""
import argparse
import json
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

from config import config
from logger import setup_logging, get_logger
from core.translator_agent import TranslationAgent
from core.utils import load_input_data, save_output_data, validate_input_data
from core.backend.configs.llm_config import LLMConfig, LLMType
from core.backend.provider.llm_provider import LLM_REGISTER


setup_logging(config.get("LOG_LEVEL", "INFO"), config.get("LOG_FILE", "logs/translation_agent.log"))
logger = get_logger("translation_mcp")


def _build_agent(
    provider: str,
    model_name: str,
    prompt_type: str,
    api_key: Optional[str] = None,
) -> TranslationAgent:
    llm_type = LLMType(provider)
    llm_config = LLMConfig.from_args(type("Args", (), config.get_all())(), llm_type)
    llm_config.model = model_name
    if api_key:
        llm_config.api_key = api_key
    return TranslationAgent(
        config.get_all(),
        llm_config,
        LLM_REGISTER,
        prompt_type=prompt_type,
    )


def _parse_json_payload(payload: str) -> dict:
    data = json.loads(payload)
    if not validate_input_data(data):
        raise ValueError("Input data format is incorrect")
    return data


def create_mcp(host: str, port: int) -> FastMCP:
    mcp = FastMCP("Translation Agent", json_response=True, host=host, port=port)

    @mcp.tool()
    def translate_text(
        text: str,
        model_name: str,
        provider: str = "openai",
        prompt_type: str = "translate",
        api_key: Optional[str] = None,
    ) -> dict:
        """
        Translate plain text.

        Args:
            text: Plain French text to translate
            provider: LLM provider (default: openai)
            model_name: Model name (required)
            prompt_type: Prompt type (translate, summary, check, polish)

        Returns:
            Dictionary with 'success', 'result', and optional 'error' keys
        """
        try:
            if not model_name.strip():
                raise ValueError("model_name is required")
            agent = _build_agent(provider, model_name, prompt_type, api_key=api_key)
            result = agent.translate({"text": text}, provider)
            return {"success": True, "result": result}
        except Exception as exc:
            logger.error("translation.failed", extra={"error": str(exc)})
            return {"success": False, "error": f"Translation failed: {str(exc)}"}

    @mcp.tool()
    def translate_json(
        input_json: str,
        model_name: str,
        provider: str = "openai",
        prompt_type: str = "translate",
        api_key: Optional[str] = None,
    ) -> dict:
        """
        Translate JSON input with segments or text.

        Args:
            input_json: JSON string with segments or { "text": "..." }
            provider: LLM provider (default: openai)
            model_name: Model name (required)
            prompt_type: Prompt type (translate, summary, check, polish)

        Returns:
            Dictionary with 'success', 'result', and optional 'error' keys
        """
        try:
            input_data = _parse_json_payload(input_json)
            if not model_name.strip():
                raise ValueError("model_name is required")
            agent = _build_agent(provider, model_name, prompt_type, api_key=api_key)
            result = agent.translate(input_data, provider)
            return {"success": True, "result": result}
        except Exception as exc:
            logger.error("translation.failed", extra={"error": str(exc)})
            return {"success": False, "error": f"Translation failed: {str(exc)}"}

    @mcp.tool()
    def translate_from_file(
        input_path: str,
        model_name: str,
        provider: str = "openai",
        prompt_type: str = "translate",
        api_key: Optional[str] = None,
    ) -> dict:
        """
        Translate data from a JSON or text file.

        Args:
            input_path: Path to the input file
            provider: LLM provider (default: openai)
            model_name: Model name (required)
            prompt_type: Prompt type (translate, summary, check, polish)

        Returns:
            Dictionary with 'success', 'result', and optional 'error' keys
        """
        try:
            data = load_input_data(input_path)
            if not validate_input_data(data):
                raise ValueError("Input data format is incorrect")
            if not model_name.strip():
                raise ValueError("model_name is required")
            agent = _build_agent(provider, model_name, prompt_type, api_key=api_key)
            result = agent.translate(data, provider)
            return {"success": True, "result": result}
        except Exception as exc:
            logger.error("translation.failed", extra={"error": str(exc)})
            return {"success": False, "error": f"Translation failed: {str(exc)}"}

    @mcp.tool()
    def translate_and_save(
        input_path: str,
        output_path: str,
        model_name: str,
        provider: str = "openai",
        prompt_type: str = "translate",
        api_key: Optional[str] = None,
    ) -> dict:
        """
        Translate an input file and save the result.

        Args:
            input_path: Path to the input file
            output_path: Path to save the translation
            provider: LLM provider (default: openai)
            model_name: Model name (required)
            prompt_type: Prompt type (translate, summary, check, polish)

        Returns:
            Dictionary with 'success', 'output_path', and optional 'error' keys
        """
        try:
            data = load_input_data(input_path)
            if not validate_input_data(data):
                raise ValueError("Input data format is incorrect")
            if not model_name.strip():
                raise ValueError("model_name is required")
            agent = _build_agent(provider, model_name, prompt_type, api_key=api_key)
            result = agent.translate(data, provider)
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            save_output_data(result, str(output_file))
            return {"success": True, "output_path": str(output_file)}
        except Exception as exc:
            logger.error("translation.failed", extra={"error": str(exc)})
            return {"success": False, "error": f"Translation failed: {str(exc)}"}

    return mcp


def _parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Translation Agent MCP server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="MCP transport to use (default: stdio)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Bind host for SSE transport (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Bind port for SSE transport (default: 8000)",
    )
    return parser.parse_args(argv)


def run_server(transport: str, host: str, port: int) -> None:
    mcp = create_mcp(host=host, port=port)
    if transport == "stdio":
        mcp.run()
        return
    if transport == "sse":
        mcp.run(transport="sse")
        return
    raise ValueError(f"Unsupported transport: {transport}")


def main(argv: Optional[list[str]] = None) -> None:
    args = _parse_args(argv)
    run_server(args.transport, args.host, args.port)


if __name__ == "__main__":
    main()
