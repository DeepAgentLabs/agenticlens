# AgenticLens Product Roadmap

## Release Status

Shipped PyPI releases: `0.1.1` → `0.1.2` → `0.2.0` → `0.3.0` → `0.4.0`
(current, 2026-08-08) — see [CHANGELOG.md](CHANGELOG.md). The version labels
below are this roadmap's release-plan sequence, not PyPI tags — shipped
`0.4.0` already covers most of planned `v0.2` and `v0.3`, and pulled pieces
forward from `v0.5` and `v1.0`.

- **v0.2** ✅ Delivered in `0.3.0` — Trace and Comparison Foundation
  (hierarchical tracing, cyclic-parent detection, retry attribution,
  regression detection, baseline/candidate comparison, and Markdown reports)
- **v0.2.x** ✅ Delivered in `0.4.0` — Evidence Provenance & Operational
  Intelligence (`Evidence` objects, next-best-analysis guidance,
  import-layer enforcement, OpenTelemetry trace export, and AIOS draft
  validation/conformance CLI are delivered)
- **v0.3** 🏗️ Mostly complete — Evaluation Foundation (evaluator framework,
  deterministic checks, custom/LLM-judge evaluators, release gates,
  `evaluate`/`gate` CLI, and live agent targets); judge calibration and
  dataset management still open
- **v0.4** 🚧 Planned — Experiments and Statistical Comparison
- **v0.5** 🚧 Planned — Advanced Evaluation and Diagnosis (semantic/safety/RAG
  scoring partially pulled forward into `v0.3`)
- **v0.6** 🚧 Planned — Test-Suite and Dataset Management
- **v0.7** 🚧 Planned — ModelFit
- **v0.8** 🚧 Planned — Advisory Runtime Routing
- **v0.9** 🚧 Planned — Optimization Intelligence
- **v1.0** 🚧 Planned — Production and Enterprise Readiness (release gates
  partially pulled forward into `v0.3`)

## Purpose

This roadmap defines the planned evolution of AgenticLens from a local workflow
profiler into an open-source runtime intelligence and evaluation framework for
agentic AI systems.

The roadmap is directional. Release scope may change as implementation evidence,
compatibility requirements, and contributor feedback develop. Features are
considered complete only when they are implemented, documented, tested, and
available through a stable Python or CLI interface.

## Product Direction

AgenticLens provides local-first tools to observe, evaluate, compare, optimize,
and govern AI workflows.

The platform is intended to answer:

- What happened during an agent run?
- Where were tokens, latency, and cost consumed?
- Did the agent complete the intended task?
- Which model, prompt, retrieval strategy, or workflow performed best?
- Did a candidate configuration introduce a regression?
- Which execution steps added cost without improving outcomes?
- Is a workflow operating within defined reliability and policy limits?

The primary operating principle is:

> Instrument once, evaluate continuously, and optimize from recorded evidence.

## Product Principles

### Package-first

Core capabilities must remain usable through Python and the CLI without a
hosted service.

### Local-first

Tracing, evaluation, comparison, and reporting must work with local artifacts by
default.

### Framework-neutral

Core models must not depend on one provider, agent framework, orchestration
library, or telemetry backend.

### Evidence-backed

Findings and recommendations must identify the measurements, thresholds, and
trace evidence on which they are based.

### Advisory-first

Early release and control features should report and recommend before they
enforce or modify production behavior.

### Compatible evolution

Schemas and public APIs must use explicit versioning. Additive changes are
preferred where practical.

### Honest measurement

Measured, estimated, projected, and inferred values must be distinguishable in
reports and APIs.

## Cross-Project Dependencies

AgenticLens is intentionally package-first, but several roadmap items need
cross-project coordination before they should be marked complete.

- `ai-operations-spec`
  Provides the normative artifact model and conformance rules for AIOS-aligned
  validation, schema references, and interoperability claims.
- `agentic-chaos`
  Produces resilience/fault evidence that AgenticLens may analyze, summarize,
  or validate as part of cross-tool workflows.
- `deep-agentic-core-mcp`
  Exposes AgenticLens capabilities through MCP and is a useful sibling check
  for CLI/API behavior that is expected to be consumable by hosts and tools.

For roadmap items with ecosystem impact, contributors should distinguish:

- `Depends on`: a sibling repo or spec milestone that must exist first.
- `Coordinate with`: sibling repos that should be updated or verified together.
- `Validate in`: the sibling repos or fixtures that should be checked before
  the roadmap item is marked done.

## Definition of Done

A roadmap item is done only when all applicable work is complete:

- implementation is merged and usable through the intended Python API, CLI, or
  artifact surface
- tests or regression fixtures cover the behavior
- user-facing examples and docs are added or updated
- `README.md` and this roadmap are updated when the feature changes user
  expectations or milestone status
- schema/version compatibility is handled explicitly for any public contract
  change
- sibling-project dependencies and coordination checks are recorded for
  ecosystem-facing work
- release metadata (`pyproject.toml`, `src/agenticlens/__init__.py`,
  `CHANGELOG.md`) is updated when the work is part of a release-ready change
  set

## Current Capabilities

The following capabilities are implemented in the current development line.

### Workflow profiling

- explicit `profile()` and `step()` instrumentation
- OpenAI and Anthropic usage extraction
- prompt, completion, and total-token metrics
- latency, time-to-first-token, and throughput metrics
- per-step, per-agent, and workflow summaries
- JSON, CSV, Markdown, and Jira-oriented exports

### Cost intelligence

- user-defined pricing overrides
- cached live pricing from the LiteLLM community feed
- bundled offline pricing fallback
- stale-cache fallback when pricing refresh fails
- explicit unknown-pricing behavior
- workflow and step cost calculation
- model-swap cost recommendations
- projected per-run and monthly savings

### Optimization analysis

- repeated prompt detection
- excessive retrieval detection
- RAG chunk-utility analysis
- long-history detection
- duplicate tool-call detection
- multi-agent handoff analysis, including handoff-bloat findings
- agent-aware summaries in CLI analysis output
- model-tier cost comparison
- agentic-chaos impact findings

### Research trace foundation

- framework-neutral `Run` and nested `Span` models
- planning, model, memory, retrieval, tool, validation, retry, delegation, and
  final-response span types
- token, latency, cost, status, and error capture
- parent-child trace validation
- opt-in payload capture with recursive redaction
- JSON trace persistence
- trace inspection through the CLI

### Diagnostics and comparison

- memory-share analysis
- retry token, latency, and cost analysis
- deterministic findings with span-level evidence
- repeated-run baseline and candidate groups
- mean, median, P95, standard deviation, and coefficient of variation
- success-rate and cost-per-successful-task reporting
- configurable regression detection
- JSON and CSV comparison reports
- CI-compatible regression exit status

### Evaluation and release gates

- versioned YAML and JSON test suites (`TestSuite`, `TestCase`)
- a unified, provider-neutral evaluator contract (`Evaluator`, `EvaluationContext`,
  `Score`, `EvaluatorRegistry`)
- built-in deterministic checks: exact match, required-substring match, required
  and forbidden tool calls, latency threshold, cost threshold
- custom evaluators via `CallableEvaluator`, and model-based judges via
  `LLMJudgeEvaluator`, sharing one normalized score contract
- evaluation against recorded samples and their AgenticLens traces (not yet
  live Python or HTTP agent invocation)
- JSON and standalone HTML evaluation reports
- configurable release gates on pass rate, average score, failed-case count,
  average latency, and total cost, with CI-friendly exit codes
- `evaluate` and `gate` CLI commands
- a deterministic, offline LangGraph reference workflow demonstrating tracing,
  evaluation, and release-gate output together

### Artifact contracts

- versioned trace schema
- versioned finding schema
- versioned comparison-report schema
- schema inclusion in wheel distributions

## Capability Architecture

```text
Application and agent runtimes
            |
            v
Instrumentation
├── workflow profiler
└── structured trace API
            |
            v
Local artifacts and schemas
            |
     +------+------+----------------+
     |             |                |
     v             v                v
Diagnostics    Evaluation      Comparison
     |             |                |
     +-------------+----------------+
                   |
                   v
          Recommendations and gates
                   |
          +--------+---------+
          |                  |
          v                  v
        CLI/API        Optional dashboard
```

## Release Plan

## v0.2 — Trace and Comparison Foundation

### Objective

Establish reproducible execution traces, cost intelligence, deterministic
diagnostics, and baseline comparison.

### Delivered

- hierarchical run and span tracing
- raw token, latency, cost, retry, and tool metrics
- payload redaction
- memory and retry findings
- cyclic parent detection
- retry attribution and retry outcome classification
- duplicated-context detection
- repeated-run statistics
- baseline-versus-candidate regression detection
- minimum-sample guidance in comparison reports
- trace inspection and comparison CLI commands
- JSON, CSV, and Markdown comparison exports
- Markdown trace reports
- versioned research schemas

### Remaining work

- measure instrumentation overhead

### Completion criteria

- all trace artifacts validate against published schemas
- existing profiler APIs remain compatible
- comparison results reproduce from saved traces
- privacy defaults and redaction behavior are documented
- [ ] performance overhead is measured

## v0.2.x — Evidence Provenance & Operational Intelligence

### Objective

Make every finding and recommendation traceable to its source evidence, and add
intelligent guidance for what analysis to run next.

### Delivered

- first-class `Evidence` object on findings and recommendations (source
  step/span, timestamp, confidence, derived reasoning chain)
- "next best analysis" recommendations — suggest what the user should inspect
  next based on workflow shape and current findings
- import-layer enforcement in CI — prevent architectural drift as the package
  grows (e.g., `exporters/` must not import from `cli/`)
- OpenTelemetry trace export — let agenticlens traces flow into
  Grafana/Jaeger/OTel-native systems via OTLP/HTTP JSON export
- AIOS draft validation and conformance tooling in the CLI — commands such as
  `agenticlens validate workflow.json` and
  `agenticlens conformance --version 0.4 workflow.json`, with normative rules,
  fixtures, and expected behavior defined by `ai-operations-spec`, and
  draft-alignment reporting that distinguishes AIOS-defined pass/fail rules
  from AgenticLens-specific presentation

### Completion criteria

- [x] every recommendation includes a provenance reference to its source spans
- [x] next-step suggestions are generated from current findings
- [x] OTel spans are emitted for profiled workflows when configured
- [x] CI rejects forbidden cross-module imports
- [x] conformance reports clearly distinguish AIOS-defined pass/fail rules from
      AgenticLens-specific presentation and CLI behavior

## v0.3 — Evaluation Foundation

### Objective

Evaluate task outcomes and execution requirements using versioned, reusable test
suites.

### Delivered

- `TestCase` and `TestSuite` models with versioned YAML/JSON loading
- `Evaluator`, `EvaluationContext`, `Score`, and `EvaluatorRegistry` interfaces
- built-in deterministic checks: exact match, required-substring match,
  required/forbidden tools, JSON Schema validation, required fields,
  required tool arguments, turn-count threshold, latency threshold, and cost
  threshold
- `CallableEvaluator` for custom Python rules, semantic, safety, and RAG
  checks, `BusinessRuleEvaluator`, and `LLMJudgeEvaluator` for model-based
  judgments, on one shared score contract
- JSON and standalone HTML evaluation reports (HTML in place of the
  originally planned Markdown report)
- configurable release gates (pass rate, average score, failed cases,
  latency, cost) with CI-friendly exit codes, via the `evaluate` and `gate`
  CLI commands
- live Python and HTTP evaluation targets via `evaluate-live`
- a deterministic, offline LangGraph reference workflow demonstrating the
  full trace-to-evaluation-to-gate path

This pulled forward parts of the semantic, safety, RAG, and LLM-judge scoring
originally planned for [v0.5](#v05--advanced-evaluation-and-diagnosis), and
part of the release-gate concept originally planned for
[v1.0](#v10--production-and-enterprise-readiness), via the shared evaluator
contract rather than as separate subsystems.

### Remaining work

- built-in provider clients for LLM-judge calls (applications currently
  supply the model call themselves)
- asynchronous and batched evaluation execution
- judge calibration reports and statistical confidence intervals
- evaluation dataset management
- automatic framework event adapters beyond the LangGraph reference demo
- structured judge verdict fields on `LLMJudgeEvaluator` — verdict
  (agree/partially-agree/disagree), confidence score, and a factual-grounding
  breakdown (unsupported claims, evidence missed), plus guidance to run the
  judge on a different model than the one under evaluation to avoid
  self-confirmation bias; modeled on `devops-open-agent`'s LLM-as-a-Judge
  verifier output
- cooldown-protected webhook notifications on `gate` threshold breaches
  (generic webhook, Slack/Teams-shaped payload) so CI/scheduled `gate` runs
  can alert without paging on every single run; modeled on
  `devops-open-agent`'s per-user alert-cooldown pattern for budget and
  investigation alerts

### Completion criteria

- [x] every score identifies its evaluator and version
- [x] reports distinguish measured and estimated values (evaluated scores vs.
      unavailable/omitted cost and latency data)
- [x] failed cases retain trace-level evidence
- [x] one Python agent and one HTTP agent can run the same suite live

## v0.4 — Experiments and Statistical Comparison

### Objective

Compare models and agent configurations against the same test suite with
repeated trials.

### Planned deliverables

- experiment and variant manifests
- repeated trials per test case
- prompt, model, retrieval, memory, and retry-policy comparison
- pass@k and pass^k
- confidence intervals
- consistency and stability summaries
- baseline regression analysis
- test-level score heatmaps
- Pareto analysis
- HTML and CSV reports

### Completion criteria

- at least three variants can be compared in one experiment
- trial counts and randomization settings are recorded
- regression reports include minimum-sample warnings
- quality, cost, latency, and reliability are shown together

## v0.5 — Advanced Evaluation and Diagnosis

### Objective

Evaluate semantic quality and execution trajectories, then attribute failures to
recorded evidence.

### Planned deliverables

- model-based judge interface
- judge prompt and model versioning
- groundedness, relevance, completeness, and citation evaluators
- tool-trajectory and agent-goal evaluators
- handoff and loop evaluators
- safety evaluators
- evaluator calibration reports
- failure taxonomy
- deterministic diagnosis rules
- anomaly detection
- faulty-step and faulty-agent attribution
- incident timeline reconstruction
- investigation-style narratives on top of recommendations — root-cause
  explanations of waste, retries, handoff bloat, or tool inefficiency
- richer CLI subcommands for inspection (`inspect`, `compare`, `trace show`,
  `report explain`)
- richer conformance commands and reporting (`conformance`, spec-version
  selection, structured pass/fail summaries)
- analysis guardrails (budget limits, recursion-depth caps, stagnation
  detection for automated analyzers)

### Completion criteria

- deterministic and model-based scores are reported separately
- judge cost is recorded
- evaluator disagreement is visible
- diagnoses include confidence and supporting spans
- attribution accuracy is evaluated on controlled failures

## v0.6 — Test-Suite and Dataset Management

### Objective

Support the creation, review, versioning, and reuse of evaluation datasets.

### Planned deliverables

- test-case and suite editors
- immutable suite versions
- CSV and JSON imports
- production trace conversion
- user-feedback conversion
- synthetic variation generation
- tags and domain categories
- train, validation, and test splits
- duplicate detection
- PII masking
- approval metadata

### Completion criteria

- traces can be converted into reviewable test cases
- approved suite versions are immutable
- regression suites can run in CI
- sensitive fields can be masked before storage

## v0.7 — ModelFit

### Objective

Recommend models for defined task categories under quality, cost, latency,
safety, provider, and deployment constraints.

### Planned deliverables

- task taxonomy
- constraint configuration
- weighted scoring
- Pareto frontier
- cost-per-success ranking
- recommendation confidence
- recommendation explanation
- alternative and fallback models
- task-level model matrix

### Completion criteria

- recommendations are generated by task category
- hard constraints are enforced
- savings estimates are tied to experiment evidence
- quality risks and alternatives are reported

## v0.8 — Advisory Runtime Routing

### Objective

Use evaluation evidence to recommend or select models at runtime with complete
decision records.

### Planned deliverables

- routing SDK
- rule-based and score-based routing
- policy-aware routing
- fallback chains
- provider failover
- confidence thresholds
- human escalation
- shadow and canary modes
- routing audit log

### Completion criteria

- routing decisions are explainable
- fallback behavior is tested
- shadow-mode performance is measurable
- policy violations can be blocked when enforcement is enabled

## v0.9 — Optimization Intelligence

### Objective

Generate evidence-backed recommendations across prompts, retrieval, memory,
tools, models, and multi-agent workflows.

### Planned deliverables

- prompt compression and caching recommendations
- retrieval and reranking recommendations
- memory retention and summarization recommendations
- tool caching and retry recommendations
- redundant-step and unnecessary-handoff detection
- quality-cost trade-off analysis
- projected benefit, confidence, and risk
- accepted and rejected recommendation tracking

### Completion criteria

- recommendations cite measured evidence
- expected benefit and quality risk are separated
- projected and observed outcomes are reported independently
- recommendation outcomes can be evaluated after adoption

## v1.0 — Production and Enterprise Readiness

### Objective

Provide stable contracts, policy controls, audit evidence, and supported
deployment options.

### Planned deliverables

- stable public APIs and schemas
- organizations and projects
- authentication and role-based access controls
- audit logs
- model and prompt registries
- policy-as-code
- retention and PII controls
- release gates
- compliance exports
- private evaluator support
- Kubernetes and Helm deployment options

### Completion criteria

- public compatibility policy is published
- upgrade and migration paths are documented
- governance decisions produce audit evidence
- release gates are reproducible
- supported deployment modes pass security review

## Ecosystem Integrations

Integrations will be introduced after the trace and evaluation contracts are
stable enough to map framework behavior consistently.

A deterministic LangGraph example demonstrates tracing, evaluation, and
release-gate output together (see [v0.3](#v03--evaluation-foundation)), but
this is a reference demo, not a first-class, maintained integration package.

Planned targets include:

- LangGraph
- OpenAI Agents SDK
- CrewAI
- AutoGen
- Semantic Kernel
- LlamaIndex
- Haystack
- HTTP agents
- MCP-hosted agents
- OpenInference
- OpenTelemetry and OTLP

Integration packages must document coverage and any framework behavior that
cannot be represented in the core schema.

## Success Measures

### Developer experience

- time required to instrument a representative workflow
- percentage of runs that produce valid artifacts
- reproducibility of local and CI reports
- compatibility across supported Python versions

### Evaluation quality

- evaluator agreement and calibration
- regression-detection precision and recall
- repeated-run stability
- trace coverage for failed cases

### Operational value

- cost per successful task
- reduction in avoidable tokens and retries
- improvement in P95 latency
- reduction in undiagnosed failures
- time required to identify the responsible step

## Early Non-Goals

The following are not near-term core objectives:

- autonomous production prompt rewriting
- automatic production model replacement
- live traffic shifting
- a general-purpose infrastructure monitoring platform
- a full SOC or SIEM replacement
- a full deployment orchestrator
- a universal score intended to summarize every agent quality dimension
- a hosted multi-tenant service as a requirement for core functionality

## Documentation Policy

Public documentation must:

- describe implemented and planned capabilities separately
- use stable product terminology
- avoid unsupported performance or quality claims
- identify experimental APIs
- state limitations and required operator judgment
- include runnable examples where practical
- remain consistent with the current code and schemas

The supporting research plan is maintained in
`AgenticLens_Research_and_Development_Roadmap.md`. Research metrics described
there remain experimental until implemented and validated.
