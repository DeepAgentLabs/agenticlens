# Changelog

All notable changes to this project will be documented here.

This project follows [Semantic Versioning](https://semver.org/).

## Unreleased

### Added

- `agenticlens.adapters.langchain.AgenticLensCallbackHandler`, an optional
  (`pip install "agenticlens[langchain]"`) LangChain/LangGraph callback
  handler that auto-instruments LLM, tool, and retriever calls as AgenticLens
  steps without manual `step()` blocks. Documented in
  `docs/langchain-integration.md`.
- `benchmarks/`, a cross-framework benchmark harness that profiles the same
  refund-ticket workload through AutoGen, CrewAI, LangGraph, LlamaIndex,
  Semantic Kernel, and native Python for an apples-to-apples token/cost/latency
  comparison. Linked from the README.
- `examples/support_copilot.py` and `examples/multiagent_edge_cases_demo.py`,
  additional practical and edge-case profiling examples.

## 0.2.0 - 2026-07-13

### Added

- `chaos_events` schema extension (v1.1) to `Workflow`/`workflow.json`, documented
  in `docs/workflow-schema-spec.md`, so fault-injection tools such as
  [agentic-chaos](https://github.com/DeepAgentLabs/agentic-chaos) can report through
  AgenticLens's existing analysis engine.
- `ChaosImpactRecommender`, registered by default, surfaces resilience findings
  (unhandled failures, silent output degradation) from `chaos_events`.

### Changed

- The recommendation engine's budget-impact pass no longer overwrites the
  severity of recommendations with zero token savings, so non-savings-based
  recommenders like `ChaosImpactRecommender` can set their own severity.

## 0.1.2 - 2026-07-07

### Added

- Budget-impact ranking for recommendations, including dollar-per-run and monthly
  savings projections.
- Recommendation confidence and quality-risk fields for heuristic advice.
- Low-utility RAG chunk recommendation to flag retrieved context that appears
  unlikely to influence the final answer.
- Expanded open-source README with quickstart, CLI usage, cost calculation,
  examples, development workflow, and roadmap.

### Changed

- CLI analysis output now leads with a budget optimization summary.
- Recommendation severity is now based on estimated token and dollar impact.

## 0.1.1 - 2026-07-05

Initial release.

### Added

- Core data models for profiling sessions, steps, and token usage
- Provider abstraction layer with pricing support
- Explicit `profile()` / `step()` instrumentation API
- CLI interface via Typer with `report` and `export` commands
- Rich terminal output for profiling reports
- Recommendation engine framework (rules pending implementation)
- JSON and YAML export support
- pytest-based test suite with coverage reporting
- CI workflow with linting, type checking, and multi-version testing
