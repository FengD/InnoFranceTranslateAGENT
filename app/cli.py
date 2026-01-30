"""
CLI tool for Translation Agent.
"""
import argparse
import os
import sys
from pathlib import Path
from typing import Optional

from config import config
from logger import setup_logging, get_logger
from core.translator_agent import TranslationAgent
from core.utils import load_input_data, save_output_data
from core.backend.configs.llm_config import LLMConfig, LLMType
from core.backend.provider.llm_provider import add_llm_arguments, LLM_REGISTER


def _parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Translation Agent - French to Chinese colloquial translation"
    )
    parser.add_argument("--input", "-i", required=True, help="Input file path (JSON or TXT)")
    parser.add_argument("--output", "-o", help="Output file path (optional, defaults to stdout)")
    parser.add_argument(
        "--provider",
        "-p",
        default=config.get("DEFAULT_MODEL", "openai"),
        choices=["openai", "ollama", "qwen", "glm", "deepseek", "sglang", "vllm"],
        help="LLM provider to use",
    )
    parser.add_argument("--model-name", "-m", required=True, help="Specific model name to use")
    parser.add_argument(
        "--prompt-type",
        default="translate",
        choices=["translate", "summary", "check"],
        help="Prompt type to use (translate, summary, check)",
    )
    add_llm_arguments(parser)
    return parser.parse_args(argv)


def _setup_logger() -> None:
    setup_logging(config.get("LOG_LEVEL", "INFO"), config.get("LOG_FILE", "logs/translation_agent.log"))
    log_dir = os.path.dirname(config.get("LOG_FILE", "logs/translation_agent.log"))
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)


def _build_agent(args: argparse.Namespace) -> TranslationAgent:
    llm_type = LLMType(args.provider)
    llm_config = LLMConfig.from_args(args, llm_type)
    llm_config.model = args.model_name
    return TranslationAgent(
        config.get_all(),
        llm_config,
        LLM_REGISTER,
        prompt_type=args.prompt_type,
    )


def main(argv: Optional[list[str]] = None) -> int:
    args = _parse_args(argv)
    _setup_logger()
    logger = get_logger("translation_cli")

    try:
        input_data = load_input_data(args.input)
        agent = _build_agent(args)

        logger.info("translation.start", extra={"provider": args.provider, "model": agent.llm_config.model})
        result = agent.translate(input_data, args.provider)

        if args.output:
            save_output_data(result, args.output)
            output_path = Path(args.output).resolve()
            logger.info("translation.saved", extra={"output_path": str(output_path)})
            print(f"Translation result saved to {output_path}")
        else:
            print(result)

        logger.info("translation.success", extra={"provider": args.provider})
        return 0
    except Exception as exc:
        logger.error("translation.failed", extra={"error": str(exc)})
        print(f"Translation failed: {str(exc)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
