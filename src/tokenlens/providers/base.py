from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class TokenUsage(BaseModel):
    """Normalized token usage extracted from a provider response."""

    prompt_tokens: int
    completion_tokens: int


class BaseProvider(ABC):
    """Abstract interface for extracting token usage from a provider's response object.

    New providers (Gemini, Ollama, vLLM, LiteLLM, ...) implement this interface
    without requiring changes to the profiler or any other provider.
    """

    name: str

    @abstractmethod
    def extract_usage(self, response: Any) -> TokenUsage:
        """Extract prompt/completion token counts from a raw provider response."""
        raise NotImplementedError

    @abstractmethod
    def supports(self, response: Any) -> bool:
        """Return True if this provider knows how to read `response`."""
        raise NotImplementedError
