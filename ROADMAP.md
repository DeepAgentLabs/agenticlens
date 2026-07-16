# Roadmap

## Product Direction

AgenticLens should aim to be a **local-first observability, evaluation,
operational intelligence, and governance-evidence toolkit for production AI
systems**.

The package should own the developer workflow that happens closest to code,
experiments, and CI:

- instrumentation and workflow capture
- AI Operations Specification adoption and reference implementation
- graph-aware trace structure
- cost, latency, and token analysis
- inference and serving observability
- framework and ecosystem integrations
- step-level and workflow-level scoring
- evaluator interfaces and local eval runs
- datasets, experiments, and regression checks
- prompt/version/config tracking
- incident and change-impact analysis
- standards-readiness and audit-style reporting
- advisory release and control decisions for production AI systems
- agent planning and decision-trace capture
- platform and infrastructure correlation, scoped to AI-relevant signals only

AgenticLens should **not** try to become a hosted observability platform or
full enterprise control plane inside the core package. Multi-user dashboards,
auth/RBAC, hosted storage, alert routing, deployment orchestration, and
enterprise ops workflows are useful, but they should remain optional layers on
top of the package rather than the center of the project.

## Ecosystem Role

Within the DeepAgentLabs ecosystem, the package boundary should stay clear:

- **AgenticLens observes, evaluates, explains, and recommends**
- **Agentic Chaos injects, validates, tests, and proves resilience**

That split keeps both packages coherent on PyPI while still telling one larger
story around operational reliability for production AI systems.

## AI Operations Specification

DeepAgentLabs defines and stewards the **AI Operations Specification**, a
versioned operational data model that enables interoperability between AI
frameworks, observability, resilience testing, and operational tooling.

The specification serves as the common model shared across:

- AgenticLens
- Agentic Chaos
- DeepAgentLabs MCP

AgenticLens is the flagship Python reference implementation for this
specification. Framework integrations convert framework-specific execution data
into it. The specification should evolve independently of any one framework,
provider SDK, orchestration library, or telemetry backend.

Third parties may define compatible extensions while preserving core
interoperability.

The specification should follow explicit versioning over time, for example
through `v1`, `v1.1`, and future major revisions once the format stabilizes.

When this roadmap refers to the workflow artifact, the primary concept is the
**AI Operations Specification**. `workflow.json` is the reference JSON
representation of that specification, not the specification itself.

## Architecture View

![AI Operations Ecosystem](https://raw.githubusercontent.com/DeepAgentLabs/.github/main/profile/assets/ai-operations-ecosystem.png)

## Guiding Principles

- **Package-first**: every major feature should be usable through Python and the
  CLI without requiring a backend.
- **Local-first**: runs, datasets, scores, regressions, incidents, and audits
  should work on local files by default.
- **CI-first**: the output should be useful not only for inspection, but for
  automated quality and release gates.
- **Framework-agnostic**: integrations matter, but the core data model should
  not depend on one framework.
- **Advisory-first**: when adding release or control functionality, start with
  evidence and recommendations before enforcement.
- **Additive evolution**: extend the AI Operations Specification in
  ways that preserve compatibility across its reference representations,
  including `workflow.json`.

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
- [x] Agentic-chaos interop via additive AI Operations Specification
  extensions

This release line establishes AgenticLens as a **cost and workflow profiling
tool** and the flagship Python reference implementation of the AI Operations
Specification.

## Capability Map

These capability families should be introduced gradually inside one coherent
package:

```text
agenticlens
├── observe
├── inference
├── infra
├── evaluate
├── compare
├── incidents
├── telemetry
├── safety
├── security
├── slos
├── lineage
├── planning
├── audit
├── release
├── control
├── integrations
└── workflow
```

Not all of these need to become top-level import packages immediately, but
they provide the long-term product map.

An initial integrations target map could include:

```text
integrations
├── langgraph
├── crewai
├── openai_agents
├── autogen
├── semantic_kernel
├── llamaindex
├── haystack
├── openinference
└── opentelemetry
```

Inference and serving observability should be treated as a first-class part of
the package direction, including:

- request latency distributions
- timeout and error rates
- fallback rates
- token consumption per request
- model and provider version correlation
- routing or serving-path visibility for AI requests

Platform and infrastructure correlation should stay a thin, narrowly-scoped
capability rather than a general infrastructure observability platform. It
should ingest basic accelerator and orchestration signals — GPU/NPU/TPU
utilization, CPU/memory pressure, Kubernetes pod and node health — only where
they help explain AI system behavior, such as correlating a latency spike or
failed step with GPU memory pressure or a pod eviction. Existing
infrastructure observability tools (Prometheus, Grafana, DCGM exporters, and
similar) remain authoritative for general infra monitoring; AgenticLens only
needs the slice of that signal that touches AI workload behavior.

## Roadmap

### v0.2 — Compare, SLOs, and Incident Foundations

Goal: extend profiling into operational comparison and reliability reporting
without changing the package identity.

Why this comes first:

- it is the most natural extension of today's profiling and analysis features
- it strengthens the package's runtime observability and operational-analysis
  story
- it keeps AgenticLens clearly library-first and PyPI-friendly

Planned work:

- [ ] Add baseline-versus-candidate workflow comparison
- [ ] Add compare reports for prompts, models, workflows, and RAG
  configurations
- [ ] Add a reproducible compare/eval harness with committed local artifacts,
  so benchmark deltas are reviewable in git and usable in CI
- [ ] Add explicit compare control-arm methodology where relevant, to separate
  real optimization gains from generic prompt-shortening or configuration noise
- [ ] Add built-in SLIs/SLO reports such as:
  `success_rate`, `timeout_rate`, `fallback_rate`, `tool_failure_rate`,
  `grounded_answer_rate`, `cost_per_successful_task`, `p95_latency`
- [ ] Add explicit inference-serving summaries covering latency distributions,
  error rates, timeout rates, fallback behavior, and token consumption
- [ ] Add cache-aware observability for providers that expose prompt-cache or
  cached-token usage, including cache-hit metrics and uncached-versus-cached
  input accounting
- [ ] Add lightweight incident summaries for failed or anomalous runs
- [ ] Add local run-history and trend summaries for cost, latency, token
  consumption, and estimated reducible spend across repeated workflow runs
- [ ] Add provenance metadata fields such as:
  `prompt_version`, `model_version`, `tool_version`, `run_id`, `environment`
- [ ] Add CLI commands such as:
  `agenticlens compare`, `agenticlens slos report`,
  `agenticlens incidents summarize`, `agenticlens trends`

Definition of done:

- AgenticLens can answer "what changed?", "did reliability regress?", and
  "what failed?" using local workflow artifacts derived from the AI Operations
  Specification.
- Compare results are reproducible locally and in CI, with saved artifacts that
  make regressions and claimed improvements easy to inspect.

### v0.3 — Evaluate, Lineage, Audit, and Richer Incidents

Goal: make AgenticLens an operational-intelligence toolkit rather than only a
profiler.

Why this matters:

- this is where GenAIOps alignment becomes much more visible
- observability becomes far more valuable when it is tied to readiness,
  lineage, and evidence
- it strengthens the standards-aligned story without turning the package into a
  deployment platform

Planned work:

- [ ] Add typed evaluation result models and pass/fail thresholds
- [ ] Add evaluation categories such as:
  `groundedness`, `faithfulness`, `retrieval_quality`, `task_completion`,
  `policy_compliance`
- [ ] Add evaluation harness documentation and artifact conventions that state
  clearly what is measured, what is estimated, and which claims are out of
  scope for a given report
- [ ] Add release-readiness scoring for candidate runs
- [ ] Add lineage tracking for prompts, models, configs, tools, and knowledge
  sources
- [ ] Add agent planning/decision-trace capture: recorded plan steps,
  replanning events, branch decisions, selected tool/agent choices, and other
  structured planning annotations where the underlying framework exposes them
- [ ] Add richer inference metadata such as provider/model version history,
  routing decisions, and serving-path context where available
- [ ] Add cache-effectiveness reporting that shows when repeated context is
  actually benefiting from provider-side caching versus remaining fully billed
- [ ] Add audit-style outputs such as:
  `observability coverage report`, `operational maturity assessment`,
  `standards-readiness report`
- [ ] Add richer incident reporting:
  timeline reconstruction, failed-run evidence, root-cause hints,
  postmortem-style exports
- [ ] Add normal-versus-degraded comparison flows using `agentic-chaos`
  artifacts
- [ ] Add CLI commands such as:
  `agenticlens evaluate`, `agenticlens audit`,
  `agenticlens incidents summarize`

Definition of done:

- AgenticLens can capture evaluation evidence, run lineage, and operational
  audit signals in a form that is exportable, scriptable, and reusable.
- Evaluation outputs are honest about limitations and preserve enough context to
  support code review, audit review, and regression triage.

### Cross-Cutting UX and CLI

These improvements support the roadmap above without changing the package's
local-first scope.

- [ ] Add `agenticlens init` to scaffold starter instrumentation, config, and
  CI-friendly commands for new repositories
- [ ] Expand CLI export flows so built-in formats are consistently reachable
  from commands, including Markdown and Jira-oriented outputs where available
- [ ] Add cache-savings displays to CLI and exported reports, including cached
  token counts, cache-hit percentages, and estimated cost avoided when pricing
  data is available
- [ ] Add cache-oriented recommendations that identify repeated prompts or
  stable context blocks that are likely cacheable on supported providers
- [ ] Keep setup idempotent and safe to re-run, with dry-run support where it
  improves developer trust

### v0.4 — Safety, Security, and Advisory Release Controls

Goal: expand into production AI operational intelligence while staying
advisory-first.

Why this matters:

- it covers more of the GenAIOps operational story without trying to replace
  CI/CD, Kubernetes, or security platforms
- it keeps the package focused on evidence, analysis, and recommendations
- it creates a strong standards-informed story while preserving a clean PyPI
  identity

Planned work:

- [ ] Add safety-observability signals such as:
  hallucination indicators, groundedness failures, unsafe-output counts,
  guardrail activations, human-escalation triggers
- [ ] Add security-observability signals such as:
  prompt-injection indicators, suspicious tool activity, secret leakage
  signals, abnormal agent loops, unauthorized tool attempts
- [ ] Add advisory release checks such as:
  `agenticlens release check`,
  `agenticlens release rollback-recommendation`
- [ ] Add configurable release gates based on evaluation, reliability, and
  policy thresholds
- [ ] Add advisory runtime-control recommendations such as:
  model fallback, tool disable, cost ceiling breach, latency threshold breach,
  human-review routing
- [ ] Keep external systems optional via adapters rather than re-implementing
  deployment infrastructure

Definition of done:

- AgenticLens can evaluate whether a production AI system is healthy,
  release-ready, and regressing or improving, while still acting primarily as a
  local-first analysis toolkit.

### v0.5 — Framework Integrations

Goal: make it easy for real-world AI frameworks and agent runtimes to emit the
AI Operations Specification without each team hand-rolling adapters.

Why this matters:

- it makes the specification concrete and adoptable across ecosystems
- it reduces instrumentation friction without abandoning the explicit core model
- it clarifies how AgenticLens interoperates with the broader AI tooling stack

Planned work:

- [ ] Add an `integrations` capability area with stable adapter interfaces
- [ ] Add first-party framework targets such as LangGraph, CrewAI,
  OpenAI Agents SDK, AutoGen, Semantic Kernel, LlamaIndex, and Haystack
- [ ] Add interoperability adapters for OpenInference and OpenTelemetry where
  they help convert external traces into the AI Operations Specification
- [ ] Document framework-to-spec mapping rules and coverage expectations
- [ ] Ensure framework execution can be normalized into the reference JSON
  representation, `workflow.json`, without making any one framework the core
  model

Definition of done:

- Framework execution can be converted into the AI Operations Specification
  through documented integrations and adapter interfaces.

### v0.6 — Telemetry Export and Observability Interop

Goal: make AgenticLens interoperable with mainstream observability platforms
without making any vendor format the core model.

Why this matters:

- the `AI Operations Specification` should remain the canonical,
  richest artifact
- many teams still want traces and attributes to flow into existing APM and
  observability systems
- OpenTelemetry and OTLP give AgenticLens a vendor-neutral bridge to tools such
  as Grafana, New Relic, Dynatrace, Datadog, Elastic, Honeycomb, and others

Planned work:

- [ ] Add a `telemetry` capability area and exporter layer for workflow-to-trace
  conversion
- [ ] Define canonical mapping rules from workflow artifacts to observability
  formats:
  workflow -> trace, steps -> spans, workflow/step metadata -> attributes,
  chaos/incidents/evaluations -> events or annotations
- [ ] Ensure inference-serving attributes such as provider, model, latency,
  timeout, routing, and token counts map cleanly into exported telemetry
- [ ] Add OpenTelemetry trace export support
- [ ] Add OTLP export support for downstream ingestion by external platforms
- [ ] Document compatibility targets for popular observability platforms such as
  Grafana, Datadog, New Relic, Dynatrace, Elastic, and Honeycomb
- [ ] Add CLI flows such as:
  `agenticlens export --format otel`
  `agenticlens export --format otlp`
- [ ] Preserve the AI Operations Specification reference JSON
  representation, `workflow.json`, as the richest portable artifact even when
  exporting to other telemetry formats
- [ ] Keep vendor-specific adapters optional and downstream from the common
  OTEL/OTLP mapping layer

Definition of done:

- AgenticLens can export AI workflow observability data into standard telemetry
  pipelines while keeping the AI Operations Specification as its source of
  truth.

### v0.7 — Platform & Infrastructure Correlation

Goal: close the remaining gap between AI-workload observability and the
supporting hardware/orchestration layer, without duplicating general-purpose
infrastructure observability platforms.

Why this comes after telemetry export:

- it depends on having stable step/workflow telemetry to correlate against
- it should stay a thin, AI-relevant slice of infra signal, not a competing
  infra observability product
- it closes out the last uncovered capability area in the roadmap

Planned work:

- [ ] Add lightweight infra-signal ingestion adapters: GPU/NPU/TPU utilization
  and memory via NVML/DCGM, and CPU/memory/pod/node health via the Kubernetes
  metrics API
- [ ] Correlate ingested infra signals with step-level latency, timeout, and
  failure events already captured in the AI Operations Specification
  reference artifact, `workflow.json`
- [ ] Add infra-correlation findings such as "latency spike coincided with GPU
  memory pressure" or "step failure coincided with a pod eviction/restart"
- [ ] Scope ingestion strictly to signals that plausibly explain AI system
  behavior; do not attempt general infra monitoring, alerting, or dashboards
- [ ] Add CLI commands such as: `agenticlens infra correlate`
- [ ] Document this as a supporting capability, explicitly deferring to
  Prometheus/Grafana/DCGM-style tools for general infrastructure observability

Definition of done:

- AgenticLens can point to a specific infra signal (accelerator pressure, pod
  health) as a plausible cause behind an observed latency spike or failure,
  by correlating local workflow artifacts from the AI Operations Specification
  with optional imported infra-signal data.
- The capability stays additive and optional — it does not become a dependency
  for any other roadmap area.

## Additional Longer-Term Foundations

These foundations still matter and can be pulled forward if later work depends
on them:

- graph-aware trace structure
- score and evaluator APIs
- datasets and trace-to-dataset curation
- experiment runner
- integrations and importers
- observability-platform adapters built on top of the common telemetry export
  layer, including Grafana, Datadog, New Relic, Dynatrace, Elastic, and
  Honeycomb targets
- optional local UI

They should support the operational roadmap above rather than compete with it.

## Explicitly Out of Scope for Core

These may become separate projects, optional services, or future add-ons, but
they should not define the core package roadmap:

- hosted trace storage
- multi-tenant auth, RBAC, and organizations
- enterprise review queues and annotation operations
- Slack / PagerDuty / Teams alert routing
- SaaS billing, retention, and access-control workflows
- full deployment orchestration
- live traffic shifting
- Kubernetes operator behavior
- general-purpose infrastructure observability platform (full
  Prometheus/Grafana/DCGM replacement)
- enterprise approval workflow engines
- full SOC / SIEM replacement platforms

## Possible Future Modularization

If the project grows significantly, modular packaging may become useful later,
but it should remain a deployment detail rather than a near-term roadmap
commitment. For now, the default story should stay simple: `pip install
agenticlens`.

Possible future splits could include:

1. `agenticlens-core`
   Models, tracing, evaluation, SLOs, incidents, lineage, audit, policies.
2. `agenticlens-integrations`
   Providers, frameworks, OTEL/OpenInference importers, release adapters.
3. `agenticlens-ui`
   Optional local inspection UI.
