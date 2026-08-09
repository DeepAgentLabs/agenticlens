import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from agenticlens import profile, step  # noqa: E402
from benchmarks.shared.live_travel_tasks import (  # noqa: E402
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

if USE_REAL_OPENAI:
    from openai import OpenAI

    client = OpenAI()


def classify_trip_native(framework: str) -> tuple[LLMResponse, float]:
    """Raw OpenAI SDK call -- the "control" with no framework prompt wrapping."""
    if not USE_REAL_OPENAI:
        return classify_trip(framework)

    start = time.time()
    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "user",
                "content": f"Classify this trip request in one short line:\n{QUESTION}",
            }
        ],
        max_tokens=30,
    )
    content = resp.choices[0].message.content
    return LLMResponse(content, resp.usage.prompt_tokens, resp.usage.completion_tokens), (
        time.time() - start
    )


def synthesize_briefing_native(
    framework: str, place: dict, weather: dict, fx: dict, summary: dict
) -> tuple[LLMResponse, float]:
    if not USE_REAL_OPENAI:
        return synthesize_briefing(framework, place)

    start = time.time()
    prompt = (
        f"Traveler question: {QUESTION}\n\n"
        f"Live weather at {place['name']}: {weather}\n"
        f"Live USD->JPY rate: {fx['rate']} (as of {fx['date']})\n"
        f"Destination facts: {summary['extract']}\n\n"
        "Write a concise, friendly travel briefing (3-4 sentences) using only this data."
    )
    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=180,
    )
    content = resp.choices[0].message.content
    return LLMResponse(content, resp.usage.prompt_tokens, resp.usage.completion_tokens), (
        time.time() - start
    )


def main() -> None:
    framework = "Native Python"

    with profile(f"Benchmark - {framework} - Live Travel Briefing"):
        with step(
            f"{framework} - Classify Trip Request",
            type="planner",
            provider="openai",
            model=OPENAI_MODEL,
            prompt=QUESTION,
            framework="native_python",
        ) as s:
            response, latency = classify_trip_native(framework)
            s.record(response)
            s.step.metrics.latency = latency

        with step(
            f"{framework} - Geocode Destination",
            type="tool_call",
            tool_name="open_meteo_geocoding",
            tool_args={"city": TRIP["destination"]},
            framework="native_python",
        ) as s:
            place, latency = geocode_city(TRIP["destination"])
            s.step.metrics.latency = latency
            s.step.metadata["tool_result"] = place

        with step(
            f"{framework} - Fetch Live Weather",
            type="tool_call",
            tool_name="open_meteo_forecast",
            tool_args={"lat": place["lat"], "lon": place["lon"]},
            framework="native_python",
        ) as s:
            weather, latency = fetch_weather(place["lat"], place["lon"])
            s.step.metrics.latency = latency
            s.step.metadata["tool_result"] = weather

        with step(
            f"{framework} - Fetch Live Exchange Rate",
            type="tool_call",
            tool_name="frankfurter_exchange_rate",
            tool_args={"base": "USD", "target": "JPY"},
            framework="native_python",
        ) as s:
            fx, latency = fetch_exchange_rate("USD", "JPY")
            s.step.metrics.latency = latency
            s.step.metadata["tool_result"] = fx

        with step(
            f"{framework} - Retrieve Destination Facts",
            type="retriever",
            query=TRIP["destination"],
            framework="native_python",
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
            framework="native_python",
        ) as s:
            response, latency = synthesize_briefing_native(framework, place, weather, fx, summary)
            s.record(response)
            s.step.metrics.latency = latency

    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
