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
    framework = "LlamaIndex"

    try:
        from llama_index.core import Document
    except ImportError as exc:
        raise RuntimeError("LlamaIndex is not installed. Run: pip install llama-index") from exc

    with profile(f"Benchmark - {framework} - Live Travel Briefing"):
        with step(
            f"{framework} - Classify Trip Request",
            type="planner",
            provider="openai",
            model="gpt-4o-mini",
            prompt=QUESTION,
            framework="llamaindex",
        ) as s:
            response, latency = classify_trip(framework)
            s.record(response)
            s.step.metrics.latency = latency

        with step(
            f"{framework} - Geocode Destination",
            type="tool_call",
            tool_name="open_meteo_geocoding",
            tool_args={"city": TRIP["destination"]},
            framework="llamaindex",
        ) as s:
            place, latency = geocode_city(TRIP["destination"])
            s.step.metrics.latency = latency
            s.step.metadata["tool_result"] = place

        with step(
            f"{framework} - Fetch Live Weather",
            type="tool_call",
            tool_name="open_meteo_forecast",
            tool_args={"lat": place["lat"], "lon": place["lon"]},
            framework="llamaindex",
        ) as s:
            weather, latency = fetch_weather(place["lat"], place["lon"])
            s.step.metrics.latency = latency
            s.step.metadata["tool_result"] = weather

        with step(
            f"{framework} - Fetch Live Exchange Rate",
            type="tool_call",
            tool_name="frankfurter_exchange_rate",
            tool_args={"base": "USD", "target": "JPY"},
            framework="llamaindex",
        ) as s:
            fx, latency = fetch_exchange_rate("USD", "JPY")
            s.step.metrics.latency = latency
            s.step.metadata["tool_result"] = fx

        with step(
            f"{framework} - Retrieve Destination Facts",
            type="retriever",
            query=TRIP["destination"],
            framework="llamaindex",
        ) as s:
            summary, paragraphs, latency = fetch_destination_summary(TRIP["destination"])
            # Framework-specific object: wrap the live Wikipedia extract as a
            # LlamaIndex Document, matching how this framework represents
            # retrieved context, without building a real embedding index.
            document = Document(text=summary["extract"], metadata={"title": summary["title"]})
            s.step.metrics.latency = latency
            s.step.metadata["chunk_count"] = len(paragraphs)
            s.step.metadata["avg_tokens_per_chunk"] = estimate_avg_tokens_per_chunk(paragraphs)
            s.step.metadata["retrieved_doc_ids"] = [document.doc_id]

        with step(
            f"{framework} - Synthesize Travel Briefing",
            type="final_response",
            provider="openai",
            model="gpt-4o-mini",
            prompt=QUESTION,
            framework="llamaindex",
        ) as s:
            response, latency = synthesize_briefing(framework, place)
            s.record(response)
            s.step.metrics.latency = latency

    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
