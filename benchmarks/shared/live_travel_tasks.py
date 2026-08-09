"""Shared real-API + LLM task functions for the live cross-framework benchmark.

Unlike benchmarks/shared/support_tasks.py, the tool/retriever calls here hit
real, live, free, no-auth-required APIs, so latency (and the underlying data)
is genuinely non-deterministic run to run and framework to framework -- this
is what makes it a meaningful latency comparison rather than a fixed-timing
fixture.
"""

import json
import os
import time
import urllib.request
from typing import Any

USE_REAL_OPENAI = bool(os.getenv("OPENAI_API_KEY"))
OPENAI_MODEL = "gpt-4o-mini"

USER_AGENT = "AgenticLens-Benchmark/1.0 (+https://github.com/DeepAgentLabs/agenticlens)"

TRIP = {"origin": "New York", "destination": "Tokyo", "purpose": "work trip"}

QUESTION = (
    "I'm flying from New York to Tokyo next week for a work trip. What should I know before I go?"
)


class FakeUsage:
    def __init__(self, prompt_tokens: int, completion_tokens: int):
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens


class FakeMessage:
    def __init__(self, content: str):
        self.content = content


class FakeChoice:
    def __init__(self, content: str):
        self.message = FakeMessage(content)


class FakeResponse:
    def __init__(self, content: str, prompt_tokens: int, completion_tokens: int):
        self.usage = FakeUsage(prompt_tokens, completion_tokens)
        self.choices = [FakeChoice(content)]


# Also used to normalize *real* per-framework LLM responses (CrewAI's
# CrewOutput.token_usage, AutoGen's RequestUsage, LlamaIndex's
# additional_kwargs, Semantic Kernel's metadata["usage"], LangChain's
# usage_metadata) into the single shape `StepHandle.record()` understands,
# so every framework's real call still flows through the same AgenticLens
# provider-detection path as the fallback.
LLMResponse = FakeResponse


def classify_trip(framework: str) -> tuple[FakeResponse, float]:
    start = time.time()
    response = FakeResponse(
        content=f"{framework}: intent=trip_briefing_request; destination={TRIP['destination']}",
        prompt_tokens=140,
        completion_tokens=28,
    )
    return response, time.time() - start


def synthesize_briefing(
    framework: str,
    place: dict[str, Any],
) -> tuple[FakeResponse, float]:
    start = time.time()
    response = FakeResponse(
        content=(
            f"[{framework}] Heads-up for your {place['name']} trip: pack for the current "
            "conditions, budget at today's live rate, and skim the destination facts below."
        ),
        prompt_tokens=460,
        completion_tokens=140,
    )
    return response, time.time() - start


def fetch_json(url: str) -> dict[str, Any]:
    """Real HTTP call -- no mocking, no API key required for any of these."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.load(resp)  # type: ignore[no-any-return]


def geocode_city(city: str) -> tuple[dict[str, Any], float]:
    start = time.time()
    data = fetch_json(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1")
    result = data["results"][0]
    place = {
        "name": result["name"],
        "country": result.get("country"),
        "lat": result["latitude"],
        "lon": result["longitude"],
    }
    return place, time.time() - start


def fetch_weather(lat: float, lon: float) -> tuple[dict[str, Any], float]:
    start = time.time()
    data = fetch_json(
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,weather_code,wind_speed_10m"
    )
    return data["current"], time.time() - start  # type: ignore[no-any-return]


def fetch_exchange_rate(base: str, target: str) -> tuple[dict[str, Any], float]:
    start = time.time()
    data = fetch_json(f"https://api.frankfurter.app/latest?from={base}&to={target}")
    fx = {"base": data["base"], "date": data["date"], "rate": data["rates"][target]}
    return fx, time.time() - start


def fetch_destination_summary(city: str) -> tuple[dict[str, Any], list[str], float]:
    start = time.time()
    data = fetch_json(f"https://en.wikipedia.org/api/rest_v1/page/summary/{city}")
    summary = {"title": data["title"], "extract": data["extract"]}
    paragraphs = [p.strip() for p in summary["extract"].split(". ") if p.strip()]
    return summary, paragraphs, time.time() - start


def estimate_avg_tokens_per_chunk(paragraphs: list[str]) -> int:
    if not paragraphs:
        return 0
    return round(sum(len(p) for p in paragraphs) / len(paragraphs) / 4)
