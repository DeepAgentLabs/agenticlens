from tokenlens.providers.anthropic import AnthropicProvider
from tokenlens.providers.base import BaseProvider
from tokenlens.providers.openai import OpenAIProvider

_PROVIDERS: dict[str, BaseProvider] = {
    "openai": OpenAIProvider(),
    "anthropic": AnthropicProvider(),
}


def get_provider(name: str) -> BaseProvider:
    try:
        return _PROVIDERS[name]
    except KeyError as exc:
        known = ", ".join(sorted(_PROVIDERS))
        raise ValueError(f"Unknown provider '{name}'. Known providers: {known}") from exc


def detect_provider(response: object) -> BaseProvider | None:
    """Best-effort detection of which provider produced `response`."""
    for provider in _PROVIDERS.values():
        if provider.supports(response):
            return provider
    return None
