# Roadmap

## Product Direction

AgenticLens should aim to be a **local-first observability, evaluation,
operational intelligence, and governance-evidence toolkit for production AI
systems**.

The package should own the developer workflow that happens closest to code,
experiments, and CI:

- instrumentation and workflow capture
- graph-aware trace structure
- cost, latency, and token analysis
- inference and serving observability
- step-level and workflow-level scoring
- evaluator interfaces and local eval runs
- datasets, experiments, and regression checks
- prompt/version/config tracking
- incident and change-impact analysis
- standards-readiness and audit-style reporting
- advisory release and control decisions for production AI systems

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

## Capability Map

These capability families should be introduced gradually inside one coherent
package:

```text
agenticlens
├── observe
├── inference
├── evaluate
├── compare
├── incidents
├── telemetry
├── safety
├── security
├── slos
├── lineage
├── audit
├── release
└── control
```

Not all of these need to become top-level import packages immediately, but
they provide the long-term product map.

Inference and serving observability should be treated as a first-class part of
the package direction, including:

- request latency distributions
- timeout and error rates
- fallback rates
- token consumption per request
- model and provider version correlation
- routing or serving-path visibility for AI requests

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
- [ ] Add built-in SLIs/SLO reports such as:
  `success_rate`, `timeout_rate`, `fallback_rate`, `tool_failure_rate`,
  `grounded_answer_rate`, `cost_per_successful_task`, `p95_latency`
- [ ] Add explicit inference-serving summaries covering latency distributions,
  error rates, timeout rates, fallback behavior, and token consumption
- [ ] Add lightweight incident summaries for failed or anomalous runs
- [ ] Add provenance metadata fields such as:
  `prompt_version`, `model_version`, `tool_version`, `run_id`, `environment`
- [ ] Add CLI commands such as:
  `agenticlens compare`, `agenticlens slos report`,
  `agenticlens incidents summarize`

Definition of done:

- AgenticLens can answer "what changed?", "did reliability regress?", and
  "what failed?" using local workflow artifacts.

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
- [ ] Add release-readiness scoring for candidate runs
- [ ] Add lineage tracking for prompts, models, configs, tools, and knowledge
  sources
- [ ] Add richer inference metadata such as provider/model version history,
  routing decisions, and serving-path context where available
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

### v0.5 — Telemetry Export and Observability Interop

Goal: make AgenticLens interoperable with mainstream observability platforms
without making any vendor format the core model.

Why this matters:

- the `AI Operations Workflow Specification` should remain the canonical,
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
- [ ] Preserve `workflow.json` as the richest portable artifact even when
  exporting to other telemetry formats
- [ ] Keep vendor-specific adapters optional and downstream from the common
  OTEL/OTLP mapping layer

Definition of done:

- AgenticLens can export AI workflow observability data into standard telemetry
  pipelines while keeping the workflow specification as its source of truth.

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
- enterprise approval workflow engines
- full SOC / SIEM replacement platforms

## Suggested Package Shape Over Time

If the project grows, the cleanest long-term structure is still package-first
and modular:

1. `agenticlens-core`
   Models, tracing, evaluation, SLOs, incidents, lineage, audit, policies.
2. `agenticlens-integrations`
   Providers, frameworks, OTEL/OpenInference importers, release adapters.
3. `agenticlens-ui`
   Optional local inspection UI.
