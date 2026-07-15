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
    framework = "CrewAI"

    try:
        from crewai import Agent, Crew, Process, Task
    except ImportError as exc:
        raise RuntimeError("CrewAI is not installed. Run: pip install crewai") from exc

    # Framework-specific objects.
    # These make this a CrewAI benchmark adapter, while AgenticLens measures each
    # real step. We do not call crew.kickoff() because that would require a live
    # LLM -- the tool/retriever steps below already make real network calls.
    planner_agent = Agent(
        role="Trip Planner",
        goal="Classify a trip briefing request",
        backstory="You classify traveler requests into structured trip intents.",
        verbose=False,
        allow_delegation=False,
    )
    briefing_agent = Agent(
        role="Briefing Writer",
        goal="Write a concise travel briefing from live data",
        backstory="You synthesize weather, currency, and destination facts for travelers.",
        verbose=False,
        allow_delegation=False,
    )
    tasks = [
        Task(
            description="Classify the trip briefing request.",
            expected_output="Trip intent and destination.",
            agent=planner_agent,
        ),
        Task(
            description="Write the final travel briefing from live data.",
            expected_output="Customer-facing travel briefing.",
            agent=briefing_agent,
        ),
    ]
    crew = Crew(
        agents=[planner_agent, briefing_agent],
        tasks=tasks,
        process=Process.sequential,
        verbose=False,
    )

    with profile(f"Benchmark - {framework} - Live Travel Briefing"):
        with step(
            f"{framework} - Classify Trip Request",
            type="planner",
            provider="openai",
            model="gpt-4o-mini",
            prompt=QUESTION,
            framework="crewai",
            crew_agents=len(crew.agents),
        ) as s:
            response, latency = classify_trip(framework)
            s.record(response)
            s.step.metrics.latency = latency

        with step(
            f"{framework} - Geocode Destination",
            type="tool_call",
            tool_name="open_meteo_geocoding",
            tool_args={"city": TRIP["destination"]},
            framework="crewai",
        ) as s:
            place, latency = geocode_city(TRIP["destination"])
            s.step.metrics.latency = latency
            s.step.metadata["tool_result"] = place

        with step(
            f"{framework} - Fetch Live Weather",
            type="tool_call",
            tool_name="open_meteo_forecast",
            tool_args={"lat": place["lat"], "lon": place["lon"]},
            framework="crewai",
        ) as s:
            weather, latency = fetch_weather(place["lat"], place["lon"])
            s.step.metrics.latency = latency
            s.step.metadata["tool_result"] = weather

        with step(
            f"{framework} - Fetch Live Exchange Rate",
            type="tool_call",
            tool_name="frankfurter_exchange_rate",
            tool_args={"base": "USD", "target": "JPY"},
            framework="crewai",
        ) as s:
            fx, latency = fetch_exchange_rate("USD", "JPY")
            s.step.metrics.latency = latency
            s.step.metadata["tool_result"] = fx

        with step(
            f"{framework} - Retrieve Destination Facts",
            type="retriever",
            query=TRIP["destination"],
            framework="crewai",
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
            framework="crewai",
        ) as s:
            response, latency = synthesize_briefing(framework, place)
            s.record(response)
            s.step.metrics.latency = latency

    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
