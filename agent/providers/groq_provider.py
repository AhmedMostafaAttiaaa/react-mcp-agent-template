import os
from typing import Optional

from groq import Groq

from .base import GenerationResult, Provider


class GroqProvider(Provider):
    """Optional, generation-only, cloud provider. Requires GROQ_API_KEY in the environment.

    Only used when config.yaml sets `provider: groq`. If you stick with `provider: ollama`,
    this class is never instantiated and no network calls or API keys are needed.
    """

    def __init__(self, config: dict):
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Add it to .env, or switch config.yaml's `provider` "
                "back to `ollama` to run fully offline with zero API keys."
            )
        self.client = Groq(api_key=api_key)
        self.model = config.get("model") or "llama-3.1-8b-instant"
        self.temperature = config.get("temperature")

    def list_models(self) -> list:
        response = self.client.models.list()
        return [m.id for m in response.data]

    def generate(self, prompt: str, stop: Optional[list] = None) -> GenerationResult:
        kwargs = {}
        if self.temperature is not None:
            kwargs["temperature"] = self.temperature
        if stop:
            kwargs["stop"] = stop
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            **kwargs,
        )
        return GenerationResult(text=response.choices[0].message.content, model=self.model)
