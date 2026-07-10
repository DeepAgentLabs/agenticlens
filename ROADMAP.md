# Roadmap

## MVP (current)

- [x] Repository scaffold
- [x] Project configuration (`pyproject.toml`, `ruff`, `mypy`)
- [x] Complete package structure
- [x] Data models (Pydantic v2)
- [x] Provider abstraction (abstract base class) + OpenAI/Anthropic
- [x] Profiler skeleton (`profile()` / `step()`)
- [x] Metrics engine skeleton (cost calculation, pricing resolution)
- [x] CLI skeleton (Typer)
- [x] Unit test setup (pytest)
- [x] GitHub Actions CI pipeline
- [x] Recommendation engine heuristic rules (repeated system prompt, excessive chunks, long history, duplicate tool calls)
- [x] CLI `profile`/`report`/`analyze` business logic
- [x] Documentation structure (MkDocs)
- [x] Markdown and Jira exporters
- [x] RAG chunk-utility scoring (citation, reranker, embedding signals)
- [x] Recommendation output in exporters (JSON, CSV, Markdown)

## Post-MVP

See "Future Roadmap" in [AgenticLens_Spec.md](AgenticLens_Spec.md):

- LangGraph / CrewAI / OpenAI Agents SDK integrations
- MCP server-level token attribution
- Automated prompt compression
- Context utilization metrics
- Evaluation framework (quality vs. cost)
- Dashboard / visual workflow explorer
- Enterprise reporting
