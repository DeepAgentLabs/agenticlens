# AgenticLens Research Program

## Document Status

| Field | Value |
| --- | --- |
| Document type | Supporting research program |
| Product roadmap | `agenticlens-roadmap.md` |
| Implementation repository | `DeepAgentLabs/agenticlens` |
| Status | Active |
| Scope | Measurement, evaluation, diagnosis, and optimization research |

This document defines the AgenticLens research program. It records research
questions, experimental constructs, benchmark requirements, validation methods,
and publication outputs. It does not establish committed product scope.
Product commitments are defined only in `agenticlens-roadmap.md`.

## Research Objective

The program evaluates whether structured execution traces can make agentic AI
systems measurable, diagnosable, and optimizable across frameworks, models, and
task categories.

The primary research question is:

> To what extent can structured execution traces support reliable measurement,
> failure attribution, and evidence-based optimization of agentic AI workflows?

The research program covers five capability areas:

1. execution measurement
2. agent evaluation
3. runtime observability
4. failure diagnosis
5. workflow optimization

Research must proceed in this order. Diagnostic and optimization claims require
validated measurements and reproducible execution artifacts.

## Repository Governance

The installable research implementation remains within the AgenticLens product
repository.

```text
DeepAgentLabs/
├── agenticlens
├── agenticlens-benchmarks
└── agenticlens-research
```

### AgenticLens

The `agenticlens` repository contains:

- instrumentation
- trace schemas
- raw metrics
- evaluation interfaces
- deterministic diagnosis
- optimization analysis
- CLI commands
- reports
- framework adapters

### AgenticLens Benchmarks

The `agenticlens-benchmarks` repository may be created when benchmark datasets,
framework implementations, recorded traces, and reproduction scripts can no
longer be maintained effectively in the product repository.

Its scope is limited to:

- benchmark datasets
- framework-specific benchmark agents
- experiment configurations
- baseline results
- reproduction scripts

### AgenticLens Research

The `agenticlens-research` repository may be created when a publication package
requires independent versioning.

Its scope is limited to:

- paper-specific experiments
- statistical analysis
- figures and tables
- ablation studies
- supplementary material
- archived publication artifacts

The research program must not introduce a second product implementation or
competing package identity.

# Measurement Model

## Unified Trace

Every execution is represented as one run containing hierarchical spans.

```text
Run
├── PlanningSpan
├── ModelCallSpan
├── MemoryReadSpan
├── MemoryWriteSpan
├── RetrievalSpan
├── ToolCallSpan
├── ValidationSpan
├── RetrySpan
├── DelegationSpan
└── FinalResponseSpan
```

### Run Fields

The minimum run representation includes:

- schema version
- run ID
- trace ID
- application name
- framework and version
- task ID and type
- experiment and variant IDs
- start and completion timestamps
- status
- task-success result
- total latency
- input and output tokens
- estimated cost
- error classification
- extensible metadata

### Span Fields

The minimum span representation includes:

- span ID
- parent span ID
- span name and type
- agent name
- provider and model
- tool name
- retry number
- start and completion timestamps
- latency
- input and output tokens
- estimated cost
- status
- error classification
- input and output references
- redacted payload fields
- extensible attributes

### Trace Requirements

Trace artifacts must be:

- framework-neutral
- provider-neutral
- hierarchical
- JSON serializable
- explicitly versioned
- safe for configurable redaction
- validatable without network access
- inexpensive enough for repeated experiments
- compatible with distributed-tracing concepts

# Raw Metrics

Composite metrics must not replace raw measurements in reports. Every composite
score must retain the raw measurements required to reproduce it.

## Token Metrics

Required token measurements include:

- total input tokens
- total output tokens
- total tokens
- tokens by agent
- tokens by span type
- tokens by model
- memory tokens
- retrieval-context tokens
- tool-schema tokens
- retry tokens
- duplicated-context tokens
- final-answer tokens

### Memory Share

```text
memory_share = memory_tokens / total_tokens
```

### Retry Token Share

```text
retry_token_share = retry_tokens / total_tokens
```

### Planning Token Share

```text
planning_token_share = planning_tokens / total_tokens
```

### Output Efficiency

```text
output_efficiency = final_answer_tokens / total_tokens
```

Output efficiency measures token allocation. It does not measure answer quality.

## Latency Metrics

Required latency measurements include:

- end-to-end latency
- latency by span
- latency by span type
- model latency
- tool latency
- retrieval latency
- memory latency
- retry latency
- time to first model request
- model time to first token, when available
- agent response-start latency
- P50, P95, and P99 across repeated runs

Agent response-start latency should be decomposed where instrumentation permits:

```text
agent_response_start =
    planning_latency
  + memory_latency
  + retrieval_latency
  + tool_latency
  + model_queue_latency
  + model_time_to_first_token
```

Missing components must remain missing rather than being reported as zero.

## Cost Metrics

Required cost measurements include:

- input cost
- output cost
- total run cost
- cost by model
- cost by agent
- cost by span type
- retry cost
- failed-run cost
- cost per successful task

```text
cost_per_successful_task =
    total_cost / successful_tasks
```

Estimated costs must identify the pricing source and pricing timestamp where
available.

## Reliability Metrics

Required reliability measurements include:

- task-success rate
- failure rate
- timeout rate
- tool-failure rate
- fallback rate
- retry rate
- recovery rate
- validation-failure rate
- human-escalation rate

```text
task_success_rate = successful_runs / total_runs
```

```text
recovery_rate = recovered_failures / recoverable_failures
```

# Experimental Metrics

Experimental metrics must satisfy the following requirements:

- explicit version identifier
- published formula
- defined input measurements
- configurable weights where applicable
- sensitivity analysis
- ablation analysis
- comparison with raw metrics
- stated limitations
- no universal validity claim without cross-domain evidence

## Agent Efficiency Utility

### Objective

Measure the relationship between task outcome and operational consumption.

### Candidate Form

```text
efficiency_utility =
    quality_score
    / normalized(cost + latency + token_consumption)
```

The final formulation must address:

- scale normalization
- zero and near-zero denominators
- quality-score calibration
- workload-specific weighting
- failure treatment
- cross-model comparability

### Validation

- compare against cost per successful task
- evaluate rank stability under weight changes
- report domain-specific performance
- perform ablations for cost, latency, and token components

## Trajectory Quality

### Objective

Measure whether an execution path was effective, valid, and economical.

Candidate components include:

- task completion
- valid tool selection
- valid tool arguments
- unnecessary-step rate
- loop count
- handoff completeness
- recovery behavior
- policy compliance

A trajectory score must not obscure component results. Reports must show each
component and the aggregate separately.

## Execution Stability

### Objective

Measure variation across repeated runs under the same experimental condition.

Required statistics include:

- success-rate variance
- latency coefficient of variation
- token coefficient of variation
- cost coefficient of variation
- trajectory similarity
- output agreement where appropriate

At least 20 runs per condition are required for formal stability analysis unless
a documented power analysis supports a different sample size.

## Memory Utility

### Objective

Measure whether memory consumption contributes to task performance.

Required conditions include:

- full memory
- summarized memory
- limited-window memory
- retrieval-based memory
- no memory

Required measurements include:

- memory tokens
- memory share
- memory latency
- memory cost
- task quality
- task-success rate
- factual contribution
- contradiction rate

### Candidate Form

```text
memory_utility =
    quality_gain_attributable_to_memory
    / normalized(memory_tokens + memory_latency + memory_cost)
```

Causal language requires controlled intervention or an equivalent experimental
design.

## Retry Efficiency

### Objective

Distinguish retries that recover a task from retries that add cost without
changing the outcome.

Retry classifications include:

- recovered
- partially recovered
- repeated identical failure
- invalid retry
- policy-exhausted
- unresolved

Required measurements include:

- triggering failure
- retry number
- retry tokens
- retry latency
- retry cost
- state change between attempts
- final task outcome

### Candidate Form

```text
retry_efficiency =
    recovered_value
    / normalized(retry_tokens + retry_latency + retry_cost)
```

## Observability Value

### Objective

Measure whether additional telemetry improves diagnosis or reduces investigation
time.

Telemetry levels:

| Level | Captured evidence |
| --- | --- |
| 0 — Minimal | Run status, total latency, total tokens |
| 1 — Operational | Span timing, usage, cost, error type |
| 2 — Contextual | Tool, retrieval, memory, retry, and lineage metadata |
| 3 — Diagnostic | Redacted payload evidence and decision annotations |

Required outcomes include:

- diagnosis accuracy
- time to diagnosis
- attribution confidence
- false-positive rate
- instrumentation overhead
- storage overhead

# Diagnostic Program

## Failure Taxonomy

The diagnostic taxonomy includes:

### Planning failures

- incomplete plan
- invalid ordering
- unnecessary decomposition
- repeated replanning
- unreachable objective

### Memory failures

- missing relevant memory
- stale memory
- contradictory memory
- excessive memory
- incorrect memory write

### Retrieval failures

- no relevant result
- irrelevant result
- stale source
- conflicting source
- excessive context

### Tool failures

- incorrect tool selection
- invalid arguments
- authorization failure
- timeout
- partial response
- duplicate invocation

### Coordination failures

- incomplete handoff
- context loss
- circular delegation
- redundant agent
- unresolved disagreement

### Validation failures

- invalid structured output
- missing required field
- policy violation
- unsupported citation
- incomplete answer

### Model failures

- refusal
- hallucination
- malformed output
- context overflow
- provider error

### Infrastructure failures

- rate limit
- network failure
- process restart
- resource pressure
- orchestration eviction

## Rule-Based Diagnosis

Initial diagnosis must remain deterministic and reproducible.

Every diagnostic finding requires:

- finding ID and version
- failure category
- severity
- confidence
- affected run and span IDs
- measured evidence
- threshold or rule identifier
- remediation text
- known limitations

## Statistical Anomaly Detection

Initial anomaly-detection targets include:

- latency shifts
- token-consumption shifts
- cost shifts
- failure-rate shifts
- tool-call frequency changes
- retry-rate changes
- trajectory-length changes

Models must be evaluated against simple statistical baselines before additional
complexity is introduced.

## Root-Cause Attribution

Attribution research must report:

- top-ranked responsible span
- top-ranked responsible agent
- confidence
- supporting evidence
- alternative hypotheses
- attribution accuracy
- false-positive and false-negative rates

Attribution claims require controlled failure injection or independently labeled
incident data.

# Optimization Program

## Recommendation Categories

### Prompt optimization

- repeated instruction removal
- stable-prefix caching
- contradictory instruction detection
- prompt-version comparison

### Memory optimization

- history summarization
- retention limits
- stale-memory removal
- retrieval-based memory

### Retry optimization

- retry-limit adjustment
- invalid-retry prevention
- backoff correction
- fallback activation

### Model optimization

- lower-cost candidate evaluation
- workload-specific selection
- fallback analysis
- provider comparison

### Workflow optimization

- redundant-step removal
- unnecessary-handoff reduction
- tool-result caching
- retrieval top-k adjustment

## Recommendation Confidence

Recommendation confidence must account for:

- evidence completeness
- sample size
- repeatability
- evaluator agreement
- intervention history
- domain transfer risk

Confidence is not equivalent to expected quality.

## Before-and-After Validation

Every optimization study must preserve:

- baseline configuration
- candidate configuration
- controlled variables
- repeated trials
- raw traces
- quality measurements
- cost, latency, and reliability measurements
- regression analysis
- accepted and rejected recommendations

Projected benefit and observed benefit must be reported separately.

# Benchmark Program

## Benchmark Principles

Benchmarks must be:

- reproducible
- versioned
- framework-neutral at the task level
- transparent about external dependencies
- capable of preserving failures
- suitable for repeated trials
- explicit about measured and estimated values

## Framework Coverage

Initial framework targets include:

- native Python
- HTTP agents
- LangGraph
- OpenAI Agents SDK
- CrewAI
- AutoGen

Additional frameworks may be added after core trace coverage is validated.

## Task Categories

### Single-agent tasks

- instruction following
- structured output
- retrieval question answering
- tool selection
- tool argument generation

### Multi-step tasks

- planning and execution
- retrieval and synthesis
- validation and correction
- tool failure and recovery

### Multi-agent tasks

- delegation
- handoff preservation
- disagreement resolution
- shared-memory use
- final synthesis

## Experimental Conditions

Experiments must record:

- model and model version
- provider
- prompt version
- sampling parameters
- framework and version
- tool versions
- dataset and suite versions
- memory strategy
- retrieval strategy
- retry policy
- environment
- random seed where applicable

## Failure Injection

Controlled failure conditions include:

- model timeout
- tool timeout
- invalid tool response
- retrieval omission
- stale memory
- conflicting context
- malformed output
- provider failure
- agent handoff loss

Normal and degraded conditions must use equivalent task sets.

# Statistical Validation

## Descriptive Analysis

Required descriptive statistics include:

- count
- mean
- median
- standard deviation
- coefficient of variation
- minimum and maximum
- P50, P95, and P99 where appropriate

## Comparative Analysis

Comparative methods may include:

- paired tests
- non-parametric paired tests
- bootstrap confidence intervals
- effect sizes
- multiple-comparison correction

Method selection must match the data distribution and experimental design.

## Relationship Analysis

Relationship analysis may include:

- correlation
- partial correlation
- regression
- mixed-effects models

Correlation must not be reported as causation.

## Evaluator Reliability

Evaluator studies must include:

- inter-rater agreement
- human-model agreement
- deterministic-model agreement
- calibration error
- disagreement analysis

## Metric Validation

Experimental metric validation must include:

- construct validity
- convergent validity
- discriminant validity
- sensitivity analysis
- ablation analysis
- cross-domain robustness

# Development Program

## Phase 0 — Compatibility Baseline

### Deliverables

- current release tag
- regression suite
- compatibility policy
- experimental API labels
- roadmap publication

### Completion criteria

- existing profiler behavior is covered by regression tests
- public compatibility expectations are documented

## Phase 1 — Trace Foundation

### Deliverables

- run and span models
- versioned JSON schemas
- nested instrumentation
- timing, token, cost, and error capture
- validation
- redaction
- console and JSON reporting

### Completion criteria

- malformed traces are rejected
- parent-child relationships remain valid
- existing profiling remains compatible
- instrumentation overhead is measured

## Phase 2 — Raw Metrics

### Deliverables

- token metrics
- latency metrics
- cost metrics
- reliability metrics
- metrics by agent and span type
- baseline comparison

### Completion criteria

- metrics reproduce from saved traces
- estimated values are labeled
- composite scores are not required for basic reports

## Phase 3 — Memory and Retry Analysis

### Deliverables

- memory-share analysis
- memory-relevance interface
- retry classification
- retry overhead
- context-duplication detection
- deterministic findings

### Completion criteria

- memory strategies can be compared experimentally
- retries reference triggering failures
- findings cite exact evidence

## Phase 4 — Evaluation and Stability

### Deliverables

- evaluator interface
- repeated-run grouping
- stability statistics
- experimental efficiency metrics
- trajectory evaluator
- human-annotation format

### Completion criteria

- at least 20 runs per formal stability condition are supported
- raw and composite metrics are reported together
- metric weights are configurable
- sensitivity reports are available

## Phase 5 — Diagnosis

### Deliverables

- failure taxonomy
- deterministic rule engine
- anomaly detection
- span and agent attribution
- confidence and evidence output

### Completion criteria

- controlled failure dataset is available
- attribution accuracy is measured
- false-positive analysis is complete
- core diagnosis does not require an LLM

## Phase 6 — Optimization

### Deliverables

- memory optimization
- retry optimization
- prompt optimization
- model-selection experiments
- workflow optimization
- before-and-after validation

### Completion criteria

- recommendations are measurable
- projected and observed effects are separated
- quality regression checks are applied
- optimization components can be disabled independently

# Initial Implementation Sequence

## Sprint 1 — Trace and Raw Metrics

- core run and span models
- trace, finding, and report schemas
- nested trace context manager
- total and per-span token metrics
- total and per-span latency metrics
- retry and tool-call counts
- run inspection report
- native Python example

## Sprint 2 — Memory and Retry Diagnostics

- memory spans
- memory share
- retry spans
- retry overhead
- triggering-failure references
- context-duplication analysis
- deterministic findings
- unit and integration tests

## Sprint 3 — Repeated-Run Evaluation

- experiment manifests
- run grouping
- success rate
- confidence intervals
- coefficient of variation
- baseline comparison
- regression report
- CSV export

# Testing Requirements

## Unit Tests

Unit tests must cover:

- schema validation
- parent-child relationships
- metric formulas
- redaction
- retry classification
- finding thresholds
- comparison deltas
- serialization compatibility

## Integration Tests

Integration tests must cover:

- native Python tracing
- saved-trace inspection
- baseline and candidate comparison
- failure capture
- offline operation
- existing profiler compatibility

## Golden Trace Tests

Golden artifacts must cover:

- successful run
- failed run
- nested tool retry
- memory-intensive run
- multi-agent delegation
- malformed trace

Schema or serializer changes require explicit golden-artifact review.

## Performance Tests

Performance tests must measure:

- trace creation overhead
- span creation overhead
- serialization time
- artifact size
- comparison time
- redaction overhead

# Research Integrity

## Prohibited Claims

Publication and product material must not claim:

- universal agent quality measurement
- causal attribution from observational correlation alone
- guaranteed quality equivalence between models
- complete PII removal by default redaction
- statistically significant improvement without an appropriate test
- framework independence without demonstrated coverage

## Permitted Claim Structure

Claims must identify:

- evaluated task set
- experimental conditions
- sample size
- metric version
- statistical method
- effect size
- confidence interval where applicable
- known limitations

## Reproducibility Requirements

Every research result must preserve:

- source revision
- environment and dependency lock
- dataset version
- experiment manifest
- prompt and model versions
- raw traces
- evaluator versions
- configuration
- analysis code
- generated tables and figures

## Privacy and Security

Research artifacts must:

- minimize payload capture
- apply redaction before persistence
- document retained sensitive fields
- separate public and restricted datasets
- avoid committing credentials
- define retention and access controls

# Publication Program

## Study 1 — Measurement and Evaluation

Primary contributions:

- unified trace representation
- raw operational metric framework
- repeated-run methodology
- initial efficiency and stability validation

## Study 2 — Memory and Retry Efficiency

Primary contributions:

- memory contribution experiments
- retry classification
- memory and retry efficiency metrics
- controlled strategy comparisons

## Study 3 — Failure Attribution

Primary contributions:

- failure taxonomy
- controlled failure dataset
- deterministic attribution baseline
- agent and span attribution evaluation

## Study 4 — Agent Response-Start Latency

Primary contributions:

- response-start decomposition
- planning, memory, retrieval, tool, and model latency analysis
- framework and workload comparison

# Program Priorities

## Active Priorities

1. unified run and span trace schema
2. token and latency breakdown by span
3. memory-share analysis
4. retry-overhead analysis
5. repeated-run comparison

## Deferred Scope

- autonomous prompt rewriting
- automatic production changes
- LLM-only root-cause analysis
- complex runtime routing
- large dashboard development
- broad framework-adapter coverage
- a universal agent score

# Program Completion Standard

The research foundation is complete when AgenticLens provides:

```text
standardized execution traces
        +
multidimensional raw measurements
        +
experimentally validated metrics
        +
measured failure attribution
        +
evidence-backed optimization
```

Research outputs must remain reproducible, versioned, explicit about
limitations, and separable from committed product claims.
