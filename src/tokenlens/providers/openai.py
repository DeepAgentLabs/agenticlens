from typing import Any

from tokenlens.providers.base import BaseProvider, TokenUsage


class OpenAIProvider(BaseProvider):
    """Reads token usage from OpenAI SDK chat/completion response objects."""

    name = "openai"

    def supports(self, response: Any) -> bool:
        return hasattr(response, "usage") and hasattr(response.usage, "prompt_tokens")

    def extract_usage(self, response: Any) -> TokenUsage:
        usage = response.usage
        return TokenUsage(
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
        )
