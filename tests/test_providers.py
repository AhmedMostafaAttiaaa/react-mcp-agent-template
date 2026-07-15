import types

import pytest

from agent.providers.base import GenerationResult, Provider
from agent.providers.groq_provider import GroqProvider
from agent.providers.ollama_provider import OllamaProvider


class DummyOllamaClient:
    def __init__(self, host=None):
        self.host = host

    def list(self):
        return {"models": [{"model": "qwen3:4b"}, {"model": "llama3:latest"}]}

    def generate(self, model, prompt, options=None):
        return {"response": f"Final Answer: ok ({model})"}


class DummyGroqModels:
    def list(self):
        data = [
            types.SimpleNamespace(id="llama-3.1-8b-instant"),
            types.SimpleNamespace(id="llama-3.1-70b-versatile"),
        ]
        return types.SimpleNamespace(data=data)


class DummyGroqCompletions:
    def create(self, model, messages, **kwargs):
        message = types.SimpleNamespace(content=f"Final Answer: ok ({model})")
        choice = types.SimpleNamespace(message=message)
        return types.SimpleNamespace(choices=[choice])


class DummyGroqChat:
    def __init__(self):
        self.completions = DummyGroqCompletions()


class DummyGroqClient:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.models = DummyGroqModels()
        self.chat = DummyGroqChat()


@pytest.fixture
def ollama_provider(monkeypatch):
    monkeypatch.setattr("agent.providers.ollama_provider.ollama.Client", DummyOllamaClient)
    return OllamaProvider({"model": "qwen3:4b"})


@pytest.fixture
def groq_provider(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setattr("agent.providers.groq_provider.Groq", DummyGroqClient)
    return GroqProvider({"model": "llama-3.1-8b-instant"})


def test_ollama_provider_implements_interface(ollama_provider):
    assert isinstance(ollama_provider, Provider)


def test_groq_provider_implements_interface(groq_provider):
    assert isinstance(groq_provider, Provider)


def test_ollama_list_models(ollama_provider):
    assert ollama_provider.list_models() == ["qwen3:4b", "llama3:latest"]


def test_groq_list_models(groq_provider):
    assert groq_provider.list_models() == ["llama-3.1-8b-instant", "llama-3.1-70b-versatile"]


def test_ollama_generate_returns_generation_result(ollama_provider):
    result = ollama_provider.generate("hello", stop=["Observation:"])
    assert isinstance(result, GenerationResult)
    assert "Final Answer" in result.text
    assert result.model == "qwen3:4b"


def test_groq_generate_returns_generation_result(groq_provider):
    result = groq_provider.generate("hello", stop=["Observation:"])
    assert isinstance(result, GenerationResult)
    assert "Final Answer" in result.text
    assert result.model == "llama-3.1-8b-instant"


def test_ollama_auto_selects_first_model_when_unset(monkeypatch):
    monkeypatch.setattr("agent.providers.ollama_provider.ollama.Client", DummyOllamaClient)
    provider = OllamaProvider({"model": None})
    assert provider.model == "qwen3:4b"


def test_groq_provider_requires_api_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setattr("agent.providers.groq_provider.Groq", DummyGroqClient)
    with pytest.raises(RuntimeError):
        GroqProvider({"model": "llama-3.1-8b-instant"})
