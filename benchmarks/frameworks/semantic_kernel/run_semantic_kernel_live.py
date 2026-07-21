import asyncio
import time

from agenticlens import profile, step
from benchmarks.shared.live_travel_tasks import (
    OPENAI_MODEL,
    QUESTION,
    TRIP,
    USE_REAL_OPENAI,
    LLMResponse,
    classify_trip,
    estimate_avg_tokens_per_chunk,
    fetch_destination_summary,
    fetch_exchange_rate,
    fetch_weather,
    geocode_city,
    synthesize_briefing,
)


async def _get_completion(service, prompt: str) -> tuple[str, int, int]:
    from semantic_kernel.contents import ChatHistory

    history = ChatHistory()
    history.add_user_message(prompt)
    settings = service.get_prompt_execution_settings_class()()
    result = await service.get_chat_message_content(chat_history=history, settings=settings)
    usage = result.metadata.get("usage")
    prompt_tokens = usage.prompt_tokens if usage else 0
    completion_tokens = usage.completion_tokens if usage else 0
    return str(result), prompt_tokens, completion_tokens


def classify_trip_native(service) -> tuple[LLMResponse, float]:
    """Real call runs through Semantic Kernel's chat completion service --
    its own ChatHistory/settings wrapper, not a raw OpenAI SDK call."""
    if not USE_REAL_OPENAI:
        return classify_trip("Semantic Kernel")

    start = time.time()
    content, prompt_tokens, completion_tokens = asyncio.run(
        _get_completion(service, f"Classify this trip request in one short line:\n{QUESTION}")
    )
    return LLMResponse(content, prompt_tokens, completion_tokens), (time.time() - start)


def synthesize_briefing_native(
    service, place: dict, weather: dict, fx: dict, summary: dict
) -> tuple[LLMResponse, float]:
    if not USE_REAL_OPENAI:
        return synthesize_briefing("Semantic Kernel", place)

    start = time.time()
    prompt = (
        f"Traveler question: {QUESTION}\n\n"
        f"Live weather at {place['name']}: {weather}\n"
        f"Live USD->JPY rate: {fx['rate']} (as of {fx['date']})\n"
        f"Destination facts: {summary['extract']}\n\n"
        "Write a concise, friendly travel briefing (3-4 sentences) using only this data."
    )
    content, prompt_tokens, completion_tokens = asyncio.run(_get_completion(service, prompt))
    return LLMResponse(content, prompt_tokens, completion_tokens), (time.time() - start)


def main() -> None:
    framework = "Semantic Kernel"

    try:
        import semantic_kernel as sk
    except ImportError as exc:
        raise RuntimeError(
            "Semantic Kernel is not installed. Run: pip install semantic-kernel"
        ) from exc

    # Framework-specific kernel object.
    # This confirms the implementation is using the Semantic Kernel runtime surface.
    kernel = sk.Kernel()
    service = None
    if USE_REAL_OPENAI:
        from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

        service = OpenAIChatCompletion(ai_model_id=OPENAI_MODEL, service_id="chat")
        kernel.add_service(service)

    with profile(f"Benchmark - {framework} - Live Travel Briefing"):
        with step(
            f"{framework} - Classify Trip Request",
            type="planner",
            provider="openai",
            model=OPENAI_MODEL,
            prompt=QUESTION,
            framework="semantic_kernel",
            kernel_type=type(kernel).__name__,
        ) as s:
            response, latency = classify_trip_native(service)
            s.record(response)
            s.step.metrics.latency = latency

        with step(
            f"{framework} - Geocode Destination",
            type="tool_call",
            tool_name="open_meteo_geocoding",
            tool_args={"city": TRIP["destination"]},
            framework="semantic_kernel",
        ) as s:
            place, latency = geocode_city(TRIP["destination"])
            s.step.metrics.latency = latency
            s.step.metadata["tool_result"] = place

        with step(
            f"{framework} - Fetch Live Weather",
            type="tool_call",
            tool_name="open_meteo_forecast",
            tool_args={"lat": place["lat"], "lon": place["lon"]},
            framework="semantic_kernel",
        ) as s:
            weather, latency = fetch_weather(place["lat"], place["lon"])
            s.step.metrics.latency = latency
            s.step.metadata["tool_result"] = weather

        with step(
            f"{framework} - Fetch Live Exchange Rate",
            type="tool_call",
            tool_name="frankfurter_exchange_rate",
            tool_args={"base": "USD", "target": "JPY"},
            framework="semantic_kernel",
        ) as s:
            fx, latency = fetch_exchange_rate("USD", "JPY")
            s.step.metrics.latency = latency
            s.step.metadata["tool_result"] = fx

        with step(
            f"{framework} - Retrieve Destination Facts",
            type="retriever",
            query=TRIP["destination"],
            framework="semantic_kernel",
        ) as s:
            summary, paragraphs, latency = fetch_destination_summary(TRIP["destination"])
            s.step.metrics.latency = latency
            s.step.metadata["chunk_count"] = len(paragraphs)
            s.step.metadata["avg_tokens_per_chunk"] = estimate_avg_tokens_per_chunk(paragraphs)
            s.step.metadata["retrieved_doc_ids"] = [summary["title"]]

        with step(
            f"{framework} - Synthesize Travel Briefing",
            type="final_response",
            provider="openai",
            model=OPENAI_MODEL,
            prompt=QUESTION,
            framework="semantic_kernel",
        ) as s:
            response, latency = synthesize_briefing_native(service, place, weather, fx, summary)
            s.record(response)
            s.step.metrics.latency = latency

    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
