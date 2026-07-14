# Roadmap

## Product Direction

AgenticLens should aim to be a **local-first observability, evaluation, and
regression toolkit for agentic AI applications**.

That means the PyPI package should own the developer workflow that happens
closest to code and CI:

- instrumentation and workflow capture
- graph-aware trace structure
- cost, latency, and token analysis
- step-level and workflow-level scoring
- evaluator interfaces and local eval runs
- datasets, experiments, and regression checks
- prompt/version/config tracking
- policy and guardrail enforcement in CI

It should **not** try to become a hosted observability platform inside the core
package. Multi-user dashboards, auth/RBAC, hosted storage, alert routing, and
enterprise ops workflows are useful, but they should remain optional layers on
top of the package rather than the center of the project.

## Guiding Principles

- **Package-first**: every major feature should be usable through Python and the
  CLI without requiring a backend.
- **Local-first**: runs, datasets, scores, and regressions should work on local
  files by default.
- **CI-first**: the output should be useful not only for inspection, but for
  automated quality gates.
- **Framework-agnostic**: integrations matter, but the core data model should
  not depend on one framework.
- **Additive evolution**: extend the existing `workflow.json` contract in ways
  that preserve compatibility.

## Current Status

### v0.1.x (current)

- [x] Repository scaffold
- [x] Project configuration (`pyproject.toml`, `ruff`, `mypy`)
- [x] Complete package structure
- [x] Data models (Pydantic v2)
- [x] Provider abstraction + OpenAI/Anthropic usage extraction
- [x] Profiler (`profile()` / `step()`)
- [x] Metrics and cost calculation
- [x] CLI `profile` / `report` / `analyze`
- [x] JSON, CSV, Markdown, and Jira exporters
- [x] Rule-based recommendation engine
- [x] RAG chunk-utility scoring
- [x] Agentic-chaos interop via additive `workflow.json` extensions

This release line establishes AgenticLens as a **cost and workflow profiling
tool**.

## Roadmap

### v0.2 — Graph-Aware Tracing Foundation

Goal: move from flat step lists to a workflow model that can describe real
agent execution structure.

Why this comes first:
- nearly every higher-level feature depends on better trace structure
- step-level evaluation is much stronger when parent/child and retry
  relationships exist
- this creates the bridge from "LLM profiler" to "agent observability toolkit"

Planned work:

- [ ] Extend `Step` with graph-oriented fields such as:
  `parent_step_id`, `span_kind`, `attempt`, `status`
- [ ] Add optional ownership/identity fields such as:
  `agent_name`, `tool_name`, `session_id`, `thread_id`
- [ ] Support retry groups, handoffs, and sub-agent relationships
- [ ] Preserve backward compatibility with existing flat `workflow.json`
- [ ] Add CLI rendering improvements for nested/related steps
- [ ] Add tests and schema docs for graph-aware traces

Definition of done:
- AgenticLens can represent planners, retrievers, tools, sub-agents, retries,
  and final responses as a connected workflow rather than only a linear list.

### v0.3 — Scores and Evaluator API

Goal: make quality a first-class concept, not just a free-form recommendation
description.

Why this matters:
- observability without quality scoring becomes a trace viewer
- the strongest next step is to score decisions, not just costs

Planned work:

- [ ] Add typed score models:
  `numeric`, `boolean`, `categorical`
- [ ] Support score scopes:
  `workflow`, `step`, `thread`, and `dataset_run`
- [ ] Add evaluator interface with three local evaluator types:
  `heuristic`, `llm_judge`, `python_callable`
- [ ] Add built-in evaluator categories:
  `tool_selection`, `retrieval_quality`, `plan_quality`,
  `task_completion`, `policy_compliance`
- [ ] Add score export support to JSON, CSV, and Markdown outputs
- [ ] Add score-aware CLI views

Definition of done:
- a workflow can carry explicit quality signals that are queryable, exportable,
  and reusable in experiments and regression checks.

### v0.4 — Datasets and Trace-to-Dataset Curation

Goal: turn one-off debugging into reusable evaluation coverage.

Why this matters:
- this is the clearest product gap today
- production failures should become future regression cases

Planned work:

- [ ] Add local dataset models:
  `Dataset`, `DatasetItem`, `ExpectedOutput`, `ScenarioTags`, `DatasetRun`
- [ ] Add CLI commands for curation and inspection
- [ ] Support trace-to-dataset extraction from saved workflow files
- [ ] Add a package-friendly flow such as:
  `agenticlens curate run.json --to-dataset regressions.jsonl`
- [ ] Support attaching scores and notes to curated items
- [ ] Document local storage format and compatibility guarantees

Definition of done:
- users can collect interesting runs, convert them into datasets, and reuse
  them later without external infrastructure.

### v0.5 — Experiment Runner

Goal: compare prompt/model/tool variants across the same dataset and see
 quality-cost-latency tradeoffs clearly.

Why this matters:
- developers need more than profiling; they need decision support
- experiments are the natural layer above datasets and evaluators

Planned work:

- [ ] Add experiment models and run manifests
- [ ] Support comparing variants across a dataset:
  prompt versions, model choices, tool configurations
- [ ] Report deltas for:
  cost, latency, token usage, and quality scores
- [ ] Add experiment summaries in Markdown and JSON
- [ ] Add baseline-vs-candidate comparison output for CI
- [ ] Keep execution local and scriptable

Definition of done:
- AgenticLens can answer "which variant is better?" using repeatable local
  runs instead of manual trace inspection.

### v0.6 — Prompt Registry and Configuration Tracking

Goal: make prompt and configuration changes explicit and traceable.

Why this matters:
- prompt drift and silent config changes are frequent causes of regressions
- traces are much more useful when they reference versioned artifacts

Planned work:

- [ ] Add local prompt objects with:
  `name`, `version`, `labels`, `tags`, `config`, `commit_message`
- [ ] Let steps reference prompt versions via `prompt_ref` instead of only raw
  prompt text
- [ ] Track per-step config metadata such as:
  `prompt_version`, `model_params`, `tool_schema_version`,
  `retrieval_index_version`
- [ ] Add prompt-aware comparisons in reports and experiments
- [ ] Keep the registry file-based and package-native

Definition of done:
- a regression can be tied back to the exact prompt/config change that caused
  it, without requiring a central prompt service.

### v0.7 — CI Guardrails and Policy Layer

Goal: convert observability and evaluation into enforceable release gates.

Why this matters:
- the real value of local-first tooling shows up in automation
- teams need "fail the build if quality regresses", not only richer reports

Planned work:

- [ ] Add policy models and CLI commands for rule execution
- [ ] Support local checks such as:
  cost caps, latency caps, retrieval-quality floors, score thresholds,
  duplicate-tool-call growth, and regression deltas
- [ ] Add exit-code semantics for CI pipelines
- [ ] Add baseline comparison commands for candidate-vs-main checks
- [ ] Support policy bundles checked into the repo

Definition of done:
- AgenticLens can be used as a local quality gate in CI, not just an offline
  analysis tool.

### v0.8 — Integrations and Importers

Goal: make the core model easy to adopt across real agent stacks.

Planned work:

- [x] LangChain / LangGraph adapter (`agenticlens.adapters.langchain`,
  optional `langchain` extra) — auto-instruments LLM/tool/retriever calls via
  callbacks
- [ ] Add integrations for:
  LiteLLM, OpenAI Agents SDK, CrewAI
- [ ] Add OpenTelemetry and OpenInference import paths
- [ ] Broaden provider support:
  Gemini, Ollama, vLLM, LiteLLM, Azure OpenAI
- [ ] Keep integrations in clearly separated modules

Definition of done:
- users can bring existing traces and frameworks into AgenticLens without
  rewriting their entire application.

### v0.9 — Optional Local UI

Goal: add a lightweight local inspection surface without turning the project
into a SaaS platform.

Planned work:

- [ ] Optional local web UI for traces, scores, datasets, and experiments
- [ ] Graph visualization for workflow structure
- [ ] Variant comparison and regression diff views
- [ ] Local file-backed mode first

Definition of done:
- users who want richer inspection get a local UI, while the package remains
  useful without it.

## Explicitly Out of Scope for Core

These may become separate projects, optional services, or future add-ons, but
they should not define the core package roadmap:

- hosted trace storage
- multi-tenant auth, RBAC, and organizations
- enterprise review queues and annotation operations
- Slack / PagerDuty / Teams alert routing
- SaaS billing, retention, and access-control workflows

## Suggested Package Shape Over Time

If the project grows, the cleanest long-term structure is:

1. `agenticlens-core`
   Models, tracing, scoring, datasets, evaluators, experiments, policies.
2. `agenticlens-integrations`
   Providers, frameworks, OTEL/OpenInference importers.
3. `agenticlens-ui`
   Optional local inspection UI.

This keeps the PyPI story clear: the core package remains the installable,
local-first engine, while richer layers stay optional.
