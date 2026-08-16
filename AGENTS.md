## AgenticLens Development Reference

## Ecosystem Context

### Role in DeepAgentLabs

`agenticlens` is the observability, evaluation, and operational intelligence
layer in DeepAgentLabs. It helps teams understand what ran, what the model and
agent did, what context and tools were involved, what it cost, and whether the
system performed well over time.

### Owns

- Runtime instrumentation, trace capture, analysis, evaluation, reporting, and
  evidence-backed recommendations
- The flagship Python reference implementation for emitting and working with AI
  Operations Specification-compatible artifacts
- Export surfaces and analysis workflows that turn raw traces into actionable
  operational findings

### Does Not Own

- The normative definition of the shared contract — that belongs in
  `ai-operations-spec`
- Fault injection or resilience experimentation — that belongs in
  `agentic-chaos`
- Pre-action agent supervision and decision interception — that belongs in
  `agentic-sidecar`
- At the ecosystem-role level, `agentic-sidecar` is the **SUPERVISE** layer,
  while its concrete functionality spans both supervision and governance.
- A generic MCP server or remote orchestration surface — that belongs in
  `deep-agentic-core-mcp`

### Integrates With

- `ai-operations-spec` as the canonical object model and long-term
  interoperability target
- `agentic-chaos` for ingesting and analyzing resilience/failure evidence
- `agentic-sidecar` when decision and escalation events need to become part of
  the operational record
- `deep-agentic-core-mcp` as a thin delivery surface for AgenticLens-powered
  workflows and analysis tools

### Current Roadmap Focus

The next milestone centers on judge calibration, evaluation dataset management,
and experiments/statistical comparison. New work here should deepen evidence
quality and repeatable analysis, not drift into spec stewardship or chaos
simulation.

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
| `src/agenticlens/evaluation/` | Test cases, suites, evaluators, and scoring |
| `src/agenticlens/exporters/` | JSON, CSV, Markdown, Jira exports |
| `src/agenticlens/metrics/` | Cost and performance calculation |
| `src/agenticlens/models/` | Pydantic data models (Workflow, Step, ChaosEvent) |
| `src/agenticlens/providers/` | Provider response usage extraction (OpenAI, Anthropic) |
| `src/agenticlens/recommenders/` | Rule-based optimization suggestions |
| `src/agenticlens/reports/` | Trace inspection rendering |
| `src/agenticlens/cli/` | Typer CLI and Rich rendering |
| `src/agenticlens/utils/` | Shared utilities |
| `schemas/` | Versioned JSON Schemas (trace, finding, report) |
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

Two phases, split by the merge to `main` — bumping happens before, tagging
and releasing happen after:

**1. Pre-release (on the feature branch, before merge):** Bump version in
`pyproject.toml`, `src/agenticlens/__init__.py`, and `CHANGELOG.md` (a
dated release section under `[Unreleased]`). Commit as part of the
branch's normal history; goes in with the rest of the PR.

**2. Release (on `main`, once that branch has merged):** plain `git`, no
`gh` CLI required.

1. Pull the merge commit on `main`.
2. Tag: create an annotated `vX.Y.Z` tag pointing at the merge commit,
   using the CHANGELOG's release section as the tag message:
   `git tag -a vX.Y.Z -F <file-with-that-section> --cleanup=verbatim`.
   `--cleanup=verbatim` is required — git's default cleanup silently strips
   lines starting with `#`, which would eat the CHANGELOG's `###` headers.
3. Push the tag: `git push origin vX.Y.Z`.

That's the whole release: `release-pypi.yml` triggers on the tag push and
publishes to PyPI via Trusted Publishing (OIDC) — no API token/secret
required, but the `pypi` GitHub Environment must exist and be configured
as a Trusted Publisher on PyPI before the first release. (`release-testpypi.yml`
is a separate, manual `workflow_dispatch` staging flow — unaffected.)

Note this deliberately does not create a GitHub Release object (that's a
`gh`/API-only action, not a `git` one) — the tag alone is enough to
publish to PyPI, but it means the repo's Releases tab stays empty unless
someone creates one by hand later (GitHub UI: Releases → Draft a new
release → pick the existing tag). That's an accepted tradeoff here, not
an oversight.
