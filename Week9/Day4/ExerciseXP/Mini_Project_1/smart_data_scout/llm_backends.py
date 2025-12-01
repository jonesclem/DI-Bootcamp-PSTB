# smart_data_scout/llm_backends.py
import os
from abc import ABC, abstractmethod
from typing import List, Dict

import requests
from groq import Groq  # Groq official SDK :contentReference[oaicite:4]{index=4}

from .config import LLMConfig

Message = Dict[str, str]  # {"role": "...", "content": "..."}


class LLMBackend(ABC):
    @abstractmethod
    def chat(self, messages: List[Message]) -> str:  # pragma: no cover - interface
        ...


class GroqBackend(LLMBackend):
    def __init__(self, cfg: LLMConfig) -> None:
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is required when LLM_BACKEND=groq")
        self.client = Groq(api_key=api_key)
        self.model = cfg.model

    def chat(self, messages: List[Message]) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )
        return resp.choices[0].message.content  # type: ignore[return-value]


class OllamaBackend(LLMBackend):
    """
    Talks to Ollama's OpenAI-compatible /v1/chat/completions endpoint.
    """

    def __init__(self, cfg: LLMConfig) -> None:
        self.model = cfg.model
        self.api_base = cfg.api_base or "http://localhost:11434/v1"

    def chat(self, messages: List[Message]) -> str:
        url = f"{self.api_base.rstrip('/')}/chat/completions"
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }
        resp = requests.post(url, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


def create_llm_backend(cfg: LLMConfig) -> LLMBackend:
    if cfg.backend == "groq":
        return GroqBackend(cfg)
    if cfg.backend == "ollama":
        return OllamaBackend(cfg)
    raise ValueError(f"Unknown backend: {cfg.backend}")