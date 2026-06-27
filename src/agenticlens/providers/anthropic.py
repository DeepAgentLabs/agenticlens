from typing import Any

from agenticlens.providers.base import BaseProvider, TokenUsage


class AnthropicProvider(BaseProvider):
    """Reads token usage from Anthropic SDK message response objects."""

    name = "anthropic"

    def supports(self, response: Any) -> bool:
        return hasattr(response, "usage") and hasattr(response.usage, "input_tokens")

    def extract_usage(self, response: Any) -> TokenUsage:
        usage = response.usage
        return TokenUsage(
            prompt_tokens=usage.input_tokens,
            completion_tokens=usage.output_tokens,
        )
