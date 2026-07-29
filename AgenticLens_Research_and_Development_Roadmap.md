# AgenticLens Research and Development Roadmap

## 1. Project Vision

**AgenticLens** will evolve from a token-profiling library into an open-source framework for:

- agent evaluation
- agent observability
- execution-trace analysis
- failure diagnosis
- inference and workflow optimization

### Proposed positioning

> AgenticLens is an open-source evaluation, observability, and optimization framework for agentic AI systems. It measures how agents execute, identifies inefficient or unreliable behavior, and recommends changes that improve quality, cost, latency, and stability.

### Core research question

> How can execution traces be used to measure, diagnose, and optimize agentic AI workflows?

---

## 2. Repository Decision

### Recommendation: Continue using the existing AgenticLens repository

Do **not** create a separate repository for the core research framework yet.

The new research direction is a natural expansion of AgenticLens:

```text
Token profiling
      ↓
Execution tracing
      ↓
Evaluation
      ↓
Diagnosis
      ↓
Optimization
```

Creating a separate repository now would:

- divide contributors and GitHub visibility
- duplicate instrumentation code
- create confusion about which project users should install
- make the research look disconnected from the existing open-source work
- increase maintenance and release effort

### Recommended structure

Use the existing repository as the main product:

```text
DeepAgentLabs/
├── agenticlens
├── agenticlens-benchmarks
└── agenticlens-research
```

Only `agenticlens` needs to exist immediately.

The other repositories can be created later when the content becomes large enough:

#### `agenticlens`

The installable Python framework.

Contains:

- instrumentation
- trace schema
- metrics
- evaluation
- diagnosis
- optimization
- CLI
- reports
- framework adapters

#### `agenticlens-benchmarks`

Create this when the benchmark contains many datasets, framework implementations, recorded traces, and experiment scripts.

Contains:

- common task datasets
- framework-specific benchmark agents
- experiment configurations
- baseline results
- reproduction scripts

#### `agenticlens-research`

Create this after the first paper is mature.

Contains:

- paper-specific experiments
- notebooks
- statistical analysis
- figures
- ablation studies
- supplementary material
- accepted-paper artifacts

### Avoid creating

Do not create a second competing product repository such as:

```text
agent-observer
agent-evaluator
agent-optimizer
```

These capabilities should remain modules under the AgenticLens identity.

---

## 3. Research Scope

AgenticLens will study five connected areas:

1. **Execution measurement**
2. **Agent evaluation**
3. **Agent observability**
4. **Failure diagnosis**
5. **Workflow optimization**

The work should proceed in that order. Reliable diagnosis and optimization require trustworthy raw measurements.

---

# Part I: Measurement and Trace Infrastructure

## 4. Unified Agent Trace Schema

Every agent execution should be represented as a run containing nested spans.

```text
AgentRun
├── PlanningSpan
├── ModelCallSpan
├── MemoryReadSpan
├── MemoryWriteSpan
├── RetrievalSpan
├── ToolCallSpan
├── ValidationSpan
├── RetrySpan
└── FinalResponseSpan
```

## 4.1 Run-level fields

```yaml
run_id:
trace_id:
application_name:
framework:
framework_version:
task_id:
task_type:
started_at:
completed_at:
status:
total_latency_ms:
total_input_tokens:
total_output_tokens:
total_tokens:
estimated_cost_usd:
task_success:
error_type:
metadata:
```

## 4.2 Span-level fields

```yaml
span_id:
parent_span_id:
span_type:
agent_name:
model_name:
provider:
started_at:
completed_at:
latency_ms:
input_tokens:
output_tokens:
estimated_cost_usd:
tool_name:
retry_number:
status:
error_type:
input_reference:
output_reference:
attributes:
```

## 4.3 Initial span types

```python
MODEL_CALL = "model_call"
PLANNING = "planning"
MEMORY_READ = "memory_read"
MEMORY_WRITE = "memory_write"
RETRIEVAL = "retrieval"
TOOL_CALL = "tool_call"
VALIDATION = "validation"
RETRY = "retry"
DELEGATION = "delegation"
FINAL_RESPONSE = "final_response"
```

## 4.4 Design principles

The trace schema must be:

- framework-neutral
- model-provider-neutral
- hierarchical
- serializable to JSON
- compatible with distributed tracing concepts
- safe for redaction
- inexpensive to capture
- extensible through attributes

---

# Part II: Raw Metrics

## 5. Token Metrics

Implement raw token metrics before composite scores.

### Required metrics

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

### Initial formulas

#### Memory share

\[
\text{Memory Share}
=
\frac{\text{Memory Tokens}}
{\text{Total Tokens}}
\]

#### Retry token share

\[
\text{Retry Token Share}
=
\frac{\text{Retry Tokens}}
{\text{Total Tokens}}
\]

#### Planning token share

\[
\text{Planning Share}
=
\frac{\text{Planning Tokens}}
{\text{Total Tokens}}
\]

#### Output efficiency

\[
\text{Output Efficiency}
=
\frac{\text{Useful Output Tokens}}
{\text{Total Tokens}}
\]

The definition of useful output must be experimentally specified rather than assumed.

---

## 6. Latency Metrics

### Required metrics

- end-to-end latency
- model-call latency
- tool latency
- memory latency
- retrieval latency
- orchestration latency
- time to first token
- time per output token
- queueing delay when available
- critical-path latency
- parallelism savings
- retry latency

### Agent response-start decomposition

\[
T_{\text{response-start}}
=
T_{\text{orchestration}}
+
T_{\text{model-TTFT}}
\]

Where:

\[
T_{\text{orchestration}}
=
T_{\text{memory}}
+
T_{\text{retrieval}}
+
T_{\text{tool-preprocessing}}
+
T_{\text{prompt-assembly}}
\]

And:

\[
T_{\text{model-TTFT}}
=
T_{\text{network}}
+
T_{\text{queue}}
+
T_{\text{prefill}}
+
T_{\text{first-token}}
\]

Not every provider exposes every component. AgenticLens must clearly distinguish:

- directly measured values
- provider-reported values
- estimated values
- unavailable values

---

## 7. Cost Metrics

### Required metrics

- estimated cost per run
- cost by model
- cost by agent
- cost by span type
- retry cost
- memory-processing cost
- tool cost when known
- cost per successful task

### Cost per successful task

\[
C_{\text{success}}
=
\frac{\text{Total Experiment Cost}}
{\text{Number of Successful Runs}}
\]

This metric is more useful than average run cost when systems have different failure rates.

---

## 8. Reliability Metrics

### Required metrics

- task success rate
- tool-call success rate
- retry rate
- recovery rate
- timeout rate
- invalid-output rate
- repeated-run variance
- path divergence
- framework failure rate

### Task success rate

\[
SR =
\frac{\text{Successful Runs}}
{\text{Total Runs}}
\]

### Recovery rate

\[
RR =
\frac{\text{Failed Attempts Recovered}}
{\text{Recoverable Failed Attempts}}
\]

---

# Part III: Proposed Research Metrics

## 9. Important Research Rule

The following are **proposed metrics**, not established standards.

They must initially be labeled:

- experimental
- beta
- research metric
- proposed metric

AgenticLens should always show the raw measurements used to calculate a composite score.

---

## 10. Agent Efficiency Utility

### Research objective

Measure whether an agent achieves high-quality, reliable results without excessive tokens, cost, latency, or retries.

### Candidate formulation

\[
AEU =
\frac{Q \times R}
{\alpha T_n+\beta C_n+\gamma L_n+\delta Y_n+\epsilon}
\]

Where:

- \(Q\): normalized task-quality score
- \(R\): reliability score
- \(T_n\): normalized token consumption
- \(C_n\): normalized monetary cost
- \(L_n\): normalized latency
- \(Y_n\): normalized retry overhead
- \(\alpha,\beta,\gamma,\delta\): configurable weights
- \(\epsilon\): small constant preventing division by zero

### Research questions

1. Does AEU align with human preference between competing agents?
2. How sensitive is it to each weight?
3. Does it preserve rankings across task categories?
4. Should reliability multiply quality or appear as a separate term?
5. Is a ratio preferable to a weighted additive score?

### Required experiments

- compare against quality-only ranking
- compare against cost-only ranking
- compare against Pareto-front analysis
- collect human rankings of agent executions
- measure Spearman correlation with human rankings
- perform weight sensitivity analysis
- test stability across frameworks and models

---

## 11. Trajectory Quality Score

### Research objective

Evaluate the quality of the execution path, not only the final answer.

### Candidate components

- planning quality
- memory relevance
- retrieval relevance
- tool-selection correctness
- tool-result utilization
- validation quality
- retry usefulness
- final-answer quality

### Candidate formulation

\[
TQS =
w_pE_p+
w_mE_m+
w_rE_r+
w_tE_t+
w_vE_v+
w_yE_y+
w_fE_f
\]

### Contribution requirement

The weighted sum itself is not novel. Novelty must come from:

- operational definitions
- annotation protocol
- benchmark dataset
- evaluator implementation
- weight-learning method
- human agreement analysis
- predictive value for production failures

### Research hypothesis

> Trajectory-quality measurements predict agent failures and inefficiencies better than final-answer evaluation alone.

---

## 12. Execution Stability Score

### Research objective

Measure nondeterministic variation across repeated runs of the same task.

Calculate coefficients of variation separately:

\[
CV_Q =
\frac{\sigma_Q}
{\mu_Q+\epsilon}
\]

\[
CV_T =
\frac{\sigma_T}
{\mu_T+\epsilon}
\]

\[
CV_L =
\frac{\sigma_L}
{\mu_L+\epsilon}
\]

\[
CV_C =
\frac{\sigma_C}
{\mu_C+\epsilon}
\]

Candidate stability score:

\[
ESS =
1-
\left(
\alpha CV_Q+
\beta CV_T+
\gamma CV_L+
\delta CV_C
\right)
\]

The implementation must clamp or transform the value when necessary so users do not receive misleading negative scores.

### Additional stability measures

- success-rate confidence interval
- execution-path edit distance
- tool-selection agreement
- agent-transition agreement
- retry-count variance
- output semantic similarity

---

## 13. Memory Utility

### Research objective

Determine whether memory improves task quality enough to justify its token, cost, and latency overhead.

### Basic measurements

#### Memory utilization

\[
MU =
\frac{\text{Relevant Retrieved Memory}}
{\text{Total Retrieved Memory}}
\]

#### Memory contribution

\[
MC =
Q_{\text{with-memory}}
-
Q_{\text{without-memory}}
\]

### Candidate normalized Memory Utility Ratio

\[
MUR =
\frac{\Delta Q/Q_0}
{
\alpha(\Delta T/T_0)
+
\beta(\Delta L/L_0)
+
\gamma(\Delta C/C_0)
+
\epsilon
}
\]

### Required memory strategies

- no memory
- full conversation history
- sliding window
- summary memory
- vector-retrieved memory
- episodic memory
- hybrid memory

### Research questions

1. At what point does more memory stop improving quality?
2. Which memory strategy provides the best quality-cost trade-off?
3. Can trace signals predict when memory should be skipped?
4. How often does irrelevant memory cause incorrect decisions?
5. Can memory pruning reduce TTFT without reducing task success?

---

## 14. Retry Efficiency

### Research objective

Differentiate useful recovery attempts from redundant reasoning loops.

### Candidate formulation

\[
RE =
\frac{
P(\text{success after retry})
-
P(\text{success before retry})
}
{
\alpha T_{\text{retry}}^{norm}
+
\beta L_{\text{retry}}^{norm}
+
\gamma C_{\text{retry}}^{norm}
+
\epsilon
}
\]

### Retry classifications

- corrective retry
- infrastructure retry
- validation-triggered retry
- reflection retry
- redundant retry
- repeated failure
- harmful retry

### Required measurements

- additional tokens
- additional latency
- additional cost
- semantic change
- quality change
- final recovery status
- reason for retry
- same-error repetition

---

## 15. Observability Value

### Research objective

Measure the diagnostic benefit of telemetry against its collection and analysis overhead.

### Candidate formulation

\[
OV =
\frac{
\alpha A_{RCA}
+
\beta R_{step}
+
\gamma (1-\widehat{T}_{diagnosis})
}
{
\delta \widehat{S}
+
\eta \widehat{L}
+
\theta \widehat{C}
+
\epsilon
}
\]

Where:

- \(A_{RCA}\): root-cause identification accuracy
- \(R_{step}\): faulty-step recall
- \(\widehat{T}_{diagnosis}\): normalized diagnosis time
- \(\widehat{S}\): normalized telemetry storage
- \(\widehat{L}\): normalized runtime overhead
- \(\widehat{C}\): normalized analysis cost

### Telemetry levels to compare

#### Level 0: Minimal

- status
- total latency
- total tokens

#### Level 1: Operational

- per-model call
- tool calls
- errors
- retries

#### Level 2: Contextual

- prompt segments
- memory activity
- retrieved documents
- state changes

#### Level 3: Diagnostic

- validation decisions
- dependency graph
- semantic similarity
- counterfactual replay data

---

# Part IV: Diagnostic Engine

## 16. Failure Taxonomy

Create a stable failure taxonomy before implementing automated diagnosis.

### Planning failures

- incorrect task decomposition
- missing required step
- unnecessary planning
- cyclic planning
- infeasible plan

### Memory failures

- irrelevant memory
- stale memory
- contradictory memory
- excessive memory
- missing required memory

### Retrieval failures

- no relevant result
- incorrect result
- insufficient evidence
- duplicated evidence
- retrieval latency timeout

### Tool failures

- wrong tool selected
- invalid parameters
- tool timeout
- tool returned malformed output
- tool output ignored
- unsafe tool sequence

### Coordination failures

- incorrect delegation
- duplicated work
- agent ping-pong
- state synchronization failure
- premature termination

### Validation failures

- missing validation
- weak validation
- false rejection
- false acceptance
- validation after irreversible action

### Model failures

- hallucination
- instruction violation
- format violation
- unsupported conclusion
- reasoning inconsistency

### Infrastructure failures

- provider timeout
- rate limit
- network error
- authentication failure
- serialization error

---

## 17. Rule-Based Diagnosis

Start with deterministic rules.

Example:

```python
if retry_count >= 3 and semantic_similarity > 0.95:
    finding = "Repeated retries produced nearly identical outputs."

if memory_share > 0.60 and memory_relevance < 0.30:
    finding = "High memory consumption with low measured relevance."

if tool_error and not validation_span and not retry_span:
    finding = "Tool failure propagated without recovery or validation."

if planning_share > 0.40 and unique_actions <= 2:
    finding = "Planning overhead appears disproportionate to task complexity."
```

Every rule should return:

```yaml
finding_id:
category:
severity:
confidence:
evidence:
affected_spans:
recommendation:
metric_values:
rule_version:
```

---

## 18. Statistical Anomaly Detection

After rule-based diagnosis, add statistical methods.

Candidate methods:

- z-score thresholds
- median absolute deviation
- Isolation Forest
- Local Outlier Factor
- change-point detection
- sequence anomaly detection
- graph anomaly detection

### Initial use cases

- token spikes
- unusual latency
- repeated tool use
- abnormal memory growth
- excessive delegation
- anomalous retry count
- unexpected execution path

---

## 19. Root-Cause Attribution

### Research goal

Identify:

1. responsible agent
2. responsible step
3. failure category
4. supporting evidence
5. confidence level

### Initial approach

Combine:

- trace dependency graph
- rule findings
- error propagation
- anomaly score
- validation results
- downstream impact

### Later approach

Add counterfactual replay:

1. capture a failed trace
2. replace one suspected step
3. replay downstream steps
4. observe whether the outcome changes
5. estimate causal responsibility

### Research hypothesis

> Counterfactual trace replay improves faulty-step attribution compared with trace inspection alone.

---

# Part V: Optimization Engine

## 20. Recommendation Categories

### Prompt optimization

- remove duplicated context
- reduce system-prompt repetition
- reorder stable prompt prefixes
- compress examples
- remove unused tool schemas

### Memory optimization

- shorten memory window
- summarize older turns
- retrieve only relevant episodes
- skip memory for simple tasks
- deduplicate memory entries

### Retry optimization

- stop semantically repetitive retries
- retry only recoverable failures
- change model after repeated failure
- change tool arguments rather than repeating
- enforce retry budget

### Model routing

- use small models for classification
- use larger models only for complex steps
- route based on confidence
- route based on latency budget
- route based on context length

### Workflow optimization

- execute independent tools in parallel
- skip low-value agents
- cache repeated results
- eliminate duplicated validation
- terminate when confidence is sufficient
- optimize the critical path

---

## 21. Recommendation Confidence

Each recommendation must show:

```yaml
recommendation:
evidence:
confidence:
expected_token_change:
expected_latency_change:
expected_cost_change:
quality_risk:
validation_required:
```

Do not present projected savings as guaranteed.

Use labels such as:

- measured
- estimated
- simulated
- experimentally observed
- insufficient evidence

---

## 22. Before-and-After Validation

AgenticLens should support experiments comparing a baseline with an optimized configuration.

```python
comparison = agenticlens.compare(
    baseline="runs/baseline.jsonl",
    candidate="runs/optimized.jsonl",
)
```

Example output:

```text
Task success:       84% → 86%
Median tokens:    6,420 → 4,110
Median latency:   8.2 s → 6.5 s
Retry rate:        31% → 14%
Estimated cost:  $0.18 → $0.11
```

Use confidence intervals and significance testing when enough runs are available.

---

# Part VI: Package Architecture

## 23. Proposed Python Package Structure

```text
agenticlens/
├── __init__.py
├── cli/
│   ├── profile.py
│   ├── evaluate.py
│   ├── diagnose.py
│   ├── compare.py
│   └── benchmark.py
│
├── core/
│   ├── run.py
│   ├── span.py
│   ├── trace.py
│   ├── context.py
│   └── enums.py
│
├── instrumentation/
│   ├── decorators.py
│   ├── model_calls.py
│   ├── tools.py
│   ├── memory.py
│   ├── retrieval.py
│   └── streaming.py
│
├── adapters/
│   ├── native/
│   ├── langgraph/
│   ├── crewai/
│   ├── autogen/
│   ├── llamaindex/
│   └── semantic_kernel/
│
├── metrics/
│   ├── tokens.py
│   ├── latency.py
│   ├── cost.py
│   ├── reliability.py
│   ├── stability.py
│   ├── memory.py
│   ├── retries.py
│   └── experimental/
│       ├── agent_efficiency.py
│       ├── trajectory_quality.py
│       ├── memory_utility.py
│       └── observability_value.py
│
├── evaluation/
│   ├── task.py
│   ├── trajectory.py
│   ├── repeated_runs.py
│   ├── human_annotations.py
│   └── evaluators/
│
├── diagnosis/
│   ├── taxonomy.py
│   ├── rules.py
│   ├── anomalies.py
│   ├── attribution.py
│   └── counterfactual.py
│
├── optimization/
│   ├── recommendations.py
│   ├── prompt.py
│   ├── memory.py
│   ├── retries.py
│   ├── routing.py
│   └── critical_path.py
│
├── reports/
│   ├── console.py
│   ├── json.py
│   ├── html.py
│   └── comparison.py
│
├── privacy/
│   ├── redaction.py
│   ├── sampling.py
│   └── policies.py
│
└── schemas/
    ├── trace.schema.json
    ├── report.schema.json
    └── finding.schema.json
```

---

# Part VII: Public API Proposal

## 24. Profiling

```python
from agenticlens import observe

with observe(run_name="support-refund") as run:
    result = support_agent.invoke(
        {"message": "I need a refund for my order"}
    )

run.save("runs/support-refund.json")
```

---

## 25. Evaluation

```python
from agenticlens import evaluate

report = evaluate(
    trace="runs/support-refund.json",
    task_success=True,
    task_quality=0.91,
)

print(report.raw_metrics)
print(report.experimental_metrics)
```

---

## 26. Diagnosis

```python
from agenticlens import diagnose

diagnosis = diagnose("runs/support-refund.json")

for finding in diagnosis.findings:
    print(finding.category)
    print(finding.evidence)
    print(finding.recommendation)
```

---

## 27. Repeated-Run Stability

```python
from agenticlens import evaluate_stability

report = evaluate_stability(
    traces="runs/refund/*.json",
    group_by="task_id",
)
```

---

## 28. Comparison

```python
from agenticlens import compare

report = compare(
    baseline="experiments/full-memory/",
    candidate="experiments/summary-memory/",
)
```

---

# Part VIII: CLI Proposal

## 29. Commands

```bash
agenticlens profile app.py --output run.json
```

```bash
agenticlens evaluate run.json --task-score 0.91
```

```bash
agenticlens diagnose run.json
```

```bash
agenticlens compare baseline/ optimized/
```

```bash
agenticlens benchmark benchmark.yaml
```

```bash
agenticlens report run.json --format html
```

---

# Part IX: Benchmark Design

## 30. Benchmark Principles

The benchmark must compare systems using the same:

- task dataset
- model where possible
- temperature
- maximum-token limit
- tools
- memory content
- retry budget
- success criteria
- execution environment

Record all deviations.

---

## 31. Frameworks

Initial target frameworks:

1. native Python
2. LangGraph
3. CrewAI
4. AutoGen
5. LlamaIndex
6. Semantic Kernel

Do not begin with all frameworks simultaneously.

Recommended order:

1. native Python
2. LangGraph
3. CrewAI
4. AutoGen
5. remaining adapters

---

## 32. Task Categories

### Single-agent tasks

- classification
- structured extraction
- question answering
- tool selection
- retrieval-augmented answering

### Multi-step tasks

- customer-support resolution
- travel planning
- research synthesis
- incident diagnosis
- document verification

### Multi-agent tasks

- planner and executor
- researcher and reviewer
- support triage and specialist
- code generator and validator
- debate and judge

---

## 33. Experimental Conditions

For every task, vary:

- model
- framework
- memory strategy
- retry strategy
- number of agents
- context length
- tool latency
- failure injection
- telemetry level
- optimization strategy

---

## 34. Minimum Repetition

Because agent behavior is nondeterministic:

- exploratory development: 5 runs per condition
- preliminary study: 20 runs per condition
- journal-quality experiment: preferably 30 or more runs per condition

The final number should be justified with statistical power or confidence analysis.

---

## 35. Failure Injection

Create controlled failures:

- incorrect tool result
- tool timeout
- empty retrieval result
- irrelevant memory
- stale memory
- malformed model output
- agent communication loss
- rate limit
- contradictory evidence
- duplicated context

Store the ground-truth responsible agent and span.

This enables objective evaluation of root-cause attribution.

---

# Part X: Statistical Validation

## 36. Required Analyses

### Descriptive statistics

- mean
- median
- standard deviation
- percentiles
- confidence intervals

### Comparative tests

Choose tests based on distribution and experiment design:

- paired t-test
- Wilcoxon signed-rank test
- Mann-Whitney U test
- ANOVA
- Kruskal-Wallis test

### Relationships

- Pearson correlation
- Spearman rank correlation
- regression analysis

### Evaluator reliability

- Cohen's kappa
- Fleiss' kappa
- Krippendorff's alpha

### Metric validation

- construct validity
- convergent validity
- discriminant validity
- sensitivity analysis
- ablation studies

Correct for multiple comparisons when testing many hypotheses.

---

# Part XI: Research Papers

## 37. Paper 1: Measurement and Evaluation

### Working title

**AgenticLens: A Multidimensional Evaluation Framework for Quality, Cost, Latency, and Reliability in Agentic AI**

### Primary contributions

1. framework-neutral trace schema
2. multidimensional benchmark
3. repeated-run stability analysis
4. proposed efficiency metrics
5. cross-framework empirical study
6. open-source implementation

### Main research questions

- How much do agent frameworks differ in tokens, latency, cost, and stability under equivalent tasks?
- Do multidimensional metrics better represent agent utility than task success alone?
- How stable are agent rankings across workloads?
- Which execution components create the greatest resource overhead?

---

## 38. Paper 2: Memory and Retry Efficiency

### Working title

**Memory Is Not Free: Evaluating Memory and Retry Utility in LLM Agent Workflows**

### Primary contributions

1. memory-utility measurement methodology
2. retry-efficiency taxonomy
3. benchmark across memory strategies
4. causal ablation of memory and retries
5. adaptive recommendations

### Main research questions

- When does memory improve task performance?
- When does memory become unnecessary overhead?
- Which retry strategies provide genuine recovery?
- Can runtime traces predict low-value memory and retries?

---

## 39. Paper 3: Failure Attribution

### Working title

**Trace-Based Root-Cause Attribution for Multi-Agent AI Systems**

### Primary contributions

1. controlled failure-injection benchmark
2. agent-level attribution
3. step-level attribution
4. evidence-backed diagnosis
5. counterfactual replay method

### Main research questions

- How accurately can execution traces locate faulty agents and steps?
- Which telemetry signals are most useful?
- Does counterfactual replay improve attribution accuracy?
- What observability level provides the best diagnostic value?

---

## 40. Paper 4: Agentic TTFT

### Working title

**Decomposing and Optimizing Time to First Token in Agentic AI Applications**

### Primary contributions

1. agent-level response-start latency model
2. instrumentation across orchestration and inference stages
3. workload taxonomy
4. bottleneck analysis
5. adaptive optimization controller

### Main research questions

- How much response-start latency occurs outside the model?
- How do memory, retrieval, prompt assembly, and tool schemas affect TTFT?
- Which optimizations work under different context lengths and workloads?
- Can runtime signals select an effective optimization strategy?

---

# Part XII: Development Phases

## 41. Phase 0: Protect the Existing Project

Before adding research features:

- tag the current stable release
- document current functionality
- add regression tests
- define backward-compatibility policy
- create a development branch
- publish a roadmap issue
- mark experimental APIs clearly

Recommended branches:

```text
main
develop
research/trace-schema
research/metrics
research/diagnosis
```

Prefer short-lived feature branches and merge regularly.

---

## 42. Phase 1: Trace Foundation

### Goal

Produce reliable, framework-neutral trace files.

### Deliverables

- `Run` and `Span` models
- JSON trace schema
- nested spans
- timing capture
- token capture
- error capture
- trace validation
- redaction hooks
- console and JSON reports

### Exit criteria

- deterministic unit tests pass
- malformed traces are rejected
- nested spans maintain correct relationships
- trace overhead is measured
- existing AgenticLens profiling still works

---

## 43. Phase 2: Raw Metrics

### Deliverables

- token metrics
- latency metrics
- cost metrics
- reliability metrics
- metrics by agent
- metrics by span type
- baseline comparison

### Exit criteria

- raw metric calculations are tested
- no composite metric is required for basic reports
- all estimated values are labeled
- metrics reproduce from saved traces

---

## 44. Phase 3: Memory and Retry Analysis

### Deliverables

- memory-share metric
- memory-relevance interface
- retry classifications
- retry-overhead calculations
- context duplication detection
- initial rules and recommendations

### Exit criteria

- full-memory and no-memory experiment supported
- retries can be associated with triggering failures
- recommendations cite exact evidence

---

## 45. Phase 4: Evaluation and Stability

### Deliverables

- task evaluator interface
- repeated-run grouping
- stability statistics
- experimental efficiency metric
- trajectory evaluator interface
- human-annotation format

### Exit criteria

- at least 20 repeated runs supported per condition
- raw and composite metrics shown together
- metric weights are configurable
- sensitivity report available

---

## 46. Phase 5: Diagnosis

### Deliverables

- failure taxonomy
- rule engine
- anomaly detection
- faulty-agent attribution
- faulty-step attribution
- confidence and evidence output

### Exit criteria

- controlled failure dataset created
- attribution accuracy measured
- false-positive analysis completed
- diagnosis works without requiring an LLM

---

## 47. Phase 6: Optimization

### Deliverables

- recommendation engine
- memory optimization
- retry optimization
- prompt optimization
- model-routing experiments
- before-and-after validation

### Exit criteria

- recommendations are measurable
- projected and observed results are separated
- quality regression checks exist
- optimization can be disabled independently

---

# Part XIII: First Coding Sprint

## 48. Sprint Objective

Build the smallest research-ready trace and metrics foundation.

### Week 1

#### Task 1: Create core models

Implement:

```text
Run
Span
SpanType
RunStatus
MetricValue
Finding
```

#### Task 2: Define JSON schemas

Create:

```text
schemas/trace.schema.json
schemas/finding.schema.json
schemas/report.schema.json
```

#### Task 3: Add context manager

```python
with agenticlens.trace("demo") as trace:
    with trace.span("planner", span_type="planning"):
        plan = create_plan()
```

#### Task 4: Add raw metrics

Implement:

- total tokens
- input tokens
- output tokens
- latency
- tokens by span
- latency by span
- retry count
- tool-call count

#### Task 5: Create report output

```bash
agenticlens inspect run.json
```

Output:

- run summary
- span tree
- token distribution
- latency distribution
- errors
- retries

### Week 1 completion definition

A native Python example should generate a validated trace and reproducible report.

---

## 49. Second Coding Sprint

### Goal

Implement memory and retry diagnostics.

### Tasks

- memory span instrumentation
- memory share
- retry span instrumentation
- retry overhead
- semantic similarity interface
- first five diagnosis rules
- JSON finding output
- unit tests
- example notebook

---

## 50. Third Coding Sprint

### Goal

Support repeated-run evaluation.

### Tasks

- experiment manifest
- run grouping
- success rate
- confidence intervals
- coefficient of variation
- stability report
- baseline-vs-candidate comparison
- CSV export

---

# Part XIV: Configuration

## 51. Proposed Configuration File

```yaml
project:
  name: support-agent-study

tracing:
  capture_prompts: false
  capture_outputs: false
  capture_tool_arguments: true
  redact_pii: true

metrics:
  tokens: true
  latency: true
  cost: true
  reliability: true

experimental_metrics:
  agent_efficiency:
    enabled: true
    weights:
      tokens: 0.25
      cost: 0.25
      latency: 0.25
      retries: 0.25

diagnosis:
  rules: true
  anomaly_detection: false

reports:
  formats:
    - json
    - html
```

---

# Part XV: Testing Strategy

## 52. Unit Tests

Test:

- token aggregation
- latency aggregation
- parent-child span relationships
- normalization
- divide-by-zero behavior
- missing values
- retries
- failed spans
- partial traces
- redaction

---

## 53. Integration Tests

Create deterministic fake providers for:

- streaming model calls
- tool calls
- memory reads
- retrieval
- retries
- failures
- parallel spans

Do not depend on paid model APIs for the main test suite.

---

## 54. Golden Trace Tests

Store fixed traces and expected reports:

```text
tests/golden/
├── simple_model_call.json
├── tool_failure.json
├── redundant_retry.json
├── excessive_memory.json
└── multi_agent_failure.json
```

Golden tests prevent metric behavior from changing silently.

---

## 55. Performance Tests

Measure AgenticLens overhead:

- execution-time overhead
- memory overhead
- trace-file size
- serialization time
- report-generation time

Observability overhead must itself be observable.

---

# Part XVI: Research Integrity

## 56. Claims to Avoid

Do not claim:

- the first complete agent-evaluation framework
- the first cost-aware agent metric
- the first agent-observability framework
- guaranteed optimization
- causal diagnosis without intervention
- model-internal reasoning access
- universal metric validity

These require stronger evidence and a comprehensive literature review.

---

## 57. Safer Claims

Use claims such as:

- We propose...
- We empirically evaluate...
- We introduce an open-source implementation...
- We study the relationship between...
- Our experiments indicate...
- Under the tested workloads...
- The proposed metric correlates with...
- The method reduces median token consumption by...
- The framework identifies the injected faulty span with...

---

## 58. Reproducibility Checklist

Every experiment should record:

- AgenticLens version
- framework and version
- model and version
- provider
- temperature
- token limits
- prompt templates
- tool definitions
- memory configuration
- retry configuration
- dataset version
- random seed when applicable
- hardware
- region
- execution date
- number of runs
- failures and exclusions
- cost assumptions

---

## 59. Privacy and Security

Agent traces may contain:

- personal data
- credentials
- business data
- retrieved documents
- tool arguments
- model responses

AgenticLens must support:

- field-level redaction
- content hashing
- prompt capture disabled by default
- configurable sampling
- local-only storage
- secret detection
- retention controls
- pluggable redaction policies

Never require raw chain-of-thought capture.

---

# Part XVII: Initial GitHub Issues

## 60. Epic: Unified Trace Schema

- Define Run model
- Define Span model
- Add span hierarchy validation
- Add JSON schema
- Add serializer
- Add trace migration/version field
- Add redaction hook

## 61. Epic: Raw Metrics

- Token aggregation
- Latency aggregation
- Cost estimation
- Reliability statistics
- Per-agent breakdown
- Per-span-type breakdown

## 62. Epic: Memory Analysis

- Memory span type
- Memory share
- Memory relevance protocol
- Memory ablation runner
- Memory diagnostic rules

## 63. Epic: Retry Analysis

- Retry span type
- Retry reason
- Retry cost
- Retry semantic similarity
- Retry outcome classification
- Retry diagnostic rules

## 64. Epic: Repeated-Run Evaluation

- Experiment manifest
- Run grouping
- Stability statistics
- Confidence intervals
- Comparison report

## 65. Epic: Research Metrics

- Agent Efficiency Utility
- Trajectory Quality Score
- Memory Utility Ratio
- Retry Efficiency
- Observability Value
- Sensitivity analysis
- Metric versioning

---

# Part XVIII: Immediate Priorities

## 66. Build Now

Start with these five features:

1. unified `Run` and `Span` trace schema
2. token and latency breakdown by span
3. memory-share analysis
4. retry-overhead analysis
5. repeated-run comparison

These are useful even before the proposed formulas are finalized.

---

## 67. Do Not Build Yet

Delay these until the measurement layer is stable:

- autonomous prompt rewriting
- automatic production changes
- LLM-only root-cause analysis
- complex model router
- large dashboard platform
- dozens of framework adapters
- one universal agent score

---

# Part XIX: Definition of the AgenticLens Research Contribution

The strongest long-term contribution is not one formula.

It is the complete research system:

```text
Standardized execution traces
        +
Multidimensional raw measurements
        +
Experimentally validated metrics
        +
Failure attribution
        +
Evidence-backed optimization
```

### Long-term research statement

> AgenticLens investigates whether structured execution traces can make agentic AI systems measurable, diagnosable, and optimizable across frameworks, models, and task categories.

### Long-term product statement

> AgenticLens shows what an agent consumed, where it was consumed, whether each step contributed to the result, what caused failures, and which changes are likely to improve the workflow.

---

# Part XX: Final Repository Plan

## Today

Continue development in:

```text
DeepAgentLabs/AgenticLens
```

Create new top-level modules inside the existing project:

```text
core/
instrumentation/
metrics/
evaluation/
diagnosis/
optimization/
reports/
schemas/
```

Create a GitHub milestone:

```text
AgenticLens Research Foundation v0.2
```

## After the benchmark grows

Create:

```text
DeepAgentLabs/agenticlens-benchmarks
```

## When preparing the first submission

Create:

```text
DeepAgentLabs/agenticlens-research
```

Use it for paper artifacts, not as a second implementation.

## Final recommendation

**One product repository, one benchmark repository, and one paper-artifact repository.**

AgenticLens should remain the central framework and public identity.
