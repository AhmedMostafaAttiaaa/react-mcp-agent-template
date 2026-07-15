import argparse
import asyncio
import sys

from agent.config import load_config
from agent.core import Agent
from agent.providers.groq_provider import GroqProvider
from agent.providers.ollama_provider import OllamaProvider


def build_provider(config: dict):
    name = config["provider"]
    temperature = config.get("temperature", 0.2)
    if name == "ollama":
        return OllamaProvider({**config.get("ollama", {}), "temperature": temperature})
    if name == "groq":
        return GroqProvider({**config.get("groq", {}), "temperature": temperature})
    raise ValueError(f"Unknown provider '{name}' in config.yaml — expected 'ollama' or 'groq'.")


def main() -> None:
    # Windows consoles default to a legacy code page (e.g. cp1252) that can't
    # encode characters LLMs commonly produce (em dashes, curly quotes, ...).
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Run the ReAct MCP agent on a single question.")
    parser.add_argument("question", help="The question to ask the agent.")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    args = parser.parse_args()

    config = load_config(args.config)
    provider = build_provider(config)
    agent = Agent(config, provider)

    answer = asyncio.run(agent.run(args.question))
    print(answer)


if __name__ == "__main__":
    main()
