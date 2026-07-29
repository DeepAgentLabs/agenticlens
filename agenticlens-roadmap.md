# AgenticLens Roadmap

## Vision

AgenticLens will evolve from a lightweight AI workflow profiler into an open-source **AI runtime intelligence and evaluation platform** for production agentic systems.

It should help teams:

- observe agent behavior
- evaluate output quality and task success
- compare models, prompts, tools, retrieval strategies, and agent architectures
- select the best model for each workload
- detect regressions before deployment
- optimize cost, latency, reliability, safety, and quality
- enforce enterprise policies
- generate audit-ready operational evidence

> **Instrument once, evaluate continuously, optimize intelligently, and govern confidently.**

---

## Product Positioning

AgenticLens should not be positioned only as a token and latency profiler.

> **AgenticLens is an open-source AI runtime intelligence platform that helps teams observe, evaluate, compare, optimize, and govern production AI agents.**

### Questions it should answer

- What happened during an agent workflow?
- Did the agent complete the intended task?
- Which model performed best for this workload?
- Is the premium model worth its additional cost?
- Which prompt or retrieval configuration produced the best result?
- What caused a regression?
- Can a smaller model handle this task safely?
- Which agent steps add cost without improving quality?
- Does the workflow comply with enterprise policies?
- Can the system recover from model, tool, memory, or provider failures?

---

# Product Architecture

```text
Enterprise AI Applications
          |
          v
AgenticLens Instrumentation Layer
          |
          +--------------------+
          |                    |
          v                    v
   Runtime Tracing       Evaluation Runtime
          |                    |
          +----------+---------+
                     |
                     v
              AI Operations Store
                     |
      +--------------+--------------+
      |              |              |
      v              v              v
 Experiment      ModelFit       Governance
   Engine         Engine          Engine
      |              |              |
      +--------------+--------------+
                     |
                     v
              Recommendations
                     |
        +------------+------------+
        |                         |
        v                         v
   Web Dashboard             CLI / API / MCP
```

---

# Core Product Modules

## 1. AgenticLens Observe

Captures and visualizes the complete AI runtime.

### Capabilities

- workflow tracing
- agent-step tracing
- LLM call tracing
- prompt and context inspection
- token and cost tracking
- latency breakdown
- retrieval activity
- memory reads and writes
- tool and MCP calls
- agent handoffs
- retries and failures
- safety and reliability events
- OpenTelemetry export
- local artifact export

---

## 2. AgenticLens Evaluate

Evaluates both the final outcome and the execution path of an AI agent.

### Evaluation dimensions

- task success
- correctness
- relevance
- completeness
- groundedness
- citation quality
- tool-selection accuracy
- tool-argument accuracy
- structured-output validity
- instruction adherence
- policy compliance
- safety
- consistency
- failure recovery
- business outcome quality

### Evaluator types

- deterministic evaluators
- reference-based evaluators
- model-based judges
- trajectory evaluators
- RAG evaluators
- tool-use evaluators
- safety evaluators
- human feedback
- custom enterprise evaluators

---

## 3. AgenticLens Experiments

Compares alternative AI system configurations against the same test suite.

### Experiment dimensions

- model and model version
- provider
- prompt version
- system prompt
- temperature and sampling parameters
- RAG strategy
- embedding model
- reranker
- top-k
- memory strategy
- tool configuration
- agent architecture
- fallback strategy
- retry policy

### Experiment outputs

- model leaderboard
- test-level score comparison
- score heatmap
- regression analysis
- trace comparison
- cost comparison
- latency comparison
- reliability comparison
- Pareto frontier
- recommended configuration

---

## 4. AgenticLens ModelFit

Selects the best model for each task category under enterprise constraints.

### Inputs

- task type
- task complexity
- domain
- risk level
- expected quality
- latency target
- cost limit
- tool-use requirements
- structured-output requirements
- data sensitivity
- provider restrictions
- deployment region
- historical success rate
- provider health
- safety requirements

### Outputs

- recommended model
- recommendation confidence
- alternative models
- expected quality
- expected cost
- expected latency
- policy compliance status
- explanation for selection
- fallback chain
- routing recommendation

### Primary business metric

> **Cost per successful task**

Additional metrics:

- cost per approved response
- cost per resolved ticket
- cost per completed workflow
- latency per successful task
- retries per successful task
- human escalations per model
- quality-adjusted cost

---

## 5. AgenticLens Optimize

Provides evidence-based optimization recommendations.

### Models

- replace unnecessarily expensive models
- route simple tasks to smaller models
- reserve premium models for high-risk tasks
- identify provider-specific strengths

### Prompts

- detect repeated instructions
- identify contradictory sections
- compare prompt versions
- detect quality regressions
- recommend prompt compression
- recommend caching stable prompt blocks

### RAG

- optimize top-k
- detect irrelevant chunks
- detect stale context
- evaluate chunk utility
- compare rerankers
- compare embedding models
- identify cases where RAG adds no value

### Memory

- detect excessive history
- identify repeated context
- identify stale or contradictory memory
- recommend summarization
- recommend retention limits

### Tools

- identify duplicate calls
- detect invalid arguments
- identify low-value tools
- detect unnecessary retries
- recommend caching
- evaluate tool success rates

### Multi-agent systems

- detect unnecessary handoffs
- identify redundant agents
- detect loops
- identify context loss
- measure handoff cost
- recommend simpler execution paths

---

## 6. AgenticLens Govern

Adds enterprise controls and auditability.

### Governance features

- model allowlists
- provider restrictions
- prompt approval
- policy-as-code
- cost limits
- latency limits
- minimum quality thresholds
- data residency controls
- PII masking
- retention policies
- human-review requirements
- model-version history
- prompt-version history
- audit trails
- release gates
- compliance reports

---

## 7. AgenticLens Test Suites

Provides versioned datasets for evaluating AI agents.

### Test suite sources

- manually authored golden cases
- production traces
- user feedback
- escalated failures
- synthetic variations
- chaos-generated failures
- imported public benchmarks
- domain-specific datasets

### Starter suites

#### Universal Agent Suite

- instruction following
- structured output
- invalid input handling
- tool selection
- tool argument validation
- timeout recovery
- turn-limit enforcement
- prompt injection resistance
- sensitive-data handling

#### RAG Suite

- grounded answers
- citation correctness
- irrelevant context
- conflicting documents
- missing answers
- stale documents
- adversarial documents
- multi-document synthesis

#### Tool-Calling Suite

- correct tool selection
- correct arguments
- authorization
- duplicate-call prevention
- idempotency
- timeout handling
- partial responses
- fallback behavior

#### Multi-Agent Suite

- correct delegation
- handoff completeness
- context preservation
- circular delegation
- shared-memory handling
- agent disagreement
- final synthesis
- step efficiency

#### Safety Suite

- prompt injection
- data exfiltration
- PII leakage
- unauthorized actions
- unsafe tool invocation
- policy bypass
- harmful output

---

# Evaluation Framework

## Core objects

```text
Test Suite
    |
    +-- Test Cases
           |
           +-- Experiment Variant
                  |
                  +-- Agent Run
                         |
                         +-- Trace
                                |
                                +-- Scores
```

## Evaluation result example

```json
{
  "task_success": 1.0,
  "answer_correctness": 0.92,
  "groundedness": 0.96,
  "tool_selection": 1.0,
  "tool_argument_accuracy": 0.88,
  "policy_compliance": 1.0,
  "safety": 1.0,
  "latency_ms": 2840,
  "cost_usd": 0.031,
  "turn_count": 4
}
```

## Evaluator interface

```python
from dataclasses import dataclass
from typing import Any, Protocol


@dataclass
class EvalContext:
    test_case: dict[str, Any]
    output: Any
    trace: dict[str, Any]
    reference: Any | None = None


@dataclass
class Score:
    name: str
    value: float
    passed: bool
    explanation: str
    metadata: dict[str, Any]


class Evaluator(Protocol):
    name: str

    def evaluate(self, context: EvalContext) -> Score:
        ...
```

---

# Dashboard Vision

The UI should feel like an MLOps experiment platform designed specifically for agentic systems.

## Dashboard sections

### Overview

- total runs
- active experiments
- model usage
- monthly cost
- task-success rate
- policy violations
- regression alerts
- estimated savings

### Experiment comparison

- variants
- models
- prompts
- test suites
- aggregate scores
- cost
- latency
- reliability
- recommendation

### Model leaderboard

| Model | Success | Quality | Groundedness | Tool Score | Safety | P95 Latency | Cost/Success |
|---|---:|---:|---:|---:|---:|---:|---:|
| Model A | 91% | 0.89 | 0.94 | 0.93 | 0.99 | 3.2s | $0.08 |
| Model B | 87% | 0.85 | 0.92 | 0.96 | 0.99 | 1.8s | $0.03 |
| Model C | 96% | 0.94 | 0.97 | 0.91 | 1.00 | 5.1s | $0.21 |

### Test-case heatmap

- rows: test cases
- columns: models or variants
- cells: pass, fail, score, or regression

### Trace viewer

- workflow tree
- agent steps
- tool calls
- retrieval
- memory
- handoffs
- retries
- errors
- scores per step

### ModelFit view

- recommended model by task type
- reason for recommendation
- confidence
- constraint violations
- expected savings
- fallback option

### Governance view

- approved models
- policy violations
- sensitive workflows
- human reviews
- audit evidence
- release-gate status

---

# Framework Support

AgenticLens should remain framework-agnostic.

## Adapter interface

```python
class AgentAdapter(Protocol):
    name: str

    def invoke(self, test_case):
        ...

    def extract_trace(self, result):
        ...

    def reset_state(self):
        ...
```

## Planned adapters

- native Python
- LangGraph
- OpenAI Agents SDK
- CrewAI
- AutoGen
- Semantic Kernel
- LlamaIndex
- HTTP agents
- MCP-hosted agents
- custom enterprise runtimes

---

# Platform Architecture

## Initial stack

### Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL
- Redis
- background workers
- object storage

### Frontend

- React or Next.js
- TypeScript
- TanStack Table
- charting library
- trace-tree component
- JSON and prompt editor

### Deployment

- local SQLite mode
- Docker Compose
- Kubernetes
- Helm chart
- self-hosted enterprise deployment

## Core entities

```text
organizations
projects
applications
agents
models
model_versions
prompts
prompt_versions
tools
datasets
dataset_versions
test_cases
test_suites
experiments
experiment_variants
runs
traces
spans
evaluators
evaluator_versions
scores
feedback
policies
recommendations
deployments
```

---

# AI Operations Specification Extensions

## New runtime objects

- `TestSuite`
- `TestCase`
- `Experiment`
- `ExperimentVariant`
- `Evaluation`
- `Evaluator`
- `Score`
- `ModelRecommendation`
- `PolicyDecision`
- `HumanFeedback`

## New semantic events

```text
evaluation.started
evaluation.completed
score.computed
human_feedback.recorded
experiment.started
experiment.completed
test_case.failed
regression.detected
model.recommended
policy.gate.failed
```

---

# CLI Vision

```bash
# Run a test suite
agenticlens eval run \
  --suite suites/support.yaml \
  --target examples/support_agent.py \
  --save results.json

# Compare models
agenticlens eval compare \
  --suite customer-support-v1.yaml \
  --variants model-variants.yaml \
  --trials 3

# Compare against a baseline
agenticlens eval regression \
  --baseline production-results.json \
  --candidate candidate-results.json

# Apply a release gate
agenticlens gate \
  --results candidate-results.json \
  --min-success-rate 0.90 \
  --max-regression 0.02

# Open the dashboard
agenticlens ui
```

---

# Implementation Roadmap

## Phase 0: Product and specification alignment

### Goal

Define stable product and evaluation contracts before expanding implementation.

### Deliverables

- finalize product positioning
- define evaluation vocabulary
- define test-suite schema
- define experiment schema
- define score schema
- define evaluator interface
- extend the AI Operations Specification
- create architecture decision records
- define compatibility and versioning rules

### Exit criteria

- schemas reviewed
- example artifacts validated
- cross-repository compatibility agreed
- roadmap published

---

## Phase 1: Evaluation SDK

### Goal

Create the minimum framework for evaluating any Python or HTTP-based agent.

### Deliverables

- `TestCase`
- `TestSuite`
- `Experiment`
- `ExperimentVariant`
- `Evaluator`
- `Score`
- evaluation runner
- YAML and JSON test suites
- deterministic evaluators
- custom evaluator registration
- JSON report
- Markdown report
- CLI commands

### Initial evaluators

- exact match
- contains match
- JSON schema
- required fields
- required tool
- forbidden tool
- tool arguments
- latency threshold
- cost threshold
- turn-count threshold
- business-rule evaluator

### Exit criteria

- one native Python agent evaluated
- one HTTP agent evaluated
- reports generated
- test-suite version captured
- evaluator version captured

---

## Phase 2: Model and configuration comparison

### Goal

Compare models and agent configurations against the same test suite.

### Deliverables

- multiple variants
- repeated trials
- model comparison
- prompt comparison
- aggregated metrics
- pass@k
- pass^k
- consistency score
- cost per successful task
- baseline comparison
- regression detection
- HTML report
- CSV export

### Exit criteria

- three models compared
- three trials per test case
- regressions identified
- recommendation summary generated

---

## Phase 3: Local dashboard

### Goal

Provide an MLOps-style UI for experiments and agent traces.

### Deliverables

- FastAPI service
- SQLite mode
- PostgreSQL mode
- experiment list
- run list
- model leaderboard
- score heatmap
- trace viewer
- test-case details
- failure filters
- search
- comparison charts
- Docker Compose setup

### Command

```bash
agenticlens ui
```

### Exit criteria

- experiment results visible in UI
- test-level drilldown works
- trace comparison works
- model comparison works
- local setup documented

---

## Phase 4: Advanced evaluation

### Goal

Evaluate output quality, trajectories, RAG, tools, safety, and recovery.

### Deliverables

- LLM judge interface
- judge-prompt versioning
- judge-model metadata
- groundedness evaluator
- relevance evaluator
- completeness evaluator
- citation evaluator
- tool-trajectory evaluator
- agent-goal evaluator
- handoff evaluator
- loop evaluator
- safety evaluator
- human feedback API
- human-review queue
- evaluator calibration reports

### Exit criteria

- deterministic and judge scores shown separately
- evaluator disagreement visible
- human feedback stored
- judge cost reported
- calibration dataset supported

---

## Phase 5: Test-suite management

### Goal

Help teams create and maintain enterprise evaluation datasets.

### Deliverables

- suite editor
- test-case editor
- suite versioning
- dataset import
- CSV and JSON import
- production trace to test case
- user feedback to test case
- synthetic variation generation
- approval workflow
- tagging
- domain categories
- train, validation, and test splits
- duplicate detection
- PII masking

### Exit criteria

- test cases created from traces
- test cases reviewed and approved
- suite versions immutable
- regression suite reusable in CI

---

## Phase 6: AgenticLens ModelFit

### Goal

Recommend the best model for each enterprise task.

### Deliverables

- task taxonomy
- constraint configuration
- weighted scoring
- Pareto frontier
- cost-per-success ranking
- workload-specific recommendations
- recommendation confidence
- recommendation explanation
- fallback recommendations
- task-level model matrix

### Example output

```text
Recommended model: Model B

Reason:
- Meets the 90% task-success threshold
- Meets the 95% groundedness threshold
- Reduces cost per successful task by 42%
- Improves P95 latency by 31%

Fallback:
- Use Model C for high-risk legal requests
```

### Exit criteria

- recommendations explainable
- enterprise constraints enforced
- recommendations generated by task type
- savings estimate generated

---

## Phase 7: Runtime routing

### Goal

Use evaluation evidence to select models dynamically.

### Deliverables

- routing SDK
- rule-based router
- score-based router
- policy-aware routing
- fallback chain
- provider failover
- confidence threshold
- escalation
- shadow mode
- canary mode
- routing audit log

### Exit criteria

- routing works in shadow mode
- routing decisions explainable
- fallback tested
- policy violations blocked
- routing performance measured

---

## Phase 8: Optimization intelligence

### Goal

Recommend improvements beyond model selection.

### Deliverables

- prompt recommendations
- RAG recommendations
- memory recommendations
- tool recommendations
- multi-agent recommendations
- redundant-step detection
- low-value agent detection
- quality-cost tradeoff analysis
- projected savings
- recommendation confidence
- recommendation risk

### Exit criteria

- recommendations tied to evidence
- expected benefit quantified
- quality risk stated
- accepted and rejected recommendations tracked

---

## Phase 9: Governance and enterprise readiness

### Goal

Make AgenticLens deployable in enterprise environments.

### Deliverables

- organizations and projects
- SSO
- RBAC
- audit logs
- model registry
- prompt registry
- policy-as-code
- model allowlists
- retention controls
- PII controls
- data residency configuration
- human approvals
- release gates
- compliance exports
- private evaluator support
- Kubernetes deployment
- Helm chart

### Exit criteria

- multi-user deployment
- role separation
- audit-ready records
- private deployment documented
- enterprise security review completed

---

## Phase 10: Ecosystem integrations

### Goal

Make AgenticLens the central intelligence layer of DeepAgentLabs.

### Deliverables

- Agentic Chaos integration
- Deep Agentic Core MCP integration
- AI Operations Specification conformance
- framework adapters
- OpenTelemetry integration
- CI integrations
- Jira integration
- GitHub integration
- data warehouse export

### Exit criteria

- AgenticLens and Agentic Chaos share artifacts
- MCP exposes evaluation and comparison tools
- conformance suite passes
- at least three framework adapters stable

---

# Suggested Release Sequence

## v0.2 — Evaluation foundation

- test cases
- test suites
- deterministic evaluators
- CLI evaluation runner
- JSON and Markdown reports

## v0.3 — Experiment comparison

- variants
- repeated trials
- model comparison
- baseline regression
- cost per successful task

## v0.4 — Local dashboard

- experiment UI
- model leaderboard
- score heatmap
- trace comparison

## v0.5 — Advanced evaluators

- LLM judges
- RAG evaluators
- trajectory evaluators
- safety evaluators
- human feedback

## v0.6 — Test-suite manager

- trace-to-test
- dataset versioning
- suite editor
- synthetic cases
- approval workflow

## v0.7 — ModelFit

- enterprise constraints
- weighted ranking
- Pareto analysis
- model recommendations

## v0.8 — Runtime routing

- routing SDK
- fallback chains
- shadow mode
- policy-aware selection

## v0.9 — Optimization intelligence

- prompt optimization
- RAG optimization
- agent architecture optimization
- savings analysis

## v1.0 — Enterprise-ready open platform

- governance
- RBAC
- audit
- self-hosted dashboard
- stable schemas
- stable APIs
- framework adapters
- MCP integration

---

# First 90-Day Execution Plan

## Days 1–30

- finalize schemas
- implement evaluator interface
- implement test-suite loader
- implement deterministic evaluators
- create evaluation runner
- create two sample suites
- add CLI commands
- generate JSON and Markdown reports
- write unit tests
- publish architecture documentation

## Days 31–60

- implement experiment variants
- implement repeated trials
- implement aggregation
- add pass@k and pass^k
- calculate cost per successful task
- implement baseline comparison
- add regression detection
- generate HTML comparison report
- compare at least three models

## Days 61–90

- add FastAPI backend
- add SQLite persistence
- create experiment dashboard
- create model leaderboard
- create test-case heatmap
- add trace drilldown
- provide Docker Compose setup
- publish an end-to-end demonstration
- release AgenticLens Evals preview

---

# Initial Reference Use Case

## Customer Support Agent

### Test suite

- refund eligibility
- return-window enforcement
- damaged product
- unauthorized refund attempt
- missing order
- duplicate request
- provider timeout
- tool timeout
- corrupted memory
- irrelevant retrieval

### Variants

- small model
- medium model
- premium model
- prompt version A
- prompt version B
- RAG top-k 4
- RAG top-k 8

### Evaluators

- task success
- policy compliance
- required tools
- forbidden tools
- groundedness
- citation correctness
- output format
- latency
- cost
- failure recovery

### Dashboard outcome

- model leaderboard
- test-case heatmap
- failed trace comparison
- cost per successful task
- recommended model by scenario
- optimization suggestions

---

# Success Metrics

## Developer adoption

- package downloads
- GitHub stars
- active contributors
- documentation usage
- framework integrations
- test suites created

## Evaluation quality

- evaluator agreement
- judge-human agreement
- regression detection accuracy
- false-positive rate
- suite coverage
- repeatability

## Enterprise value

- inference cost reduction
- task-success improvement
- latency improvement
- reduced human escalation
- faster model selection
- fewer production regressions
- policy violations prevented
- time saved during release validation

---

# Design Principles

- framework-agnostic
- specification-first
- local-first
- open-source core
- explainable recommendations
- deterministic checks before model judges
- traceable scores
- versioned everything
- enterprise extensibility
- no hidden composite score
- quality before cost
- cost per successful outcome
- human review for high-risk use cases
- composable with Agentic Chaos and MCP

---

# Non-Goals for Early Releases

AgenticLens should not initially attempt to:

- replace every existing MLOps system
- provide a hosted SaaS before the local product is stable
- train foundation models
- create one universal score for every agent
- depend on one agent framework
- automatically change production routing without review
- rely entirely on model-based judges
- create many separate repositories before core abstractions stabilize

---

# Immediate Next Milestone

## AgenticLens Evals v0.1

The first major milestone should support:

1. Define a test suite in YAML.
2. Execute any Python callable or HTTP-based agent.
3. Compare multiple models or configurations.
4. Run deterministic and custom evaluators.
5. Repeat each test several times.
6. Calculate quality, success, cost, latency, and consistency.
7. Detect regressions against a baseline.
8. Generate JSON, Markdown, CSV, and HTML reports.
9. Open results in a local dashboard.
10. Recommend the best eligible model under defined constraints.

### Proposed command

```bash
agenticlens eval compare \
  --suite customer-support-v1.yaml \
  --variants model-variants.yaml \
  --trials 3 \
  --serve
```

---

# Long-Term Direction

```text
Profiler
   |
   v
Observability Toolkit
   |
   v
Evaluation Platform
   |
   v
Experimentation Platform
   |
   v
Model Intelligence Platform
   |
   v
Runtime Optimization Platform
   |
   v
Enterprise AI Operations Platform
```

> **Most tools show traces. AgenticLens should turn runtime evidence into decisions.**
