# Changelog

All notable changes to this project will be documented here.

This project follows [Semantic Versioning](https://semver.org/).

## 0.4.0 - 2026-08-08

### Added

- Markdown trace and comparison reports, including CLI support via
  `agenticlens inspect --save` and `agenticlens compare --format md`.
- Minimum-sample guidance for repeated-run comparison, plus `--min-samples`
  enforcement in the CLI for CI-friendly under-sampling checks.
- First-class `Evidence` objects on findings and recommendations, with
  provenance carried through analysis and reporting.
- Duplicate-context detection, retry attribution, retry outcome
  classification, and next-best-analysis suggestions for structured traces.
- AIOS draft validation and conformance commands in the CLI, including
  `agenticlens validate` and `agenticlens conformance` backed by local
  `ai-operations-spec` draft schemas and semantic checks.
- OTLP/HTTP JSON trace export for structured runs, including optional
  export-on-trace-completion support for configured endpoints.
- Additional deterministic evaluation checks for JSON Schema validation,
  required output fields, required tool arguments, and turn-count thresholds.
- `BusinessRuleEvaluator` and trusted live evaluation targets for Python and
  HTTP workflows via `evaluate-live`.
- Architecture import-layer enforcement tests and a runnable live-evaluation
  example covering structured-output checks.

### Changed

- The finding schema now reflects evidence as structured arrays rather than an
  untyped object, matching shipped runtime artifacts.
- Trace analysis no longer mutates the input run while computing retry
  attribution.
- AIOS schema resolution now uses the non-deprecated `referencing` registry
  path instead of `jsonschema.RefResolver`.
- Documentation, examples, and roadmap details now match the shipped trace,
  comparison, and evaluation feature surface.

## 0.3.0 - 2026-08-05

### Added

- Structured run-and-span tracing with payload redaction, trace inspection, raw metric
  distributions, and versioned trace, finding, and report JSON Schemas.
- A unified evaluation framework for deterministic, semantic, safety, RAG, LLM-judge,
  tool-behavior, latency, and cost scoring, with JSON and standalone HTML reports.
- Configurable release gates that enforce evaluation pass rate, score, failed-case,
  latency, and cost thresholds with CI-friendly exit codes.
- Repeated-run baseline/candidate comparison with regression detection and JSON or CSV
  export.
- Agent-aware reporting and multi-agent diagnostics, including handoff-bloat findings
  and reference LangGraph workflows.
- Live model pricing with on-disk caching and bundled fallback data.
- A model-swap simulator that recommends compatible lower-cost models and reports
  estimated dollar savings.
- An interactive product website, expanded architecture and research roadmaps, and
  contributor automation through Make targets and documented CI workflows.

### Changed

- The CLI now includes `inspect`, `compare`, `evaluate`, and `gate` workflows and
  presents agent summaries and token-optimization results in analysis output.
- Recommendation findings now carry richer evidence, confidence, quality-risk, and
  cost-savings information.
- Python 3.14 is now included in the supported and tested version matrix.
- Bundled pricing data is now a fallback behind user overrides and live pricing.

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
