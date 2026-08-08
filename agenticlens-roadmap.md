# AgenticLens Product Roadmap

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
- multi-agent handoff analysis
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
- repeated-run statistics
- baseline-versus-candidate regression detection
- trace inspection and comparison CLI commands
- JSON and CSV comparison exports
- versioned research schemas

### Remaining work

- detect cyclic parent relationships
- associate retry spans with triggering failures
- classify retry outcomes
- detect duplicated context
- measure instrumentation overhead
- add minimum-sample guidance to comparison reports
- add Markdown trace and comparison reports

### Completion criteria

- all trace artifacts validate against published schemas
- existing profiler APIs remain compatible
- comparison results reproduce from saved traces
- privacy defaults and redaction behavior are documented
- performance overhead is measured

## v0.2.x — Evidence Provenance & Operational Intelligence

### Objective

Make every finding and recommendation traceable to its source evidence, and add
intelligent guidance for what analysis to run next.

### Planned deliverables

- first-class `Evidence` object on all findings and recommendations (source
  step/span, timestamp, confidence, derived reasoning chain)
- "next best analysis" recommendations — suggest what the user should inspect
  next based on workflow shape and current findings
- OpenTelemetry trace export — let agenticlens traces flow into
  Grafana/Jaeger/OTel-native systems
- import-layer enforcement in CI — prevent architectural drift as the package
  grows (e.g., `exporters/` must not import from `cli/`)
- AIOS conformance tooling in the CLI — commands such as
  `agenticlens validate workflow.json` and
  `agenticlens conformance --version 0.4 workflow.json`, with normative rules,
  fixtures, and expected behavior defined by `ai-operations-spec`

### Completion criteria

- every recommendation includes a provenance reference to its source spans
- next-step suggestions are generated for workflows with 3+ analysis findings
- OTel spans are emitted for profiled workflows when configured
- CI rejects forbidden cross-module imports
- conformance reports clearly distinguish AIOS-defined pass/fail rules from
  AgenticLens-specific presentation and CLI behavior

## v0.3 — Evaluation Foundation

### Objective

Evaluate task outcomes and execution requirements using versioned, reusable test
suites.

### Planned deliverables

- `TestCase` and `TestSuite` models
- `Evaluator`, `EvaluationContext`, and `Score` interfaces
- YAML and JSON test-suite loading
- evaluator registration
- native Python and HTTP targets
- JSON and Markdown evaluation reports
- evaluator and suite version capture

### Initial deterministic evaluators

- exact match
- contains match
- JSON Schema validation
- required fields
- required and forbidden tools
- tool-argument validation
- latency threshold
- cost threshold
- turn-count threshold
- custom business rules

### Completion criteria

- one Python agent and one HTTP agent can run the same suite
- every score identifies its evaluator and version
- reports distinguish measured and estimated values
- failed cases retain trace-level evidence

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
