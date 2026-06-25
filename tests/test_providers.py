from tokenlens.providers import AnthropicProvider, OpenAIProvider, detect_provider, get_provider


class FakeOpenAIUsage:
    prompt_tokens = 100
    completion_tokens = 20


class FakeOpenAIResponse:
    usage = FakeOpenAIUsage()


class FakeAnthropicUsage:
    input_tokens = 80
    output_tokens = 15


class FakeAnthropicResponse:
    usage = FakeAnthropicUsage()


def test_openai_provider_extracts_usage() -> None:
    provider = OpenAIProvider()
    usage = provider.extract_usage(FakeOpenAIResponse())
    assert usage.prompt_tokens == 100
    assert usage.completion_tokens == 20


def test_anthropic_provider_extracts_usage() -> None:
    provider = AnthropicProvider()
    usage = provider.extract_usage(FakeAnthropicResponse())
    assert usage.prompt_tokens == 80
    assert usage.completion_tokens == 15


def test_detect_provider_picks_correct_provider() -> None:
    assert isinstance(detect_provider(FakeOpenAIResponse()), OpenAIProvider)
    assert isinstance(detect_provider(FakeAnthropicResponse()), AnthropicProvider)
    assert detect_provider(object()) is None


def test_get_provider_unknown_raises() -> None:
    import pytest

    with pytest.raises(ValueError, match="Unknown provider"):
        get_provider("does-not-exist")
