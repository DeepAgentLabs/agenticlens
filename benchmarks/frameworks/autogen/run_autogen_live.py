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


async def _run_agent(agent, task: str) -> tuple[str, int, int]:
    result = await agent.run(task=task)
    last = result.messages[-1]
    usage = last.models_usage
    prompt_tokens = usage.prompt_tokens if usage else 0
    completion_tokens = usage.completion_tokens if usage else 0
    return last.content, prompt_tokens, completion_tokens


def classify_trip_native(planner_agent) -> tuple[LLMResponse, float]:
    """Real call runs through AssistantAgent.run() -- AutoGen's own
    system-message + task framing, not a raw OpenAI SDK call."""
    if not USE_REAL_OPENAI:
        return classify_trip("AutoGen")

    start = time.time()
    content, prompt_tokens, completion_tokens = asyncio.run(
        _run_agent(planner_agent, f"Classify this trip request in one short line:\n{QUESTION}")
    )
    return LLMResponse(content, prompt_tokens, completion_tokens), (time.time() - start)


def synthesize_briefing_native(
    briefing_agent, place: dict, weather: dict, fx: dict, summary: dict
) -> tuple[LLMResponse, float]:
    if not USE_REAL_OPENAI:
        return synthesize_briefing("AutoGen", place)

    start = time.time()
    prompt = (
        f"Traveler question: {QUESTION}\n\n"
        f"Live weather at {place['name']}: {weather}\n"
        f"Live USD->JPY rate: {fx['rate']} (as of {fx['date']})\n"
        f"Destination facts: {summary['extract']}\n\n"
        "Write a concise, friendly travel briefing (3-4 sentences) using only this data."
    )
    content, prompt_tokens, completion_tokens = asyncio.run(_run_agent(briefing_agent, prompt))
    return LLMResponse(content, prompt_tokens, completion_tokens), (time.time() - start)


def main() -> None:
    framework = "AutoGen"

    try:
        from autogen_agentchat.agents import AssistantAgent
    except ImportError as exc:
        raise RuntimeError(
            "AutoGen AgentChat is not installed. Run: pip install autogen-agentchat autogen-core"
        ) from exc

    model_client = None
    if USE_REAL_OPENAI:
        from autogen_ext.models.openai import OpenAIChatCompletionClient

        model_client = OpenAIChatCompletionClient(model=OPENAI_MODEL)

    planner_agent = AssistantAgent(name="trip_planner", model_client=model_client)
    briefing_agent = AssistantAgent(name="briefing_writer", model_client=model_client)

    with profile(f"Benchmark - {framework} - Live Travel Briefing"):
        with step(
            f"{framework} - Classify Trip Request",
            type="planner",
            provider="openai",
            model=OPENAI_MODEL,
            prompt=QUESTION,
            framework="autogen",
            agent_name=planner_agent.name,
        ) as s:
            response, latency = classify_trip_native(planner_agent)
            s.record(response)
            s.step.metrics.latency = latency

        with step(
            f"{framework} - Geocode Destination",
            type="tool_call",
            tool_name="open_meteo_geocoding",
            tool_args={"city": TRIP["destination"]},
            framework="autogen",
        ) as s:
            place, latency = geocode_city(TRIP["destination"])
            s.step.metrics.latency = latency
            s.step.metadata["tool_result"] = place

        with step(
            f"{framework} - Fetch Live Weather",
            type="tool_call",
            tool_name="open_meteo_forecast",
            tool_args={"lat": place["lat"], "lon": place["lon"]},
            framework="autogen",
        ) as s:
            weather, latency = fetch_weather(place["lat"], place["lon"])
            s.step.metrics.latency = latency
            s.step.metadata["tool_result"] = weather

        with step(
            f"{framework} - Fetch Live Exchange Rate",
            type="tool_call",
            tool_name="frankfurter_exchange_rate",
            tool_args={"base": "USD", "target": "JPY"},
            framework="autogen",
        ) as s:
            fx, latency = fetch_exchange_rate("USD", "JPY")
            s.step.metrics.latency = latency
            s.step.metadata["tool_result"] = fx

        with step(
            f"{framework} - Retrieve Destination Facts",
            type="retriever",
            query=TRIP["destination"],
            framework="autogen",
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
            framework="autogen",
            agent_name=briefing_agent.name,
        ) as s:
            response, latency = synthesize_briefing_native(
                briefing_agent, place, weather, fx, summary
            )
            s.record(response)
            s.step.metrics.latency = latency

    if USE_REAL_OPENAI:
        asyncio.run(model_client.close())

    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
