## AgenticLens Development Reference

## Ecosystem Context

### Role in DeepAgentLabs

`agenticlens` is the observability, evaluation, and operational intelligence
layer in DeepAgentLabs. It helps teams understand what ran, what the model and
agent did, what context and tools were involved, what it cost, and whether the
system performed well over time.

### Owns

- Runtime instrumentation, trace capture, analysis, evaluation workflows, reporting, and
  evidence-backed recommendations
- The flagship Python reference implementation for emitting and working with AI
  Operations Specification-compatible artifacts
- Export surfaces and analysis workflows that turn raw traces into actionable
  operational findings

### Does Not Own

- Standalone scoring and release-gate computation — those belong in
  `agentic-evals`, which Lens composes for evaluation workflows

- The normative definition of the shared contract — that belongs in
  `ai-operations-spec`
- Fault injection or resilience experimentation — that belongs in
  `agentic-chaos`
- Pre-action agent supervision and decision interception — that belongs in
  `agentic-sidecar`
- At the ecosystem-role level, `agentic-sidecar` is the **SUPERVISE** layer,
  while its concrete functionality spans both supervision and governance.
- Fleet inventory and control-plane orchestration — those belong in
  `agenticops-control-tower`; MCP-native access belongs in `deep-agentic-core-mcp`

### Integrates With

- `agenticops-control-tower` as a consumer of explicitly attributed native
  evidence; its deployment health remains separate from producer outcomes
- `agentic-evals` for standalone scoring/report and release-gate boundaries

- `ai-operations-spec` as the canonical object model and long-term
  interoperability target
- `agentic-chaos` for ingesting and analyzing resilience/failure evidence
- `agentic-sidecar` when decision and escalation events need to become part of
  the operational record
- `deep-agentic-core-mcp` as a thin delivery surface for AgenticLens-powered
  workflows and analysis tools

### Current Roadmap Focus

v0.3 (evaluation evidence) and v0.4 (experiments and statistical comparison)
shipped in 0.6.0; v0.5 (advanced evaluation and diagnosis: failure taxonomy,
diagnosis rules, faulty-step attribution measured on controlled failures,
timelines, anomalies, guardrails, trace-aware evaluators, judge cost, and
score analysis) shipped in 0.7.0; v0.6 (test-suite and dataset management:
imports, trace and feedback conversion, editors, splits, variations,
duplicates, PII masking, approval, and an immutable suite store) shipped in
0.8.0; v0.7 (ModelFit: task taxonomy, fail-closed hard constraints,
weighted scoring, Pareto frontiers, cost-per-success ranking, confidence,
explanations, fallbacks, evidence-tied savings, quality risks, and a
task-level model matrix) shipped in 0.9.0. v0.8 Advisory Runtime Routing ships in 0.10.0. The next milestone is v0.9
Optimization Intelligence. New work here should deepen evidence quality and
repeatable analysis, not drift into spec stewardship or chaos simulation.

### Before You Build Here

- If a change defines a cross-package object, event meaning, or schema, move it
  to `ai-operations-spec` instead of making AgenticLens the de facto standard
- Prefer consuming chaos, sidecar, or MCP artifacts through clean boundaries
  rather than reimplementing sibling-package behavior here
- Keep findings evidence-backed: this package should explain and evaluate what
  happened, not become a policy engine or fault injector

## Build and Run

- Install: `make install` (runs `uv sync --extra dev --extra docs`)
- Test: `make test` or `make check` (lint + format + typecheck + test)
- Lint: `make lint`
- Type check: `make typecheck`
- Build docs: `make docs`
- CLI: `uv run agenticlens <command>`

## Code Style

- Strict typing (mypy strict mode, Python 3.10+)
- Line length: 100
- Ruff rules: E, F, I, UP, B, SIM, N
- Per-file ignores: E501 for `html_report.py`
- One purpose per file (separation of concerns)
- Evidence-backed: findings must identify measurements, thresholds, and trace
  evidence on which they are based

## Repo Map

| Path | Purpose |
|------|---------|
| `src/agenticlens/profiler/` | Workflow and step profiling (`profile()`, `step()`) |
| `src/agenticlens/instrumentation/` | Structured Run/Span tracing, payload redaction |
| `src/agenticlens/analysis/` | Memory and retry diagnostics |
| `src/agenticlens/analyzers/` | Analyzer implementations |
| `src/agenticlens/comparison/` | Repeated-run statistics, regression reports |
| `src/agenticlens/config/` | Pricing data, settings, configuration |
| `src/agenticlens/evaluation/` | agentic-evals adapters, trace-aware evaluators, score analysis, evidence audit, structured judges, calibration, gate alerts |
| `src/agenticlens/experiments/` | Multi-variant experiments, pass@k statistics, HTML/CSV experiment reports |
| `src/agenticlens/diagnosis/` | Failure taxonomy, diagnosis rules, attribution, timelines, anomalies, guardrails, narratives, attribution accuracy |
| `src/agenticlens/suites/` | Suite imports, trace/feedback conversion, editors, variations, duplicates, PII masking, splits, approval, immutable store |
| `src/agenticlens/routing/` | Evidence-based routing, constraints, failover, shadow/canary, local journal |
| `src/agenticlens/modelfit/` | ModelFit: experiment evidence, task taxonomy, constraints, scoring, Pareto analysis, recommendations, model matrix |
| `src/agenticlens/exporters/` | JSON, CSV, Markdown, Jira exports |
| `src/agenticlens/metrics/` | Cost and performance calculation |
| `src/agenticlens/models/` | Pydantic data models (Workflow, Step, ChaosEvent) |
| `src/agenticlens/providers/` | Provider response usage extraction (OpenAI, Anthropic) |
| `src/agenticlens/recommenders/` | Rule-based optimization suggestions |
| `src/agenticlens/reports/` | Trace inspection rendering |
| `src/agenticlens/cli/` | Typer CLI and Rich rendering |
| `src/agenticlens/utils/` | Shared utilities |
| `schemas/` | Versioned JSON Schemas (trace, finding, report, experiments, diagnosis, score analysis, suites, modelfit) |
| `tests/` | Pytest test suite |
| `docs/` | MkDocs documentation source |
| `Makefile` | Local dev automation |

## Entry Points

- Console script: `agenticlens` → `cli/main.py:app`
- Profiling API: `from agenticlens import profile, step`
- Analysis CLI: `agenticlens analyze <workflow.json>`

## Module Boundaries

- `exporters/` must not import from `cli/`
- `models/` must not import from `recommenders/` or `analysis/`
- `providers/` extracts usage data only — no analysis logic
- `recommenders/` reads models and metrics, produces findings
- `cli/` composes everything for user-facing commands

## Adding a New Diagnosis Rule

1. Add a class with `rule_id`, `version`, and
   `diagnose(view: TraceView, config: DiagnosisConfig) -> list[Diagnosis]` to
   `src/agenticlens/diagnosis/rules.py` (or pass it via `diagnose_run(rules=...)`)
2. Use an existing `FailureCategory`; adding or changing a category bumps
   `TAXONOMY_VERSION`
3. Cite every supporting span with `view.evidence(...)` and give a confidence
4. Add it to `DEFAULT_RULES`, add tests, and re-run
   `agenticlens attribution-accuracy examples/diagnosis/controlled_failures`;
   regenerate `examples/diagnosis/attribution-accuracy.json` if it changes
5. Keep reports reproducible: no wall-clock values in `DiagnosisReport`

## Changing Suite Management

1. Suites must stay valid agentic-evals `TestSuite`s; keep management state in
   case `metadata` under the keys in `suites/models.py`
2. Never change how `content_sha256` is computed for stored versions: it
   would make every approved version fail verification
3. Reports (masking, duplicates) must never contain masked values
4. Regenerate `schemas/suites/` when a published model changes, and re-run
   `uv run python examples/suite_management_demo.py` if the example output
   changes (`tests/test_examples_suites.py` checks it)

## Changing ModelFit

1. Candidates are experiment variants; never recommend from list prices or
   benchmarks. Every number must come from experiment attempts
2. Constraints fail closed: a limit the evidence cannot verify is a violation
3. Keep savings (benefit) and quality risks separate, and keep savings
   `available: false` when either side's cost is incomplete
4. Regenerate `schemas/modelfit/` when a published model changes, and re-run
   `uv run python examples/modelfit_demo.py` if the example output changes
   (`tests/test_examples_modelfit.py` checks it)

## Adding a New Recommender

1. Create `src/agenticlens/recommenders/my_recommender.py`
2. Implement the recommender (takes a Workflow, returns findings)
3. Register in `DEFAULT_RECOMMENDERS` in `recommenders/engine.py`
4. Add tests in `tests/`
5. Every finding must include source evidence (step/span reference)

## Feature Completion Expectations

- Every behavior change must include tests.
- User-facing features must include or update examples in `README.md`, `docs/`,
  `examples/`, or test fixtures that demonstrate expected usage.
- When a roadmap item or milestone meaningfully changes status, update
  `README.md` and `agenticlens-roadmap.md` in the same change.
- If that milestone or release changes the public ecosystem story, also update
  the shared org-profile docs in the `.github` repository:
  `profile/README.md` and, when relevant, `profile/ROADMAP.md`.
- When work is packaged as a release-ready change, also update
  `pyproject.toml`, `src/agenticlens/__init__.py`, and `CHANGELOG.md`.

## Schema Versioning

- Schemas live in `schemas/` and are included in the wheel via `force-include`
- Trace, finding, and comparison-report schemas are versioned independently
- Additive changes preferred; breaking changes require version bump

## Pre-push Checklist

Run `make check` before every push. It runs: lint → format-check → typecheck → test.

## Release

Two phases, split by the merge to `main` — bumping happens before, and the
tag-driven release automation happens after.

**1. Pre-release (on the feature branch, before merge):** Bump version in
`pyproject.toml`, `src/agenticlens/__init__.py`, and `CHANGELOG.md` (a
dated release section under `[Unreleased]`). Commit as part of the
branch's normal history; goes in with the rest of the PR.

**2. Release (on `main`, once that branch has merged):** plain `git`, no
manual `gh release` step required.

1. Pull the merge commit on `main`.
2. Tag: create an annotated `vX.Y.Z` tag pointing at the merge commit,
   using the `CHANGELOG.md` release section for that version as the tag
   message:
   `git tag -a vX.Y.Z -F <file-with-that-section> --cleanup=verbatim`.
   `--cleanup=verbatim` is required — git's default cleanup silently strips
   lines starting with `#`, which would eat the changelog's `###` headers.
3. Push the tag: `git push origin vX.Y.Z`.

That tag push is the release trigger. `release-pypi.yml` runs automatically
and does both of the following from the same tag:

- publishes the package to PyPI using `PYPI_API_TOKEN`
- creates the GitHub Release object for `vX.Y.Z`

The GitHub Release title is the tag name, and its body is copied from the
matching `CHANGELOG.md` section so the changelog, tag, PyPI release, and
GitHub Releases page stay aligned. (`release-testpypi.yml` is a separate,
manual `workflow_dispatch` staging flow — unaffected.)
