"""Live multi-agent demo: real external APIs, profiled end-to-end with AgenticLens.

Unlike the other examples, every tool/retriever step here makes a real network
call to a live, free, no-auth-required API:

- Open-Meteo Geocoding  -- resolve a city name to coordinates
- Open-Meteo Forecast   -- current weather at those coordinates
- Frankfurter           -- live currency exchange rate
- Wikipedia REST API    -- destination summary, used as retrieved context

LLM steps use a real OpenAI call when OPENAI_API_KEY is set, and a
deterministic fallback otherwise -- the same pattern as
examples/support_copilot.py. The point is to profile a workflow where latency
and step behavior are genuinely variable (live network calls), not scripted.
"""

import json
import os
import time
import urllib.request
from typing import Any

from agenticlens import profile, step
from agenticlens.recommenders import RecommendationEngine

USE_REAL_OPENAI = bool(os.getenv("OPENAI_API_KEY"))
USER_AGENT = "AgenticLens-Demo/1.0 (+https://github.com/DeepAgentLabs/agenticlens)"

if USE_REAL_OPENAI:
    from openai import OpenAI

    client = OpenAI()


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


def fake_llm(task: str) -> FakeResponse:
    if task == "classify":
        return FakeResponse(
            content="intent: trip_briefing_request; origin=New York; destination=Tokyo",
            prompt_tokens=140,
            completion_tokens=28,
        )
    return FakeResponse(
        content=(
            "Heads-up for your Tokyo trip: pack for the current conditions, budget in "
            "JPY at today's live rate, and skim the destination facts below before you go."
        ),
        prompt_tokens=460,
        completion_tokens=140,
    )


def call_llm(task: str, prompt: str) -> Any:
    if not USE_REAL_OPENAI:
        return fake_llm(task)

    return client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )


def fetch_json(url: str) -> dict[str, Any]:
    """Real HTTP call -- no mocking, no API key required for any of these."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.load(resp)  # type: ignore[no-any-return]


def geocode_city(city: str) -> dict[str, Any]:
    data = fetch_json(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1")
    result = data["results"][0]
    return {
        "name": result["name"],
        "country": result.get("country"),
        "lat": result["latitude"],
        "lon": result["longitude"],
    }


def fetch_weather(lat: float, lon: float) -> dict[str, Any]:
    data = fetch_json(
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,weather_code,wind_speed_10m"
    )
    return data["current"]  # type: ignore[no-any-return]


def fetch_exchange_rate(base: str, target: str) -> dict[str, Any]:
    data = fetch_json(f"https://api.frankfurter.app/latest?from={base}&to={target}")
    return {"base": data["base"], "date": data["date"], "rate": data["rates"][target]}


def fetch_destination_summary(city: str) -> dict[str, Any]:
    data = fetch_json(f"https://en.wikipedia.org/api/rest_v1/page/summary/{city}")
    return {"title": data["title"], "extract": data["extract"]}


def main() -> None:
    trip = {"traveler_id": "TRV-4471", "origin": "New York", "destination": "Tokyo"}
    question = (
        "I'm flying from New York to Tokyo next week for a work trip. "
        "What should I know before I go?"
    )

    with profile("Live Travel Briefing - Multi-Agent") as workflow:
        with step(
            "Planner - Classify Trip Request",
            type="planner",
            provider="openai" if USE_REAL_OPENAI else None,
            model="gpt-4o-mini" if USE_REAL_OPENAI else None,
            prompt=question,
            traveler_id=trip["traveler_id"],
        ) as s:
            start = time.time()
            resp = call_llm("classify", f"Classify this trip request:\n{question}")
            s.record(resp)
            s.step.metrics.latency = time.time() - start
            intent = resp.choices[0].message.content

        with step(
            "Geocode Destination",
            type="tool_call",
            tool_name="open_meteo_geocoding",
            tool_args={"city": trip["destination"]},
        ) as s:
            start = time.time()
            place = geocode_city(trip["destination"])
            s.step.metrics.latency = time.time() - start
            s.step.metadata["tool_result"] = place

        with step(
            "Fetch Live Weather",
            type="tool_call",
            tool_name="open_meteo_forecast",
            tool_args={"lat": place["lat"], "lon": place["lon"]},
        ) as s:
            start = time.time()
            weather = fetch_weather(place["lat"], place["lon"])
            s.step.metrics.latency = time.time() - start
            s.step.metadata["tool_result"] = weather

        with step(
            "Fetch Live Exchange Rate",
            type="tool_call",
            tool_name="frankfurter_exchange_rate",
            tool_args={"base": "USD", "target": "JPY"},
        ) as s:
            start = time.time()
            fx = fetch_exchange_rate("USD", "JPY")
            s.step.metrics.latency = time.time() - start
            s.step.metadata["tool_result"] = fx

        with step(
            "Retrieve Destination Facts",
            type="retriever",
            query=trip["destination"],
        ) as s:
            start = time.time()
            summary = fetch_destination_summary(trip["destination"])
            paragraphs = [p.strip() for p in summary["extract"].split(". ") if p.strip()]
            s.step.metrics.latency = time.time() - start
            s.step.metadata["chunk_count"] = len(paragraphs)
            s.step.metadata["avg_tokens_per_chunk"] = round(
                sum(len(p) for p in paragraphs) / max(len(paragraphs), 1) / 4
            )
            s.step.metadata["retrieved_doc_ids"] = [summary["title"]]

        with step(
            "Synthesize Travel Briefing",
            type="final_response",
            provider="openai" if USE_REAL_OPENAI else None,
            model="gpt-4o-mini" if USE_REAL_OPENAI else None,
            prompt=question,
        ) as s:
            start = time.time()
            synth_prompt = (
                f"Traveler question: {question}\n\n"
                f"Intent: {intent}\n"
                f"Live weather at {place['name']}: {weather}\n"
                f"Live USD->JPY rate: {fx['rate']} (as of {fx['date']})\n"
                f"Destination facts: {summary['extract']}\n\n"
                "Write a concise, friendly travel briefing using only this data."
            )
            resp = call_llm("brief", synth_prompt)
            s.record(resp)
            s.step.metrics.latency = time.time() - start
            briefing = resp.choices[0].message.content

    print("=" * 72)
    print("TRAVEL BRIEFING")
    print("=" * 72)
    print(briefing)
    print()
    print(f"(live weather: {weather})")
    print(f"(live rate:    1 USD = {fx['rate']} JPY as of {fx['date']})")

    print("\nWorkflow summary:")
    print(f"  Total tokens: {workflow.total_tokens}")
    print(f"  Total cost:   ${workflow.total_cost or 0:.6f}")
    wall = (workflow.end_time - workflow.start_time).total_seconds()
    print(f"  Wall latency: {wall:.3f}s (dominated by real network calls, not tokens)")

    print("\nStep breakdown:")
    for st in workflow.steps:
        print(
            f"  - {st.name:<32} {st.type.value:<15} "
            f"{st.metrics.total_tokens:>5} tok  {st.metrics.latency * 1000:>8.1f} ms"
        )

    recs = RecommendationEngine().run(workflow)
    print(f"\nRecommendations: {len(recs)}")
    for r in recs:
        print(f"  - {r.title}: {r.description}")


if __name__ == "__main__":
    main()
