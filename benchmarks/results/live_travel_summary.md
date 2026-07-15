# AgenticLens Live Travel Briefing Benchmark

Use case: real-time trip briefing (weather, currency, destination facts).

Every tool/retriever step below calls a real, live, free API (Open-Meteo geocoding + forecast, Frankfurter exchange rates, Wikipedia REST summary) -- no API key required, no mocking. LLM steps use a deterministic fallback unless OPENAI_API_KEY is set, so token counts are stable across frameworks but latency is genuinely live.

| Framework | Total Tokens | Cost | Latency | Steps | Tool Calls | Retrieved Chunks | Highest Latency Step |
|---|---:|---:|---:|---:|---:|---:|---|
| native_python | 768 | $0.000191 | 1.592s | 6 | 3 | 3 | Native Python - Geocode Destination |
| langgraph | 768 | $0.000191 | 1.480s | 6 | 3 | 3 | LangGraph - Geocode Destination |
| crewai | 768 | $0.000191 | 1.578s | 6 | 3 | 3 | CrewAI - Geocode Destination |
| autogen | 768 | $0.000191 | 1.465s | 6 | 3 | 3 | AutoGen - Geocode Destination |
| llamaindex | 768 | $0.000191 | 1.486s | 6 | 3 | 3 | LlamaIndex - Geocode Destination |
| semantic_kernel | 768 | $0.000191 | 1.609s | 6 | 3 | 3 | Semantic Kernel - Geocode Destination |

## Interpretation

Total tokens and cost are near-identical across frameworks because the LLM steps are a deterministic fallback (no OPENAI_API_KEY set). Latency is the meaningful column here: it reflects real network round-trips to four live APIs, not scripted timings, so it varies between runs and frameworks based on real network conditions and per-framework overhead.