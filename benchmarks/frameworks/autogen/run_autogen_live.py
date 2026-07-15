from agenticlens import profile, step
from benchmarks.shared.live_travel_tasks import (
    QUESTION,
    TRIP,
    classify_trip,
    estimate_avg_tokens_per_chunk,
    fetch_destination_summary,
    fetch_exchange_rate,
    fetch_weather,
    geocode_city,
    synthesize_briefing,
)


def main() -> None:
    framework = "AutoGen"

    try:
        from autogen_agentchat.agents import AssistantAgent
    except ImportError as exc:
        raise RuntimeError(
            "AutoGen AgentChat is not installed. Run: pip install autogen-agentchat autogen-core"
        ) from exc

    # Framework-specific agents.
    # We instantiate agents for benchmark identity, but do not call a live model
    # client -- the tool/retriever steps below already make real network calls.
    planner_agent = AssistantAgent(name="trip_planner", model_client=None)
    briefing_agent = AssistantAgent(name="briefing_writer", model_client=None)

    with profile(f"Benchmark - {framework} - Live Travel Briefing"):
        with step(
            f"{framework} - Classify Trip Request",
            type="planner",
            provider="openai",
            model="gpt-4o-mini",
            prompt=QUESTION,
            framework="autogen",
            agent_name=planner_agent.name,
        ) as s:
            response, latency = classify_trip(framework)
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
            model="gpt-4o-mini",
            prompt=QUESTION,
            framework="autogen",
            agent_name=briefing_agent.name,
        ) as s:
            response, latency = synthesize_briefing(framework, place)
            s.record(response)
            s.step.metrics.latency = latency

    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
