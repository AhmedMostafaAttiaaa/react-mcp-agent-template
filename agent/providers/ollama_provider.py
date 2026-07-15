import os
from typing import Optional

import ollama

from .base import GenerationResult, Provider


class OllamaProvider(Provider):
    """Fully local generation via a running Ollama server. No API key required."""

    def __init__(self, config: dict):
        self.host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        self.client = ollama.Client(host=self.host)
        self.model = config.get("model") or self._first_available_model()
        self.temperature = config.get("temperature")

    def _first_available_model(self) -> str:
        models = self.client.list()["models"]
        if not models:
            raise RuntimeError(
                f"No models found on Ollama host {self.host}. Pull one first, e.g. "
                "`ollama pull qwen3:4b`, or set `ollama.model` in config.yaml."
            )
        # Embedding-only models (e.g. nomic-embed-text) can't serve /api/generate,
        # so prefer a model that isn't one when auto-selecting.
        generation_models = [m["model"] for m in models if not self._is_embedding_model(m)]
        return (generation_models or [m["model"] for m in models])[0]

    @staticmethod
    def _is_embedding_model(model_info) -> bool:
        name = str(model_info.get("model", "")).lower()
        families = [str(f).lower() for f in (model_info.get("details") or {}).get("families") or []]
        return "embed" in name or any("bert" in f for f in families)

    def list_models(self) -> list:
        return [m["model"] for m in self.client.list()["models"]]

    def generate(self, prompt: str, stop: Optional[list] = None) -> GenerationResult:
        options = {}
        if self.temperature is not None:
            options["temperature"] = self.temperature
        if stop:
            options["stop"] = stop
        response = self.client.generate(model=self.model, prompt=prompt, options=options)
        return GenerationResult(text=response["response"], model=self.model)
