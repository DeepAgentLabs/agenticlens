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


def classify_trip_native(planner_agent, Task, Crew, Process) -> tuple[LLMResponse, float]:
    """Real call runs through Crew.kickoff() -- CrewAI wraps the task in its
    own role/goal/backstory prompt template before it ever reaches the model,
    so token usage genuinely differs from a raw SDK call."""
    if not USE_REAL_OPENAI:
        return classify_trip("CrewAI")

    start = time.time()
    task = Task(
        description=f"Classify this trip request in one short line:\n{QUESTION}",
        expected_output="A short trip intent classification.",
        agent=planner_agent,
    )
    crew = Crew(agents=[planner_agent], tasks=[task], process=Process.sequential, verbose=False)
    result = crew.kickoff()
    usage = result.token_usage
    return LLMResponse(str(result), usage.prompt_tokens, usage.completion_tokens), (
        time.time() - start
    )


def synthesize_briefing_native(
    briefing_agent, Task, Crew, Process, place: dict, weather: dict, fx: dict, summary: dict
) -> tuple[LLMResponse, float]:
    if not USE_REAL_OPENAI:
        return synthesize_briefing("CrewAI", place)

    start = time.time()
    prompt = (
        f"Traveler question: {QUESTION}\n\n"
        f"Live weather at {place['name']}: {weather}\n"
        f"Live USD->JPY rate: {fx['rate']} (as of {fx['date']})\n"
        f"Destination facts: {summary['extract']}\n\n"
        "Write a concise, friendly travel briefing (3-4 sentences) using only this data."
    )
    task = Task(
        description=prompt,
        expected_output="A concise, friendly travel briefing.",
        agent=briefing_agent,
    )
    crew = Crew(agents=[briefing_agent], tasks=[task], process=Process.sequential, verbose=False)
    result = crew.kickoff()
    usage = result.token_usage
    return LLMResponse(str(result), usage.prompt_tokens, usage.completion_tokens), (
        time.time() - start
    )


def main() -> None:
    framework = "CrewAI"

    try:
        from crewai import LLM, Agent, Crew, Process, Task
    except ImportError as exc:
        raise RuntimeError("CrewAI is not installed. Run: pip install crewai") from exc

    llm = LLM(model=OPENAI_MODEL) if USE_REAL_OPENAI else None

    # Framework-specific objects. When a real key is available these agents
    # are actually executed via crew.kickoff() below; otherwise they exist
    # only for benchmark identity, matching the deterministic support-refund
    # benchmark's design.
    planner_agent = Agent(
        role="Trip Planner",
        goal="Classify a trip briefing request",
        backstory="You classify traveler requests into structured trip intents.",
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )
    briefing_agent = Agent(
        role="Briefing Writer",
        goal="Write a concise travel briefing from live data",
        backstory="You synthesize weather, currency, and destination facts for travelers.",
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )

    with profile(f"Benchmark - {framework} - Live Travel Briefing"):
        with step(
            f"{framework} - Classify Trip Request",
            type="planner",
            provider="openai",
            model=OPENAI_MODEL,
            prompt=QUESTION,
            framework="crewai",
        ) as s:
            response, latency = classify_trip_native(planner_agent, Task, Crew, Process)
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
            model=OPENAI_MODEL,
            prompt=QUESTION,
            framework="crewai",
        ) as s:
            response, latency = synthesize_briefing_native(
                briefing_agent, Task, Crew, Process, place, weather, fx, summary
            )
            s.record(response)
            s.step.metrics.latency = latency

    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
