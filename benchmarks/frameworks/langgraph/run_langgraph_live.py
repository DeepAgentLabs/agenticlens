import time
from typing import Any, TypedDict

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

if USE_REAL_OPENAI:
    from langchain_openai import ChatOpenAI

    _llm = ChatOpenAI(model=OPENAI_MODEL)


def classify_trip_native() -> tuple[LLMResponse, float]:
    """Real call goes through LangChain's ChatOpenAI -- its own message
    formatting and response object, not a raw OpenAI SDK call."""
    if not USE_REAL_OPENAI:
        return classify_trip("LangGraph")

    start = time.time()
    ai_message = _llm.invoke(f"Classify this trip request in one short line:\n{QUESTION}")
    usage = ai_message.usage_metadata or {}
    return LLMResponse(
        ai_message.content, usage.get("input_tokens", 0), usage.get("output_tokens", 0)
    ), (time.time() - start)


def synthesize_briefing_native(
    place: dict, weather: dict, fx: dict, summary: dict
) -> tuple[LLMResponse, float]:
    if not USE_REAL_OPENAI:
        return synthesize_briefing("LangGraph", place)

    start = time.time()
    prompt = (
        f"Traveler question: {QUESTION}\n\n"
        f"Live weather at {place['name']}: {weather}\n"
        f"Live USD->JPY rate: {fx['rate']} (as of {fx['date']})\n"
        f"Destination facts: {summary['extract']}\n\n"
        "Write a concise, friendly travel briefing (3-4 sentences) using only this data."
    )
    ai_message = _llm.invoke(prompt)
    usage = ai_message.usage_metadata or {}
    return LLMResponse(
        ai_message.content, usage.get("input_tokens", 0), usage.get("output_tokens", 0)
    ), (time.time() - start)


class TravelState(TypedDict, total=False):
    intent: str
    place: dict[str, Any]
    weather: dict[str, Any]
    fx: dict[str, Any]
    summary: dict[str, Any]
    final_answer: str


def classify_node(state: TravelState) -> TravelState:
    with step(
        "LangGraph - Classify Trip Request",
        type="planner",
        provider="openai",
        model=OPENAI_MODEL,
        prompt=QUESTION,
        framework="langgraph",
    ) as s:
        response, latency = classify_trip_native()
        s.record(response)
        s.step.metrics.latency = latency

    state["intent"] = response.choices[0].message.content
    return state


def geocode_node(state: TravelState) -> TravelState:
    with step(
        "LangGraph - Geocode Destination",
        type="tool_call",
        tool_name="open_meteo_geocoding",
        tool_args={"city": TRIP["destination"]},
        framework="langgraph",
    ) as s:
        place, latency = geocode_city(TRIP["destination"])
        s.step.metrics.latency = latency
        s.step.metadata["tool_result"] = place

    state["place"] = place
    return state


def weather_node(state: TravelState) -> TravelState:
    place = state["place"]
    with step(
        "LangGraph - Fetch Live Weather",
        type="tool_call",
        tool_name="open_meteo_forecast",
        tool_args={"lat": place["lat"], "lon": place["lon"]},
        framework="langgraph",
    ) as s:
        weather, latency = fetch_weather(place["lat"], place["lon"])
        s.step.metrics.latency = latency
        s.step.metadata["tool_result"] = weather

    state["weather"] = weather
    return state


def fx_node(state: TravelState) -> TravelState:
    with step(
        "LangGraph - Fetch Live Exchange Rate",
        type="tool_call",
        tool_name="frankfurter_exchange_rate",
        tool_args={"base": "USD", "target": "JPY"},
        framework="langgraph",
    ) as s:
        fx, latency = fetch_exchange_rate("USD", "JPY")
        s.step.metrics.latency = latency
        s.step.metadata["tool_result"] = fx

    state["fx"] = fx
    return state


def retrieve_node(state: TravelState) -> TravelState:
    with step(
        "LangGraph - Retrieve Destination Facts",
        type="retriever",
        query=TRIP["destination"],
        framework="langgraph",
    ) as s:
        summary, paragraphs, latency = fetch_destination_summary(TRIP["destination"])
        s.step.metrics.latency = latency
        s.step.metadata["chunk_count"] = len(paragraphs)
        s.step.metadata["avg_tokens_per_chunk"] = estimate_avg_tokens_per_chunk(paragraphs)
        s.step.metadata["retrieved_doc_ids"] = [summary["title"]]

    state["summary"] = summary
    return state


def synthesize_node(state: TravelState) -> TravelState:
    with step(
        "LangGraph - Synthesize Travel Briefing",
        type="final_response",
        provider="openai",
        model=OPENAI_MODEL,
        prompt=QUESTION,
        framework="langgraph",
    ) as s:
        response, latency = synthesize_briefing_native(
            state["place"], state["weather"], state["fx"], state["summary"]
        )
        s.record(response)
        s.step.metrics.latency = latency

    state["final_answer"] = response.choices[0].message.content
    return state


def main() -> None:
    try:
        from langgraph.graph import END, StateGraph
    except ImportError as exc:
        raise RuntimeError("LangGraph is not installed. Run: pip install langgraph") from exc

    graph = StateGraph(TravelState)
    graph.add_node("classify", classify_node)
    graph.add_node("geocode", geocode_node)
    graph.add_node("weather", weather_node)
    graph.add_node("fx", fx_node)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("synthesize", synthesize_node)

    graph.set_entry_point("classify")
    graph.add_edge("classify", "geocode")
    graph.add_edge("geocode", "weather")
    graph.add_edge("weather", "fx")
    graph.add_edge("fx", "retrieve")
    graph.add_edge("retrieve", "synthesize")
    graph.add_edge("synthesize", END)

    app = graph.compile()

    with profile("Benchmark - LangGraph - Live Travel Briefing"):
        final_state = app.invoke({})

    print(final_state["final_answer"])


if __name__ == "__main__":
    main()
