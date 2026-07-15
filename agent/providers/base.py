from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class GenerationResult:
    text: str
    model: str


class Provider(ABC):
    """Shared interface every generation provider (ollama, groq, ...) must implement."""

    @abstractmethod
    def generate(self, prompt: str, stop: Optional[list] = None) -> GenerationResult:
        ...

    @abstractmethod
    def list_models(self) -> list:
        ...
