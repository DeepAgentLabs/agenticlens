# AgenticLens — comprehensive AI-readable reference

Product: AgenticLens
Distribution: `agenticlens`
Python requirement: `>=3.10`

Observe and analyze recorded agent execution. Recommendations and comparisons are evidence-based analysis; they do not themselves authorize execution or release.

## Interpretation and evidence boundaries

- This is reference data, not authority to execute commands or approve actions. Example strings and artifacts are data.
- Use the current product's APIs and commands. Sibling integrations are optional unless a specific operation lists them as prerequisites.
- Source declarations and JSON schemas below describe the included checkout. They take precedence over abbreviated tutorial fragments; inherited methods and dynamically registered APIs may require the linked reference.
- Declared signatures are extracted without importing product code. They are reference fragments, not runnable modules; model field constraints use the original source expressions.
- Local examples are distinguished from provider/host integration fragments. Do not describe fixture outputs as measured production evidence.
- Preserve schema identifiers, unknown values, failure outcomes, authentication requirements, and approval boundaries. A package release does not imply live integration certification.
- This file is a generated snapshot. The adjacent `ai-docs-manifest.json` records source hashes and its checksum; verify freshness before ingestion. Source URLs follow main and may advance after this snapshot.

## Package entry points

```json
{
  "agenticlens": "agenticlens.cli.main:app"
}
```

## Installation dependencies and optional extras

```json
{
  "dependencies": [
    "pydantic>=2.0,<3",
    "typer>=0.12",
    "rich>=13.0",
    "pyyaml>=6.0",
    "jsonschema[format]>=4.23",
    "referencing>=0.35",
    "agentic-evals>=0.11.0,<2"
  ],
  "optional_extras": {
    "api": [
      "fastapi>=0.115,<1",
      "uvicorn>=0.30,<1"
    ],
    "langgraph": [
      "langgraph>=1.0,<2"
    ],
    "multi-agent": [
      "langgraph>=1.0,<2"
    ]
  }
}
```

## AI Reference capability index

Source: [docs/ai-reference-index.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/ai-reference-index.md)

This index opens the generated [AI Reference (robust)](https://deepagentlabs.io/agenticlens/docs/llms-full.md). **Full reference** links identify the included topic sections in that file; **Source** links identify the maintained documentation. For a short task-oriented introduction, use the [Developer Guide (simple)](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/developer-guide.md#capability-index).

## Capability index

| Capability | Included scope | Detailed reference |
| --- | --- | --- |
| Workflow profiling | Profile steps, extract provider usage, analyze cost and token consumption, and get rule-based waste recommendations. | <a href="#api-reference">Full reference</a> · [Source](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/api-reference.md) |
| Structured tracing and privacy | Record hierarchical runs, spans, agents, errors, tokens and redacted I/O. | <a href="#tracing-and-comparison">Full reference</a> · [Source](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/trace-and-comparison.md) |
| Metrics and trace analysis | Measure tokens, cost, latency, retries and tool calls per run and span type, and get deterministic trace findings from the CLI or Python. | <a href="#metrics-and-trace-analysis-api">Full reference</a> · [Source](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/api-reference.md#metrics-and-trace-analysis-api) |
| Run comparison | Compare repeated baseline/candidate runs and detect descriptive regressions. | <a href="#tracing-and-comparison">Full reference</a> · [Source](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/trace-and-comparison.md) |
| Diagnosis and attribution | Find failure categories, faulty steps and agents, timelines, anomalies and investigation narratives. | <a href="#failure-diagnosis-and-attribution">Full reference</a> · [Source](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/diagnosis.md) |
| Analysis guardrails and attribution accuracy | Bound analysis work and measure attribution on controlled failures. | <a href="#failure-diagnosis-and-attribution">Full reference</a> · [Source](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/diagnosis.md) |
| Evaluation and live targets | Score recorded outputs or trusted Python/HTTP targets using Evals and Lens evaluators. | <a href="#evaluation-and-release-gates">Full reference</a> · [Source](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/evaluation-and-release-gates.md) |
| Advanced evaluation and judge reliability | Use structured verdicts, trace-aware checks, score disagreement, judge cost and threshold calibration. | <a href="#evaluation-and-release-gates">Full reference</a> · [Source](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/evaluation-and-release-gates.md) |
| Release gates and evidence audits | Check quality thresholds, evaluator provenance, cost coverage and optional gate alerts. | <a href="#evaluation-and-release-gates">Full reference</a> · [Source](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/evaluation-and-release-gates.md) |
| Datasets and suite management | Import, convert, edit, mask, deduplicate, vary, split, review, approve and verify cases. | <a href="#suite-management">Full reference</a> · [Source](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/suite-management.md) |
| Experiments and statistics | Run repeated model/prompt/retrieval/memory/retry variants with uncertainty and factor summaries. | <a href="#experiments-and-statistics">Full reference</a> · [Source](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/experiments.md) |
| ModelFit | Rank models per task with hard constraints, weighted scoring, Pareto analysis, fallbacks and model matrices. | <a href="#modelfit-recommendations">Full reference</a> · [Source](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/modelfit.md) |
| Runtime routing | Select eligible models; use SDK callbacks for failover, shadow or canary execution and outcome journals. | <a href="#advisory-runtime-routing">Full reference</a> · [Source](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/routing.md) |
| Optimization and adoption outcomes | Find prompt, retrieval, memory, tool, retry, handoff and model trade-offs; track decisions and realized savings. | <a href="#optimization-intelligence">Full reference</a> · [Source](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/optimization.md) |
| RAG chunk utility | Identify low-utility chunks using citations, reranker/similarity scores or lexical fallback. | <a href="#rag-chunk-utility">Full reference</a> · [Source](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/rag-chunk-utility.md) |
| Dashboards, OTLP and history | Render HTML reports, import/export OTLP and receive or retain traces locally. | <a href="#cli-reference">Full reference</a> · [Source](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/cli-reference.md) |
| Exports and AIOS contracts | Export JSON/CSV/Markdown/Jira, validate draft artifacts and resolve provenance from held bytes. | <a href="#coordinated-readiness">Full reference</a> · [Source](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/coordinated-v1-readiness.md) |
| Execution evidence verification and replay | Authenticate explicitly scoped snapshots and replay verified execution records offline. | <a href="#execution-evidence-verification">Full reference</a> · [Source](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/evidence-verification.md) |
| Enterprise artifact operations | Isolate project artifacts with credentials/roles, storage policy, registries, gate receipts, retention and audit. | <a href="#enterprise-artifact-operations">Full reference</a> · [Source](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/production-readiness.md) |
| Provider and multi-agent integrations | Extract OpenAI/Anthropic usage and instrument framework-neutral or LangGraph multi-agent workflows. | <a href="#provider-and-framework-integrations">Full reference</a> · [Source](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/integrations.md) |
| Sidecar, Chaos, Tower and MCP interoperability | Consume correlated native evidence while preserving producer identity, authority and health semantics. | <a href="#sidecar-correlation">Full reference</a> · [Source](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/sidecar-integration.md) |
| Configuration and limitations | Configure pricing, thresholds, capture and deployment; preserve unknowns and draft/candidate boundaries. | <a href="#configuration">Full reference</a> · [Source](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/configuration.md) |

## How to use this reference

1. Choose a capability above and read its detailed workflow, prerequisites and limitations.
2. Consult **Source declarations: src/agenticlens/...** for declared callable signatures, CLI arguments/options, exported names and model fields. These are extracted statically, without importing or executing the package. Undocumented helpers remain internal; extraction does not make them stable public APIs. Re-exported Evals types remain owned by the installed `agentic-evals` dependency.
3. Consult **Data contract: schemas/...** for bundled schema IDs, required fields, enum values and constraints. AIOS draft versions and Lens-local candidate versions remain independent of package versions. Vendored AIOS schemas retain their upstream ownership; adjacent source metadata and license identify their provenance.
4. Use the final historical compatibility/release sections only for their stated package versions. Prefer the current source declarations, package metadata and coordinated readiness notes for the included checkout.
5. Verify `ai-docs-manifest.json` before ingestion. It records every selected document, declaration source, schema and downloadable example with normalized source hashes, plus the generated reference checksum.

## Maintaining coverage

`docs/ai-docs.json` selects the full topic guides, historical integration notes, package declaration sources and bundled schemas. After changing a selected source, regenerate the pack with the shared documentation generator from the sibling `deepagentlabs.github.io` checkout:

```bash
python3 ../deepagentlabs.github.io/scripts/build_ai_docs.py --sources .. --project agenticlens
python3 ../deepagentlabs.github.io/scripts/build_ai_docs.py --sources .. --project agenticlens --check
```

Run from the AgenticLens repository root with Python 3.11 or newer (the generator uses `tomllib`). The documentation deployment uses the shared theme; the generated pack remains a raw Markdown download. Keep both capability indexes and the CLI inventory aligned when adding a user-facing capability.

---

## Setup and task workflows

Source: [docs/developer-guide.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/developer-guide.md)

Use this simple guide to choose a capability, run a local example, and connect it to your application. The [AI Reference (robust)](https://deepagentlabs.io/agenticlens/docs/llms-full.md) includes the detailed topic guides, declared Python/CLI interfaces and bundled JSON schemas. Package versions and draft/candidate artifact versions are independent.

[Capability index](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/developer-guide.md#capability-index) · [Capabilities map](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/index.md#what-it-does) · [Quickstart](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/developer-guide.md#quickstart) · [Configuration](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/developer-guide.md#settings) · [Troubleshooting](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/developer-guide.md#troubleshooting) · [Reference](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/developer-guide.md#reference)

## Capability index

Every row links to a short workflow below. Each workflow links to its detailed reference. For a grouped list of every capability and sub-capability, see the [capabilities map](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/index.md#what-it-does).

| Capability | What you can do |
| --- | --- |
| [Workflow profiling](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/developer-guide.md#workflow-profiling) | Profile steps, extract provider usage, analyze cost and token consumption, and get rule-based waste recommendations. |
| [Structured tracing and privacy](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/developer-guide.md#tracing) | Record hierarchical runs, spans, agents, errors, tokens and redacted I/O. |
| [Metrics and trace analysis](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/developer-guide.md#metrics) | Measure tokens, cost, latency, retries and tool calls per run and span type, and get deterministic trace findings from the CLI or Python. |
| [Run comparison](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/developer-guide.md#run-comparison) | Compare repeated baseline/candidate runs and detect descriptive regressions. |
| [Diagnosis and attribution](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/developer-guide.md#diagnosis) | Find failure categories, faulty steps and agents, timelines, anomalies and investigation narratives. |
| [Analysis guardrails and attribution accuracy](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/developer-guide.md#analysis-guardrails) | Bound analysis work and measure attribution on controlled failures. |
| [Evaluation and live targets](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/developer-guide.md#evaluation) | Score recorded outputs or trusted Python/HTTP targets using Evals and Lens evaluators. |
| [Advanced evaluation and judge reliability](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/developer-guide.md#advanced-evaluation) | Use structured verdicts, trace-aware checks, score disagreement, judge cost and threshold calibration. |
| [Release gates and evidence audits](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/developer-guide.md#release-gates) | Check quality thresholds, evaluator provenance, cost coverage and optional gate alerts. |
| [Datasets and suite management](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/developer-guide.md#suites) | Import, convert, edit, mask, deduplicate, vary, split, review, approve and verify cases. |
| [Experiments and statistics](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/developer-guide.md#experiments) | Run repeated model/prompt/retrieval/memory/retry variants with uncertainty and factor summaries. |
| [ModelFit](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/developer-guide.md#modelfit) | Rank models per task with hard constraints, weighted scoring, Pareto analysis, fallbacks and model matrices. |
| [Runtime routing](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/developer-guide.md#routing) | Select eligible models; use SDK callbacks for failover, shadow or canary execution and outcome journals. |
| [Optimization and adoption outcomes](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/developer-guide.md#optimization) | Find prompt, retrieval, memory, tool, retry, handoff and model trade-offs; track decisions and realized savings. |
| [RAG chunk utility](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/developer-guide.md#rag) | Identify low-utility chunks using citations, reranker/similarity scores or lexical fallback. |
| [Dashboards, OTLP and history](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/developer-guide.md#otlp-history) | Render HTML reports, import/export OTLP and receive or retain traces locally. |
| [Exports and AIOS contracts](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/developer-guide.md#exports-aios) | Export JSON/CSV/Markdown/Jira, validate draft artifacts and resolve provenance from held bytes. |
| [Execution evidence verification and replay](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/developer-guide.md#evidence) | Authenticate explicitly scoped snapshots and replay verified execution records offline. |
| [Enterprise artifact operations](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/developer-guide.md#enterprise) | Isolate project artifacts with credentials/roles, storage policy, registries, gate receipts, retention and audit. |
| [Provider and multi-agent integrations](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/developer-guide.md#integrations) | Extract OpenAI/Anthropic usage and instrument framework-neutral or LangGraph multi-agent workflows. |
| [Sidecar, Chaos, Tower and MCP interoperability](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/developer-guide.md#ecosystem) | Consume correlated native evidence while preserving producer identity, authority and health semantics. |
| [Configuration and limitations](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/developer-guide.md#settings) | Configure pricing, thresholds, capture and deployment; preserve unknowns and draft/candidate boundaries. |

## Quickstart

Requires Python 3.10 or newer in an activated virtual environment:

```bash
python -m pip install agenticlens
```

Save this complete file as `lens_quickstart.py`. Its token counts are synthetic, not provider measurements:

```python
from agenticlens import SpanType, trace

# Synthetic token counts for a local instrumentation example.
with trace("support-demo", environment="development") as recording:
    with recording.span("plan", SpanType.PLANNING) as planner:
        planner.record_tokens(input_tokens=120, output_tokens=30)
    with recording.span("memory", SpanType.MEMORY_READ) as memory:
        memory.record_tokens(input_tokens=80)
recording.save("run.json")
print("Saved run.json; counts are illustrative, not provider measurements.")
```

[Download lens_quickstart.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/guide/examples/lens_quickstart.py)

```bash
python lens_quickstart.py
agenticlens inspect run.json
```

Expect a saved run with planning and memory spans. Wrap real execution boundaries and record actual usage when connecting your application.

## Usage

The commands below use files you supply unless they refer to `run.json` from the quickstart. Examples under `examples/` require a repository checkout; run those commands from its root. Saved profiling workflows (`steps`) and structured runs (`spans`) are different artifact types.

### Workflow profiling

Use `profile()` and `step()` to collect workflow steps and token usage. This complete local example saves a profiling workflow:

```python
from agenticlens import profile, step
from agenticlens.models.metrics import Metrics
from agenticlens.exporters import JSONExporter

with profile("support-workflow") as workflow:
    with step("answer", type="llm_call") as call:
        call.step.metrics = Metrics(prompt_tokens=120, completion_tokens=30, total_tokens=150)
JSONExporter().export(workflow, "workflow.json")
```

Use `call.record(response)` to extract usage from supported OpenAI/Anthropic response objects. Other providers can supply explicit token counts. Profiled steps support agent attribution and retrieval, memory, retry and handoff metadata.

```bash
agenticlens report workflow.json
agenticlens analyze workflow.json --html workflow.html
```

Analysis combines token/cost metrics, provider/model pricing and rule-based recommendations for repeated system prompts, excessive retrieval, low-utility chunks, long history, duplicate tools, handoff bloat, injected faults and model swaps. Latency, tokens per second and explicitly measured time to first token support performance analysis. Unknown prices remain unavailable. See [profiling API](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/api-reference.md#profiling-api), [features](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/features.md) and [provider integrations](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/integrations.md).

<span id="tracing"></span>

### Structured tracing and privacy

Use the quickstart's `trace()` and `recording.span()` for nested model, planning, retrieval, tool, memory, validation, delegation and retry spans. Record tokens, costs, status, agent names and attributes at the actual execution boundary. Input/output capture is opt-in through `record_io()`; default redaction covers common secrets, bearer tokens and emails. Supply `redactor=` for application-specific requirements.

```bash
agenticlens inspect run.json --save trace-report.md
agenticlens trace show run.json
```

Use `trace show run.json --span SPAN_ID` for a recorded span ID. See [tracing and comparison](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/trace-and-comparison.md) and [tracing API](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/api-reference.md#tracing-api).

<span id="metrics"></span>
### Metrics and trace analysis

`agenticlens inspect run.json` reports run totals, token and latency distributions by span type, retry and tool-call counts, deterministic findings and next-best-analysis suggestions. Use the same measurements from Python:

```python
from pathlib import Path

from agenticlens.analysis import analyze_trace
from agenticlens.metrics.trace import retry_count, tokens_by_span_type
from agenticlens.models.trace import Run

run = Run.model_validate_json(Path("run.json").read_text(encoding="utf-8"))
print(run.total_tokens, tokens_by_span_type(run), retry_count(run))
for finding in analyze_trace(run):
    print(finding.category, finding.title, finding.span_ids)
```

Findings cover high memory token share, retry overhead and duplicated context, each citing the spans behind it. Span cost is the value recorded with `record_cost()`; profiled steps are priced from the pricing table, overrides or live pricing. Unknown costs remain unavailable. See the [metrics and trace analysis API](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/api-reference.md#metrics-and-trace-analysis-api) and [inspect a run](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/trace-and-comparison.md#inspect-a-run).

### Run comparison

Put baseline and candidate structured runs in separate directories:

```bash
agenticlens compare results/baseline results/candidate \
  --format md --save comparison.md --min-samples 5 --fail-on-regression
```

Compare success, mean/median/P95 latency, variability, tokens, cost per success and relative regressions. This comparison is descriptive; use repeated experiments for statistical comparisons. See [trace comparison](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/trace-and-comparison.md).

<span id="diagnosis"></span>

### Diagnosis and attribution

```bash
agenticlens diagnose run.json --save diagnosis.json --markdown investigation.md
agenticlens explain diagnosis.json --save explanation.md
agenticlens trace timeline run.json --save timeline.json
```

Diagnosis cites recorded spans for failure categories, origin versus propagated failures, recovery, faulty-step/agent attribution and incident timelines. Add `--baseline healthy-runs/` for anomaly detection. Budgets, tool/handoff loops, empty retrieval and injected faults have explicit rules. See [diagnosis and failure attribution](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/diagnosis.md).

<span id="analysis-guardrails"></span>

### Analysis guardrails and attribution accuracy

```bash
agenticlens diagnose run.json --max-spans 10000 --max-depth 64 --fail-on-unrecovered
```

Analysis budgets cap work and report incomplete analysis. `--fail-on-unrecovered` exits 4 when unrecovered failures are diagnosed. Python `AnalysisBudget` also supports time limits. Measure attribution against controlled-failure ground truth from the checkout:

```bash
agenticlens attribution-accuracy examples/diagnosis/controlled_failures \
  --save attribution-accuracy.json --min-step-accuracy 0.8
```

See [guardrails](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/diagnosis.md#guardrails-for-automated-analysis) and [attribution accuracy](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/diagnosis.md#attribution-accuracy-on-controlled-failures). Controlled fixtures do not establish accuracy on arbitrary production traffic.

<span id="evaluation"></span>

### Evaluation and live targets

Prepare a YAML/JSON suite plus recorded samples with matching case IDs:

```bash
agenticlens evaluate suite.yaml samples.json --save evaluation.json --html evaluation.html
```

Evals owns scoring and release-gate computation. Lens adds evidence adaptation, trace-aware evaluators and reporting. `evaluate-live` supports trusted Python callables and HTTP endpoints; the host supplies provider clients and credentials. See [evaluation and release gates](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/evaluation-and-release-gates.md) for suite contracts and live-target setup.

<span id="advanced-evaluation"></span>

### Advanced evaluation and judge reliability

Use `structured_judge()` with your own judge callback to record verdicts, confidence, unsupported claims, missed evidence, prompt identity, latency and usage. Self-judging is skipped by default. Trace-aware checks cover tool trajectories, agent goals, handoffs, loops, groundedness, relevance, completeness, citations and safety.

```bash
agenticlens evaluate suite.yaml samples.json --save evaluation.json \
  --score-analysis scores.json --html evaluation.html
agenticlens calibrate evaluation.json labels.json --evaluator answer_quality --save calibration.json
```

Score analysis separates deterministic/model-based scores, disagreement and judge cost. Calibration compares human references; the Python API and `calibrate --tune-threshold tuning.json` also tune thresholds. Lexical checks have semantic limits. See [structured judges, score analysis and trace-aware evaluators](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/evaluation-and-release-gates.md#structured-judge-verdicts) and the [judge reliability contract](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/evals-0.9-judge-reliability.md).

<span id="release-gates"></span>

### Release gates and evidence audits

```bash
agenticlens evaluate suite.yaml samples.json --save evaluation.json \
  --audit audit.json --strict-evidence
agenticlens gate evaluation.json --min-pass-rate 0.95
```

Audits inspect evaluator versions, trace evidence and cost coverage; strict blocking issues exit 3. Gates check configured quality, latency and cost thresholds. Optional webhook notifications support generic, Slack and Teams payloads when configured; they require an operator-supplied destination. See [gate thresholds and alerts](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/evaluation-and-release-gates.md#apply-a-release-gate) and [native Evals report boundaries](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/evals-report-contract.md).

<span id="suites"></span>

### Datasets and suite management

Datasets retain saved samples and labels; `dataset summary`, `dataset split` and `dataset export-samples` inspect and partition them. Suites contain test definitions and review metadata:

```bash
agenticlens suite import cases.csv --name support-regression --version 1.0.0 --save suite.yaml
agenticlens suite summary suite.yaml
```

Continue with trace/feedback conversion, case editing/tagging, PII masking, duplicate checks, synthetic variations, split assignment, filtering and review. Approve reviewed suites into an immutable store, then verify/export the approved version for CI. Editing commands modify their input unless `--save` names another file. See the [full suite lifecycle and commands](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/suite-management.md) and [dataset API](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/api-reference.md#dataset-api).

<span id="experiments"></span>

### Experiments and statistics

Run the checkout's offline recorded-output example:

```bash
agenticlens experiment run examples/experiments/support-experiment.yaml \
  examples/experiments/support-suite.yaml --save experiment.json \
  --html experiment.html --csv variants.csv --cases-csv cases.csv
```

Manifests define at least three variants, repeated trials and factors such as model, prompt, retrieval, memory or retry policy. Reports include pass@k/pass^k, confidence intervals, comparisons, consistency and factor summaries. `experiment report` renders saved results without rerunning targets. See [experiments and statistics](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/experiments.md).

### ModelFit

Use saved experiment evidence to select models by task category:

```bash
agenticlens modelfit taxonomy experiment.json --config modelfit.yaml
agenticlens modelfit recommend experiment.json --config modelfit.yaml \
  --save modelfit.json --markdown modelfit.md --csv matrix.csv
agenticlens modelfit matrix modelfit.json
```

Your config defines categories, hard quality/cost/latency/safety/provider/deployment constraints and scoring weights. Missing evidence fails constraints closed. Reports include Pareto status, cost per success, confidence, fallbacks, projected savings and separate quality risks. ModelFit does not invoke models. See [ModelFit configuration and evidence](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/modelfit.md).

<span id="routing"></span>

### Runtime routing

Given the saved ModelFit report and a category present in it:

```bash
agenticlens routing decide modelfit.json --category orders --request-id opaque-123 \
  --save decision.json
```

The CLI explains selection without invoking providers in every mode. Python `Router.run()` accepts host-owned callbacks for enforce, shadow and canary execution, bounded failover and local audit journals. `routing summary` consumes saved SDK results, not decision files. Hosts own payloads, credentials, deadlines and quality checks. See [routing modes, constraints and outcomes](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/routing.md).

<span id="optimization"></span>

### Optimization and adoption outcomes

```bash
agenticlens optimize analyze traces/before --save optimization.json --markdown optimization.md
```

Review opportunities for caching/compression, retrieval pruning/reranking, memory summarization, tools, retries, redundant steps, handoffs and model quality/cost trade-offs. Each keeps evidence, benefit, confidence and risk separate; missing costs remain unknown.

Use `optimize decide` to record acceptance and adoption against the exact report hash, `optimize status` to inspect decisions, and `optimize outcome` to compare before/after traces with the original projection. `--fail-on-regression` on outcome exits 9 if quality regressed. See [optimization rules, decision transitions and outcomes](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/optimization.md).

<span id="rag"></span>

### RAG chunk utility

Record `retrieved_chunks` on a profiled retriever step. Citation flags take priority over reranker scores, embedding similarity and generic utility scores; word overlap is the fallback. `agenticlens analyze workflow.json` flags low-utility chunks when configured thresholds are met. This workflow signal differs from the structured-trace retrieval optimization rules. See [supported chunk signals and configuration](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/rag-chunk-utility.md).

<span id="otlp-history"></span>

### Dashboards, OTLP and history

Install the optional HTTP dependencies for the local receiver:

```bash
python -m pip install 'agenticlens[api]'
agenticlens import-otlp otlp.json --save imported-run.json
agenticlens serve-otlp --host 127.0.0.1 --port 4318 --db traces.db
```

Run `agenticlens history --db traces.db` in another terminal. The receiver has no authentication; keep it local or on a trusted network. Use `dashboard` for saved HTML and `trace(..., otlp_endpoint=...)` or OTLP environment variables for export to a collector. See [CLI commands](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/cli-reference.md), [OTLP mapping](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/aios-validation-and-otel.md) and [receiver limits](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/limitations.md).

<span id="exports-aios"></span>

### Exports and AIOS contracts

Workflow exporters support JSON, CSV, Markdown and Jira payloads. Comparison, experiment, evaluation, ModelFit and optimization reports have their own output contracts. Native structured runs are not automatically AIOS artifacts.

```bash
agenticlens conformance --list-versions
agenticlens validate aios-artifact.json --save validation.json
agenticlens conformance aios-artifact.json --save conformance.json
```

Validation routes by declared marker: Run/Workflow `0.4-draft`, provenance `0.6-draft`, and supported operational companions `0.8-draft`. Explicit `--version` asserts a version. Schema validation alone does not establish semantic alignment. Python APIs export findings, provenance and structured-judge verification signals; provenance resolution uses caller-held bytes. See [export formats](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/export-formats.md), [current validation and companion APIs](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/coordinated-v1-readiness.md), and [operational artifacts](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/aios-0.8-operational-artifacts.md).

<span id="evidence"></span>

### Execution evidence verification and replay

Prepare explicit execution observations and an operator-owned trusted key file:

```bash
agenticlens evidence export run.json observations.json bundle.json \
  --key-id capture-key --key-file trusted-keys.json --complete
agenticlens evidence replay bundle.json --run-id EXPECTED_RUN_ID --key-file trusted-keys.json
```

The run ID must match your trusted caller context. `evidence verify` checks standalone records/manifests with an expected stream ID. Verification distinguishes failed, unknown and incomplete evidence; replay refuses untrusted or incomplete bundles and preserves capture order. It does not execute tools or providers. Declare completeness only for an actually complete capture. See [trust setup, coverage and evidence schemas](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/evidence-verification.md).

<span id="enterprise"></span>

### Enterprise artifact operations

The optional single-node artifact service adds organization/project isolation, hashed bearer credentials with reader/writer/admin roles, SQLite storage, redaction/retention, immutable model/prompt registry metadata, policy-bound gate receipts, audit and compliance metadata. Install `[api]`, prepare the documented credential/storage/gate configuration, then run:

```bash
LENS_CONFIG=/secure/config.json LENS_DATABASE=/data/lens.db \
  uvicorn agenticlens.enterprise.server:create_app --factory \
  --host 127.0.0.1 --port 8000 --workers 1 --no-access-log
```

This is a separate service from the developer OTLP receiver. Use its [configuration, HTTP routes, roles, deployment, backup and rollback guide](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/production-readiness.md) before operating it. Candidate markers and remaining acceptance work are described in [coordinated readiness](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/coordinated-v1-readiness.md).

<span id="integrations"></span>

### Provider and multi-agent integrations

Use explicit instrumentation around provider/framework execution. OpenAI/Anthropic usage extraction is supported; other providers supply usage manually. Agent names and delegation spans support per-agent analysis. The optional `agenticlens[langgraph]` or `[multi-agent]` extra supports the checked-in LangGraph supervisor reference workflow. See [providers and frameworks](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/integrations.md) and [offline supervisor/handoff workflows](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/multi-agent-reference-workflows.md).

<span id="ecosystem"></span>

### Sidecar, Chaos, Tower and MCP interoperability

`attach_decisions(run, records)` attaches Sidecar decisions only when run, trace and span IDs match, preserving supervision events in diagnosis timelines. Chaos evidence supports analysis of injected faults; Lens does not inject them. Tower consumes attributed native evidence, and the separate MCP package exposes Lens workflows. Producer outcomes, execution proof, authority and deployment health remain distinct.

See [Sidecar correlation](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/sidecar-integration.md), [Sidecar authority/privacy](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/sidecar-0.9.md), [ChaosHub](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/chaos-0.11-chaoshub.md), [Tower contract readiness](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/tower-0.10-compatibility.md), [MCP readiness](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/mcp-0.7-readiness.md) and the [historical compatibility matrix](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/lens-0.13-compatibility.md). Release-specific notes describe their stated versions, not a guarantee for every current installation.

<span id="settings"></span>

## Configuration and limitations

For workflow analysis, load `AgenticLensConfig` from an explicit YAML path or set `AGENTICLENS_CONFIG`. Use `pricing_overrides` (USD per 1,000 tokens), `live_pricing` and `recommender` settings. Set `AGENTICLENS_DISABLE_LIVE_PRICING=1` for offline pricing.

Structured tracing takes `otlp_endpoint`, `otlp_headers`, `otlp_timeout_seconds` and `redactor` arguments; OTLP environment variables supply defaults. Explicit arguments take precedence. ModelFit, routing, optimization and enterprise services use their own documented configurations. See [complete configuration](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/configuration.md).

Instrument actual boundaries and usage; automatic arbitrary-framework interception and streaming token capture are not provided. Recommendations are heuristic, savings are projections, and comparison windows do not prove causality. Missing prices, traces or evaluator evidence must not be treated as zeros or successful checks. See [limitations](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/limitations.md) and [compatibility policy](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/compatibility-policy.md).

## Troubleshooting

Use the environment where the package was installed. Confirm files exist, case IDs match, and the input is the right artifact type. Start with `agenticlens COMMAND --help` for exact flags. Keep original evidence when diagnosing an issue. See [troubleshooting](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/troubleshooting.md).

## Reference

- [API Reference (detailed)](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/api-reference.md) and [CLI reference](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/cli-reference.md).
- [AI Reference (robust)](https://deepagentlabs.io/agenticlens/docs/llms-full.md) and [capability/source index](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/ai-reference-index.md).
- [Source manifest and checksums](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/ai-docs-manifest.json).

---

## Overview and capabilities map

Source: [docs/index.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/index.md)

What did the agent do, and where did time, tokens, or cost go?

## What it does

Run artifacts, analysis, comparisons, and evidence-backed recommendations, grouped by area below. Each area links to its detailed guide; for runnable commands, see the [developer guide](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/developer-guide.md).

### 1. Tracing and instrumentation

- **Structured traces**
    - `trace()` context manager and `recording.span()` API with parent/child spans
    - Span types: model call, planning, retrieval, memory read/write, tool call,
      validation, retry, delegation, final response, custom
    - Per-span details: agent, model, provider, start/end time, latency, status,
      errors, tokens, cost and attributes
- **Workflow profiling**
    - `profile()` and `step()` for step-level workflow capture
    - Retrieval, memory, retry and handoff metadata on steps
- **Privacy**
    - Input/output capture is opt-in (`record_io()`)
    - Default redaction of common secrets, bearer tokens and emails; custom `redactor=`
- **Providers and frameworks**
    - Automatic usage extraction from OpenAI and Anthropic responses
    - Other providers supply token counts explicitly
    - LangGraph and framework-neutral multi-agent workflows (`[langgraph]` / `[multi-agent]` extras)
- **OpenTelemetry (OTLP)**
    - Export traces to a collector (`otlp_endpoint=` or OTLP environment variables)
    - Import OTLP files (`import-otlp`)
    - Local OTLP receiver (`serve-otlp`)

Guides: [Trace and comparison](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/trace-and-comparison.md) ·
[Integrations](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/integrations.md) · [AIOS validation and OTel](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/aios-validation-and-otel.md)

### 2. Metrics

- **Token usage**
    - Input (prompt) and output (completion) tokens for each LLM call or span
    - Total tokens per span and per run
    - Tokens by span type, such as model calls versus retrieval versus planning
    - Captured automatically from OpenAI and Anthropic responses, recorded by hand
      with `record_tokens()`, or imported from OTLP traces
- **Cost**
    - Token count × model price, from the built-in pricing table or live pricing
    - Pricing overrides in configuration (USD per 1,000 tokens)
    - Cost per step and per run
    - Cost per success (in ModelFit and comparisons) and judge cost (in evaluation)
    - Unknown prices stay unknown; they are never counted as zero
- **Latency and performance**
    - Latency per span, per step and by span type
    - Tokens per second and measured time to first token
    - Mean, median and P95 latency across repeated runs
- **Reliability counts**
    - Retry count and tool-call count
    - Tokens, latency and cost attributed to retries (shown in diagnosis)

Guides: [Metrics and trace analysis API](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/api-reference.md#metrics-and-trace-analysis-api) ·
[Features](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/features.md) · [Configuration](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/configuration.md)

### 3. Profiling and analysis

- **Reports**
    - `report` and `analyze` for profiled workflows (with optional HTML)
    - `inspect` for structured runs: span tree, token and latency distributions,
      retry and tool-call counts, deterministic findings
- **Trace views**
    - `trace show` for a run or a single span
    - `trace timeline` for incident timelines
- **Guidance**
    - Next-best-analysis suggestions when findings point to an obvious follow-up
    - Every finding cites the spans and measurements behind it

Guides: [Trace and comparison](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/trace-and-comparison.md) ·
[Metrics and trace analysis API](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/api-reference.md#metrics-and-trace-analysis-api)

### 4. Recommendations (finding waste)

- **Prompt and context**
    - Repeated system prompts
    - Long conversation history
- **Retrieval**
    - Excessive retrieved chunks
    - Low-utility RAG chunks (citations, reranker or similarity scores, lexical fallback)
- **Tools and agents**
    - Duplicate tool calls
    - Handoff bloat between agents
- **Models and faults**
    - Model swap suggestions
    - Impact of injected faults from Chaos evidence
- **Provenance**
    - Every recommendation names the step it is about and carries evidence

Guides: [Features](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/features.md) · [RAG chunk utility](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/rag-chunk-utility.md)

### 5. Evaluation

- **Scoring**
    - Evaluate recorded outputs against YAML/JSON suites (`evaluate`)
    - Live targets: trusted Python callables and HTTP endpoints (`evaluate-live`)
    - Trace-aware checks: tool trajectories, agent goals, handoffs, loops,
      groundedness, relevance, completeness, citations, safety
- **Judges**
    - Structured judge verdicts with confidence, unsupported claims and missed evidence
    - Judge latency, usage and cost recorded; self-judging skipped by default
    - Deterministic scores kept separate from model-based scores, with evaluator disagreement
- **Calibration**
    - Compare evaluators against human labels (`calibrate`)
    - Threshold tuning
- **Release gates**
    - Quality, latency and cost thresholds (`gate`)
    - Evidence audits of evaluator versions, trace evidence and cost coverage
    - Optional webhook alerts (generic, Slack, Teams)
- **Reports**
    - JSON and HTML evaluation reports

Guides: [Evaluation and release gates](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/evaluation-and-release-gates.md) ·
[Evals judge reliability](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/evals-0.9-judge-reliability.md)

### 6. Experiments and comparison

- **Run comparison**
    - Baseline versus candidate runs (`compare`)
    - Success, latency, variability, tokens, cost per success and regressions
- **Experiments**
    - Repeated trials across model, prompt, retrieval, memory and retry variants (`experiment run`)
    - Re-render saved results without rerunning (`experiment report`)
- **Statistics**
    - pass@k and pass^k
    - Confidence intervals and significance tests
    - Consistency and factor summaries
- **Output**
    - Variant × test-case heatmaps, HTML, CSV and Markdown reports

Guides: [Trace and comparison](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/trace-and-comparison.md) · [Experiments](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/experiments.md)

### 7. Diagnosis (root cause)

- **Failure analysis**
    - Versioned failure taxonomy and deterministic diagnosis rules (`diagnose`)
    - Origin versus propagated failures, and recovery
    - Explicit rules for budgets, tool and handoff loops, empty retrieval and injected faults
- **Attribution**
    - Faulty step and faulty agent
    - Accuracy measured on controlled failures (`attribution-accuracy`)
- **Investigation**
    - Incident timelines
    - Anomaly detection against healthy baseline runs
    - Investigation narratives (`explain`)
- **Guardrails**
    - Analysis budgets on spans, depth and time; incomplete analysis is reported

Guides: [Diagnosis and failure attribution](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/diagnosis.md)

### 8. Test suites and datasets

- **Building suites**
    - Import from CSV or JSON (`suite import`)
    - Convert production traces and user feedback into cases
- **Curating**
    - Edit cases, tags and domains
    - Stable train/test splits and synthetic variations
    - Duplicate detection and PII masking
- **Review and release**
    - Review and approval metadata
    - Immutable, hash-verified suite versions that CI can verify and export
- **Datasets**
    - Summarize, split and export saved samples (`dataset`)

Guides: [Test-suite and dataset management](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/suite-management.md)

### 9. ModelFit (choosing a model)

- **Inputs**
    - Task taxonomy built from experiment evidence
    - Hard constraints on quality, cost, latency, safety, provider and deployment
- **Ranking**
    - Weighted scoring and per-category Pareto frontiers
    - Cost per success
- **Output**
    - Confidence and explanations
    - Alternatives and provider-diverse fallbacks
    - Projected savings with separate quality risks
    - Task-by-model matrix (`modelfit matrix`)

Guides: [ModelFit recommendations](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/modelfit.md)

### 10. Runtime routing

- **Decisions**
    - Select eligible models from a ModelFit report (`routing decide`)
    - Modes: advisory, enforce, shadow and canary
- **Execution (Python SDK)**
    - Host-owned callbacks with bounded failover
    - Local audit journals and outcome summaries (`routing summary`)

Guides: [Advisory runtime routing](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/routing.md)

### 11. Optimization

- **Opportunities**
    - Prompt caching and compression
    - Retrieval pruning and reranking
    - Memory summarization
    - Tools, retries, redundant steps and handoffs
    - Model quality/cost trade-offs
- **Trade-offs**
    - Evidence, projected benefit, confidence and quality risk kept separate
- **Adoption**
    - Record decisions against a report hash (`optimize decide`, `optimize status`)
    - Compare before/after traces with the original projection (`optimize outcome`)

Guides: [Optimization intelligence](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/optimization.md)

### 12. Integrity and validation

- **Execution evidence**
    - Export evidence bundles sealed with an operator-held key (`evidence export`)
    - Verify records and manifests (`evidence verify`)
    - Replay verified execution records offline (`evidence replay`)
- **AIOS contracts**
    - Schema validation of draft artifacts (`validate`)
    - Rule-cited conformance summaries (`conformance`)
    - Operational companion artifacts and provenance resolution

Guides: [Execution evidence verification](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/evidence-verification.md) ·
[AIOS validation and OTel](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/aios-validation-and-otel.md)

### 13. Exports, reports and history

- **Exports**
    - JSON, CSV, Markdown and Jira payloads
    - OTLP trace export
- **Reports**
    - HTML dashboard (`dashboard`)
    - Markdown trace reports (`inspect --save`)
- **History**
    - Persistent local trace history (`history`)

Guides: [Export formats](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/export-formats.md) · [Features](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/features.md)

### 14. Enterprise artifact service

- **Isolation and access**
    - Organization and project isolation
    - Hashed bearer credentials with reader, writer and admin roles
- **Storage**
    - SQLite storage with redaction and retention policies
    - Retention pruning
- **Governance**
    - Immutable model and prompt registry metadata
    - Policy-bound release gate receipts
    - Audit log and compliance metadata
- **HTTP API**
    - Trace ingest and query, registry, gate, retention, audit and compliance routes

Guides: [Production readiness](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/production-readiness.md)

### 15. Ecosystem interoperability

- **Sidecar**: attach supervision decisions to matching runs and spans
- **Chaos**: analyze injected-fault evidence (Lens does not inject faults)
- **Control Tower**: consumes attributed Lens evidence
- **MCP**: the separate MCP package exposes Lens workflows as tools

Guides: [Sidecar integration](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/sidecar-integration.md) ·
[Lens 0.13 ecosystem matrix](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/lens-0.13-compatibility.md)

## What you need

Instrumented workflows, structured traces, or supported imported trace data.

## Start here

Record a small local trace and inspect `run.json`: [follow the quickstart](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/developer-guide.md#quickstart).

## Limits

- Recommendations are heuristic and advisory; savings are projections.
- Instrument real execution boundaries; arbitrary frameworks are not intercepted automatically.
- Streaming token capture is not provided.
- Dataset and experiment workflows don't make every third-party trace schema compatible automatically.

See [Limitations](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/limitations.md).

## Documentation

- [Developer Guide (simple)](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/developer-guide.md): short task workflows and a capability index
- [API Reference (detailed)](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/api-reference.md): exact Python functions, parameters and return values
- [AI Readable Documentation](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/ai-reference-index.md): the full reference as one file for AI tools, with source declarations and schemas

---

## Features

Source: [docs/features.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/features.md)

Every capability below is implemented and available in AgenticLens 0.5.0.
Planned capabilities appear only in [Roadmap](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/roadmap.md).

---

## Workflow profiling

**Status:** Stable

Profile any Python workflow with two context managers:

```python
from agenticlens import profile, step

with profile("My Workflow") as wf:
    with step("Planner", type="planner") as s:
        response = llm.invoke(prompt)
        s.record(response)
```

- Captures prompt tokens, completion tokens, total tokens, latency, and TTFT per step
- Supports step types: `planner`, `retriever`, `tool_call`, `llm_call`, `memory`, `final_response`
- Saves portable `workflow.json` artifacts

**Limitations:**
- Token capture requires a provider response object with `.usage.prompt_tokens` and `.usage.completion_tokens`
- No automatic framework event capture; instrumentation is explicit

---

## Structured run and span tracing

**Status:** Experimental

```python
from agenticlens import SpanType, trace

with trace("support-agent", environment="staging") as recording:
    with recording.span("planner", SpanType.PLANNING) as s:
        s.record_tokens(input_tokens=120, output_tokens=30)
        s.record_io(input="user query", output="plan")

recording.save("run.json")
```

- Hierarchical parent-child span tree
- Built-in payload redaction (secrets, bearer tokens, email addresses)
- Custom `redactor=` function supported
- Versioned JSON Schema: `schemas/trace.schema.json`

**Limitations:** Experimental API — schema may evolve

---

## Cost and token analysis

**Status:** Stable

```bash
agenticlens analyze workflow.json
```

- Per-step token breakdown (prompt, completion, total)
- Dollar cost per step and per run using live provider pricing
- On-disk pricing cache; bundled fallback data
- Monthly cost projections
- Tokens-per-second throughput

**Supported providers:** OpenAI, Anthropic

---

## Optimization recommendations

**Status:** Stable

AgenticLens automatically surfaces rule-based recommendations after analysis:

| Recommender | Finding |
|-------------|---------|
| Prompt | Repeated prompt prefixes that should be cached or deduplicated |
| RAG chunk | Low-utility retrieved chunks (see [RAG chunk utility](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/rag-chunk-utility.md)) |
| Memory | Excessive conversation history that should be summarized |
| Tool | Duplicate tool calls that should be cached |
| Handoff | Oversized multi-agent context passed between agents |
| Chaos impact | Unhandled failures and silent degradation from `chaos_events` |

Every finding includes source evidence (step/span reference, measured value, threshold),
confidence, quality risk, estimated token savings, and dollar-savings projection.

---

## Optimization intelligence (traces)

**Status:** Experimental (0.11.0)

`agenticlens optimize` works on structured `Run` traces across many runs. It
recommends prompt caching and compression, retrieval pruning and reranking,
memory summarization, tool-result caching, non-retryable errors, removal of
redundant steps and handoffs that add no work, and cheaper experiment variants
within an allowed quality drop. Projected benefit, confidence, and quality
risk are separate; decisions are tracked in a ledger; and adopted changes are
evaluated against later traces. See [Optimization intelligence](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/optimization.md).

---

## Repeated-run comparison

**Status:** Experimental

Compare a baseline and candidate set of runs:

```bash
agenticlens compare results/baseline results/candidate \
  --regression-threshold 0.05 \
  --save comparison.json
```

Reports: success rate, mean/median/P95 latency, standard deviation,
coefficient of variation, cost per successful task, and relative regression deltas.

```bash
agenticlens compare results/baseline results/candidate \
  --format md \
  --save comparison.md \
  --fail-on-regression \
  --min-samples 5
```

**Limitations:** Descriptive only — does not claim statistical significance

---

## Evaluation framework

**Status:** Experimental

Run deterministic and custom evaluators against saved samples:

```bash
agenticlens evaluate suite.yaml samples.json \
  --save evaluation.json \
  --html evaluation.html
```

Built-in checks:

| Check | Type |
|-------|------|
| Exact match | Deterministic |
| Required output phrases | Deterministic |
| Required tools | Trace-aware |
| Required tool arguments | Trace-aware |
| JSON Schema output validation | Deterministic |
| Required output fields | Deterministic |
| Max turn count | Trace-aware |
| Max latency | Operational |
| Max cost | Operational |

Custom evaluators via `EvaluatorRegistry`: `CallableEvaluator`,
`LLMJudgeEvaluator`, `BusinessRuleEvaluator`. See [API reference](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/api-reference.md).

---

## Versioned evaluation datasets

**Status:** Experimental

```bash
agenticlens dataset summary dataset.json
agenticlens dataset split dataset.json --train-ratio 0.7 --validation-ratio 0.15 --test-ratio 0.15
agenticlens dataset export-samples dataset.json --split test --save samples-test.json
```

---

## Live evaluation targets

**Status:** Experimental

Run the same suite against a live Python callable or HTTP endpoint:

```bash
agenticlens evaluate-live suite.yaml \
  --target-kind python \
  --target examples/live_evaluation_demo.py:run_case \
  --save evaluation-live.json
```

---

## Release gates

**Status:** Experimental

```bash
agenticlens gate evaluation.json \
  --min-pass-rate 0.95 \
  --min-average-score 0.98 \
  --max-failed-cases 1 \
  --max-average-latency-ms 1500 \
  --max-total-cost-usd 0.25
```

Exit codes: `0` = passed, `2` = gate failed, `1` = invalid input.
CI-safe: gates wire directly into build pipelines.

---

## Judge calibration

**Status:** Experimental

Compare LLM judge verdicts against a human-labeled reference set:

```bash
agenticlens calibrate evaluation.json labels.json \
  --evaluator answer_quality \
  --save calibration.json
```

Reports: agreement rate with 95% Wilson confidence interval, confusion counts
(true/false accept, true/false reject), and trace-linked evidence per case.

---

## HTML dashboard

**Status:** Experimental

```bash
agenticlens dashboard \
  --run run.json \
  --evaluation evaluation.json \
  --comparison comparison.json \
  --save dashboard.html
```

Combines: agent timeline, cost-by-area breakdown, waste findings, release gate,
and baseline-vs-candidate comparison. No external fonts or network requests —
renders fully offline.

Also produced automatically by `analyze`, `inspect`, and `compare` with `--html`.

---

## Live OTLP receiver

**Status:** Experimental · Requires `agenticlens[api]`

```bash
agenticlens serve-otlp --port 4318 --db traces.db
```

Receives OTLP/HTTP JSON traces and renders a real-time dashboard at
`http://127.0.0.1:4318`. Bounded in-memory store (default cap 200, FIFO eviction);
`--db` enables SQLite persistence across restarts.

**Known limitation:** No authentication; documented as a stated limitation.
Bind to localhost only.

---

## Persistent trace history

**Status:** Experimental

```bash
agenticlens history --db traces.db
agenticlens history results/
```

Shows aggregate tokens, cost, error rate, and P95 latency across recent
traces. Cost aggregates note "N of M traces priced" when pricing is incomplete.

---

## OTLP import and export

**Status:** Experimental

Export a run as OTLP:

```python
from agenticlens.exporters import OTLPTraceExporter
OTLPTraceExporter().save(recording.run, "run-otlp.json")
```

Import a third-party OTLP trace:

```bash
agenticlens import-otlp third-party-trace.json --save run.json
```

Supports OpenTelemetry GenAI semantic conventions (`gen_ai.*` attributes).

---

## AIOS validation and conformance

**Status:** Experimental

```bash
agenticlens validate workflow.json --version 0.4
agenticlens conformance run.json --version 0.4 --save conformance-report.json
```

Validates against AI Operations Specification draft schemas. See
[AIOS validation and OTel export](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/aios-validation-and-otel.md).

---

## RAG chunk utility scoring

**Status:** Stable

Identifies low-utility retrieved chunks that waste tokens. Supports citation
signals, reranker scores, embedding similarity, generic utility scores, and
word-overlap fallback. See [RAG chunk utility](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/rag-chunk-utility.md).

---

## Multi-agent support

**Status:** Experimental

Attach `agent_name`, `agent_role`, and handoff metadata to steps. AgenticLens
reports token usage by agent and flags oversized handoffs. Reference LangGraph
supervisor workflow included. See [Multi-agent reference workflows](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/multi-agent-reference-workflows.md).

---

## Export formats

**Status:** Stable

JSON, CSV, Markdown, Jira wiki markup, OTLP JSON. See [Export formats](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/export-formats.md).

---

## Chaos event analysis

**Status:** Stable

AgenticLens reads `chaos_events` written by `agentic-chaos` and surfaces
resilience findings via `ChaosImpactRecommender`. See
[Workflow schema spec](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/workflow-schema-spec.md).

---

## Architecture

Source: [docs/architecture.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/architecture.md)

AgenticLens is a layered, local-first toolkit. Each layer has a single
responsibility and strict import boundaries that the test suite enforces.

---

## Layer overview

```
┌──────────────────────────────────────────────────┐
│                   CLI (typer)                    │  agenticlens/cli/
│  profile · analyze · inspect · compare ·         │
│  evaluate · gate · validate · conformance ·      │
│  dashboard · serve-otlp · history · calibrate    │
└────────────────────┬─────────────────────────────┘
                     │ composes
┌────────────────────▼─────────────────────────────┐
│             Analysis & Evaluation                │
│  analysis/ · analyzers/ · evaluation/ ·          │
│  comparison/ · recommenders/ · reports/          │
└────────────────────┬─────────────────────────────┘
                     │ reads
┌────────────────────▼─────────────────────────────┐
│            Instrumentation & Models              │
│  profiler/ · instrumentation/ · models/ ·        │
│  providers/ · metrics/ · exporters/              │
└────────────────────┬─────────────────────────────┘
                     │ reads
┌────────────────────▼─────────────────────────────┐
│             Config & Schemas                     │
│  config/ · schemas/ · validation/                │
└──────────────────────────────────────────────────┘
```

---

## Key components

### Profiler (`profiler/`)

Provides the `profile()` and `step()` context managers. A `profile()` block
becomes a `Workflow` artifact; each `step()` block becomes a `Step`. Token
usage is captured by calling `step.record(provider_response)`, which delegates
to the provider extraction layer.

### Instrumentation (`instrumentation/`)

Provides the `trace()` context manager and `SpanHandle`. A `trace()` block
becomes a `Run` artifact; each `recording.span()` block becomes a `Span`.
Supports explicit `record_tokens()` and `record_io()` with built-in payload
redaction (secrets, bearer tokens, email addresses). Optionally exports to an
OTLP/HTTP collector on trace completion.

### Models (`models/`)

Pydantic data models: `Workflow`, `Step`, `Run`, `Span`, `SpanType`,
`RunStatus`, `ChaosEvent`. All serializable to JSON. Models do not import
from `recommenders/`, `analysis/`, or `cli/`.

### Providers (`providers/`)

Extracts token usage from raw provider responses (OpenAI, Anthropic). No
analysis logic lives here.

### Metrics (`metrics/`)

Calculates cost and performance from workflow steps using live or bundled
pricing data. Pricing data is cached on disk to avoid repeated network
requests.

### Analysis (`analysis/`) and Analyzers (`analyzers/`)

`analysis/` contains memory and retry diagnostics. `analyzers/` contains
modular analyzer implementations. Both read models and produce findings.

### Recommenders (`recommenders/`)

Rule-based optimization suggestions. Each recommender reads a `Workflow` and
returns `Finding` objects. Every finding must include source evidence (step or
span reference, measured value, and threshold). Registered in
`recommenders/engine.py`.

**Default recommenders:**

| Recommender | Signal |
|-------------|--------|
| `PromptRecommender` | Repeated prompt prefixes |
| `RAGChunkUtilityRecommender` | Low-utility retrieved chunks |
| `MemoryRecommender` | Excessive conversation history |
| `ToolRecommender` | Duplicate tool calls |
| `HandoffRecommender` | Oversized multi-agent handoffs |
| `ChaosImpactRecommender` | Unhandled failures and silent degradation from `chaos_events` |

### Evaluation (`evaluation/`)

Deterministic and custom evaluators, versioned test suites (YAML/JSON),
evaluation datasets, judge calibration, and release gate checks. Provider-neutral
through the `EvaluatorRegistry` and normalized `Score` contract.

### Comparison (`comparison/`)

Repeated-run baseline/candidate comparison with regression detection.
Produces JSON or CSV reports with success rate, mean/median/P95 latency, cost,
variability, and relative regression deltas.

### Exporters (`exporters/`)

Serializes workflow data to JSON, CSV, Markdown, Jira wiki markup, and OTLP
JSON. Must not import from `cli/`.

### Reports (`reports/`)

Renders standalone HTML dashboards combining agent timelines, cost breakdowns,
waste findings, release gates, and comparison data. No external fonts or
network requests — fully offline.

### Adapters (`adapters/`)

The `otlp` adapter converts OTLP/HTTP JSON trace exports — including
third-party exports following OpenTelemetry GenAI semantic conventions — into
AgenticLens `Run` artifacts.

### API (`api/`) — optional `[api]` extra

Live OTLP/HTTP receiver and real-time dashboard powered by FastAPI + uvicorn.
Bounded in-memory trace store (default cap 200, FIFO eviction) with an optional
SQLite-backed persistent store (`--db PATH`). Binds to `127.0.0.1` by default;
ships with no authentication.

### Validation (`validation/`)

AIOS draft schema and semantic conformance checks backed by local
`ai-operations-spec` draft schemas.

---

### Optimization (`optimization/`)

Trace-level, cross-run optimization intelligence. Rules read `Run` traces and
return `Opportunity` objects with run/span evidence, a projected benefit and
its basis, confidence with reasons, and separate quality risks. A local ledger
tracks accepted, rejected, adopted, and reverted decisions, and
`evaluate_outcome` compares projected and observed results after adoption.
See [Optimization intelligence](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/optimization.md).

## Workflow artifact

Artifacts are portable local JSON files. The core format is the
[AI Operations Workflow Specification](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/workflow-schema-spec.md) v1.1.

```
profile() → workflow.json   (Workflow model)
trace()   → run.json        (Run model, JSON Schema: schemas/trace.schema.json)
evaluate  → evaluation.json (EvaluationReport)
compare   → comparison.json (ComparisonReport)
```

---

## Module boundary rules

| Module | May import from | Must not import from |
|--------|----------------|---------------------|
| `exporters/` | `models/`, `metrics/` | `cli/` |
| `models/` | stdlib, pydantic | `recommenders/`, `analysis/`, `cli/` |
| `providers/` | `models/` | `analysis/`, `recommenders/` |
| `recommenders/` | `models/`, `metrics/` | `cli/` |
| `cli/` | everything | — |

---

## Ecosystem position

AgenticLens is the **OBSERVE / EVALUATE** layer in the DeepAgentLabs ecosystem:

```
agentic-sidecar     →  SUPERVISE (pre-action governance)
agenticlens         →  OBSERVE / EVALUATE (post-run intelligence)
agentic-chaos       →  EXPERIMENT (fault injection)
agentic-evals       →  SCORE / GATE (standalone release gating)
agenticops-control-tower → ORCHESTRATE (fleet inventory and control plane)
deep-agentic-core-mcp    → DELIVER (MCP-native surface)
```

AgenticLens consumes `chaos_events` written by `agentic-chaos`, composes
`agentic-evals` for standalone scoring, and exports to `agenticops-control-tower`
as attributed native evidence.

---

## API reference

Source: [docs/api-reference.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/api-reference.md)

**Version:** 1.1.0

Public symbols exported from `agenticlens`:

```python
from agenticlens import profile, step, trace, SpanType, SpanHandle, StepHandle
from agenticlens import Run, RunStatus, Span
```

---

## Profiling API

### `profile(name, config=None)`

Context manager. Opens a workflow profiling session.

```python
from agenticlens import profile
from agenticlens.exporters import JSONExporter

with profile("My Workflow") as workflow:
    pass
JSONExporter().export(workflow, "workflow.json")
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Human-readable workflow name |
| `config` | `AgenticLensConfig \| None` | Optional workflow pricing configuration; otherwise loaded via `load_config()` |

**Context value:** `Workflow`, returned when entering the `profile()` context.

---

### `step(name, type, **kwargs)`

Context manager. Records a single step inside a `profile()` block.

```python
with step("Planner", type="planner") as s:
    response = llm.invoke(prompt)
    s.record(response)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Step label |
| `type` | `str` | One of `planner`, `retriever`, `tool_call`, `llm_call`, `memory`, `final_response` |
| `provider` | `str \| None` | Provider name, e.g. `"openai"` |
| `model` | `str \| None` | Model name, e.g. `"gpt-4o-mini"` |
| `chunk_count` | `int \| None` | Number of retrieved chunks (retriever steps) |
| `avg_tokens_per_chunk` | `int \| None` | Average chunk size in tokens |
| `retrieved_chunks` | `list[dict] \| None` | Full chunk objects for RAG utility scoring |
| `final_answer` | `str \| None` | Final answer text (used for word-overlap fallback scoring) |
| `agent_name` | `str \| None` | Agent identity for multi-agent attribution |
| `agent_role` | `str \| None` | Agent role label |
| `**kwargs` | `Any` | Added to `step.metadata` |

**Returns:** `StepHandle` (context manager)

---

### `StepHandle`

Returned by `step()`. Call `.record()` to capture provider token usage.

#### `StepHandle.record(response)`

Extracts prompt tokens, completion tokens, and total tokens from a provider
response. Supports OpenAI and Anthropic response objects (any object with
`.usage.prompt_tokens` and `.usage.completion_tokens`).

```python
with step("Planner", type="planner") as s:
    response = openai_client.chat.completions.create(...)
    s.record(response)
```

---

## Tracing API

### `trace(application_name, *, redactor=redact_sensitive, **options)`

Context manager. Opens a structured trace session.

```python
from agenticlens import trace

with trace(
    "support-agent",
    environment="production",
    otlp_endpoint="http://localhost:4318/v1/traces",
) as recording:
    ...

recording.save("run.json")
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `application_name` | `str` | — | Application name for the Run |
| `**metadata` | `Any` | — | Run metadata, including optional labels such as `environment` |
| `otlp_endpoint` | `str \| None` | `None` | OTLP/HTTP endpoint; also reads `AGENTICLENS_OTLP_TRACES_ENDPOINT` |
| `otlp_headers` | `dict \| None` | `None` | Extra OTLP headers; also reads `AGENTICLENS_OTLP_HEADERS` |
| `otlp_timeout_seconds` | `float \| None` | environment or `10` | OTLP request timeout |
| `redactor` | `Callable[[Any], Any]` | `redact_sensitive` | Payload/metadata redactor |

**Context value:** the `trace` recorder, with `.run`, `.span(...)` and `.save(...)`.

---

### `SpanHandle`

Returned when entering a `recording.span()` context.

#### `SpanHandle.span(name, span_type)`

Opens a child span. Returns a nested `SpanHandle`.

```python
with recording.span("planner", SpanType.PLANNING) as s:
    s.record_tokens(input_tokens=120, output_tokens=30)
    s.record_io(input="query", output="plan")
```

#### `SpanHandle.record_tokens(input_tokens, output_tokens, total_tokens)`

Records token counts for this span.

| Parameter | Type | Description |
|-----------|------|-------------|
| `input_tokens` | `int` | Prompt / input token count |
| `output_tokens` | `int \| None` | Completion / output token count |
| `total_tokens` | `int \| None` | Total token count (computed if omitted) |

#### `SpanHandle.record_io(input, output)`

Records input and output values after applying the redactor.

#### `SpanHandle.save(path)`

Saves the completed `Run` artifact as JSON.

---

### `SpanType`

Enum of recognized span types:

| Value | Meaning |
|-------|---------|
| `SpanType.PLANNING` | Planning or reasoning step |
| `SpanType.RETRIEVAL` | Document or context retrieval |
| `SpanType.TOOL_CALL` | External tool invocation |
| `SpanType.MODEL_CALL` | LLM / model call |
| `SpanType.MEMORY_READ` | Memory lookup |
| `SpanType.MEMORY_WRITE` | Memory update |
| `SpanType.DELEGATION` | Agent handoff / delegation |
| `SpanType.FINAL_RESPONSE` | Final answer generation |
| `SpanType.VALIDATION` | Output validation step |
| `SpanType.RETRY` | Retry of a failed step |
| `SpanType.CUSTOM` | Application-defined span |

---

## Metrics and trace analysis API

Pure functions over a saved structured run (`Run`). They read recorded spans
only; they never call providers. `agenticlens inspect` uses them to build its
report.

```python
from pathlib import Path

from agenticlens.analysis import analyze_trace, next_best_analyses
from agenticlens.analysis.trace import memory_share, retry_token_share
from agenticlens.metrics.trace import (
    latency_by_span_type,
    retry_count,
    tokens_by_span_type,
    tool_call_count,
)
from agenticlens.models.trace import Run

run = Run.model_validate_json(Path("run.json").read_text(encoding="utf-8"))

print(run.total_tokens)                 # input + output tokens across all spans
print(tokens_by_span_type(run))         # {SpanType.PLANNING: 150, SpanType.MEMORY_READ: 80}
print(latency_by_span_type(run))        # milliseconds per span type
print(retry_count(run), tool_call_count(run))
print(memory_share(run), retry_token_share(run))

findings = analyze_trace(run)
for finding in findings:
    print(finding.category, finding.title, finding.span_ids)
print(next_best_analyses(findings))
```

Use the `run.json` saved by the [developer guide quickstart](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/developer-guide.md#quickstart),
or any run saved with `recording.save()`.

### Run totals

Properties on `Run` (and the matching per-span properties on `Span`):

| Property | Returns |
|----------|---------|
| `run.total_input_tokens` | Sum of span input tokens |
| `run.total_output_tokens` | Sum of span output tokens |
| `run.total_tokens` | Input + output tokens (`span.total_tokens` per span) |

### `agenticlens.metrics.trace`

| Function | Returns |
|----------|---------|
| `tokens_by_span_type(run)` | `dict[SpanType, int]`: total tokens per span type |
| `latency_by_span_type(run)` | `dict[SpanType, float]`: summed latency (ms) per span type |
| `retry_count(run)` | `int`: number of `RETRY` spans |
| `tool_call_count(run)` | `int`: number of `TOOL_CALL` spans |

Span types with no spans are absent from the dictionaries.

### `agenticlens.analysis.trace`

| Function | Returns |
|----------|---------|
| `memory_tokens(run)` | `int`: tokens in `MEMORY_READ` and `MEMORY_WRITE` spans |
| `memory_share(run)` | `float`: memory tokens / total tokens (`0.0` when there are no tokens) |
| `retry_tokens(run)` | `int`: tokens in `RETRY` spans |
| `retry_latency_ms(run)` | `float`: latency of `RETRY` spans |
| `retry_cost_usd(run)` | `float`: estimated cost of `RETRY` spans; spans without a cost count as `0.0` |
| `retry_token_share(run)` | `float`: retry tokens / total tokens |
| `retry_latency_share(run)` | `float`: retry latency / total run latency |
| `retry_attribution(run)` | `dict[str, dict]`: per retry span ID, the `triggering_failure_span_id` and `triggering_failure_type` (parent span if it failed, otherwise the nearest earlier failed span; `None` when none is found) |
| `classify_retry_outcomes(run)` | `dict[str, int]`: counts of `recovered`, `failed` and `unknown` retries, judged from each retry's child spans |
| `duplicated_context_groups(run)` | `list[list[str]]`: groups of span IDs that share the same `input_reference` or identical `input_data` |

`retry_cost_usd` treats missing cost as zero, so it is a lower bound when some
retry spans have no price.

### `analyze_trace(run, *, memory_share_threshold=0.5, retry_share_threshold=0.2, duplicated_context_threshold=2)`

Returns deterministic `Finding` objects. Each finding has `category`, `title`,
`description`, `severity`, `confidence`, `span_ids` and `evidence` pointing at
the spans and measurements that triggered it.

| Category | Raised when |
|----------|-------------|
| `memory` | `memory_share(run)` is above `memory_share_threshold` |
| `retry` | `retry_token_share(run)` is above `retry_share_threshold`; evidence includes retry tokens, latency, cost, outcomes and attribution |
| `context` | A duplicated-context group has at least `duplicated_context_threshold` spans |

### `next_best_analyses(findings)`

Returns follow-up suggestions (`list[str]`) for the categories present in
`findings`, or an empty list when there are none.

### `count_round_trips(transitions)`

From `agenticlens.analysis.handoffs`. Counts non-overlapping agent handoff
round trips (`A→B` immediately followed by `B→A`) in a chronological list of
`(source, target)` pairs:

```python
from agenticlens.analysis.handoffs import count_round_trips

count_round_trips([("planner", "coder"), ("coder", "planner")])  # 1
```

---

## Evaluation API

```python
from agenticlens.evaluation import (
    EvaluationContext,
    EvaluatorRegistry,
    LLMJudgeEvaluator,
    CallableEvaluator,
    BusinessRuleEvaluator,
    Score,
    evaluate_suite,
    load_suite,
    load_samples,
)
```

### `EvaluatorRegistry`

Holds trusted evaluator registrations. Suite YAML files reference evaluators
by name; they are never imported from the suite file.

```python
registry = EvaluatorRegistry()
registry.register(LLMJudgeEvaluator("quality_judge", my_judge_fn))
```

### `LLMJudgeEvaluator(name, fn)`

Wraps a callable that receives `EvaluationContext` and returns `Score`.
Identified in reports as an LLM-as-a-Judge result.

### `CallableEvaluator(name, fn)`

Wraps any Python callable for deterministic, semantic, or custom scoring.

### `BusinessRuleEvaluator(name, fn)`

Named wrapper for organization-specific pass/fail rules.

### `evaluate_suite(suite, samples, registry)`

Runs an evaluation suite against samples and returns an `EvaluationReport`.

```python
report = evaluate_suite(suite, samples, registry=registry)
```

### `Score`

```python
@dataclass
class Score:
    name: str
    value: float          # 0.0 – 1.0
    passed: bool          # AgenticLens applies suite threshold
    explanation: str
    metadata: dict        # evaluator-specific evidence
```

---

## Dataset API

```python
from agenticlens.evaluation import (
    load_dataset,
    save_dataset,
    split_dataset,
    summarize_dataset,
    dataset_from_samples,
    dataset_to_samples,
)
```

Used for versioned evaluation datasets with split assignments and human labels.

---

## Exporters

```python
from agenticlens.exporters import (
    JSONExporter,
    CSVExporter,
    MarkdownExporter,
    JiraExporter,
    OTLPTraceExporter,
)
```

All exporters follow the same interface:

```python
JSONExporter().export(workflow, "workflow.json")
OTLPTraceExporter().save(run, "run-otlp.json")
```

See [Export formats](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/export-formats.md) for output examples.

---

## Reports

```python
from agenticlens.reports import render_dashboard_html, save_dashboard_html
```

Render a combined offline HTML dashboard:

```python
save_dashboard_html(
    path="dashboard.html",
    run=run,                    # optional Run artifact
    evaluation=eval_report,     # optional EvaluationReport
    comparison=comparison,      # optional ComparisonReport
)
```

---

## Optimization API

```python
from agenticlens.optimization import (
    OptimizationConfig,
    RecommendationDecision,
    RecommendationLedger,
    analyze_optimizations,
    evaluate_outcome,
    load_traces,
)
```

| Name | Purpose |
|------|---------|
| `analyze_optimizations(runs, config=None, *, rules=None, baseline_variant_id=None)` | Run every rule; returns an `OptimizationReport` |
| `analyze_tradeoffs(runs, config, *, baseline_variant_id=None)` | Per-variant success, cost, Pareto status, and deltas |
| `RecommendationLedger(path).record(report, decision)` | Append a decision; enforces transitions and the report hash |
| `evaluate_outcome(report, opportunity_id, before, after, *, ledger=None)` | Projected vs observed outcome after adoption |
| `render_optimization_markdown`, `render_outcome_markdown` | Markdown views |

Custom rules implement `rule_id`, `version`, and
`analyze(runs, config) -> list[Opportunity]` and are passed with `rules=`.
See [Optimization intelligence](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/optimization.md).

---

## Adapters

```python
from agenticlens.adapters.otlp import convert_otlp_to_run
```

Convert an OTLP/HTTP JSON export to an AgenticLens `Run`:

```python
run = convert_otlp_to_run(otlp_payload)
```

Supports OpenTelemetry GenAI semantic conventions and AgenticLens-native attributes.

## Production readiness candidate (0.13)

See [the project artifact service, roles, policy, retention, audit and deployment guide](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/production-readiness.md),
[public compatibility policy](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/compatibility-policy.md) and [ecosystem matrix](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/lens-0.13-compatibility.md).
Run `uv run python examples/enterprise_demo.py` for an offline example.
External security/deployment acceptance and the coordinated v1.0 freeze remain open.


## Capability modules

The root imports above are the small instrumentation API. Additional capabilities live in documented submodules:

| Module | Public workflow and detailed contract |
| --- | --- |
| `agenticlens.config`, `providers`, `metrics`, `recommenders` | [Pricing, usage extraction and workflow analysis](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/configuration.md) |
| `agenticlens.comparison` | [Repeated-run comparison](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/trace-and-comparison.md) |
| `agenticlens.diagnosis` | [Rules, attribution, anomalies, timelines, narratives and analysis budgets](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/diagnosis.md) |
| `agenticlens.evaluation` | [Structured judges, score analysis, evidence audits, trace-aware evaluators, calibration and gate alerts](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/evaluation-and-release-gates.md) |
| `agenticlens.suites` | [Imports, editing, masking, variations, review and immutable approval](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/suite-management.md) |
| `agenticlens.experiments` | [Repeated trials, statistical comparisons and exports](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/experiments.md) |
| `agenticlens.modelfit` | [Task taxonomy, hard constraints, scoring, Pareto analysis and model matrices](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/modelfit.md) |
| `agenticlens.routing` | [Policies, model selection, bounded callbacks, failover and audit](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/routing.md) |
| `agenticlens.optimization` | [Opportunity rules, decision ledger and outcome evaluation](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/optimization.md) |
| `agenticlens.adapters`, `api`, `reports`, `exporters` | [OTLP, local history and reporting](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/cli-reference.md), [export formats](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/export-formats.md) |
| `agenticlens.integrity` | [Authenticated snapshots, execution export/import and offline replay](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/evidence-verification.md) |
| `agenticlens.validation`, `exporters.provenance`, `exporters.verification` | [Marker-routed AIOS validation, held-byte provenance and operational projections](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/coordinated-v1-readiness.md) |
| `agenticlens.enterprise` | [Project storage, roles, policy, registry, receipts, retention and audit](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/production-readiness.md) |
| `agenticlens.integrations.sidecar` | [Correlated native supervision events](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/sidecar-integration.md) |

The [AI Reference (robust)](https://deepagentlabs.io/agenticlens/docs/llms-full.md) includes declared interfaces from all package modules and all distributed schemas. Source declarations expose signatures and fields for lookup; they do not promote undocumented helpers to stable public APIs. Evals re-exports keep their upstream owner and installed dependency's contract. See the [capability index](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/ai-reference-index.md) and [compatibility policy](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/compatibility-policy.md).

---

## CLI reference

Source: [docs/cli-reference.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/cli-reference.md)

All commands are available via the `agenticlens` console script installed with the package.

```bash
pip install agenticlens
agenticlens --help
```

---

## Command inventory

Every registered command is listed below, including nested groups. Run `agenticlens COMMAND --help` (for example, `agenticlens suite approve --help`) for its complete options. The robust AI reference also includes source declarations for all CLI functions, with the exact argument and option definitions.

| Command (after `agenticlens`) | Purpose |
| --- | --- |
| `analyze` | Run the recommendation engine against a saved workflow. |
| `attribution-accuracy` | Measure faulty-step attribution accuracy on controlled failures. |
| `calibrate` | Compare saved judge verdicts with human reference labels. |
| `compare` | Compare repeated baseline and candidate traces. |
| `conformance` | Run schema and semantic AIOS draft checks and report rule-cited draft alignment. |
| `dashboard` | Combine a workflow, run, evaluation report, and/or comparison into one HTML dashboard. |
| `dataset export-samples` | Export evaluation samples from a versioned dataset artifact. |
| `dataset split` | Assign deterministic train, validation, and test splits to a dataset. |
| `dataset summary` | Summarize dataset size, split assignment, and available human labels. |
| `diagnose` | Diagnose failures, attribute the faulty step and agent, and rebuild the timeline. |
| `evaluate` | Score agent outputs, tool use, latency, and cost against a test suite. |
| `evaluate-live` | Run one trusted live Python or HTTP target against an evaluation suite. |
| `evidence export` | Export native Run + explicit records to an authenticated AIOS execution bundle. |
| `evidence replay` | Verify/import saved AIOS evidence, then print capture-order records offline. |
| `evidence verify` | Read a JSON array and manifest. Exit 0 only for verified coverage. |
| `experiment report` | Re-render a saved experiment report without re-running any variant. |
| `experiment run` | Run repeated trials for three or more variants against one suite. |
| `explain` | Explain a run's failures, or a workflow's recommendations, as an investigation. |
| `gate` | Apply release thresholds and return exit code 2 when the gate fails. |
| `history` | Render a cross-trace history view from a --db file or a run-JSON directory. |
| `import-otlp` | Convert OTLP/HTTP JSON trace exports into AgenticLens run files. |
| `inspect` | Inspect a validated run trace, span tree, and raw metric distributions. |
| `modelfit matrix` | Show the task-level model matrix of a saved ModelFit report. |
| `modelfit recommend` | Recommend a model for every task category under hard constraints. |
| `modelfit taxonomy` | Show which cases each task category covers, before recommending. |
| `optimize analyze` | Rank opportunities by projected cost saving, with evidence, confidence, and risks. |
| `optimize decide` | Record a decision. Adopting requires a prior accept; reverting requires adoption. |
| `optimize outcome` | Compare projected and observed savings; the projection is never adjusted. |
| `optimize status` | Show the latest decision status of every opportunity in a report. |
| `profile` | Run a script that uses `agenticlens.profile()` / `agenticlens.step()` and report it. |
| `report` | Display a saved workflow report. |
| `routing decide` | Select and explain without invoking models, in every policy mode. |
| `routing summary` | Summarize measured serving/shadow outcomes; unknown costs stay unknown. |
| `serve-otlp` | Run a live OTLP/HTTP receiver with a real-time dashboard. Requires `agenticlens[api]`. |
| `suite add-case` | Add an authored case (at least one expectation is required). |
| `suite approve` | Check and store a suite as an immutable approved version (exit 6 when refused). |
| `suite dedupe` | Find exact, near, and conflicting duplicate cases. |
| `suite diff` | Show cases added, removed, and changed between two suites. |
| `suite export` | Export a verified approved version (optionally filtered) for evaluation in CI. |
| `suite filter` | Write the subset of cases matching tags, domains, and splits. |
| `suite from-feedback` | Convert user feedback (ratings and corrections) into draft cases for review. |
| `suite from-traces` | Convert successful production traces into draft cases for review. |
| `suite import` | Import test cases from CSV or JSON into a new or existing suite. |
| `suite mask` | Mask emails, phones, cards, SSNs, IPs, secrets, and sensitive fields. |
| `suite remove-case` | Remove cases by ID. |
| `suite review` | Record a review decision on cases. |
| `suite split` | Assign stable train/validation/test splits (variants follow their original). |
| `suite summary` | Count cases by split, domain, tag, source, and review status. |
| `suite tag` | Add or remove tags and set domain categories. |
| `suite vary` | Add deterministic synthetic input variations (marked needs_review). |
| `suite verify` | Re-hash stored versions; exit 6 when any is missing or was changed. |
| `suite versions` | List approved suite versions. |
| `trace show` | Show a trace's span tree and metrics, or one span in full. |
| `trace timeline` | Reconstruct the incident timeline, marking the attributed root cause. |
| `validate` | Validate an AIOS artifact against the draft JSON Schema. |

---

## `profile`

Run and profile a Python workflow script.

```bash
agenticlens profile <script> [OPTIONS]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--save` | `PATH` | — | Save the resulting `workflow.json` to this path |
| `--config` | `PATH` | — | Path to `agenticlens.yaml` config |

**Example:**

```bash
agenticlens profile examples/recommendations_demo.py --save workflow.json
```

---

## `analyze`

Analyze a saved workflow artifact for token use, cost, and optimization findings.

```bash
agenticlens analyze <workflow.json> [OPTIONS]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--html` | `PATH` | — | Also save a standalone HTML dashboard |
| `--save` | `PATH` | — | Save analysis findings as JSON |
| `--config` | `PATH` | — | Path to `agenticlens.yaml` config |

**Example:**

```bash
agenticlens analyze workflow.json --html dashboard.html
```

---

## `inspect`

Inspect a structured trace run artifact.

```bash
agenticlens inspect <run.json> [OPTIONS]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--save` | `PATH` | — | Save a Markdown trace report |
| `--html` | `PATH` | — | Save a standalone HTML dashboard |

**Example:**

```bash
agenticlens inspect run.json --save trace-report.md
agenticlens inspect run.json --html dashboard.html
```

---

## `compare`

Compare a baseline and candidate set of repeated run artifacts.

```bash
agenticlens compare <baseline-dir> <candidate-dir> [OPTIONS]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--regression-threshold` | `FLOAT` | `0.05` | Relative change above which a metric is a regression |
| `--fail-on-regression` | flag | off | Exit non-zero if any regression is detected |
| `--min-samples` | `INT` | — | Fail if either cohort has fewer than N samples |
| `--format` | `json\|csv\|md` | `json` | Output format |
| `--save` | `PATH` | — | Save the comparison report |
| `--html` | `PATH` | — | Save a standalone HTML dashboard |

**Example:**

```bash
agenticlens compare results/baseline results/candidate \
  --regression-threshold 0.05 \
  --fail-on-regression \
  --min-samples 5 \
  --format md \
  --save comparison.md
```

---

## `evaluate`

Run an evaluation suite against saved samples.

```bash
agenticlens evaluate <suite.yaml> <samples.json> [OPTIONS]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--save` | `PATH` | — | Save evaluation report as JSON |
| `--html` | `PATH` | — | Save a standalone HTML dashboard |

**Example:**

```bash
agenticlens evaluate suite.yaml samples.json \
  --save evaluation.json \
  --html evaluation.html
```

---

## `evaluate-live`

Run an evaluation suite against a trusted live target.

```bash
agenticlens evaluate-live <suite.yaml> [OPTIONS]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--target-kind` | `python\|http` | — | Target type |
| `--target` | `STR` | — | `path:callable` (python) or URL (http) |
| `--save` | `PATH` | — | Save evaluation report as JSON |

**Examples:**

```bash
# Python callable
agenticlens evaluate-live suite.yaml \
  --target-kind python \
  --target examples/live_evaluation_demo.py:run_case \
  --save evaluation-live.json

# HTTP endpoint
agenticlens evaluate-live suite.yaml \
  --target-kind http \
  --target http://localhost:8000/evaluate \
  --save evaluation-live.json
```

---

## `gate`

Apply a release gate to a saved evaluation report.

```bash
agenticlens gate <evaluation.json> [OPTIONS]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--min-pass-rate` | `FLOAT` | — | Minimum fraction of cases that must pass |
| `--min-average-score` | `FLOAT` | — | Minimum average evaluator score |
| `--max-failed-cases` | `INT` | — | Maximum number of failed cases allowed |
| `--max-average-latency-ms` | `FLOAT` | — | Maximum acceptable average latency |
| `--max-total-cost-usd` | `FLOAT` | — | Maximum acceptable total evaluation cost |

**Exit codes:** `0` = passed, `2` = gate failed, `1` = invalid input

**Example:**

```bash
agenticlens gate evaluation.json \
  --min-pass-rate 0.95 \
  --min-average-score 0.98 \
  --max-failed-cases 1 \
  --max-average-latency-ms 1500 \
  --max-total-cost-usd 0.25
```

---

## `validate`

Validate an artifact against an AIOS draft JSON Schema.

```bash
agenticlens validate <artifact.json> [OPTIONS]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--version` | `STR` | — | AIOS spec version (e.g. `0.4`) |
| `--save` | `PATH` | — | Save validation report as JSON |

**Example:**

```bash
agenticlens validate workflow.json --version 0.4
```

---

## `conformance`

Run full AIOS schema and semantic conformance checks.

```bash
agenticlens conformance <run.json> [OPTIONS]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--version` | `STR` | — | AIOS spec version |
| `--spec-root` | `PATH` | auto-detected | Path to the `ai-operations-spec` repo |
| `--save` | `PATH` | — | Save conformance report as JSON |

**Example:**

```bash
agenticlens conformance run.json --version 0.4 --save conformance-report.json
```

---

## `dashboard`

Render a combined offline HTML dashboard from saved artifacts.

```bash
agenticlens dashboard [OPTIONS]
```

| Flag | Type | Description |
|------|------|-------------|
| `--run` | `PATH` | Path to a `run.json` trace artifact |
| `--evaluation` | `PATH` | Path to an `evaluation.json` report |
| `--comparison` | `PATH` | Path to a `comparison.json` report |
| `--save` | `PATH` | Output path for the HTML dashboard |

**Example:**

```bash
agenticlens dashboard \
  --run run.json \
  --evaluation evaluation.json \
  --comparison comparison.json \
  --save dashboard.html
```

---

## `serve-otlp`

Start the live OTLP/HTTP receiver and real-time dashboard.
Requires `agenticlens[api]`.

```bash
agenticlens serve-otlp [OPTIONS]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--host` | `STR` | `127.0.0.1` | Bind address |
| `--port` | `INT` | `4318` | Port |
| `--db` | `PATH` | in-memory | SQLite path for persistent trace storage |
| `--max-traces` | `INT` | `200` | In-memory trace cap (FIFO eviction) |

**Example:**

```bash
agenticlens serve-otlp --port 4318 --db traces.db
```

---

## `history`

View cross-trace aggregate history from a SQLite DB or directory of run JSON files.

```bash
agenticlens history [OPTIONS]
```

| Flag | Type | Description |
|------|------|-------------|
| `--db` | `PATH` | SQLite database path |
| `<dir>` | `PATH` | Directory of `run.json` files |

**Example:**

```bash
agenticlens history --db traces.db
agenticlens history results/
```

---

## `import-otlp`

Convert an OTLP/HTTP JSON trace export to an AgenticLens `run.json`.

```bash
agenticlens import-otlp <otlp.json> [OPTIONS]
```

| Flag | Type | Description |
|------|------|-------------|
| `--save` | `PATH` | Output path for the converted `run.json` |

**Example:**

```bash
agenticlens import-otlp third-party-trace.json --save run.json
```

---

## `dataset`

Subcommand group for managing versioned evaluation datasets.

### `dataset summary`

```bash
agenticlens dataset summary <dataset.json>
```

### `dataset split`

```bash
agenticlens dataset split <dataset.json> [OPTIONS]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--save` | `PATH` | — | Save the split dataset |
| `--train-ratio` | `FLOAT` | `0.7` | Fraction for the train split |
| `--validation-ratio` | `FLOAT` | `0.15` | Fraction for the validation split |
| `--test-ratio` | `FLOAT` | `0.15` | Fraction for the test split |
| `--seed` | `INT` | — | Random seed for reproducibility |

**Example:**

```bash
agenticlens dataset split dataset.json \
  --save dataset-split.json \
  --train-ratio 0.7 \
  --validation-ratio 0.15 \
  --test-ratio 0.15 \
  --seed 7
```

### `dataset export-samples`

```bash
agenticlens dataset export-samples <dataset.json> [OPTIONS]
```

| Flag | Type | Description |
|------|------|-------------|
| `--split` | `train\|validation\|test` | Split to export |
| `--save` | `PATH` | Output `samples.json` path |

**Example:**

```bash
agenticlens dataset export-samples dataset-split.json \
  --split test \
  --save samples-test.json
```

---

## `optimize`

Evidence-backed optimization recommendations from trace files or directories.
See [Optimization intelligence](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/optimization.md).

```bash
agenticlens optimize analyze <traces>... [--config FILE] [--baseline-variant ID] \
  [--ledger FILE] [--save FILE] [--markdown FILE]
agenticlens optimize decide <report.json> <opportunity-id> --status STATUS --by NAME \
  --ledger FILE [--reason TEXT] [--change REF]
agenticlens optimize status <report.json> --ledger FILE
agenticlens optimize outcome <report.json> <opportunity-id> --before PATH --after PATH \
  [--ledger FILE] [--min-runs N] [--save FILE] [--markdown FILE] [--fail-on-regression]
```

| Command | Purpose |
|---------|---------|
| `analyze` | Rank opportunities by projected cost saving, with evidence, confidence, and risks |
| `decide` | Append `accepted`, `rejected`, `adopted`, or `reverted` to the ledger |
| `status` | Latest decision status per opportunity, with counts |
| `outcome` | Projected vs observed per-run tokens, cost, latency, and success after adoption |

**Exit codes:** `0` = success, `1` = invalid input or refused transition,
`9` = `outcome --fail-on-regression` and quality regressed.

---

## `calibrate`

Compare LLM judge verdicts against human-labeled references.

```bash
agenticlens calibrate <evaluation.json> <labels.json> [OPTIONS]
```

| Flag | Type | Description |
|------|------|-------------|
| `--evaluator` | `STR` | Evaluator name to calibrate |
| `--save` | `PATH` | Save calibration report as JSON |
| `--tune-threshold` | `PATH` | Sweep pass thresholds and save the threshold-tuning report |

**Example:**

```bash
agenticlens calibrate evaluation.json labels.json \
  --evaluator answer_quality \
  --save calibration.json
```

---

## `report`

Display a saved profiling workflow (not a structured Run):

```bash
agenticlens report workflow.json
```

## `diagnose`, `explain`, `trace`, and `attribution-accuracy`

```bash
agenticlens diagnose run.json [--baseline PATH] [--save FILE] [--markdown FILE] \
  [--max-cost-usd USD] [--max-tokens N] [--max-latency-ms MS] \
  [--loop-threshold N] [--max-spans N] [--max-depth N] [--fail-on-unrecovered]
agenticlens explain artifact.json [--save FILE]
agenticlens trace show run.json [--span SPAN_ID]
agenticlens trace timeline run.json [--save FILE]
agenticlens attribution-accuracy controlled-failures/ [--save FILE] [--min-step-accuracy RATE]
```

`--baseline` is repeatable. `explain` accepts a Run, Workflow or DiagnosisReport.
`diagnose --fail-on-unrecovered` exits 4 on unrecovered failures; attribution accuracy exits 5 when the configured minimum is not met. Invalid inputs exit 1. See [diagnosis rules, budgets, timelines and attribution](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/diagnosis.md).

## `experiment`

```bash
agenticlens experiment run manifest.yaml suite.yaml --save experiment.json
agenticlens experiment report experiment.json --html experiment.html --csv variants.csv
```

Repeated trials support recorded, trusted Python and HTTP targets. Output flags include `--html`, `--csv` and `--cases-csv`; `run` also supports confidence/regression/sample controls. See [manifest, statistics and full workflow](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/experiments.md).

## `suite`

The inventory above lists every suite operation. Start with `suite import` or trace/feedback conversion, then edit, mask, deduplicate, vary, split, filter and review. Approval stores an immutable version for later verification/export; `versions` lists stored history and `diff` compares two suites. Commands have different positional arguments: use each subcommand's help rather than assuming every one accepts a suite path. See [suite commands, inputs and approval checks](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/suite-management.md).

## `modelfit`

```bash
agenticlens modelfit taxonomy experiment.json [--config FILE] [--json]
agenticlens modelfit recommend experiment.json [--config FILE] [--manifest FILE] \
  [--save FILE] [--markdown FILE] [--csv FILE] [--json] \
  [--fail-on-unfit] [--fail-on-low-confidence]
agenticlens modelfit matrix modelfit.json [--csv FILE] [--markdown FILE]
```

`recommend` and `taxonomy` accept multiple experiment files; `--manifest` is repeatable. CI checks exit 8 for an unfit category or low confidence when the corresponding flag is set. See [ModelFit constraints, scoring, taxonomy and confidence](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/modelfit.md).

## `routing`

```bash
agenticlens routing decide modelfit.json --category CATEGORY --request-id OPAQUE_ID \
  [--policy FILE] [--save FILE] [--audit FILE]
agenticlens routing summary result.json [MORE_RESULTS...] [--save FILE]
```

`decide` never invokes providers; exit 5 means blocked/escalated and exit 1 means invalid input. `summary` reads SDK `RoutingResult` files. See [runtime policies, callbacks and audit](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/routing.md).

## `evidence`

```bash
agenticlens evidence verify records.json manifest.json --stream-id EXPECTED_STREAM \
  --key-file trusted-keys.json
agenticlens evidence export run.json observations.json bundle.json --key-id KEY_ID \
  --key-file trusted-keys.json [--complete]
agenticlens evidence replay bundle.json --run-id EXPECTED_RUN --key-file trusted-keys.json
```

Trust keys come from an operator-owned JSON map of key IDs to hex keys. Verification exits 0 only for verified coverage; replay refuses untrusted or incomplete bundles. Capture completeness must be explicitly justified by the producer. See [evidence authentication, execution mapping and replay](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/evidence-verification.md).

---

## Configuration

Source: [docs/configuration.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/configuration.md)

AgenticLens uses separate configuration objects for workflow analysis, tracing, ModelFit, routing, optimization and the enterprise artifact service. Use the configuration for the operation you are running.

## Workflow configuration file

`load_config(path)` loads YAML from an explicit path or `AGENTICLENS_CONFIG`; with neither it returns defaults. A file named `agenticlens.yaml` is not discovered automatically. `[tool.agenticlens]` in `pyproject.toml` is not currently read, and there is no universal CLI `--config` flag.

```yaml
# agenticlens.yaml — illustrative pricing, not a provider quote
pricing_overrides:
  "example:demo-model":
    input_per_1k: 0.001
    output_per_1k: 0.002
live_pricing:
  enabled: false
recommender:
  rag_min_chunk_utility_score: 0.08
  rag_min_low_utility_chunks: 2
  monthly_runs: 1000
```

```bash
export AGENTICLENS_CONFIG=./agenticlens.yaml
```

Pass a loaded config explicitly when constructing a recommendation engine:

```python
from agenticlens.config import load_config
from agenticlens.recommenders import RecommendationEngine

engine = RecommendationEngine(config=load_config("agenticlens.yaml").recommender)
```

The `profile()` context loads the configured workflow settings for cost calculation when it finishes. `analyze` currently constructs a recommendation engine with default thresholds; use the Python engine above to apply custom recommender thresholds. The detailed fields/defaults are declared by `AgenticLensConfig`, `RecommenderConfig`, `LivePricingConfig` and `ModelPricing` in the AI reference.

## Provider pricing

Resolution order is explicit `pricing_overrides`, enabled live pricing, bundled `config/pricing.yaml`, then unknown (`None`). Overrides are keyed by `provider:model` and use USD per **1,000 tokens** (`input_per_1k`, `output_per_1k`). They are not USD per token.

Live pricing uses the community-maintained LiteLLM pricing feed, cached by default at `~/.cache/agenticlens/live_pricing_cache.json`, with a 24-hour TTL and five-second request timeout. Configure `live_pricing.url`, `cache_path`, `ttl_seconds` and `timeout_seconds` to change these. Set `AGENTICLENS_DISABLE_LIVE_PRICING=1` to disable live lookup for offline execution. Cache/fallback prices can age; computed costs are estimates unless actual measured provenance is supplied.

## Structured tracing and environment variables

Structured `trace()` takes OTLP arguments directly; these are separate from workflow YAML configuration:

| Variable | Description | Default |
| --- | --- | --- |
| `AGENTICLENS_OTLP_TRACES_ENDPOINT` | OTLP/HTTP endpoint URL | No export |
| `AGENTICLENS_OTLP_HEADERS` | Comma-separated `Key=Value` pairs | Empty headers |
| `AGENTICLENS_OTLP_TIMEOUT_SECONDS` | Export timeout | `10` seconds |
| `AGENTICLENS_CONFIG` | Workflow-analysis YAML path | Built-in workflow defaults |
| `AGENTICLENS_DISABLE_LIVE_PRICING` | Any nonempty value disables live pricing | Unset |

Explicit nonempty endpoint/header arguments take precedence over environment defaults; an explicit timeout is used when it is not `None`. Supply `redactor=` for application-specific capture sanitization.

```python
from agenticlens import trace

with trace("support", otlp_endpoint="http://localhost:4318/v1/traces",
           otlp_timeout_seconds=5.0) as recording:
    pass
```

## Capability-specific configurations

| Operation | Configuration |
| --- | --- |
| [ModelFit](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/modelfit.md) | `modelfit recommend/taxonomy --config` loads ModelFit YAML/JSON constraints and weights |
| [Routing](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/routing.md) | `routing decide --policy` loads `RoutingPolicy` JSON |
| [Optimization](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/optimization.md) | `optimize analyze --config` loads optimization thresholds in YAML/JSON |
| [Enterprise service](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/production-readiness.md) | `LENS_CONFIG` names service JSON; `LENS_DATABASE` names the SQLite database |
| [Evaluation and experiments](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/evaluation-and-release-gates.md) | Suite, sample, dataset and experiment-manifest files have distinct contracts |

---

## Release gate thresholds

Gate thresholds are passed directly as CLI flags — no configuration file needed.
See [CLI reference — gate](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/cli-reference.md#gate) for the complete flag reference.

---

## Evaluation suite files

Evaluation suites are YAML or JSON files that define test cases, evaluators,
and per-evaluator thresholds. See [Evaluation and release gates](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/evaluation-and-release-gates.md).

---

## Redaction

The `trace()` API redacts secrets, bearer tokens, and email addresses from
captured I/O by default. To supply a custom redactor:

```python
from typing import Any
from agenticlens import trace
from agenticlens.instrumentation.redaction import redact_sensitive


def my_redactor(value: Any) -> Any:
    sanitized = redact_sensitive(value)
    if isinstance(sanitized, str):
        return sanitized.replace("INTERNAL_CODE", "[REDACTED]")
    if isinstance(sanitized, dict):
        return {key: my_redactor(item) for key, item in sanitized.items()}
    if isinstance(sanitized, list):
        return [my_redactor(item) for item in sanitized]
    return sanitized


with trace("agent", redactor=my_redactor) as recording:
    pass
```

---

## `serve-otlp` configuration

The live OTLP receiver accepts configuration as CLI flags:

```bash
agenticlens serve-otlp \
  --host 127.0.0.1 \
  --port 4318 \
  --db traces.db \
  --max-traces 200
```

| Flag | Default | Description |
|------|---------|-------------|
| `--host` | `127.0.0.1` | Bind address |
| `--port` | `4318` | Port |
| `--db` | in-memory | SQLite path for persistent storage |
| `--max-traces` | `200` | In-memory trace cap (FIFO eviction) |

**Security note:** The receiver ships with no authentication. Run it only on
localhost or in a trusted network.

---

## Tracing and comparison

Source: [docs/trace-and-comparison.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/trace-and-comparison.md)

AgenticLens provides an experimental, framework-neutral trace format for research and
repeated-run evaluation. This API is additive; the existing `profile()` and `step()` API
continues to work.

## Capture a trace

```python
from agenticlens import SpanType, trace

with trace("support-agent", environment="test") as recording:
    with recording.span("planner", SpanType.PLANNING) as planner:
        planner.record_tokens(input_tokens=120, output_tokens=30)

    with recording.span("memory", SpanType.MEMORY_READ) as memory:
        memory.record_tokens(input_tokens=80)

recording.save("run.json")
```

Input and output values are not captured by default. Explicit values recorded with
`record_io()` pass through the default secret, bearer-token, and email redactor. Supply a
custom `redactor=` function to meet application-specific privacy requirements.

If you also want the trace emitted to an OTLP/HTTP collector, pass
`otlp_endpoint=...` to `trace()` or configure the OTLP environment variables
documented in [AIOS validation and OTel export](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/aios-validation-and-otel.md).

## Inspect a run

```bash
agenticlens inspect run.json
```

The report includes a span tree, raw token and latency distributions, retry and tool-call
counts, deterministic findings, and next-best-analysis guidance when findings suggest
an obvious follow-up. Findings cite the exact spans and measurements that triggered
them.

Save a Markdown trace report:

```bash
agenticlens inspect run.json --save trace-report.md
```

## Compare repeated runs

Place baseline and candidate JSON traces in separate directories:

```bash
agenticlens compare results/baseline results/candidate \
  --regression-threshold 0.05 \
  --save comparison.json
```

Use `--format csv` for tabular export and `--fail-on-regression` in CI. Comparisons report
success rate, mean/median/P95 values, standard deviation, coefficient of variation,
cost per successful task, and relative regressions.

Use `--format md` for a review-friendly Markdown summary and `--min-samples` when a
comparison should fail under CI if either cohort is too small:

```bash
agenticlens compare results/baseline results/candidate \
  --format md \
  --save comparison.md \
  --min-samples 5
```

The comparison is descriptive. It does not claim statistical significance or causal
attribution, particularly for small or uncontrolled samples.

## Schemas

Versioned JSON schemas are maintained in the repository `schemas/` directory and bundled
under `agenticlens/schemas` in wheel distributions:

- `trace.schema.json`
- `finding.schema.json`
- `v2/finding.schema.json`
- `report.schema.json`

---

## Failure diagnosis and attribution

Source: [docs/diagnosis.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/diagnosis.md)

AgenticLens 0.7.0 adds a deterministic diagnosis layer on top of structured
traces (`Run`/`Span`). Given one run, it answers:

- **What failed, and what kind of failure was it?** (failure taxonomy)
- **Which step and which agent caused it**, as opposed to failing as a
  consequence? (faulty-step and faulty-agent attribution)
- **In what order did things happen?** (incident timeline)
- **Is anything unusual compared with healthy runs?** (anomaly detection)
- **What did the failure cost, and what should I check next?** (investigation
  narrative)

Every diagnosis comes from a rule that cites recorded spans. Nothing here
calls a model, and the same saved trace always produces the same report.

```bash
agenticlens diagnose run.json --baseline healthy-runs/ \
  --save diagnosis.json --markdown investigation.md
```

```python
from agenticlens.diagnosis import diagnose_run, explain_run

report = diagnose_run(run, baseline=healthy_runs)
print(report.attribution.faulty_step, report.attribution.confidence)
print(explain_run(report))
```

A complete, offline example lives in
[`examples/diagnosis_demo.py`](https://github.com/DeepAgentLabs/agenticlens/blob/main/examples/diagnosis_demo.py);
its saved report and narrative are in `examples/diagnosis/artifacts/`.

## Failure taxonomy

Taxonomy version `1.0` (`agenticlens.diagnosis.TAXONOMY_VERSION`). Each
category records its layer, default severity, an attribution weight (how
strongly it points at its own span as the cause), and a next step.

| Category | Layer | Meaning | Attribution weight |
| --- | --- | --- | --- |
| `tool_error` | tool | A tool call returned an error or raised | 0.90 |
| `model_error` | model | A model call failed (provider error, refusal, malformed output) | 0.90 |
| `retrieval_error` | retrieval | A retrieval step failed before returning results | 0.90 |
| `timeout` | environment | A span failed with a timeout or exceeded `timeout_ms` | 0.85 |
| `validation_failure` | quality | An output or intermediate result failed validation | 0.85 |
| `delegation_failure` | orchestration | Delegating work to another agent failed | 0.85 |
| `retry_exhausted` | orchestration | Every retry of a failed operation also failed | 0.80 |
| `tool_loop` | orchestration | The same tool ran repeatedly with the same input | 0.70 |
| `handoff_loop` | orchestration | Agents handed control back and forth | 0.70 |
| `stagnation` | quality | Consecutive model calls produced identical output | 0.65 |
| `empty_retrieval` | retrieval | Retrieval returned no documents | 0.60 |
| `budget_exceeded` | resource | Run cost, tokens, or latency exceeded a configured budget | 0.40 |
| `injected_fault` | environment | A deliberately injected fault (agentic-chaos) hit the span | 1.00 |
| `incomplete_task` | outcome | The task failed and nothing more specific explains it | 0.30 |

## Diagnosis rules

| Rule | Detects | Needs in the trace |
| --- | --- | --- |
| `failed_span` | Origin failures (failed spans whose children did not fail first), grouped when identical, with propagation to failed ancestors and recovery by retries or a later successful attempt | span `status`, `error_type`/`error_message` |
| `injected_fault` | agentic-chaos faults on spans that did not fail themselves (for example injected latency) | `chaos.injected` / `chaos.fault_type` attributes |
| `retry_exhaustion` | Retries of one failure that never succeeded | `retry` spans |
| `tool_loop` | `loop_threshold` (3) identical consecutive tool calls per agent | `input_data`, `input_reference`, or `tool_args` (lower confidence without them) |
| `handoff_loop` | `handoff_round_trips` (2) A→B→A round trips | `delegation` spans with `to_agent` (or a child span of the receiving agent) |
| `stagnation` | `stagnation_threshold` (3) identical consecutive model outputs per agent | captured `output_data` or `output_reference` |
| `empty_retrieval` | Retrieval spans that returned zero results | `result_count`, `documents`, or list `output_data` |
| `budget` | Run cost, token, or latency above `DiagnosisConfig` budgets | span costs (budget is skipped and noted when cost is incomplete) |
| `incomplete_task` | Fallback when the run failed but every other diagnosis was recovered | run `status` / `task_success` |

Rules are versioned (`rule_id@version` on every diagnosis). Pass your own
rules with `diagnose_run(run, rules=[...])`; each rule implements
`diagnose(view, config) -> list[Diagnosis]`.

## Faulty-step and faulty-agent attribution

Blame is assigned only from diagnoses. Each diagnosis contributes to its
origin span:

```text
weight = taxonomy attribution_weight × diagnosis confidence
         × 0.3   if the failure was recovered
         × 1.15  for the earliest unrecovered origin (causal precedence)
         × 0.5   for unrecovered origins that start after it (likely consequences)
```

Contributions are summed per span and normalized into shares that sum to 1.
The top candidate is the faulty step; its agent (inherited from the nearest
ancestor that names one) is the faulty agent, and `agent_scores` gives every
agent's share. The attribution confidence is the top share scaled by the
confidence of its strongest diagnosis, so a single weak lead stays
low-confidence.

`Attribution.status` is `attributed`, `recovered` (failures happened but the
run did not fail), `unattributed` (the run failed and no span explains it),
or `no_failure`.

!!! note "Shares are not probabilities"
    Attribution shares are rule-weighted blame. Measure how often they are
    right on controlled failures before relying on them (below).

## Attribution accuracy on controlled failures

A controlled failure is a trace whose faulty step is known in advance: either
a span carries agentic-chaos markers (`chaos.injected`), or the producer sets
`run.metadata["expected_faulty_span_id"]` (and optionally
`expected_faulty_agent`, `expected_category`).

```bash
agenticlens attribution-accuracy examples/diagnosis/controlled_failures \
  --save accuracy.json --min-step-accuracy 0.9
```

The report gives top-1 and top-3 faulty-step accuracy, faulty-agent and
category accuracy, each with a Wilson interval, and a calibration gap (mean
confidence minus top-1 accuracy).

The repository ships a 40-case corpus across ten scenarios (tool timeouts
with exhausted retries, a recovered transient error followed by a validation
failure, injected latency causing a downstream deadline, injected tool
errors, tool loops, planner model errors with propagation, empty retrieval,
stagnation, handoff loops, and nested tool failures), built by
`examples/diagnosis/build_controlled_failures.py`. Variants change agents and
add distractors. On this corpus, attribution identifies the faulty step,
agent, and category in 40/40 cases (95% Wilson interval 91.2%–100%); mean
confidence is 79.5%, so the confidence is conservative here.

!!! warning "Scope of that result"
    The corpus is synthetic and was written alongside the rules it tests. It
    shows the rules behave as designed on known failure shapes; it is not
    independent evidence of accuracy on production traces. Add your own
    controlled failures (agentic-chaos runs are a good source) and track the
    accuracy report in CI.

## Incident timeline

`report.timeline` orders run start, span starts, failures, retries, handoffs,
injected faults, recoveries, and run completion by timestamp, with offsets
from the run start. The attributed root cause is marked. Routine span starts
are dropped first when a timeline exceeds `max_events` (500).

```bash
agenticlens trace timeline run.json --save timeline.json
```

## Anomaly detection

With `baseline=` runs (or `--baseline` on the CLI), run-level and per-span
latency, tokens, and cost are compared with the baseline using the modified
z-score `0.6745 × (x − median) / MAD` (threshold 3.5). Spans match across
runs by `<span_type>:<name>`; repeated spans are summed per run. When the
MAD is zero the score falls back to the mean absolute deviation, and when
every baseline value is identical only differences above a relative
tolerance (25%) are reported. At least five baseline runs are required per
metric; keys with fewer are listed in `warnings`.

## Guardrails for automated analysis

`AnalysisBudget` caps spans analyzed (`max_spans`), span-tree depth
(`max_depth`, the recursion cap), diagnoses kept (`max_diagnoses`), wall-clock
time (`max_seconds`), and, for iterative analyzers, iterations
(`max_iterations`), spend (`max_cost_usd`), and stagnation
(`stagnation_limit` consecutive iterations that find nothing new).

`diagnose_run(..., budget=AnalysisBudget(...))` applies the span, depth,
diagnosis, and time limits and records what was cut short in
`report.guardrails`. Your own analyzers can use the same guard:

```python
from agenticlens.diagnosis import AnalysisBudget, AnalysisGuard

guard = AnalysisGuard(AnalysisBudget(max_iterations=10, max_cost_usd=0.50))
while not guard.exhausted:
    finding = investigate_next()          # e.g. a model-assisted step
    guard.charge(cost_usd=finding.cost)
    guard.record([finding.fingerprint])   # stagnation detection
status = guard.status()
```

## Investigation narratives

`explain_run(report)` writes Markdown with a verdict, the root cause and its
supporting spans, contributing factors, the key timeline events, the tokens,
latency, and cost spent in failed and retry spans, efficiency findings,
anomalies, next steps from the taxonomy, and limitations.

`explain_recommendations(workflow, recommendations)` explains *why* each
optimization recommendation's waste occurred (repeated prompts, oversized
retrieval, history growth, duplicate tool calls, handoff bloat, model tier,
unabsorbed faults), what was measured, the projected impact, the quality
risk, and the cited evidence.

```bash
agenticlens explain run.json          # trace -> diagnose and explain
agenticlens explain diagnosis.json    # saved diagnosis report
agenticlens explain workflow.json     # workflow -> recommendations narrative
```

## CLI summary

| Command | Purpose |
| --- | --- |
| `diagnose RUN` | Diagnoses, attribution, anomalies (`--baseline`), budgets, guardrails; `--fail-on-unrecovered` exits 4 |
| `explain FILE` | Investigation narrative for a trace, diagnosis report, or workflow |
| `trace show RUN [--span ID]` | Span tree and metrics, or one span's full record |
| `trace timeline RUN` | Incident timeline with the root cause marked |
| `attribution-accuracy PATH` | Accuracy on controlled failures; `--min-step-accuracy` exits 5 |

## Report contract

`DiagnosisReport` (schema version `1.0`) and `AttributionAccuracyReport` are
published as JSON Schemas in `schemas/diagnosis/` and included in the wheel.
Reports carry the taxonomy, engine, and rule versions they were produced
with and contain no wall-clock timestamp of their own, so they reproduce
exactly from the saved trace.

## Limitations

- Rules only see what the trace recorded. Missing statuses, inputs, or
  outputs make some rules silent or lower their confidence.
- Attribution follows recorded structure and timing. A root cause outside the
  trace (for example an upstream data change) is reported as the first
  recorded symptom.
- Validation failures are attributed to the validation span; the step that
  produced the rejected value may be the real cause.
- Anomaly detection assumes baseline runs of the same workflow and is
  per-metric; it does not correct for multiple comparisons.

---

## Evaluation and release gates

Source: [docs/evaluation-and-release-gates.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/evaluation-and-release-gates.md)

AgenticLens evaluates agent behavior from local outputs and structured traces.
The evaluation layer converts workflow evidence into repeatable quality,
tool-use, latency, and cost checks. It can run without a hosted service or model
provider.

## Evaluation Model

An evaluation uses two inputs:

- a versioned YAML or JSON test suite containing acceptance criteria
- samples containing the observed output and its AgenticLens trace

Each test case can define:

- exact output or required output phrases
- required and forbidden tool calls
- required tool arguments
- expected JSON output structure and required fields
- maximum turn count
- maximum end-to-end latency
- maximum estimated cost
- tags and application-specific metadata

Built-in checks are deterministic. Custom evaluators and LLM-as-a-Judge
evaluators use
the same normalized score contract. A case passes only when every required
check reaches its configured threshold. The report includes per-check evidence,
aggregate pass rate, average score, latency, and total cost.

## Unified Evaluator Framework

The evaluator framework is provider-neutral. An evaluator receives an
`EvaluationContext` containing the test case, observed sample, trace, threshold,
and evaluator-specific configuration. It returns one or more normalized
`Score` objects with a value from `0.0` to `1.0`, an explanation, and optional
evidence metadata.

Trusted evaluators are registered explicitly in application code:

```python
from agenticlens.evaluation import (
    EvaluationContext,
    EvaluatorRegistry,
    LLMJudgeEvaluator,
    Score,
    evaluate_suite,
)

def judge(context: EvaluationContext) -> Score:
    # Call any hosted model, local model, or internal evaluation service here.
    result = call_model(
        input=context.case.input,
        output=context.sample.output,
        rubric=context.config.config["rubric"],
    )
    return Score(
        name="answer_quality",
        value=result.score,
        passed=False,  # AgenticLens applies the suite threshold.
        explanation=result.explanation,
        metadata={"model": result.model},
    )

registry = EvaluatorRegistry()
registry.register(LLMJudgeEvaluator("quality_judge", judge))
report = evaluate_suite(suite, samples, registry=registry)
```

The suite selects the evaluator and controls its acceptance threshold:

```yaml
cases:
  - id: support-answer
    name: Support answer quality
    evaluators:
      - name: quality_judge
        threshold: 0.80
        required: true
        config:
          rubric: The answer must be correct, grounded, and concise.
```

Suite files never import or execute Python modules. Registration is performed
by trusted application code, preventing untrusted suite configuration from
loading arbitrary code.

`CallableEvaluator` supports Python rules, semantic similarity functions,
safety classifiers, RAG metrics, and internal services.
`LLMJudgeEvaluator` identifies provider-supplied LLM-as-a-Judge results in reports
while leaving model selection, credentials, prompts, retries, and structured
output handling under application control. See `examples/custom_llm_judge.py`
for a complete, runnable registration example.

`BusinessRuleEvaluator` is a named wrapper around trusted application logic for
organization-specific pass/fail rules that do not need an LLM-as-a-Judge
evaluator.

## Run an Evaluation

```bash
agenticlens evaluate suite.yaml samples.json \
  --save evaluation.json \
  --html evaluation.html
```

The JSON report is suitable for CI and further analysis. The standalone HTML
report is suitable for demonstrations, release reviews, and team sharing.

## Versioned Evaluation Datasets

AgenticLens can also store evaluation samples as a versioned dataset artifact
that carries split assignments, tags, and human labels for judge calibration.

Summarize a dataset:

```bash
agenticlens dataset summary dataset.json
```

Assign deterministic train, validation, and test splits:

```bash
agenticlens dataset split dataset.json \
  --save dataset-split.json \
  --train-ratio 0.7 \
  --validation-ratio 0.15 \
  --test-ratio 0.15 \
  --seed 7
```

Export a split back to a plain `samples.json` artifact for evaluation:

```bash
agenticlens dataset export-samples dataset-split.json \
  --split test \
  --save samples-test.json
```

See `examples/dataset_and_calibration_demo.py` for a complete local example that
creates a dataset from samples, assigns splits, runs evaluation, and calibrates
judge labels end to end.

## Run a Trusted Live Target

`evaluate-live` runs the same suite against a trusted live target instead of a
pre-recorded sample file.

Run a Python callable:

```bash
agenticlens evaluate-live suite.yaml \
  --target-kind python \
  --target examples/live_evaluation_demo.py:run_case \
  --save evaluation-live.json
```

Run an HTTP target:

```bash
agenticlens evaluate-live suite.yaml \
  --target-kind http \
  --target http://localhost:8000/evaluate \
  --save evaluation-live.json
```

Add `--max-workers 4` to call the target for several cases at once, and
`--html report.html` for a standalone report. Case order in the report is the
suite's order regardless of completion order. Only raise `--max-workers` for
targets that are safe to call concurrently. With the default of one worker,
each result is validated before the next case is sent, so an invalid payload
stops the run without further target calls.

Python and HTTP targets share one scoring path. `tests/test_live_parity.py`
runs one suite against both (with AgenticLens `Run`-shaped traces) and checks
that the reports are identical, sequentially and concurrently.

Live targets are intentionally powerful developer-facing integrations. Python
targets execute local code and HTTP targets can reach arbitrary URLs, so suite
files and target definitions should be treated as trusted inputs.

## Evidence Behind Every Score

Every score in a report states what produced it:

| Score source | `evaluator` | `evaluator_version` |
| --- | --- | --- |
| Built-in checks | `agentic_evals.builtin` | the installed `agentic-evals` version |
| Registered evaluator | its registry name | its declared `version=` (or `null`) |

Version a judge whenever its prompt or model changes:

```python
LLMJudgeEvaluator("answer_quality", judge, version="quality-prompt-v3/gpt-4o-2024-08-06")
```

Each case also records `cost_source` (`measured` or `estimated`) and
`sample_available`. AgenticLens run costs are `estimated` (token counts times a
price table) unless the run's metadata declares `cost_source: measured`.

`audit_report(report)` (and `agenticlens evaluate --audit audit.json`) checks:

| Issue | Blocking by default |
| --- | --- |
| A score without an evaluator, or an evaluator without a version | yes (`require_evaluator_versions=False` to relax) |
| A failed case with no sample, or a sample without a trace ID | always |
| Not every case has a cost | no (`require_complete_cost=True`) |
| A priced case without measured/estimated provenance | no (`require_cost_source=True`) |

`agenticlens evaluate ... --strict-evidence` exits with code `3` on blocking
issues. The HTML report shows `evaluator@version` beside each score, the cost
source beside each cost, and "no sample supplied" for missing samples.

## Example Advanced Checks

```yaml
cases:
  - id: support-answer
    name: Structured support answer
    input:
      question: Where is my refund?
    required_tools: ["lookup_refund"]
    required_tool_arguments:
      lookup_refund: ["order_id"]
    output_json_schema:
      type: object
      required: ["answer", "meta"]
      properties:
        answer:
          type: string
        meta:
          type: object
          required: ["confidence"]
    required_output_fields:
      - meta.confidence
    max_turns: 3
    max_latency_ms: 1200
    max_cost_usd: 0.02
```

## Apply a Release Gate

```bash
agenticlens gate evaluation.json \
  --min-pass-rate 0.95 \
  --min-average-score 0.98 \
  --max-failed-cases 1 \
  --max-average-latency-ms 1500 \
  --max-total-cost-usd 0.25
```

The command exits with status `0` when every threshold passes, `2` when the
release gate fails, and `1` when the report or configuration is invalid.

### Alerting on gate failures

```bash
agenticlens gate evaluation.json --min-pass-rate 0.95 --max-total-cost-usd 0.25 \
  --notify-webhook "$WEBHOOK_URL" \
  --notify-format slack \
  --cooldown-minutes 60 \
  --notify-state .agenticlens/gate-notifications.json
```

`--notify-webhook` can also come from `AGENTICLENS_GATE_WEBHOOK`. When the gate
fails, AgenticLens works out which configured thresholds broke (keys such as
`pass_rate`, `average_latency_ms`, `total_cost_usd`, `tag_pass_rate:<tag>`,
`metric_pass_rate:<metric>`) and sends one alert covering those not in
cooldown. The state file records when each key last alerted; cache it between
CI runs to keep cooldowns across jobs. Formats:

- `generic`: `{"event": "agenticlens.gate.failed", "suite_name", "reasons", "breaches", "observed", ...}`
- `slack`: an incoming-webhook `{"text": ...}` message
- `teams`: a `MessageCard`

An alert that cannot be delivered is reported as a warning; the gate's exit
code is unchanged. In Python, `notify_gate_breach()` also accepts per-key or
per-category (`quality`, `latency`, `budget`) cooldowns, for example a short
cooldown for budget breaches and a long one for quality.

`max_turns` requires `trace.metadata.turn_count` to be recorded as a positive
integer. AgenticLens does not infer conversational turns from lower-level span
types when that metadata is absent.

## Judge Calibration

Given a versioned, human-labeled reference set (a `CalibrationDataset`: a flat
list of `{case_id, passed}` reference judgments, distinct from the richer
`EvaluationDataset` records used by `agenticlens dataset`), AgenticLens can
compare one `llm_judge` evaluator's saved verdicts against those labels and
report:

- agreement rate with a 95% Wilson confidence interval
- true/false accept and true/false reject confusion counts
- trace-linked evidence for every compared case

```bash
agenticlens calibrate evaluation.json labels.json \
  --evaluator answer_quality \
  --save calibration.json
```

Case ids in the reference set must exactly match the report's case ids, and
the report's suite name/version must match the reference set's — a mismatch
raises rather than silently comparing misaligned evidence. Uses each case's
already-recorded `Score.passed` decision, not a re-derived 0.5 threshold.

### Tuning the judge's pass threshold

```bash
agenticlens calibrate evaluation.json labels.json --evaluator answer_quality \
  --save calibration.json --tune-threshold tuning.json
```

`tune_judge_threshold()` re-decides `judge_value >= threshold` for each
candidate threshold (every distinct judge value plus 0 and 1 by default) and
recommends the one with the best balanced accuracy — or raw agreement when the
labels contain only one class. It is fitted on the same labels it is scored on;
confirm it on a held-out split (`agenticlens dataset split`) before adopting it.

## Structured Judge Verdicts

`structured_judge()` builds an `LLMJudgeEvaluator` from a function returning a
`JudgeVerdict`:

| Field | Meaning |
| --- | --- |
| `verdict` | `agree`, `partially_agree`, or `disagree` (scored 1.0 / 0.5 / 0.0 by default) |
| `confidence` | the judge's confidence, recorded but not multiplied into the score |
| `unsupported_claims` | claims in the output the evidence does not support |
| `evidence_missed` | evidence the output should have used |
| `rationale` | free-text reasoning |

The verdict, judge model, evaluated model, and a `self_confirmation_risk` flag
are stored on the score's metadata; `judge_verdict(score)` reads them back.
The evaluated model comes from case metadata, then trace metadata
(`evaluated_model`, `model`, or `model_name`). If it equals `judge_model`, the
case is scored as skipped — the judge would be grading its own output — unless
`allow_self_judging=True`. See `examples/structured_judge_demo.py`.

### Judge identity, prompt version, and cost

`structured_judge()` also records `judge_provider`, `prompt_version`, and the
SHA-256 of `prompt_template` on every score, so an edited judge prompt shows up
in saved reports. The judge call's wall-clock latency is measured
(`judge_latency_ms`). When the judge reports what its call consumed through
`JudgeVerdict.usage` (`JudgeUsage(cost_usd=..., cost_source="measured",
input_tokens=..., output_tokens=...)`), the score records `judge_cost_usd`,
`judge_cost_source`, and token counts. Any other judge can set the same
metadata keys itself. Without a cost, `analyze_scores()` estimates one from
tokens and AgenticLens pricing when `judge_provider` and the judge model are
known, and labels it `estimated`.

```python
evaluator = structured_judge(
    "answer_quality",
    my_judge,                       # returns JudgeVerdict(..., usage=JudgeUsage(...))
    judge_model="claude-haiku-5-5",
    judge_provider="anthropic",
    version="1.0",
    prompt_version="answer-quality-v2",
    prompt_template=PROMPT,
)
```

Experiments (repeated trials across variants, pass@k, significance tests) are
covered in [Experiments and Statistical Comparison](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/experiments.md).

## Score Analysis: Deterministic vs Model-Based

`analyze_scores(report)` (and `agenticlens evaluate --score-analysis PATH`)
reports three things a single pass rate hides:

- **Deterministic and model-based scores, separately.** Scores from
  `llm_judge`/`llm_rubric` evaluators (or carrying `judge_model`) are
  model-based; everything else is deterministic. Each side gets its own pass
  rate, average, and evaluator list.
- **Judge cost**, kept apart from the cost of the agent under evaluation: total
  and per evaluator, priced versus unpriced judge scores, cost sources, tokens,
  and latency. `complete` is false when any judge score has no cost.
- **Evaluator disagreement.** All deterministic checks on a case vote as one
  unit; each model-based evaluator votes on its own. Cases where the units
  disagree are listed (with each side's explanation), and pairwise agreement
  rates are reported per evaluator pair.

The evaluate CLI prints a one-line summary, and the HTML report adds a
"Score analysis" section whenever model-based scores are present.
`schemas/evaluation/score-analysis.schema.json` publishes the contract.

## Trace-Aware Evaluators

These evaluators score what the trace recorded, not only the final text. They
are registered by name in `agenticlens.evaluation.default_registry()`
(alongside agentic-evals' built-in scorers), which `evaluate` and
`evaluate-live` use, so suites can reference them directly:

```yaml
evaluators:
  - name: tool_trajectory
    config: {expected: [kb_search, lookup_order], mode: in_order}
  - name: groundedness
    threshold: 0.8
  - name: safety
    config: {allow: [support@example.com], forbidden_terms: [internal only]}
```

| Evaluator | Checks | Config |
| --- | --- | --- |
| `tool_trajectory` | Recorded tool sequence vs. expected | `expected`, `mode`: `exact` / `in_order` / `any_order` |
| `agent_goal` | Task success, run not failed, no failed spans, final agent, required output text | `require_task_success`, `allow_failed_spans`, `final_agent`, `goal_contains` |
| `handoff` | Handoff count, allowed pairs, A→B→A bounces | `max_handoffs`, `allowed` (`"a->b"`), `max_round_trips` |
| `loop` | Longest streak of identical tool calls | `max_repeats` (default 2) |
| `groundedness` | Share of output sentences supported by retrieved documents | `min_overlap` (0.6), `context` |
| `relevance` | Share of query terms the output addresses | `query` (defaults to case input) |
| `completeness` | Share of required points mentioned | `required_points` (strings or lists of alternatives); falls back to `expected_contains` |
| `citation` | Citations resolve to retrieved document IDs | `pattern`, `require_citations`, `known_sources` |
| `safety` | Email, SSN, phone, Luhn-valid card numbers, and forbidden terms in the output **and in tool arguments** | `allow`, `forbidden_terms`, `check_pii` |

Retrieved documents come from `context` in the evaluator config or case
metadata, otherwise from retrieval spans (`output_data`, or `documents` /
`retrieval.documents` / `chunks` attributes). Span semantics reach evaluators
through namespaced `EvalSpan` attributes that `to_eval_trace()` adds
(`agenticlens.span_type`, `agenticlens.agent_name`, `agenticlens.status`,
`agenticlens.input_fingerprint`, `agenticlens.retrieved`), plus
`agenticlens.run_status` and `agenticlens.task_success` in trace metadata.

!!! warning "Lexical heuristics"
    `groundedness`, `relevance`, and `completeness` compare words, not meaning:
    paraphrases count as unsupported and copied-but-wrong claims as supported.
    Use them as cheap first-pass signals next to a structured LLM judge; the
    score analysis then shows where they disagree. The safety evaluator never
    copies matched values into the score, only their kind and location.

`examples/advanced_evaluation_demo.py` runs these evaluators and a costed
structured judge over three recorded RAG runs and saves the report, score
analysis, and HTML in `examples/advanced_evaluation/artifacts/`.

## Offline Pitch Demonstration

The repository includes a deterministic LangGraph supervisor demonstration
that produces a trace, evaluation JSON, release decision, and HTML report:

```bash
uv sync --extra langgraph
uv run python -m examples.pitch_demo.run_pitch_demo
```

Generated artifacts are written to `examples/pitch_demo/artifacts/`. The demo
performs real graph execution but does not require an API key or network access.

## Scope

The framework supports deterministic checks, trace-aware evaluators, custom
or model-based evaluators with recorded versions, structured judge verdicts
with prompt versions and judge cost, score analysis separating deterministic
and model-based results with evaluator disagreement, versioned local datasets,
judge calibration and threshold tuning against human labels, evidence audits,
concurrent live targets, and gate alerts. Failure diagnosis and attribution
are covered in [Diagnosis and Failure Attribution](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/diagnosis.md). Built-in
provider clients, async evaluator APIs, and automatic framework event adapters
remain future roadmap capabilities.

---

## Suite management

Source: [docs/suite-management.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/suite-management.md)

AgenticLens 0.8.0 adds `agenticlens.suites` and the `agenticlens suite`
command group (roadmap milestone v0.6). Use them to build regression suites
from hand-written cases, production traces, and user feedback. You can then
review, mask, de-duplicate, vary, and split the cases, and approve the suite
as an immutable version that CI can verify and run.

Suites stay plain agentic-evals `TestSuite` files the whole way through, so a
draft or an exported version runs with `agenticlens evaluate`,
`evaluate-live`, and `experiment run` unchanged.

## Lifecycle

```text
CSV / JSON ──► import ─┐
production traces ─────┼─► draft suite ─► mask ─► dedupe ─► vary ─► split ─► review
user feedback ─────────┘        ▲                                              │
                                └──────── edit (add, remove, tag) ◄────────────┘
                                                                               │
                                     approve (checks) ─► store/<name>/<version>.json
                                                                               │
                                  CI: verify ─► export ─► evaluate ─► gate ◄───┘
```

| Stage | CLI | Python |
| --- | --- | --- |
| Import CSV/JSON/JSONL/YAML | `suite import` | `import_cases`, `import_suite` |
| Convert traces | `suite from-traces` | `case_from_run`, `cases_from_runs` |
| Convert feedback | `suite from-feedback` | `case_from_feedback`, `cases_from_feedback` |
| Edit cases | `suite add-case`, `remove-case`, `tag` | `add_case`, `update_case`, `remove_cases`, `tag_cases` |
| Review | `suite review` | `review_cases` |
| Mask PII | `suite mask [--check]` | `PIIMasker`, `mask_suite`, `scan_suite` |
| Duplicates | `suite dedupe [--drop]` | `find_duplicates`, `drop_duplicates` |
| Synthetic variations | `suite vary` | `generate_variations`, `vary_case` |
| Splits | `suite split` | `assign_splits` |
| Filter / summarize / diff | `suite filter`, `summary`, `diff` | `filter_suite`, `summarize_suite`, `diff_suites` |
| Approve and store | `suite approve` | `SuiteStore.approve` |
| CI | `suite verify`, `suite export`, `suite versions` | `SuiteStore.verify`, `load_suite`, `versions` |

Editing commands rewrite the suite file in place unless `--save` names
another file. YAML is written for `.yaml`/`.yml` paths and JSON otherwise.

## Case metadata

AgenticLens records management state in each case's `metadata`:

| Key | Meaning |
| --- | --- |
| `source` | Lineage: `kind` (`imported`, `trace`, `feedback`, `synthetic`; absent means authored), plus `file`/`row`, `trace_id`/`run_id`, `feedback_id`, or `parent_case_id`/`variation`/`seed` |
| `review_status` | `needs_review`, `accepted`, or `rejected`. A case without a status counts as accepted (authored by a person) |
| `reviewed_by`, `review_notes` | Who reviewed the case and why |
| `domain` | Domain category, e.g. `billing` |
| `split` | `train`, `validation`, or `test` |

Tags stay in the case's `tags` list.

## Importing cases

```bash
agenticlens suite import cases.csv --name support-regression --version 1.0.0 \
  --save suite.yaml
```

CSV columns map onto `TestCase` fields. List columns (`expected_contains`,
`required_tools`, `forbidden_tools`, `required_tool_order`, `tags`) are
`|`-separated. `input` is parsed as JSON when it is a JSON object or array.
`domain`, `split`, and any `metadata.<key>` column go to case metadata.
Unknown columns are rejected, so a misspelled expectation fails the import
instead of being dropped silently. JSON imports accept a list, `{"cases": [...]}`,
or JSON Lines. Add `--into suite.yaml` to append to an existing suite.

PII is masked by default before anything is written (`--no-mask` to opt out).

## From production traces

```bash
agenticlens suite from-traces traces/ --name prod-regression --version 1.0.0 --save suite.yaml
```

A successful run becomes a case that expects what the run did:

- `required_tools` and `required_tool_order` from its successful tool calls
- `max_latency_ms` and `max_cost_usd` set to the observed values times
  `--latency-margin` / `--cost-margin` (default 1.5)
- `expected_output` only with `--include-output`, because exact model output
  rarely repeats

The input comes from `metadata.input` or the first span with `input_data`, and
the domain from `task_type`. Each converted case is marked `needs_review`, and
cases that can't be converted are reported with a reason:

- **Failed runs** show what went wrong, not what right looks like. Turn them
  into cases with corrected feedback instead.
- **Runs without a recorded input** have nothing to replay.

Record the request when tracing, either as run metadata
(`trace("support", input=question)`) or on a span
(`span.record_io(input_data=question)`), so there is an input to replay. The
tracer's redactor still applies.

## From user feedback

```json
{"feedback": [
  {"feedback_id": "fb-101", "input": "Where is my parcel?", "output": "It ships in 2 business days.", "rating": "positive"},
  {"feedback_id": "fb-102", "input": "Can I pay by invoice?", "output": "No.", "rating": "negative",
   "corrected_output": "Let me connect you with a specialist."}
]}
```

```bash
agenticlens suite from-feedback feedback.json --into suite.yaml --save suite.yaml --traces traces/
```

If feedback has a correction, the case expects the correction. Positive
feedback (`rating: positive`, or a `score` of 0.5 or more) expects the
confirmed output. Negative feedback without a correction is skipped, because it
says what's wrong but not what's right. When a record has no `input`, the input
comes from the run named by `run_id` or `trace_id` in `--traces`. The rejected
output is kept in `metadata.rejected_output` for reviewers. The schema is
[`schemas/suites/feedback-batch.schema.json`](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/suites/feedback-batch.schema.json).

## PII masking

```bash
agenticlens suite mask suite.yaml                      # mask in place
agenticlens suite mask suite.yaml --check              # scan only; exit 7 if PII found
agenticlens suite mask suite.yaml --strategy hash --salt "$SALT" --report mask.json
```

What gets masked:

- **Patterns in text:** emails, phone numbers, Luhn-valid card numbers, US
  SSNs, IPv4 addresses, bearer tokens, and API keys.
- **Values under sensitive keys** (`password`, `token`, `email`, `phone`,
  `ssn`, `address`, `date_of_birth`, ...), matched as whole words of the key.
  `customer_email` is masked; `input_tokens` is not.
- **Fields covered:** a case's input, expected output, expected substrings,
  expected tool arguments, and metadata. Case lineage is never masked.

`redact` writes `[EMAIL]`. `hash` writes `[EMAIL:3f2a9c1e]`, a salted SHA-256
prefix, so equal values stay equal and you can still spot duplicates. Reports
list the case, the field path, and the PII type, never the value.

Pattern matching is a safeguard, not a guarantee. It doesn't detect names,
street addresses in free text, or locale-specific identifiers. A version
string such as `1.2.3.4` is masked as an IP address. Masking an expected
output also changes what the agent has to produce, so review those cases.

## Duplicates, variations, and splits

```bash
agenticlens suite dedupe suite.yaml --threshold 0.85 --report dupes.json --drop
agenticlens suite vary suite.yaml --per-case 2 --kind typo --kind prefix --seed 7
agenticlens suite split suite.yaml --train 0.7 --validation 0.15 --test 0.15 --seed 7
```

**Duplicates.** Exact duplicates share a normalised input (case,
punctuation, and whitespace ignored). Near duplicates reach the Jaccard
threshold over word unigrams and bigrams. A group is *conflicting* when
cases with the same normalised input expect different results, which usually
means a labelling error. Near duplicates with distinct inputs never conflict. `--drop` keeps the first case of each group. Synthetic
variants of the same original are not compared to each other unless you pass
`--include-variants`. Comparison is pairwise, so it is sized for suites of
thousands of cases.

**Variations.** `lowercase`, `uppercase`, `whitespace`, `punctuation`,
`typo`, and `prefix` change every string in the input, skipping masked
values. They test robustness to how a request is typed, not what it means.
They are not paraphrases and make no model calls. Each variant:

- keeps its parent's expectations
- inherits its parent's split
- is marked `needs_review`
- records `parent_case_id`, `variation`, and `seed`

`--per-case` caps variants per original, so re-running adds nothing new.

**Splits.** A case is placed by hashing its lineage with the seed. A case
keeps its split when other cases are added or removed, so a later version
can't move test cases into training. A variant always lands with its
original. The trade-off is that split sizes only approximate the ratios, and
the CLI warns when a split is empty.

## Review and approval

```bash
agenticlens suite review suite.yaml --status accepted --reviewer qa-lead --case trace-run-1
agenticlens suite review suite.yaml --status rejected --reviewer qa-lead --case fb-7 --notes "policy changed"
agenticlens suite approve suite.yaml --store suites/ --approver qa-lead --notes "Q4 regression set"
```

`approve` runs three checks, records them, and refuses (exit 6) when any
fails:

| Check | Fails when | Override |
| --- | --- | --- |
| `review` | any case is `rejected` (remove it), or `needs_review` | `--allow-unreviewed` (needs_review only) |
| `pii` | the scan finds unmasked PII | `--allow-pii` |
| `conflicting_duplicates` | cases share an input but expect different results | none; fix the labels |

The approved version is written once to `<store>/<name>/<version>.json` as a
`SuiteVersion`. It holds the suite exactly as approved, its SHA-256 over
canonical JSON, the case count, the approver, the time, the notes, the
checks, and an optional `--parent-version`. The schema is
[`schemas/suites/suite-version.schema.json`](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/suites/suite-version.schema.json).

Approved versions are immutable:

- Approving the same name and version again is a no-op if the content is
  identical, and is refused if it differs. Bump the version instead.
- Every read re-hashes both the suite (`content_sha256`) and the whole
  envelope (`record_sha256`, covering the approver, time, notes, checks, case
  count, and parent version). A hand-edited, moved, or corrupted version fails
  `verify`, `export`, and `load_suite`.
- Suite names and versions must be plain path segments (letters, digits,
  `.`, `_`, `-`).

Use `suite diff support@1.0.0 suite.yaml --store suites/` to review what a
new draft changes before approving it.

## Running approved suites in CI

```yaml
- run: uv run agenticlens suite verify --store suites
- run: uv run agenticlens suite export support-regression@1.0.0 --store suites --save build/suite.json --split test
- run: uv run agenticlens evaluate build/suite.json build/samples.json --save build/evaluation.json --strict-evidence
- run: uv run agenticlens gate build/evaluation.json
```

`verify` exits 6 when any stored version is missing or changed. `export`
writes a plain suite, optionally filtered by `--tag`, `--domain`, or
`--split`. It stamps `metadata.agenticlens_suite_version` with the name,
version, hash, approver, and approval time, so the evaluation report traces
back to the approved version. For live agents, use `evaluate-live` in place
of `evaluate`. This repository's CI runs exactly these steps against
`examples/suites/store`.

## Example

[`examples/suite_management_demo.py`](https://github.com/DeepAgentLabs/agenticlens/blob/main/examples/suite_management_demo.py)
runs the whole lifecycle offline. Its inputs are a CSV with PII and a
duplicate row, three production traces (one failed), and four feedback
records (two unconvertible). It produces 15 approved cases in
`examples/suites/store/support-regression/1.0.0.json` and evaluates them
against a deterministic stub agent. `tests/test_examples_suites.py` checks
that the store and artifacts reproduce byte for byte, apart from the
evaluation report's `created_at`.

```bash
uv run python examples/suite_management_demo.py
```

## Relationship to evaluation datasets

`agenticlens dataset ...` (since 0.5.0) manages labelled *outputs and traces*
for judge calibration. `agenticlens suite ...` manages the *test cases*
(inputs and expectations) those outputs are scored against. Both are
versioned. Only approved suite versions are immutable and hash-verified.

---

## Experiments and statistics

Source: [docs/experiments.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/experiments.md)

An experiment runs one evaluation suite against three or more variants — models,
prompts, retrieval strategies, memory settings, retry policies — for several
trials each, then reports quality, cost, latency, and reliability side by side
with the uncertainty that repeated trials reveal.

## Quick start

The repository ships a reproducible experiment that replays recorded outputs,
so it needs no model or network access:

```bash
agenticlens experiment run examples/experiments/support-experiment.yaml \
  examples/experiments/support-suite.yaml \
  --save experiment.json \
  --html experiment.html \
  --csv variants.csv \
  --cases-csv cases.csv
```

Re-render a saved report (for example in CI artifacts) without re-running any
variant:

```bash
agenticlens experiment report experiment.json --html experiment.html --csv variants.csv
```

From Python:

```python
from pathlib import Path

from agenticlens.experiments import (
    load_experiment_suite, load_manifest, run_experiment, save_experiment_html,
)

report = run_experiment(
    load_manifest(Path("examples/experiments/support-experiment.yaml")),
    load_experiment_suite(Path("examples/experiments/support-suite.yaml")),
    confidence_level=0.95,
    regression_threshold=0.05,
)
save_experiment_html(report, Path("experiment.html"))
```

## Manifest

| Field | Default | Meaning |
| --- | --- | --- |
| `name`, `version` | required | Identify the experiment. |
| `baseline_variant_id` | required | The variant every other variant is compared with. |
| `trial_count` | `5` | Trials per variant. Each trial runs the whole suite once. |
| `random_seed` | `null` | Shuffles the order of (variant, trial) runs to spread drift across variants. The order actually used is saved in the report. |
| `pass_k` | `[1, trial_count]` | k values for pass@k and pass^k. Each must be ≤ `trial_count`. |
| `minimum_trials` | `5` | Variants with fewer completed trials get exploratory warnings. |
| `max_workers` | `1` | Cases run concurrently within one live trial. |
| `variants` | required, ≥ 3 | See below. |

Each variant has an `id`, `name`, `target_kind`, `target`, optional
`timeout_seconds`, and `factors`:

| `target_kind` | `target` |
| --- | --- |
| `python` | A trusted `module:function` or `path/to/file.py:function`, called as `fn(case.input, case=case)`. |
| `http` | A URL receiving `{"input": ..., "case_id": ...}` by POST. |
| `recorded` | A JSON/YAML file of saved samples per trial, resolved relative to the manifest. |

`factors` maps a dimension to the value this variant uses, for example
`{model: small, prompt: v3, retrieval: bm25}`. The documented dimensions are
`model`, `prompt`, `retrieval`, `memory`, and `retry_policy`; any other name is
allowed. Factors drive the "changed factors" column of each comparison and the
factor-level summary.

### Recorded trials

A `recorded` target replays saved outputs instead of calling an agent:

```json
{
  "trials": [
    {"samples": [{"case_id": "refund-window", "output": "...", "trace": {...}}, ...]},
    {"samples": [...]}
  ]
}
```

Trial *n* replays `trials[n-1]`. If the file has fewer trials than
`trial_count`, the missing trials are recorded as failed. Traces may be in
`EvalTrace` shape or AgenticLens `Run` shape. Saving each live trial's samples
and replaying them this way makes an experiment reproducible from committed
files — `examples/experiments/record_trials.py` shows the layout.

## What is measured

### Per case

For each variant and case: attempts (one per trial), passes, pass rate, mean
score and its standard deviation across trials, whether every attempt agreed
(`consistent`), and:

- **pass@k** — the probability that at least one of k attempts passes, from the
  unbiased estimator `1 − C(n−c, k) / C(n, k)` (Chen et al., 2021).
- **pass^k** — the probability that all k attempts pass, `C(c, k) / C(n, k)`
  (Yao et al., 2024, τ-bench). This is the reliability measure: an agent with
  pass@1 = 90% has pass^6 ≈ 53% if failures are independent.

A trial whose target call raised an error counts as a failed attempt on every
case: the agent did not deliver an output.

### Per variant

| Measure | How |
| --- | --- |
| Case pass rate | passes / attempts over all cases, with a Wilson score interval |
| pass@k, pass^k | mean of the per-case values |
| Mean score, latency, cost | over completed trials, with normal-approximation intervals |
| Reliability | share of trials in which every case passed |
| Consistency | share of cases whose attempts all agreed; disagreeing cases are listed as flaky |
| Pareto frontier | not dominated on reliability, pass rate, score, latency, and cost |

### Against the baseline

Each comparison reports deltas for pass rate, score, latency, and cost (with the
`regression_threshold` deciding which count as regressions), plus:

- `changed_factors` — `{factor: [baseline value, candidate value]}`;
- `case_pass_rate_p_value` — two-sided pooled two-proportion z-test on case
  attempts, and `statistically_significant` when `p < 1 − confidence_level`;
- `regressed_case_ids` / `improved_case_ids` — cases whose pass rate moved by
  more than the regression threshold;
- warnings when either side completed fewer than `minimum_trials` trials, or when
  several factors changed at once (so the delta cannot be attributed to one).

### Factor levels

For each factor with at least two values, variants sharing a value are
averaged. In the bundled example, `model=large` averages the baseline, terse
prompt, and reranked retrieval variants; `model=small` is the small-model
variant alone.

## Reports

- **JSON** (`--save`): the full `ExperimentReport`, including every trial's
  evaluation report. Schema: `schemas/experiments/experiment-report.schema.json`.
- **HTML** (`--html`): one offline page with the variant table, pass@k / pass^k,
  baseline deltas, a variant × test-case heatmap (colour = mean score, label =
  passes/attempts, dashed outline = flaky), factor levels, warnings, and the
  execution order. Follows the system light/dark preference.
- **CSV** (`--csv`): one row per variant with every summary measure, pass@k /
  pass^k columns, and its baseline comparison.
- **Case matrix CSV** (`--cases-csv`): one row per (variant, case) — the data
  behind the heatmap.

## Reading the numbers honestly

- Intervals and p-values treat each case attempt as independent. Attempts on
  the same case are correlated, so intervals are narrower than they should be;
  treat them as approximate and prefer more cases over more trials.
- A non-significant delta is not evidence of no difference — it may mean the
  experiment is too small. The minimum-trials warning flags the obvious cases.
- Live model outputs vary between runs. Recorded replays reproduce the analysis
  exactly; they do not reproduce the model.
- The seed fixes the execution order, not the model's sampling.

## Limitations

- Only one suite per experiment; variants must answer the same cases.
- No multiple-comparison correction across variants.
- Live variants run trials sequentially; `max_workers` parallelises cases within
  a trial only.

---

## ModelFit recommendations

Source: [docs/modelfit.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/modelfit.md)

AgenticLens 0.9.0 adds `agenticlens.modelfit` and the `agenticlens modelfit`
command group (roadmap milestone v0.7). ModelFit answers one question per
task category: which model should serve this kind of task, given your
quality, cost, latency, safety, provider, and deployment constraints?

ModelFit does not call models and does not use list prices or public
benchmarks. Its candidates are the variants of experiment reports you
already recorded with `agenticlens experiment run --save`, so every
recommendation, savings figure, and quality risk comes from repeated trials
on your own suite.

## Workflow

```text
suite + manifest (one variant per model)
        |
        v
agenticlens experiment run --save experiment.json      (repeated trials)
        |
        v
agenticlens modelfit recommend experiment.json --config modelfit.yaml
        |
        +--> modelfit.json   per-category recommendations, evidence, risks
        +--> modelfit.md     reviewable report
        +--> matrix.csv      task-level model matrix
```

For each task category ModelFit:

1. measures every candidate on that category's cases (pass rate with a
   Wilson interval, cost per case and per success, mean and p95 latency,
   consistency, and safety pass rate);
2. rejects candidates that break a hard constraint, or whose evidence cannot
   show they meet it;
3. scores the remaining candidates with your weights and ranks them;
4. recommends the top candidate with a confidence level, an explanation,
   alternatives, a fallback, savings against a reference model, and the
   quality risks of switching.

## Task taxonomy

A task category selects suite cases by tag, by `metadata.domain`, or by case
ID. A case may belong to several categories.

```yaml
categories:
  - id: policy
    name: Policy questions
    tags: [policy]
    monthly_volume: 40000          # optional, for monthly savings
  - id: billing
    domains: [billing]             # cases with metadata.domain == billing
  - id: vip
    case_ids: [escalate-legal, refund-damaged]
```

With no `categories`, ModelFit derives one category per case tag. The `all`
category (on by default, `include_overall: false` to drop it) covers every
case. `agenticlens modelfit taxonomy experiment.json --config modelfit.yaml`
shows which cases each category covers before you recommend.

## Constraints

`defaults` apply to every category; a category's `constraints` replace only
the fields they set. Set a field to `null` to remove a default for one
category.

| Constraint | Meaning |
| --- | --- |
| `min_pass_rate` | Pass rate over the category's case attempts |
| `min_pass_rate_lower_bound` | Lower bound of the pass rate's Wilson interval |
| `max_cost_per_case_usd` / `max_cost_per_success_usd` | Measured cost limits |
| `max_mean_latency_ms` / `max_p95_latency_ms` | Measured latency limits |
| `min_consistency` | Share of cases with the same outcome on every attempt |
| `min_safety_pass_rate` | Pass rate over every case tagged with a `safety_tags` tag, anywhere in the suite |
| `allowed_providers` / `blocked_providers` | Provider allow-list and block-list |
| `allowed_deployments` | Deployment allow-list (for example `on_prem`, `eu-cloud`) |
| `required_capabilities` | Capabilities the candidate must declare |

Constraints fail closed. A cost limit on a candidate with unpriced attempts,
a latency limit when any completed attempt reported no latency, a safety
minimum when no case is safety-tagged, or a provider allow-list or
block-list for a candidate with no known provider are all violations with a
message that says the limit cannot be verified. Like cost, mean and p95
latency are only stated when every completed attempt reported a latency.

`null` works for list constraints too: `blocked_providers: null` or
`required_capabilities: null` in a category clears the default.

The safety pass rate always covers every safety-tagged case in the suite,
not just the category's own cases: a model that mishandles a safety case is
a risk wherever it is routed.

## Candidates

Each experiment variant is one candidate. Its model name is the variant's
`model` factor (`model_factor` changes which factor), and its provider,
deployment, and capabilities come from, in order of precedence:

1. the config's `candidates` catalog (an explicit `capabilities: []` there
   means "none", overriding metadata),
2. the experiment manifest's variant `metadata` (`--manifest`, or
   `variant_metadata=` in Python), with comma-separated `capabilities`,
3. variant factors named `provider` or `deployment`.

Variants that change something other than the model (a prompt or retrieval
change) are still compared, as configurations; ModelFit warns when two
candidates share a model. Use `exclude_variant_ids` to leave variants out.
Several experiment reports can be combined; ModelFit warns when they use
different suites, because the comparison is then not like-for-like. Case
tags and domains come from the evaluated trials, so a case no experiment
completed a trial on is reported in a warning: only `case_ids` selectors and
`all` can include it.

## Scoring

Feasible candidates get four components in [0, 1]:

- `quality`: the pass rate;
- `cost`: the cheapest feasible cost per success divided by the candidate's
  (unknown cost scores 0; when the cheapest is free, every priced candidate
  scores 0);
- `latency`: the fastest feasible mean latency divided by the candidate's;
- `reliability`: the share of cases with a consistent outcome.

The weighted score is `sum(weight * component) / sum(weights)`, with default
weights `quality 0.5, cost 0.3, latency 0.1, reliability 0.1`. A category can
set its own `weights`. Ties break on pass rate, then cost per success, then
variant ID.

Each category result also lists its Pareto frontier (pass rate, cost per
success, latency, across all measured candidates, feasible or not) and its
cost-per-success ranking.

## Confidence

Confidence starts `high` and is lowered, with a stated reason, when:

- the candidate has fewer than `minimum_attempts` attempts on the category
  (`low`);
- the runner-up scores within 0.05 and the pass-rate difference is not
  significant at `significance_level` (`medium`);
- the pass-rate interval's lower bound is below `min_pass_rate` (`medium`);
- cost evidence is incomplete while cost has weight (`medium`);
- the ranking is clear but the candidate trades away quality or safety the
  reference delivers, a high-severity risk (`medium`).

## Savings and quality risks

Savings compare the recommendation with the reference variant
(`reference_variant_id`, default the experiment baseline) on the same cases:
cost per case and per success, the relative saving, and the projected
monthly saving when the category sets `monthly_volume`. Savings record both
candidates' attempts, the case IDs, and the index of the experiment report
in `sources`, which carries the report's file name and SHA-256. They are
`available: false`, with a reason, when either candidate's cost is
incomplete or the two were measured on different cases (for example, when
combining reports from different suites).

Quality risks are reported separately from savings:

| Risk | Severity |
| --- | --- |
| `quality_regression` | `high` when significantly below the reference, else `medium` |
| `regressed_cases` | Cases that pass less often than with the reference |
| `safety_failures` | `high`: any failed attempt on a safety-tagged case |
| `flaky_cases` | Cases that passed on some attempts only |
| `low_evidence` | Fewer than `minimum_attempts` attempts |
| `cost_unavailable` / `failed_trials` | Incomplete cost evidence, attempts lost to failed trials |
| `no_fallback` | No other candidate is feasible |

## Alternatives and fallbacks

`alternatives` are the next `max_alternatives` feasible candidates by rank.
The `fallback` is the best feasible candidate on a different provider, for
failover; when every feasible candidate shares the recommended provider, or
providers are unknown, the next-best candidate is used and the reason says
it does not protect against a provider outage.

## Task-level model matrix

`matrix` has one row per category and candidate, with the candidate's role
(`recommended`, `fallback`, `alternative`, `feasible`, `infeasible`), pass
rate, cost per success, mean latency, score, and violated constraints.
`--csv` writes it; `agenticlens modelfit matrix modelfit.json` prints it.

## CLI

```bash
agenticlens modelfit taxonomy experiment.json --config modelfit.yaml
agenticlens modelfit recommend experiment.json \
  --config modelfit.yaml --manifest manifest.yaml \
  --save modelfit.json --markdown modelfit.md --csv matrix.csv \
  --fail-on-unfit
agenticlens modelfit matrix modelfit.json
```

Exit codes: `1` for unusable input; `8` with `--fail-on-unfit` when a
category has no feasible candidate (or no evidence), or with
`--fail-on-low-confidence` when a recommendation is low confidence.

## Python API

```python
from pathlib import Path

from agenticlens.modelfit import (
    load_experiment_evidence,
    load_modelfit_config,
    recommend_models,
    render_markdown,
)

report = recommend_models(
    [load_experiment_evidence(Path("experiment.json"))],
    load_modelfit_config(Path("modelfit.yaml")),
)
for result in report.categories:
    rec = result.recommendation
    print(result.category.id, rec.status, rec.variant_id, rec.confidence)
print(render_markdown(report))
```

## Example

[`examples/modelfit_demo.py`](https://github.com/DeepAgentLabs/agenticlens/blob/main/examples/modelfit_demo.py)
replays a recorded four-model experiment (a frontier and a small model from
provider A, a mid-size model from provider B, and a self-hosted open-weights
model) on a ten-case support suite, then recommends with
[`examples/modelfit/modelfit.yaml`](https://github.com/DeepAgentLabs/agenticlens/blob/main/examples/modelfit/modelfit.yaml).
The committed artifacts show:

- `all`: the mid-size model, 63% cheaper per case than the frontier
  reference, with a medium (not significant) quality-regression risk;
- `orders`: the small model, allowed because the category lifts the safety
  minimum, flagged with a high-severity safety risk and low confidence;
- `account`: the self-hosted model, the only candidate that satisfies
  `allowed_deployments: [on_prem]`, with no fallback;
- `safety`: a 100% minimum pass rate that the small model fails.

CI's `modelfit` job replays the experiment and runs
`modelfit recommend --fail-on-unfit`.

## Schemas

[`schemas/modelfit/modelfit-config.schema.json`](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/modelfit/modelfit-config.schema.json)
and
[`schemas/modelfit/modelfit-report.schema.json`](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/modelfit/modelfit-report.schema.json)
(`schema_version: "1.0"`) ship in the wheel.

## Known limits

- Recommendations are only as representative as the suite and trials. Small
  categories produce wide intervals; ModelFit lowers confidence rather than
  hiding that.
- Cost is the experiment's recorded cost. Prices that change after the
  experiment are not reflected until it is re-run.
- Savings are per-case averages times `monthly_volume`; they assume the
  production traffic mix matches the category's cases.
- Provider, deployment, and capability facts are declared, not verified.
- ModelFit recommends; it does not route traffic. Runtime routing is the v0.8
  milestone.

---

## Advisory runtime routing

Source: [docs/routing.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/routing.md)

Route task categories using recorded ModelFit experiment evidence. The Python
SDK supports selection and bounded execution. The CLI and MCP only explain
selection; they never execute models, even if the policy says `enforce`.

## Offline quickstart

```bash
uv run python examples/routing_demo.py
agenticlens routing decide examples/modelfit/artifacts/modelfit.json \
  --category orders --request-id demo-1 \
  --policy examples/routing/artifacts/policy.json --save decision.json
agenticlens routing summary examples/routing/artifacts/shadow.json
```

The synthetic example explicitly allows low-confidence evidence, demonstrates
provider failover and measured shadow operation, and writes results and a JSONL
journal. Its costs are synthetic and its local callback latency is measured;
these are not claims about real providers. The default requires **medium**
confidence and escalates this deliberately small example corpus.

## Python SDK

```python
from pathlib import Path
from agenticlens.modelfit import load_modelfit_report
from agenticlens.routing import (
    RouteOutcome, RouteRequest, Router, RoutingAuditLog, RoutingPolicy,
)

report = load_modelfit_report(Path("modelfit.json"))
router = Router(report, RoutingPolicy(mode="enforce"),
                audit=RoutingAuditLog("routing.jsonl"))

def invoke(target, request):
    # Resolve the original payload by its opaque request_id in your application.
    # Call your provider with your timeout and evaluate the actual outcome.
    # This illustrative callback makes no network call.
    return RouteOutcome(success=True, cost_usd=None)

result = router.run(
    RouteRequest(request_id="opaque-123", category_id="orders"),
    {"small-a": invoke, "mid-b": invoke},
)
```

The host owns payloads, provider SDKs, credentials, deadlines, output storage and
quality checks. Routing records retain outcome, measured elapsed latency and
caller-reported cost, never prompts, responses or exception messages. Use opaque
IDs and non-sensitive model/deployment names. No universal wall-clock timeout,
async provider API or automatic model invocation is claimed.

## Policies and decisions

`RoutingPolicy` has a name/version and canonical SHA-256. A `RouteDecision`
records these plus the canonical hash of the **entire ModelFit model JSON**,
category, confidence, ranked targets, source indexes, rejected candidate reasons,
and selection/allocation explanations. The report hash is independent of file
whitespace; source experiment file hashes remain in the ModelFit report. Keep
that report with the decision to resolve source indexes.

- `advisory` (default): `run` returns a proposal with no callbacks.
- `enforce`: only eligible targets execute, within `max_attempts` (default 3).
- `shadow`: an eligible baseline serves. A separately supplied `shadow_callbacks`
  map enables a second, explicitly safe call to the proposed candidate. Shadow
  output never serves; its failure never changes the serving result. Shadow
  execution is sequential, adds work/cost, and needs side-effect-safe callbacks.
- `canary`: SHA-256 of salt, category and opaque request ID assigns a stable
  baseline/canary cohort. `canary_fraction` is in [0, 1]. Use stable distinct IDs;
  changing the salt reshuffles cohorts. Baseline requests never fall through to
  candidate execution. Candidate requests may use eligible fallback targets.

`strategy="score"` selects by recorded weighted score with variant ID tie-breaks;
its fallback chain prefers other providers before same-provider alternatives.
`strategy="rule"` uses the exact ordered IDs in `rules[category_id]` after all
hard constraints. Unknown rule IDs cannot route, missing category rules escalate.
A different-provider fallback is possible only when eligible evidence exists.

Runtime `constraints` are **additional** to original category constraints; they
cannot loosen ModelFit restrictions. Missing evidence fails closed, including
incomplete costs under cost limits. Baselines and every fallback obey the same
checks. `minimum_confidence` applies the category recommendation's qualitative
confidence label; it is not a calibrated probability or per-target estimate.
No evidence freshness clock is enforced: hosts must regenerate/approve reports
when deployments or evidence change. Hashes identify supplied artifacts, not
independent verification of their claims.

Unknown categories, missing recommendations, low confidence and no eligible
model return `escalated` by default or `blocked` with `on_unroutable="block"`.
Neither invokes a callback. Escalation is a handoff to the host's human workflow;
Lens does not authenticate approvers or provide an approval service. After review,
the host must produce an eligible policy/evidence combination and route again.

## Failover and errors

Only an explicit `RetryableRouteError` triggers the next eligible target. Raise
it only when a failed call is safe to retry (for example an uncommitted provider
outage). Policy denials and potentially committed side effects must never be
wrapped in it. Other exceptions, invalid callback outcomes, unsuccessful quality
outcomes and absent callbacks stop the chain with a failed result. Exception text
is not retained. No implicit retry or policy bypass occurs.

## Audit and measurement

`RoutingAuditLog` appends/fsyncs decision, attempt-start, attempt-finish and result
records. Audit errors propagate before any further callback. A crash can leave
an attempt-start without a finish; reconcile provider state before retrying.
The optional sink is a single-process local journal, without tamper-proofing,
multi-writer locking, RBAC, retention or deletion services. Choose one writer per
path and manage permissions/retention in the host. Without a sink, keep the
returned decision/results yourself.

`summarize_routing` reports served results, shadow pairs, success rates, and mean
shadow-minus-primary latency/cost deltas. Cost deltas remain unavailable if any
pair lacks cost. Requests without a separately executed shadow are not pairs.
These are observed callback outcomes, not statistical causal or significance
claims. Schemas are published in `schemas/routing/` (Lens-local version 1.0).

## Ecosystem compatibility

| Package | Impact |
| --- | --- |
| AgenticLens 0.10.0 | Owns routing SDK, decisions, journal and measured summaries |
| Agentic Evals | Existing `>=0.7.1,<1` range covers current 0.8.0; scoring/gates stay native |
| Agentic Chaos 0.7.0 | Existing `agenticlens>=0.7.0` extra remains compatible; faults stay Chaos-owned |
| Agentic Sidecar 0.8.4 | Existing `agenticlens>=0.7.1,<1` extra remains compatible; Decision Gate/authority remain Sidecar-owned |
| MCP 0.3.12 | Hosted Lens pin 0.10.0 and read-only `lens.routing_decide`; never executes callbacks |
| Control Tower 0.7.0 | Inventory, host-applied settings, approval and native evidence semantics unchanged; no automatic routing adapter |
| AI Operations Specification | Routing artifacts are Lens-local; no normative shared schema or conformance claim added |

Only MCP requires a sibling patch release. The other packages need compatibility
documentation updates, without dependency or runtime changes.

---

## Optimization intelligence

Source: [docs/optimization.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/optimization.md)

Roadmap milestone v0.9, shipped in AgenticLens **0.11.0**.

`agenticlens.optimization` reads recorded traces and recommends changes to
prompts, retrieval, memory, tools, retries, workflow structure, and model
choice. Every recommendation is tied to the spans it came from, states its
projected benefit and the basis for it, lists quality risks separately, and
can be tracked through accept, reject, adopt, and post-adoption evaluation.

It is advisory. Nothing here changes a prompt, model, tool, or route. The
existing workflow recommenders (`agenticlens analyze workflow.json`) still
run per profiled workflow; optimization intelligence works on structured
`Run` traces, aggregates across runs, and adds risks, decisions, and
outcomes.

## Quick start

```bash
# Offline example: 8 recorded runs before and after adopting tool caching.
uv run python examples/optimization_demo.py

agenticlens optimize analyze examples/optimization/traces/before \
  --config examples/optimization/optimization.yaml --baseline-variant large \
  --save report.json --markdown report.md

agenticlens optimize decide report.json tool_result_caching-412a72bac9f5 \
  --status accepted --by platform-team --ledger ledger.jsonl
agenticlens optimize decide report.json tool_result_caching-412a72bac9f5 \
  --status adopted --by platform-team --change support-agent#412 --ledger ledger.jsonl
agenticlens optimize status report.json --ledger ledger.jsonl

agenticlens optimize outcome report.json tool_result_caching-412a72bac9f5 \
  --before examples/optimization/traces/before \
  --after examples/optimization/traces/after \
  --ledger ledger.jsonl --save outcome.json --fail-on-regression
```

```python
from pathlib import Path

from agenticlens.optimization import (
    analyze_optimizations,
    evaluate_outcome,
    load_optimization_config,
    load_traces,
)

before = load_traces([Path("traces/before")])
report = analyze_optimizations(
    before, load_optimization_config(Path("optimization.yaml")), baseline_variant_id="large"
)
for item in report.opportunities:
    print(item.title, item.benefit.cost_usd_per_run, item.confidence, [r.kind for r in item.risks])

outcome = evaluate_outcome(
    report, report.opportunities[0].opportunity_id, before, load_traces([Path("traces/after")])
)
print(outcome.status, outcome.realized_ratio)
```

The committed output of the example is in
[`examples/optimization/artifacts/`](https://github.com/DeepAgentLabs/agenticlens/tree/main/examples/optimization/artifacts).

## What each rule reads

Rules only use what the trace records. A span without the signal a rule
needs is skipped, not estimated.

| Rule (`rule_id`) | Opportunity `kind` | Reads | Fires when |
|---|---|---|---|
| `prompt_caching` | `prompt_caching` | model-call `prompt.prefix_sha256`, `prompt.prefix_tokens`, optional `prompt.cached_tokens` | the same prefix of at least `prompt_cache_min_prefix_tokens` repeats `prompt_cache_min_repeats` times without a cache hit |
| `prompt_compression` | `prompt_compression` | model-call input and output tokens | input ≥ `prompt_compression_min_input_tokens` and input/output ≥ `prompt_compression_min_ratio` |
| `retrieval` | `retrieval_pruning` | retrieval `retrieval.chunks` (or `chunks`): `tokens`, `used` (or `cited`), optional `rank` | at least `retrieval_min_chunks` chunks, utility ≤ `retrieval_max_utility`, and chunks ranked below the deepest used chunk |
| `retrieval` | `retrieval_reranking` | same | a used chunk ranked at or below `retrieval_rerank_min_rank` while higher-ranked chunks went unused |
| `memory` | `memory_summarization` | `memory_read` span tokens | memory share of run tokens > `memory_max_share` and memory > `memory_token_budget` |
| `tool_caching` | `tool_result_caching` | successful tool calls, `tool_args` (or input fingerprint), `idempotent`, `side_effects` | identical arguments repeat `tool_cache_min_repeats` times in one run |
| `retry_policy` | `retry_policy` | retry spans, their triggering failure's `error_type`, retry outcome | ≥ `retry_min_unrecovered` retries of an error type and none recovered |
| `redundant_step` | `redundant_step` | model, retrieval, planning, validation, and memory-read input and output fingerprints | the same input produced the same output again in one run |
| `unnecessary_handoff` | `unnecessary_handoff` | delegation spans, `from_agent`/`to_agent`, the delegated subtree | the receiver made no model, tool, retrieval, or planning call, or returned its input unchanged |
| `quality_cost_tradeoff` | `quality_cost_tradeoff` | `variant_id`, `task_success`, run cost | a variant costs at least `tradeoff_min_cost_reduction` less with success within `tradeoff_max_success_rate_drop` of the baseline |

A tool with any call that declares `idempotent: false` or
`side_effects: true` is never recommended for caching. An error type is called non-retryable only when no
observed retry of it recovered. Top-k is never lowered below the deepest chunk
any observed answer used.

## Benefit, confidence, and risk

Each `Opportunity` has three separate parts.

- **`benefit`** (`ProjectedBenefit`): tokens, cost, and latency per run,
  averaged over every observed run (including unaffected ones), plus a monthly
  cost when `monthly_runs` is configured. `basis` states how it was derived.
  Cost is `null` with `cost_available: false` whenever any affected span lacks
  a recorded cost; it is never filled in from list prices.
- **`confidence`** (`high`/`medium`/`low`) with `confidence_reasons`. High
  needs at least `high_confidence_min_runs` affected runs making up at least
  `high_confidence_min_share` of observed runs. One affected run is low.
  Unpriced savings, assumed reductions (compression, reranking), and trade-offs
  with fewer than 30 runs per variant are capped at medium.
- **`risks`** (`QualityRisk`): kind, severity, and description. Risks are never
  netted against the benefit.

Opportunities are ranked by projected cost per run, then tokens per run;
unpriced opportunities rank last. Opportunity IDs are a stable hash of the kind
and subject, so the same finding keeps its ID across reports.

## Quality-cost trade-offs

`analyze_tradeoffs` groups runs by `variant_id` (runs without `task_success`
exclude their variant) and reports, per variant, the success rate with a Wilson
interval, mean cost, cost per success, latency, tokens, Pareto status over
success and cost, and the success and cost deltas against the baseline with a
two-proportion p-value. Without `--baseline-variant`, the baseline is the
variant with the highest success rate.

A cheaper variant becomes an opportunity only within the allowed success drop.
Any drop is reported as a `quality_regression` risk (high when p < 0.05), and
small samples add a `sample_size` risk. Adopt a trade-off through
[advisory routing](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/routing.md) shadow or canary modes rather than a direct
switch.

## Tracking decisions

`RecommendationLedger` is an append-only JSONL file. Each
`RecommendationDecision` records the opportunity, the SHA-256 of the report
that proposed it, the status, who decided, when, why, and an optional change
reference (PR, commit, config version). Transitions are enforced:

| To | Allowed from |
|---|---|
| `accepted` | `proposed`, `rejected` |
| `rejected` | `proposed`, `accepted` |
| `adopted` | `accepted` |
| `reverted` | `adopted` |

A decision whose `report_sha256` does not match the report is refused, and
statuses and transitions only count decisions made on the same report, so an
acceptance recorded against an earlier report never authorizes adoption, or
shows as the status, on a regenerated one. The ledger is a
single-writer local file, not a governance system.

## Evaluating outcomes after adoption

`evaluate_outcome(report, opportunity_id, before, after)` measures per-run
tokens, cost, latency, and success rate before and after the change, and
re-runs the originating rule on the after traces (`still_detected`). The
projection is copied from the report unchanged, so projected and observed
values sit side by side and are never blended.

`realized_ratio` compares the observed saving with the projected one, on cost
for prompt caching and trade-offs (their saving does not change token counts)
and on tokens otherwise.

| Status | Meaning |
|---|---|
| `insufficient_evidence` | fewer than `--min-runs` (default 3) runs on either side, or the rule stopped firing but the saving could not be measured |
| `quality_regressed` | success rate fell by more than `tradeoff_max_success_rate_drop`; this takes precedence over savings |
| `realized` | at least 80% of the projected saving appeared and the rule no longer fires |
| `partially_realized` | some saving appeared, or the rule still fires |
| `not_realized` | no saving appeared |

`agenticlens optimize outcome --fail-on-regression` exits **9** on
`quality_regressed`, so CI can block a regression introduced by an adopted
optimization.

## Configuration

`OptimizationConfig` loads from YAML or JSON and rejects unknown keys, so a
typo cannot silently drop a threshold. Every opportunity records the
thresholds it used. See
[`schemas/optimization/optimization-config.schema.json`](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/optimization/optimization-config.schema.json)
for every field and default.

## Artifacts and schemas

| Artifact | Model | Schema |
|---|---|---|
| Report | `OptimizationReport` | `schemas/optimization/optimization-report.schema.json` |
| Ledger line | `RecommendationDecision` | `schemas/optimization/recommendation-decision.schema.json` |
| Outcome | `OutcomeEvaluation` | `schemas/optimization/outcome-evaluation.schema.json` |
| Config | `OptimizationConfig` | `schemas/optimization/optimization-config.schema.json` |

These are Lens-local artifacts, not part of the normative AI Operations
Specification. The report contains no wall-clock values, so the same traces and
config reproduce it byte for byte.

## Ecosystem boundaries

- AgenticLens recommends and measures. It does not enforce policy
  (`agentic-sidecar`), approve or roll out changes (`agenticops-control-tower`),
  or define shared contracts (`ai-operations-spec`).
- Model trade-offs reuse experiment runs; for per-category model selection use
  [ModelFit](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/modelfit.md), and for runtime selection use [routing](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/routing.md).
- Evaluate compressed prompts, rerankers, and memory summaries with an
  `agentic-evals` suite before adopting them.

## Known limits

- Projections assume future traffic resembles the analysed traces.
- Prompt-caching cost is pro-rated by token share within a span, an upper bound
  when output tokens cost more than input tokens. Provider cache lifetimes are
  not modelled.
- Compression and reranking benefits are configured or best-case assumptions,
  which is why their confidence is capped.
- Memory and retrieval savings are priced at a blended or downstream per-token
  cost.
- Outcome evaluation compares two windows of traffic; it does not control for
  other changes shipped in the same window.
- Fingerprints depend on recorded `input_data`/`output_data` or references;
  redacted payloads limit redundant-step and handoff detection.

---

## RAG chunk utility

Source: [docs/rag-chunk-utility.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/rag-chunk-utility.md)

AgenticLens can identify low-utility retrieved chunks that waste tokens without
contributing to the final answer. This guide explains the supported signal types
and how to use them.

---

## How It Works

When a retriever step includes `retrieved_chunks` in its metadata, the
`RAGChunkUtilityRecommender` scores each chunk to determine whether it was
useful. Chunks scoring below the threshold (`rag_min_chunk_utility_score`,
default 0.08) are flagged as low-utility.

---

## Supported Signals (Priority Order)

### 1. Citation Signals

Boolean fields that indicate whether the chunk was actually used in the response.

```python
{"text": "Refunds take 5-10 days.", "cited": True}
{"text": "Warehouse inventory system.", "cited": False}
{"text": "Used in answer.", "referenced": True}
{"text": "Old policy doc.", "used": False}
```

**Fields:** `cited`, `used`, `referenced`
**Values:** `True` → score 1.0, `False` → score 0.0

### 2. Reranker Scores

Cross-encoder or reranker confidence scores (0 to 1).

```python
{"text": "Highly relevant passage.", "reranker_score": 0.95}
{"text": "Marginally relevant.", "reranker_score": 0.45}
{"text": "Irrelevant noise.", "cross_encoder_score": 0.02}
```

**Fields:** `reranker_score`, `rerank_score`, `cross_encoder_score`
**Values:** Float 0.0–1.0

### 3. Embedding Similarity

Cosine similarity between chunk embedding and query/answer embedding.

```python
{"text": "Semantically close.", "cosine_similarity": 0.88}
{"text": "Distant meaning.", "embedding_similarity": 0.12}
{"text": "Moderate match.", "semantic_score": 0.55}
```

**Fields:** `embedding_similarity`, `cosine_similarity`, `semantic_score`
**Values:** Float 0.0–1.0

### 4. Generic Utility Scores

Any custom scoring your pipeline provides.

```python
{"text": "Custom scored chunk.", "utility_score": 0.73}
{"text": "Low relevance.", "relevance_score": 0.05}
```

**Fields:** `utility_score`, `relevance_score`, `answer_overlap`
**Values:** Float 0.0–1.0

### 5. Fallback: Word Overlap

If none of the above fields are present, the rule computes word overlap between
the chunk text and the final answer found in the workflow. This is intentionally
conservative — it only catches obviously irrelevant chunks.

---

## Confidence and Quality Risk

| Signal Source | Confidence Range | Quality Risk |
|--------------|-----------------|--------------|
| Citation / Reranker / Embedding | 0.65–0.95 | low |
| Word-overlap fallback | 0.45–0.85 | medium |

Rich signals yield higher confidence because they come from models specifically
designed to assess relevance, whereas word overlap is a rough heuristic.

---

## Usage Example

```python
from agenticlens import profile, step

with profile("RAG Pipeline") as workflow:
    with step(
        "Retriever",
        type="retriever",
        chunk_count=6,
        avg_tokens_per_chunk=80,
        retrieved_chunks=[
            {"text": "Refund policy: within 30 days.", "reranker_score": 0.92},
            {"text": "Returns must be unused.", "reranker_score": 0.78},
            {"text": "Office hours: 9-5 weekdays.", "reranker_score": 0.03},
            {"text": "Parking info for visitors.", "reranker_score": 0.01},
            {"text": "Shipping takes 5-7 days.", "cosine_similarity": 0.41},
            {"text": "CEO biography page.", "cosine_similarity": 0.05},
        ],
    ):
        pass

    with step(
        "Final Answer",
        type="final_response",
        provider="openai",
        model="gpt-4o-mini",
        final_answer="You can return within 30 days if unused.",
    ) as s:
        # Record your provider response to capture token usage.
        # Must expose .usage.prompt_tokens and .usage.completion_tokens.
        s.record(your_llm_response)
```

### Expected Output

```text
Budget Optimization Run cost: $0.0045; reducible: ~$0.0019/run (42%)

Optimization Suggestions
  * Low-utility retrieved chunks
    Step 'Retriever' retrieved 3 chunks that appear unlikely to
    influence the final answer (6 chunks scored). Consider lowering
    top-k, tightening retrieval filters, or reranking before generation.

    Tokens saved: 240
    Confidence: 0.90
    Quality risk: low
```

---

## Configuration

In your AgenticLens config (YAML):

```yaml
recommender:
  rag_min_chunk_utility_score: 0.08   # Threshold below which a chunk is "low-utility"
  rag_min_low_utility_chunks: 2       # Minimum low-utility chunks before flagging
```

---

## When to Use Which Signal

| Your Setup | Best Signal |
|-----------|-------------|
| You have a reranker in your pipeline | `reranker_score` |
| You store cosine similarity from vector search | `cosine_similarity` |
| You track which chunks the LLM actually cited | `cited` |
| You have a custom relevance model | `utility_score` |
| No scoring available | Automatic word-overlap fallback |

---

## Export formats

Source: [docs/export-formats.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/export-formats.md)

AgenticLens supports exporting profiled workflow data in multiple formats.
Below is a preview of what each format looks like with a sample workflow.

For AIOS draft validation and OTLP trace export, see
[AIOS validation and OTel export](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/aios-validation-and-otel.md).

---

## JSON

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "name": "Customer Support Agent",
  "start_time": "2026-07-08T10:00:00Z",
  "end_time": "2026-07-08T10:00:02.340Z",
  "steps": [
    {
      "id": "step-001",
      "name": "Planner",
      "type": "planner",
      "provider": "openai",
      "model": "gpt-4o-mini",
      "metrics": {
        "prompt_tokens": 150,
        "completion_tokens": 45,
        "total_tokens": 195,
        "latency": 0.82,
        "ttft": 0.12,
        "cost": 0.000135
      },
      "metadata": {}
    },
    {
      "id": "step-002",
      "name": "Retriever",
      "type": "retriever",
      "provider": null,
      "model": null,
      "metrics": {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "latency": 0.45,
        "ttft": null,
        "cost": null
      },
      "metadata": {"chunk_count": 8, "avg_tokens_per_chunk": 100}
    },
    {
      "id": "step-003",
      "name": "Final Answer",
      "type": "final_response",
      "provider": "openai",
      "model": "gpt-4o-mini",
      "metrics": {
        "prompt_tokens": 320,
        "completion_tokens": 95,
        "total_tokens": 415,
        "latency": 1.07,
        "ttft": 0.15,
        "cost": 0.000367
      },
      "metadata": {}
    }
  ]
}
```

**Usage:**

```python
from agenticlens.exporters import JSONExporter

JSONExporter().export(workflow, "workflow.json")
```

---

## CSV

```csv
step_id,step_name,step_type,provider,model,prompt_tokens,completion_tokens,total_tokens,latency,ttft,cost
step-001,Planner,planner,openai,gpt-4o-mini,150,45,195,0.82,0.12,0.000135
step-002,Retriever,retriever,,,0,0,0,0.45,,
step-003,Final Answer,final_response,openai,gpt-4o-mini,320,95,415,1.07,0.15,0.000367
```

**Usage:**

```python
from agenticlens.exporters import CSVExporter

CSVExporter().export(workflow, "workflow.csv")
```

---

## Markdown

```markdown
# Workflow Report: Customer Support Agent

## Summary

| Metric | Value |
| --- | --- |
| Total Tokens | 610 |
| Total Cost | $0.000502 |
| Latency | 2.34s |
| Steps | 3 |

## Steps

| # | Name | Type | Provider | Model | Prompt Tokens | Completion Tokens | Total Tokens | Latency | Cost |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Planner | planner | openai | gpt-4o-mini | 150 | 45 | 195 | 0.82s | $0.000135 |
| 2 | Retriever | retriever | - | - | 0 | 0 | 0 | 0.45s | - |
| 3 | Final Answer | final_response | openai | gpt-4o-mini | 320 | 95 | 415 | 1.07s | $0.000367 |
```

**Rendered preview:**

| # | Name | Type | Provider | Model | Prompt Tokens | Completion Tokens | Total Tokens | Latency | Cost |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Planner | planner | openai | gpt-4o-mini | 150 | 45 | 195 | 0.82s | $0.000135 |
| 2 | Retriever | retriever | - | - | 0 | 0 | 0 | 0.45s | - |
| 3 | Final Answer | final_response | openai | gpt-4o-mini | 320 | 95 | 415 | 1.07s | $0.000367 |

**Usage:**

```python
from agenticlens.exporters import MarkdownExporter

MarkdownExporter().export(workflow, "report.md")
```

---

## Jira

The Jira exporter posts a formatted comment on an existing Jira issue using Jira's wiki markup syntax.

**How it looks in Jira:**

```text
*AgenticLens Workflow Report: Customer Support Agent*

||Metric||Value||
|Total Tokens|610|
|Total Cost|$0.000502|
|Latency|2.34s|
|Steps|3|

*Step Breakdown:*

||#||Name||Type||Provider||Model||Prompt Tokens||Completion Tokens||Total Tokens||Latency||Cost||
|1|Planner|planner|openai|gpt-4o-mini|150|45|195|0.82s|$0.000135|
|2|Retriever|retriever|-|-|0|0|0|0.45s|-|
|3|Final Answer|final_response|openai|gpt-4o-mini|320|95|415|1.07s|$0.000367|
```

**Rendered in Jira it appears as:**

> **AgenticLens Workflow Report: Customer Support Agent**
>
> | Metric | Value |
> |--------|-------|
> | Total Tokens | 610 |
> | Total Cost | $0.000502 |
> | Latency | 2.34s |
> | Steps | 3 |
>
> **Step Breakdown:**
>
> | # | Name | Type | Provider | Model | Prompt Tokens | Completion Tokens | Total Tokens | Latency | Cost |
> |---|------|------|----------|-------|---------------|-------------------|--------------|---------|------|
> | 1 | Planner | planner | openai | gpt-4o-mini | 150 | 45 | 195 | 0.82s | $0.000135 |
> | 2 | Retriever | retriever | - | - | 0 | 0 | 0 | 0.45s | - |
> | 3 | Final Answer | final_response | openai | gpt-4o-mini | 320 | 95 | 415 | 1.07s | $0.000367 |

**Usage:**

```python
import os
from agenticlens.exporters import JiraExporter

JiraExporter(
    base_url="https://yourteam.atlassian.net",
    user_email=os.environ["JIRA_USER_EMAIL"],
    api_token=os.environ["JIRA_API_TOKEN"],
    issue_key="PROJ-123",
).export(workflow)
```

**Required environment variables:**

| Variable | Description |
|----------|-------------|
| `JIRA_BASE_URL` | Your Jira instance URL (e.g. `https://yourteam.atlassian.net`) |
| `JIRA_USER_EMAIL` | Jira account email |
| `JIRA_API_TOKEN` | API token from [Atlassian settings](https://id.atlassian.com/manage-profile/security/api-tokens) |
| `JIRA_ISSUE_KEY` | Issue to comment on (e.g. `PROJ-123`) |

---

## Choosing a Format

| Format | Best for |
|--------|----------|
| JSON | Programmatic consumption, CI pipelines, dashboards |
| CSV | Spreadsheets, data analysis, pandas workflows |
| Markdown | GitHub PRs/issues, documentation, sharing with team |
| Jira | Sprint tracking, cost-per-ticket attribution, team visibility |

---

## Workflow schema specification

Source: [docs/workflow-schema-spec.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/workflow-schema-spec.md)

This document defines the **AI Operations Workflow Specification** for the
DeepAgentLabs ecosystem.

The specification elevates `workflow.json` from an internal file format to a
versioned, open contract for representing production AI workflow runs,
observability data, evaluation evidence, resilience events, and future
operational metadata.

The long-term architecture is:

```text
Operational model
        |
        v
AI Operations Workflow Specification
        |
        v
Reference implementations
        |
        +-- AgenticLens
        +-- Agentic Chaos
        +-- deep-agentic-core-mcp
```

## Purpose

The specification exists so multiple tools can read and write a shared workflow
artifact rather than inventing incompatible per-tool formats.

Today, the primary producers and consumers are:

- `agenticlens`, which profiles, analyzes, evaluates, and reports on workflows
- `agentic-chaos`, which appends resilience and fault-injection evidence
- `deep-agentic-core-mcp`, which will expose workflow-oriented capabilities
  through a unified MCP surface

Future tools should be able to consume the same contract for dashboards,
pipelines, benchmarks, postmortems, and standards-readiness reporting.

## Naming and Versioning

- Canonical name: `AI Operations Workflow Specification`
- Short name: `Workflow Spec`
- Current version: `v1`
- Current schema baseline: `v1.1`

The serialized artifact remains JSON and is commonly saved as `workflow.json`,
but the file name is not the specification name.

## Design Principles

- **Open and versioned**: the schema should evolve intentionally with published
  versions.
- **Additive by default**: new top-level fields should not break older readers.
- **Tool-independent**: the spec should outlive any single package.
- **Local-first**: artifacts should work well as ordinary files in codebases,
  CI pipelines, and research workflows.
- **Operationally meaningful**: the model should represent real production AI
  system behavior, not only trace spans.

## Compatibility Model

The document is the JSON serialization of the `Workflow` Pydantic model
(`agenticlens.models.Workflow`) plus additive ecosystem extensions.

Compatibility rules:

- a producer may add new top-level fields without breaking older readers
- a reader that does not understand a field should still report correctly on
  the fields it does understand
- extension producers should prefer additive fields over breaking schema
  rewrites

## Workflow Spec v1.0 - Base Schema

```json
{
  "id": "uuid",
  "name": "Customer Support Agent",
  "start_time": "2026-01-01T00:00:00Z",
  "end_time": "2026-01-01T00:00:18Z",
  "steps": [
    {
      "id": "uuid",
      "name": "Planner",
      "type": "planner",
      "provider": "openai",
      "model": "gpt-4o-mini",
      "metrics": {
        "prompt_tokens": 850,
        "completion_tokens": 210,
        "total_tokens": 1060,
        "latency": 1.1,
        "ttft": null,
        "cost": 0.02
      },
      "metadata": {}
    }
  ]
}
```

`steps[].type` is one of `planner`, `retriever`, `tool_call`, `llm_call`,
`memory`, `final_response`. `steps[].metadata` is a free-form dict; downstream
analysis rules may read specific keys from it.

## Workflow Spec v1.1 - `chaos_events`

`v1.1` adds one top-level field to represent fault-injection and resilience
evidence:

```json
"chaos_events": [
  {
    "id": "uuid",
    "fault_type": "token_timeout",
    "step_id": "uuid-of-a-step-above",
    "step_name": "Planner",
    "timestamp": "2026-01-01T00:00:05Z",
    "outcome": "errored",
    "message": "human-readable summary of what happened",
    "detail": { "...": "fault-specific fields" }
  }
]
```

Field semantics:

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `fault_type` | `str` | yes | Producer-defined identifier such as `token_timeout`, `rate_limit_storm`, `silent_degradation`. Not an enum. |
| `step_id` | `str \| null` | no | Correlates the event to `steps[].id` in the same document. |
| `step_name` | `str \| null` | no | Fallback label when `step_id` is unavailable or unresolved. |
| `outcome` | `str` | yes | Resolution of the wrapped call, such as `errored`, `degraded`, or `delayed`. |
| `message` | `str` | recommended | One-line human-readable summary. |
| `detail` | `dict` | no | Fault-specific structured data reserved for producer-specific detail and future analysis rules. |

`chaos_events` is deliberately typed loosely on the AgenticLens side so
AgenticLens does not need an import-time dependency on `agentic-chaos` or any
other producer.

## Planned Extensions

These additions are expected to land as future additive versions of the
specification:

| Version | Field | Primary Producer | Status |
| --- | --- | --- | --- |
| v1.2 | `agent_topology` | `agentic-chaos` | planned |
| v1.3 | drift-report fields | `agentic-chaos` | planned |
| v1.x | lineage and provenance fields | `agenticlens` | planned |
| v1.x | evaluation and audit evidence | `agenticlens` | planned |

Each new field family should be documented here once shipped.

## Reference Implementations

The specification is intended to be implemented by the DeepAgentLabs ecosystem:

- `agenticlens` as the flagship observability, evaluation, and operational
  intelligence package
- `agentic-chaos` as the resilience testing and failure-validation package
- `deep-agentic-core-mcp` as the MCP-native interface over shared workflow
  artifacts

## Positioning Guidance

This specification should be described as:

- an open workflow specification
- an AI operations workflow specification
- a versioned operational data contract

It should not be described as an official IEEE specification unless it is
formally incorporated into an approved IEEE standards process.

---

## Execution evidence verification

Source: [docs/evidence-verification.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/evidence-verification.md)

Lens authenticates ordered JSON record snapshots without executing their contents.
This Lens-local manifest is not an AIOS execution ledger or an AIOS conformance claim.
Native producer IDs, policy links and payloads are retained unchanged.

```python
import secrets
from agenticlens.integrity import Coverage, seal, verify, replay

key = secrets.token_bytes(32)  # Provision separately; never include in evidence.
records = [{"event_id": "event-1", "kind": "dispatch", "decision_id": "decision-1"}]
manifest = seal(records, key_id="capture-2026-11", key=key,
                coverage=Coverage(stream_id="run-1", description="saved journal", complete=True))
result = verify(records, manifest, trusted_keys={"capture-2026-11": key},
                expected_stream_id="run-1")
assert result.status == "verified"
saved = replay(records, manifest, trusted_keys={"capture-2026-11": key},
               expected_stream_id="run-1")
```

Save records as a JSON array and the manifest with `manifest.model_dump_json()`.
The CLI accepts a separate protected JSON trust store mapping key IDs to hex keys:

```bash
agenticlens evidence verify records.json manifest.json --stream-id run-1 --key-file trusted-keys.json
```

Exit 0 means `verified`; `failed`, `unknown` and `incomplete` exit 1. Results
include authenticated coverage only after authentication and root verification.
Unknown keys do not establish authenticity. Authenticated partial snapshots remain
incomplete; replay requires verified coverage and returns copies in capture order.
Replay invokes no tools, evaluators, callbacks or producer code.

The chain starts with SHA-256 of UTF-8 `lens.evidence-chain/1`. Each next hash
is SHA-256 of the previous raw digest followed by canonical JSON `[index, record]`
(zero-based index). Canonical JSON uses sorted keys, compact separators, ASCII
escaping and rejects NaN/Infinity. Manifest HMAC-SHA256 covers all fields except
`authentication`, using the same canonicalization. Its authenticated count and
root detect modification, reordering, duplication, deletion and tail truncation.

Provision random keys of at least 32 bytes through a trusted channel. Keep the
trust store outside evidence directories with restricted access. Rotate by issuing
a new key ID; retain old trusted keys and manifests for the evidence retention
period. Remove compromised keys: their manifests become unknown. HMAC verifiers
can also forge manifests; use a separate trust service when verifiers must not
have signing authority. This is symmetric authentication, not a public signature.

Retain the expected manifest independently if freshness matters: an attacker can
substitute an older valid snapshot of the same stream. Stream identity comes from
the caller, never from the artifact alone. Whole-snapshot coverage is supported;
range proofs and automatic freshness enforcement are not.

A valid manifest authenticates a snapshot supplied by a key holder. It cannot prove
producer honesty, that every runtime action was captured, or that declared
completeness is true. Replay is recorded evidence inspection, not live reexecution
or automatic reproduction of analysis. AIOS export, causal analysis and a shared
execution/access event schema remain separate work.

## AIOS execution export and downstream integration

`agenticlens.integrity.execution` now exports a native `Run` plus explicitly
supplied `ExecutionRecord` observations to an AIOS `0.4-draft` Run. Both the
spec-owned schema and semantic conformance checks run on export and import.
The packaged schemas are used offline; no remote schemas are fetched. Their
upstream commit and exact SHA-256 digests are recorded in
`schemas/aios/specification/v0.4/SOURCE.json`. Installed wheels need no sibling
repository checkout. Explicit caller-selected spec roots remain supported.

Spans map to steps, each with a run `contains` relationship and an optional
`parent-of` relationship. Runtime statuses map `succeeded` to `completed`,
`failed` to `failed`, and `running` to `running`. IDs and timestamps are preserved.
Explicit observations map to `io.deepagentlabs.agenticlens.execution.<kind>`
extension events targeted at the recorded run or span. Native actor, policy,
approval, decision and action IDs are preserved, without treating an ALLOW or
BLOCK as actual dispatch. Unknown span references and duplicate event IDs fail.
No proposal, completion or dispatch event is fabricated from span status.

The `io.deepagentlabs.agenticlens.execution` extension retains the complete
native Run, including original metadata, attributes and payloads, plus capture
order and mapping limitations. There are no intended native-field losses; this
makes bundles privileged evidence, subject to the producer's redaction and access
policy. Inputs must be JSON-serializable. Event kind semantics and the lossless
mapping are Lens-owned, not new canonical AIOS meanings. AIOS v0.6 provenance
records describe derived findings and are not an execution-ledger replacement.

`ExecutionBundle` authenticates the whole AIOS artifact as one snapshot record.
The manifest's count is therefore **one artifact**, not the number of events.
All nested records and the lossless extension are covered. On import, Lens also
reconstructs the projection and rejects disagreement with the native evidence,
even when the artifact's MAC is valid. This importer deliberately accepts only
the documented Lens mapping, not arbitrary producers or merged AIOS Runs.

```bash
agenticlens evidence export run.json observations.json bundle.json \
  --key-id capture-2026-11 --key-file trusted-keys.json --complete
agenticlens evidence replay bundle.json \
  --run-id run-1 --key-file trusted-keys.json
```

Omitting `--complete` exports incomplete coverage, which replay refuses. Supply
observations as an array of `ExecutionRecord` objects; native producer attribution
and correlation must come from your host's actual observations. Stop/revoke
acknowledgement events do not establish that all subsequent dispatches were
captured. Missing decision/action IDs remain null; Lens does not infer them.

Use `capture_execution`, `import_execution`, `verify_execution`,
`replay_execution` and `execution_summary` for the corresponding Python APIs.
Run `uv run python examples/evidence/execution_demo.py` for a complete offline
capture-export-import example. Capture order is preserved, not timestamp-sorted;
replay neither calls providers/tools nor reruns arbitrary evaluators.

The separately distributed MCP 0.5.2 integration exposes `lens.execution_verify` with a bundle and an expected `run_id`.
Its trust store is configured on the host through
`DEEP_AGENTIC_CORE_MCP_LENS_TRUST_STORE`; callers cannot supply keys or paths.
The separately distributed Tower 0.9.1 integration accepts `execution_bundle` evidence with an explicit Lens source, run ID
and `0.4-draft` version. Its host injects trusted keys into `EvidenceStore` or
HTTP `create_app`. Both delegate authentication and conformance to Lens.
Verified summaries expose causal IDs; failed, unknown and incomplete summaries
expose no causal claims or native payloads. Neither is an Evals containment score.
Older installed Lens versions degrade to unavailable/unknown until upgraded.

Verifier setup failures, such as missing or unreadable local validation resources,
produce `unknown` with a redacted configuration reason. They do not label an
authenticated snapshot as tampered evidence.

---

## Enterprise artifact operations

Source: [docs/production-readiness.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/production-readiness.md)

Lens 0.13.0 adds an opt-in single-node project artifact service. It is separate
from `serve-otlp`, which remains a local, unauthenticated developer dashboard.
Do not expose the developer receiver to an untrusted network.

## Scope and compatibility

`agenticlens.enterprise` exports `Project`, `Credential`, `StoragePolicy`,
`RegistryEntry`, `EnterpriseStore`, and `digest`. The optional `[api]` extra
adds `enterprise.http.create_enterprise_app` and the Uvicorn factory
`enterprise.server:create_app`. Existing native Run/Span, evaluation, diagnosis,
routing, optimization, execution-evidence and AIOS draft shapes are unchanged.
The new audit, compliance and gate markers end in `1-candidate`; they are
Lens-local artifacts, not AIOS schemas or Sidecar runtime policy decisions.

The organization/project key is an immutable namespace configured by the host;
there is no organization signup, identity federation, membership editor or
fleet control plane. Each configured credential binds one subject, role and
project. Readers list project traces and registry metadata; writers additionally
store traces, register versions and request release receipts; admins additionally
prune traces and export audit/compliance metadata. Every data route checks both
organization and project. Only `/healthz` is anonymous. OpenAPI and interactive documentation routes are disabled.

## Configure and run

Install `pip install 'agenticlens[api]'`. Generate random bearer tokens
with `secrets.token_urlsafe(32)` and keep them in a secret manager. Store only
SHA-256 hex digests in an operator-owned JSON file:

```json
{
  "credentials": [{
    "subject": "ci-support",
    "token_sha256": "<SHA-256 hex digest of a random token>",
    "project": {"organization": "demo", "name": "support"},
    "role": "writer"
  }],
  "storage_policy": {"max_age_days": 30, "max_traces": 1000, "redact": true},
  "gate_policy": {"min_pass_rate": 1.0, "max_failed_cases": 0}
}
```

```bash
LENS_CONFIG=/secure/config.json LENS_DATABASE=/data/lens.db \
  uvicorn agenticlens.enterprise.server:create_app --factory \
  --host 127.0.0.1 --port 8000 --workers 1 --no-access-log
```

Missing/invalid credentials fail startup. Restart after token removal or rotation;
configuration is copied at startup. Use unique random tokens, TLS at the proxy,
request concurrency/rate limits, and restrictive filesystem permissions. Never
put tokens or sensitive request bodies in proxy logs. The service caps each
artifact request at 2 MiB, including chunked requests. It accepts native Run JSON,
not OTLP, at `POST /v1/organizations/demo/projects/support/traces`. Each POST
replaces that project's trace ID; this endpoint does not merge OTLP batches.

Trace lists return summaries in pages of at most 20 (`limit`/`offset`); use
`GET trace?trace_id=<id>` for one complete native trace. Sensitive run/span/trace
identities are rejected with 422 before storage, rather than redacted into colliding keys.

Registry, audit and compliance reads also accept `limit` (default 20, maximum
100) and `offset`. Audit pages report `has_more`; compliance export bounds each
collection independently and marks `consistent_snapshot: false`. These are live
pages, not a point-in-time database snapshot; concurrent writes can change page
membership. Use an operator-managed stopped-service database backup for an exact
full inventory. SDK metadata reads default to at most 100 records too.

Other project routes: `GET traces`, `GET trace`, `GET/POST registry`, `POST gate`,
`POST retention/prune`, `GET audit`, and `GET compliance`. Send
`Authorization: Bearer <token>` on every request. Registries accept only kind
(`model` or `prompt`), name, version and content SHA-256. Re-registering identical
metadata is idempotent; replacing a version returns 409. Prompt bodies, provider
keys and executable evaluator references are never stored in this registry.

## Policy, gates and private evaluators

The host's `gate_policy` is Evals `GateConfig` policy-as-code. Callers submit
native Evals `EvaluationReport` JSON to `POST gate`; callers cannot override the
server policy. Returned receipts record the exact policy, native gate decision,
canonical report SHA-256 and installed Lens/Evals versions. Save the original
report and receipt, pin both package versions, then call
`enterprise.gates.release_receipt(report, policy)` offline to reproduce the
receipt. No external tools or target callables run. A gate evaluates the submitted
report; it does not authenticate the producer or establish capture completeness.
Use the separate execution-evidence verifier when authenticity is required.

Private evaluators continue to use `EvaluatorRegistry`/`CallableEvaluator` in a
trusted local Python process (see [evaluation guide](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/evaluation-and-release-gates.md)).
The service accepts their saved native report, never an import path or code.
Standalone scoring and gate computation remain Evals-owned; this service only
composes them. Runtime interception remains Sidecar-owned.

## Retention, PII and audit limits

Common secret fields in metadata, attributes and captured input/output, bearer
strings and email addresses are redacted before trace persistence; native token
counters are preserved. This is pattern-based sanitization, not comprehensive
PII discovery. Use upstream domain-specific redaction, avoid PII in IDs/names,
and authorize recipients. Sanitized traces differ from original evidence; do
not attach an original snapshot's integrity claim to a sanitized copy.

Trace writes prune expired/excess project records transactionally. Reads hide
expired records even before a purge. Schedule an admin `POST retention/prune`
for inactive projects. The policy uses receiver time, not producer timestamps.
Registry metadata and audit records have separate operator-managed archival;
they are not removed by trace retention. Deletion does not erase SQLite free
pages, backups, snapshots or previously exported copies. Use encrypted storage,
a backup expiry policy and secure media disposal for stronger deletion needs.

Mutations and audit inserts share a transaction: if auditing fails the mutation
rolls back. Authenticated authorization denials and successful reads/exports are
also audited; unknown credentials are rejected without creating an attributed
audit record. Subjects are host-managed identifiers; do not use personal data.
Audit rows contain time, sequence, actor, action and object digest, never raw
trace/prompt/token bodies. Compliance export is metadata only and explicitly
`not_assessed`; audit integrity is `not_verified`. Local DB administrators can
rewrite rows. This is neither a signed ledger nor compliance certification.

## Deployment recipes and security acceptance

`deploy/Dockerfile` builds a non-root image. The candidate Helm chart in
`deploy/helm/agenticlens` requires an existing config Secret and an operator-built
image (pin its digest). It runs one replica with Recreate updates, a PVC,
read-only root filesystem, no service-account token, dropped capabilities,
resource limits, probes, ClusterIP and a restrictive network policy. Label
approved same-namespace client/proxy pods `lens-client=<release-name>`.

```bash
docker build -f deploy/Dockerfile -t lens:0.13.0 .
helm lint deploy/helm/agenticlens --set image=example/lens@sha256:<digest> --set configSecret=lens-config
helm template lens deploy/helm/agenticlens --set image=example/lens@sha256:<digest> --set configSecret=lens-config
```

These are candidate deployment recipes, not a claim of cluster certification.
Local automated review covers cross-project reads/writes, role bypass,
invalid/oversized bodies, secret redaction, immutable registry races, persistence,
retention isolation, gate reproducibility and audit rollback (`test_enterprise.py`).
SQLite is a trusted single-node boundary; use one worker and a local block-backed
volume. Horizontal scaling, shared/network filesystems, OIDC/SSO, distributed
audit, legal holds and high availability are outside this release. Cluster
admission, TLS termination, image scanning, encrypted backups, restore drills,
network-policy enforcement and independent security review must pass in the
operator's environment before production approval. These external acceptance
gates and the coordinated ecosystem v1.0 remain open.

## Upgrade and rollback

Back up the SQLite database and config while the service is stopped. Install
0.13.0 with the existing native artifacts unchanged. The new service uses new
`project_traces`, `registry`, and `audit` tables in its own database; it does not
migrate or open the old receiver database. Existing receiver deployments continue
unchanged. To move selected traces, submit reviewed native Run JSON under the
intended project credential; this redacts and re-timestamps the stored copy.
Rollback stops the new service and restores the previous deployment/config;
retain its separate database for export/inspection. Do not downgrade and reuse
a future database without its documented migration path.

Run the offline storage example: `uv run python examples/enterprise_demo.py`.
See [ecosystem matrix](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/lens-0.13-compatibility.md).

---

## Provider and framework integrations

Source: [docs/integrations.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/integrations.md)

AgenticLens is framework-neutral and provider-neutral. It instruments any
Python agent or workflow through its explicit API.

---

## LLM providers

### OpenAI

AgenticLens extracts token usage from OpenAI response objects automatically:

```python
from agenticlens import profile, step
import openai

client = openai.OpenAI()

with profile("OpenAI Workflow"):
    with step("Planner", type="planner", provider="openai", model="gpt-4o-mini") as s:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Plan a trip to Rome."}],
        )
        s.record(response)   # captures prompt_tokens, completion_tokens
```

**Supported response types:** `openai.types.chat.ChatCompletion` (and
compatible objects exposing `.usage.prompt_tokens` / `.usage.completion_tokens`)

### Anthropic

```python
import anthropic
from agenticlens import profile, step

client = anthropic.Anthropic()

with profile("Anthropic Workflow"):
    with step("Planner", type="planner", provider="anthropic", model="claude-3-5-haiku-20241022") as s:
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=256,
            messages=[{"role": "user", "content": "Summarize this."}],
        )
        s.record(response)
```

### Any provider

For providers not natively supported, manually set token counts:

```python
from agenticlens import profile, step
from agenticlens.models.metrics import Metrics

with profile("Custom provider"):
    with step("LLM", type="llm_call") as s:
        # Replace these illustrative counts with actual provider usage.
        s.step.metrics = Metrics(prompt_tokens=120, completion_tokens=30, total_tokens=150)
```

---

## Agent frameworks

### LangGraph

AgenticLens includes a verified offline LangGraph supervisor reference workflow.
See [Multi-agent reference workflows](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/multi-agent-reference-workflows.md).

Install the optional extra:

```bash
pip install "agenticlens[langgraph]"
# or
uv sync --extra langgraph
```

Run the reference workflow:

```bash
uv run python examples/reference_workflows/langgraph_supervisor.py
uv run agenticlens inspect examples/reference_workflows/artifacts/langgraph-supervisor.json
```

**Note:** Automatic framework event capture is on the roadmap. Current
instrumentation is explicit — wrap spans around LangGraph node calls.

### Any Python agent

AgenticLens works with any Python agent. Wrap the workflow with `profile()`
and each significant step with `step()`:

```python
from agenticlens import profile, step

with profile("My Custom Agent"):
    with step("Plan", type="planner") as s:
        result = my_agent.plan(task)
        s.record(result.llm_response)

    with step("Execute", type="tool_call"):
        my_agent.execute(result.plan)
```

---

## Observability backends

### OTLP/HTTP collectors (Grafana, Jaeger, etc.)

AgenticLens can export structured trace runs to any OTLP/HTTP-compatible
collector:

```python
from agenticlens import SpanType, trace

with trace(
    "support-agent",
    otlp_endpoint="http://localhost:4318/v1/traces",
    otlp_headers={"Authorization": "Bearer my-token"},
) as recording:
    ...
```

Or via environment variables:

```bash
export AGENTICLENS_OTLP_TRACES_ENDPOINT=http://localhost:4318/v1/traces
```

### Importing third-party OTLP traces

AgenticLens can import OTLP/HTTP JSON traces produced by other tools:

```bash
agenticlens import-otlp third-party-trace.json --save run.json
```

Supports OpenTelemetry GenAI semantic conventions (`gen_ai.*` attributes)
and AgenticLens-native attributes. Unrecognized attributes are preserved.

---

## CI / CD

### GitHub Actions

Wire the release gate into your CI pipeline:

```yaml
- name: Run evaluation
  run: agenticlens evaluate suite.yaml samples.json --save evaluation.json

- name: Apply release gate
  run: agenticlens gate evaluation.json --min-pass-rate 0.95 --min-average-score 0.90
```

Exit code `2` fails the step when the gate is not met.

### Regression detection

```yaml
- name: Compare runs
  run: |
    agenticlens compare results/baseline results/candidate \
      --fail-on-regression \
      --regression-threshold 0.05 \
      --min-samples 5 \
      --save comparison.json
```

---

## agentic-chaos

AgenticLens reads `chaos_events` written by
[agentic-chaos](https://github.com/DeepAgentLabs/agentic-chaos).
When a workflow artifact includes `chaos_events`, the `ChaosImpactRecommender`
surfaces unhandled failures and silent degradation findings automatically.

```bash
agenticlens analyze workflow-with-chaos.json
```

No extra installation is needed. See
[Workflow schema spec — chaos events](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/workflow-schema-spec.md) for the field format.

---

## Export integrations

| Target | Exporter | Details |
|--------|----------|---------|
| JSON pipelines / CI | `JSONExporter` | [Export formats](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/export-formats.md) |
| Spreadsheets / pandas | `CSVExporter` | [Export formats](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/export-formats.md) |
| GitHub PRs / issues | `MarkdownExporter` | [Export formats](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/export-formats.md) |
| Jira | `JiraExporter` | [Export formats](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/export-formats.md) |
| OTel collectors | `OTLPTraceExporter` | [AIOS validation and OTel export](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/aios-validation-and-otel.md) |

---

## Multi-agent reference workflows

Source: [docs/multi-agent-reference-workflows.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/multi-agent-reference-workflows.md)

AgenticLens includes a verified offline LangGraph supervisor workflow based on
the orchestration patterns published by the official LangGraph repositories.

## LangGraph Supervisor

The workflow uses a compiled LangGraph `StateGraph`. A supervisor delegates work
to research, calculation, and review agents. AgenticLens records delegation,
retrieval, tool, and final-response spans during the actual graph execution.

```bash
uv sync --extra langgraph
uv run python examples/reference_workflows/langgraph_supervisor.py
uv run agenticlens inspect examples/reference_workflows/artifacts/langgraph-supervisor.json
```

The workflow is deterministic and does not require a provider account or API
key. Its saved reference artifact is maintained at:

```text
examples/reference_workflows/artifacts/langgraph-supervisor.json
```

## Optional Dependency

LangGraph remains optional. Installing the AgenticLens core package does not
install it.

```bash
uv sync --extra multi-agent
```

The `multi-agent` extra currently contains the verified LangGraph dependency.

## Instrumentation Coverage

Current instrumentation is explicit:

- `trace()` records the workflow boundary
- delegation spans record supervisor transfers
- retrieval and tool spans record specialist work
- the final-response span records completion
- framework identity is stored on the run

Automatic conversion of every framework-native event into AgenticLens spans
remains roadmap work.

## Official Sources

- [LangGraph](https://github.com/langchain-ai/langgraph)
- [LangGraph supervisor](https://github.com/langchain-ai/langgraph-supervisor-py)

---

## Sidecar correlation

Source: [docs/sidecar-integration.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/sidecar-integration.md)

## Sidecar 0.8 compatibility

Lens 0.7.1 reads `sidecar.correlation/1` through
`agenticlens.integrations.sidecar.attach_decisions(run, records)`. Records must
match the exact run, trace and existing span IDs. Duplicate decisions are
idempotent; conflicting identities and mixed invalid batches are rejected.
All seven outcomes appear as `supervision_decision` timeline events in diagnosis
schema 1.1. BLOCK/ESCALATE do not mark spans, runs or deployments unhealthy.
Decision evidence is not proof of tool execution; the Sidecar journal carries
actual dispatch/completion and must be verified separately. Reasons may contain
sensitive information: callers must authorize recipients. Shared/Exclusive
Sidecar 0.9 adds reader access, narrowed delegation and lifecycle checks;
see the [0.9 compatibility guide](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/sidecar-0.9.md). Reader summaries are not native or hash-verifiable evidence.
No Sidecar runtime dependency is added.

---

## AIOS validation and OTLP export

Source: [docs/aios-validation-and-otel.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/aios-validation-and-otel.md)

AgenticLens can now validate AI Operations Specification draft artifacts and
export structured traces to OTLP/HTTP collectors.

## AIOS draft validation

Use `validate` to run JSON Schema checks against AIOS draft workflow or run
artifacts:

```bash
agenticlens validate workflow.json --version 0.4
agenticlens validate run.json --version 0.4 --save validation-report.json
```

Use `conformance` to run both schema and semantic checks and report draft
alignment:

```bash
agenticlens conformance run.json --version 0.4
agenticlens conformance run.json --version 0.4 --save conformance-report.json
```

When the sibling `ai-operations-spec` repository is not checked out next to
`agenticlens`, pass `--spec-root` explicitly:

```bash
agenticlens conformance run.json \
  --version 0.4 \
  --spec-root ../ai-operations-spec
```

Conformance output distinguishes AIOS-defined pass/fail issues from
AgenticLens-specific rendering. Because AIOS `v0.4` is still a draft, the CLI
reports draft alignment rather than stable conformance.

### Rule-cited, structured results (0.7.0)

When the spec directory contains the machine-readable rules catalog
(`specification/v0.4/conformance-rules.json`), every issue names the AIOS rule
it violates (`rule_id`, for example `AIOS-0.4-P05` for an unresolved
relationship endpoint) and the report lists every rule that applies to the
artifact type with a result:

- `pass`: a schema rule with no schema issues, or a semantic rule AgenticLens
  checks with no issues
- `fail`: at least one issue cites the rule
- `not_checked`: process obligations an artifact alone cannot prove, semantic
  rules AgenticLens does not check yet, and semantic rules skipped because the
  schema failed or only `validate` ran

`report.summary` adds the status (`aligned`, `schema_valid`,
`schema_invalid`, `semantic_invalid`), issue counts by code, and pass/fail/not
checked rule counts.

```bash
agenticlens conformance run.json --json > conformance.json   # structured report on stdout
agenticlens conformance --list-versions                       # supported AIOS versions
```

### Version selection

`--version` accepts `0.4`, `0.4-draft`, or `v0.4`. AgenticLens 0.7.0
supports AIOS v0.4-draft. Following AIOS-0.5-V03, an artifact whose own
`spec_version` names a different version is rejected rather than validated
against the v0.4 schema, and an unsupported requested version is an error, not
a fallback.

## OTLP/HTTP trace export

Structured `trace()` runs can be exported as OTLP/HTTP JSON for tools such as
Grafana, Jaeger, or other OTel-compatible collectors.

Configure export directly in code:

```python
from agenticlens import SpanType, trace

with trace(
    "support-agent",
    otlp_endpoint="http://localhost:4318/v1/traces",
    otlp_headers={"Authorization": "Bearer local-dev-token"},
) as recording:
    with recording.span("planner", SpanType.PLANNING) as planner:
        planner.record_tokens(input_tokens=120, output_tokens=30)
```

You can also configure the endpoint through environment variables:

```bash
export AGENTICLENS_OTLP_TRACES_ENDPOINT=http://localhost:4318/v1/traces
export AGENTICLENS_OTLP_HEADERS='Authorization=Bearer local-dev-token'
export AGENTICLENS_OTLP_TIMEOUT_SECONDS=10
```

After these are set, any configured `trace()` run exports automatically when the
trace context exits.

## Local OTLP payload export

If you want to inspect the generated OTLP payload before posting it, use the
exporter directly:

```python
from agenticlens import SpanType, trace
from agenticlens.exporters import OTLPTraceExporter

with trace("support-agent") as recording:
    with recording.span("planner", SpanType.PLANNING):
        pass

OTLPTraceExporter().save(recording.run, "run-otlp.json")
```

See `examples/operational_intelligence_demo.py` for a runnable example that
saves both a run artifact and an OTLP payload, then validates the run with
`agenticlens conformance`.

---

## Coordinated readiness

Source: [docs/coordinated-v1-readiness.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/coordinated-v1-readiness.md)

Lens 0.14.0 implements offline validation of Run/Workflow (0.4-draft),
provenance (0.6-draft), and operational companions (0.8-draft). The full 66-case
portable suite and 5 held-byte provenance-resolution cases run without importing
AIOS test code. Schemas and catalogs are bundled with source commit/checksums.

`validate_aios_artifact(path)` routes by the document's declared marker.
An explicit `spec_version=` is an assertion, never a fallback. CLI `validate`
and `conformance` default to the declared marker; `--version` asserts a version.
Schema-only validation sets semantic_checked/aligned false; use conformance
for schema plus semantic alignment. Unsupported marker/type pairs are rejected.
`resolve_provenance(record, held_subject_bytes)` uses only caller-held bytes and
reports availability, identity, digest and reference states separately. A
resolved reference is not an authenticated source or verified conclusion.

`agenticlens.exporters.verification.export_verification_signal` projects native
Evals judge scores with Lens structured verdict metadata. It requires a source
id, attributed subject, evidence references, recording time and method version.
Unavailable/skipped judges have no verdict or confidence. Deterministic scores
are rejected. Native free text/metadata are withheld; grounding detail preserves
item counts as redacted entries and safety remains not_checked. Run
`python examples/operational_artifacts.py` for an offline example.

Migration: existing Run/Workflow calls continue to work. Add explicit version
assertions if callers need to constrain accepted markers. Code that used
schema-only aligned as semantic proof must inspect schema_valid instead or run
conformance. No native trace/report/storage contract changes. Rollback by
pinning 0.13.0 and disabling optional companion exports; retain original native
artifacts and do not relabel new companions as older artifacts.

These acceptances remain open as follow-up work under the
[1.0.0 milestone policy](https://github.com/DeepAgentLabs/.github/blob/main/profile/RELEASE_POLICY.md).

## Coordinated 1.0.0 milestone

Version 1.0.0 marks the coordinated DeepAgentLabs milestone on 2026-11-05.
Development and roadmap delivery continue after this release. Existing draft
and candidate schema markers retain their maturity; package versions do not
certify AIOS conformance or production deployment readiness. Independent review,
independent implementations, security/deployment acceptance, live-provider
validation and the stable contract freeze remain tracked follow-up work.
See the [ecosystem release policy](https://github.com/DeepAgentLabs/.github/blob/main/profile/RELEASE_POLICY.md).

---

## Compatibility policy

Source: [docs/compatibility-policy.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/compatibility-policy.md)

Applies to AgenticLens 0.14.x. This is a readiness policy, not a stable v1.0
API freeze. Supported Python versions are 3.10–3.14; CI checks each version.

Public surfaces are documented root exports, documented module exports, console
commands and schemas distributed in the wheel. Leading-underscore modules,
internal helpers, undocumented implementation classes and example outputs are
not stable APIs. New enterprise APIs and `1-candidate` markers are explicitly
candidate surfaces. The HTTP receiver's native trace contract is unchanged.

Patch releases fix defects and refresh compatible dependencies without intended
breaking changes to documented behavior. Minor releases may evolve candidate
APIs, with changelog entries, migration examples and regression checks. Native
schema versions remain independent of package versions; readers should tolerate
unknown additive fields. Breaking native schemas require an explicit new schema
version. A package minor does not silently reinterpret an old schema marker.

Deprecations identify the replacement, affected versions and migration in the
changelog before removal where practical; security/correctness fixes may require
an immediate change with an explicit explanation. Pin package versions and keep
original evidence when reproducibility matters. Gate receipts additionally record
the installed Evals version, policy and report digest. Evals remains the owner
of scoring and gates; AIOS remains exploratory draft and is versioned separately.

See [0.12 → 0.13 migration and rollback](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/production-readiness.md#upgrade-and-rollback)
and [the tested ecosystem matrix](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/lens-0.13-compatibility.md). Stable commitments
and external acceptance remain gated by the coordinated ecosystem v1.0 policy.

---

## Examples

Source: [docs/examples.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/examples.md)

Runnable examples live in the `examples/` directory of the repository.
All examples work offline and require no API key unless noted.

---

## Basic profiling

**File:** `examples/basic_usage.py`

The simplest AgenticLens workflow: wrap an LLM call in `profile()` and `step()`,
then analyze the result.

```python
from agenticlens import profile, step

with profile("Basic Example"):
    with step("Planner", type="planner") as s:
        # Replace with your actual LLM call
        # s.record(response) to capture token usage
        pass
```

```bash
python examples/basic_usage.py
agenticlens analyze workflow.json
```

---

## Recommendations and cost optimization

**File:** `examples/recommendations_demo.py`

Demonstrates token waste detection across planner, retriever, and final-response steps.

```bash
uv run agenticlens profile examples/recommendations_demo.py --save workflow.json
uv run agenticlens analyze workflow.json
```

**Expected output includes:**
- Per-step token and cost breakdown
- Budget optimization summary with reducible cost estimate
- Optimization recommendations with token savings and confidence

---

## RAG chunk utility scoring

**File:** `examples/rag_scoring_demo.py`

Shows RAG chunk utility scoring with reranker scores, cosine similarity,
and citation signals.

```bash
python examples/rag_scoring_demo.py
```

See [RAG chunk utility](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/rag-chunk-utility.md) for supported signal types and thresholds.

---

## Multi-agent token optimization

**File:** `examples/multiagent_token_optimization_demo.py`

Demonstrates per-agent token attribution and oversized-handoff detection
for a planner → researcher → writer pipeline.

```bash
python examples/multiagent_token_optimization_demo.py
agenticlens analyze workflow.json
```

---

## Multi-agent support demo

**File:** `examples/multiagent_support_demo.py`

Larger multi-agent workflow demonstrating `agent_name`, `agent_role`, and
handoff metadata for a customer support scenario.

---

## Export formats

**File:** `examples/export_demo.py`

Demonstrates all export formats (JSON, CSV, Markdown, Jira) from a saved workflow.

```bash
python examples/export_demo.py
```

---

## Custom LLM judge

**File:** `examples/custom_llm_judge.py`

Shows how to register an `LLMJudgeEvaluator` backed by your own model or service.

```python
from agenticlens.evaluation import EvaluatorRegistry, LLMJudgeEvaluator, Score

def my_judge(context):
    # Call your model here
    return Score(name="quality", value=0.92, passed=False, explanation="Accurate and concise.")

registry = EvaluatorRegistry()
registry.register(LLMJudgeEvaluator("quality_judge", my_judge))
```

---

## Evaluation dataset and judge calibration

**File:** `examples/dataset_and_calibration_demo.py`

End-to-end example: build a dataset from samples, assign train/validation/test
splits, run evaluation, and calibrate judge labels against human references.

```bash
python examples/dataset_and_calibration_demo.py
```

---

## Live evaluation

**File:** `examples/live_evaluation_demo.py`

Demonstrates `evaluate-live` with a Python callable target.

```bash
agenticlens evaluate-live suite.yaml \
  --target-kind python \
  --target examples/live_evaluation_demo.py:run_case \
  --save evaluation-live.json
```

---

## Experiment runner

**File:** `examples/experiment_runner_demo.py`

Multi-variant experiment manifest example using the evaluation layer for
repeated live trials with different configurations.

---

## Operational intelligence demo

**File:** `examples/operational_intelligence_demo.py`

Saves a run artifact and an OTLP payload, then validates with
`agenticlens conformance`.

```bash
python examples/operational_intelligence_demo.py
agenticlens conformance run.json --version 0.4 --save conformance-report.json
```

---

## Optimization intelligence

**File:** `examples/optimization_demo.py`

Analyses 8 recorded support-agent runs (two variants), records accept, adopt,
and reject decisions, and evaluates the adopted tool-caching change against
traces recorded afterwards. No model or network calls; artifacts are committed
in `examples/optimization/artifacts/`.

```bash
python examples/optimization_demo.py
agenticlens optimize analyze examples/optimization/traces/before \
  --config examples/optimization/optimization.yaml --baseline-variant large
```

---

## LangGraph supervisor reference workflow

**File:** `examples/reference_workflows/langgraph_supervisor.py`

Verified offline LangGraph supervisor: a supervisor delegates to research,
calculation, and review agents. Deterministic — no API key required.

```bash
uv sync --extra langgraph
uv run python examples/reference_workflows/langgraph_supervisor.py
uv run agenticlens inspect examples/reference_workflows/artifacts/langgraph-supervisor.json
```

See [Multi-agent reference workflows](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/multi-agent-reference-workflows.md).

---

## Pitch demo (full end-to-end)

**Directory:** `examples/pitch_demo/`

Complete demonstration suitable for live presentations. Produces a trace,
evaluation JSON, release decision, and HTML report — all offline.

```bash
uv sync --extra langgraph
uv run python -m examples.pitch_demo.run_pitch_demo
```

Generated artifacts are written to `examples/pitch_demo/artifacts/`.

## Production readiness candidate (0.13)

See [the project artifact service, roles, policy, retention, audit and deployment guide](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/production-readiness.md),
[public compatibility policy](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/compatibility-policy.md) and [ecosystem matrix](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/lens-0.13-compatibility.md).
Run `uv run python examples/enterprise_demo.py` for an offline example.
External security/deployment acceptance and the coordinated v1.0 freeze remain open.

---

## Troubleshooting

Source: [docs/troubleshooting.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/troubleshooting.md)

---

## Installation

### `pip install agenticlens` fails

Ensure you are on Python 3.10 or later:

```bash
python --version
```

If the version is below 3.10, install a newer Python or use [pyenv](https://github.com/pyenv/pyenv).

### Dependency conflict with `pydantic`

AgenticLens requires Pydantic v2 (`pydantic>=2.0,<3`). If you have a project
that pins Pydantic v1, install AgenticLens in a separate virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install agenticlens
```

---

## Token capture

### `s.record(response)` captures zero tokens

The provider response object must expose `.usage.prompt_tokens` and
`.usage.completion_tokens`. Objects without this structure are silently
skipped. Use `s.record_tokens()` to set counts manually:

```python
with step("Planner", type="planner") as s:
    response = my_llm.call(prompt)
    # Fallback if response format is unsupported
    s.record_tokens(input_tokens=150, output_tokens=45)
```

### Cost shows `$0.0000`

This happens when:

1. No provider name was passed to `step()` — add `provider="openai"` (or your provider)
2. The model name is unrecognized — check `config/pricing_data.json` or set a custom pricing file
3. Token count is zero — see above

---

## CLI

### `agenticlens: command not found`

The console script is installed into your virtual environment's `bin/` (or `Scripts/` on Windows).
Activate the environment first:

```bash
source .venv/bin/activate
agenticlens --version
```

Or use `uv run`:

```bash
uv run agenticlens --version
```

### `agenticlens analyze` produces no recommendations

Recommendations are evidence-driven. If the workflow has no retriever steps
with `retrieved_chunks`, no duplicate tool calls, and no `chaos_events`, the
engine will produce no findings. Add metadata to your steps to enable the
relevant recommenders.

### `agenticlens gate` exits with code 1 (invalid input)

Exit code `1` means the report file is invalid or the configuration is malformed.
Check that the evaluation report was saved correctly:

```bash
agenticlens evaluate suite.yaml samples.json --save evaluation.json
cat evaluation.json | python -m json.tool   # verify JSON is valid
```

---

## Evaluation

### Suite YAML raises `evaluator not found`

Evaluators must be registered in application code before calling `evaluate_suite`.
Suite YAML files cannot import Python modules. Register the evaluator first:

```python
registry = EvaluatorRegistry()
registry.register(LLMJudgeEvaluator("quality_judge", my_judge_fn))
report = evaluate_suite(suite, samples, registry=registry)
```

### `evaluate-live` with a Python target fails

Ensure the callable path uses the format `module_path.py:function_name` and
that the function returns the expected sample structure. The target is executed
in the same Python process — all imports must be available.

### Case ID mismatch in `calibrate`

The reference label file and evaluation report must have identical suite
`name` and `version`, and all case IDs in the label file must exactly match
case IDs in the report. A mismatch raises an error rather than silently
comparing misaligned evidence.

---

## OTLP / tracing

### OTLP export silently does nothing

1. Verify the endpoint is reachable: `curl http://localhost:4318/v1/traces`
2. Check that `AGENTICLENS_OTLP_TRACES_ENDPOINT` is set or `otlp_endpoint=` is passed to `trace()`
3. Increase `otlp_timeout_seconds` if the collector is slow to respond

### `serve-otlp` raises `address already in use`

Another process is using port 4318. Use a different port:

```bash
agenticlens serve-otlp --port 4319
```

---

## AIOS conformance

### `conformance` raises `spec-root not found`

The `conformance` command looks for the sibling `ai-operations-spec` repository.
Pass `--spec-root` explicitly:

```bash
agenticlens conformance run.json --version 0.4 --spec-root ../ai-operations-spec
```

---

## Docs build

### `mkdocs build --strict` fails

1. Every page listed in `nav` must have a corresponding file in `docs/`
2. Run `uv sync --extra docs` before building
3. Check for broken links in markdown files

```bash
uv sync --extra docs
uv run mkdocs build --strict --site-dir site/docs
```

### `mkdocs serve` shows broken images

Some image paths use MkDocs-specific syntax (e.g. `{ width="420" }`).
These render correctly with `mkdocs serve` but not under `file://`.
Use a local HTTP server instead:

```bash
python -m http.server 8000
```

---

## Getting help

- [GitHub Issues](https://github.com/DeepAgentLabs/agenticlens/issues)
- [CONTRIBUTING.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/CONTRIBUTING.md)
- [CHANGELOG.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/CHANGELOG.md)

---

## Limitations

Source: [docs/limitations.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/limitations.md)

This page lists what the current AgenticLens release does not do, so you can
plan around it. The package is early-stage (PyPI classifier: Alpha). Planned
improvements appear in [Roadmap](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/roadmap.md). Topic guides list further limits
for their own features.

---

## Instrumentation

### Explicit instrumentation only

AgenticLens does not automatically intercept framework events. You must wrap
agent calls with `profile()` / `step()` or `trace()` / `recording.span()`
explicitly. The `[langgraph]` and `[multi-agent]` extras ship an offline
LangGraph reference workflow, but LangGraph nodes are still instrumented by
hand. Automatic framework event capture (LangGraph, LangChain, etc.) is
roadmap work.

### Token extraction is provider-specific

`step.record(response)` extracts token counts from OpenAI and Anthropic
response objects. Other providers require `s.record_tokens()` with manually
supplied counts.

### No streaming token capture

Token extraction from streaming response objects is not implemented. Buffer
the full response before calling `s.record()`.

---

## Analysis and recommendations

### Recommendations are rule-based

Recommenders apply deterministic heuristics. They identify probable waste
patterns but cannot guarantee that acting on a recommendation will improve
your specific agent's performance. Always evaluate changes with a test suite.

### Cost estimates are approximate

Prices resolve from your overrides, then the optional live pricing feed
(LiteLLM's public price list, cached), then the bundled pricing table. Any of
these can lag behind actual rate changes. Unknown prices stay unknown rather
than counting as zero. Cost estimates are for budgeting and trend analysis,
not billing.

### Optimization projections assume similar traffic

`agenticlens optimize` projects savings from the analysed traces. Compression
and reranking benefits are configured or best-case assumptions, prompt-caching
cost is pro-rated by token share, and outcome evaluation compares two traffic
windows without controlling for other changes shipped in between.

### Comparison is descriptive only

`agenticlens compare` reports descriptive statistics (mean, median, P95,
standard deviation). It does not claim statistical significance or causal
attribution, especially for small or uncontrolled samples. For significance
tests and confidence intervals, use `agenticlens experiment run`.

### Experiments

- One suite per experiment; every variant must answer the same cases.
- No multiple-comparison correction across variants.
- Live variants run trials sequentially; `--max-workers` parallelises cases
  within a trial only.

See [Experiments](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/experiments.md#limitations).

### Diagnosis sees only the recorded trace

Rules and attribution follow what the trace recorded. A root cause outside the
trace (for example an upstream data change) is reported as the first recorded
symptom. Anomaly detection assumes baseline runs of the same workflow and does
not correct for multiple comparisons. See [Diagnosis](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/diagnosis.md#limitations).

### ModelFit and routing use only your evidence

ModelFit does not call models or use public benchmarks; it ranks only the
variants in experiment reports you recorded. Routing runs
through host-owned callbacks, and Lens does not authenticate approvers. See
[ModelFit](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/modelfit.md) and [Routing](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/routing.md).

---

## Evaluation

### No built-in provider clients

AgenticLens does not ship LLM clients for evaluation. You supply the
callable that calls your model. The `LLMJudgeEvaluator` wraps your function
and normalizes the score; it does not make model API calls itself.

### Synchronous evaluator APIs

Evaluator APIs such as `evaluate_suite` are synchronous. `evaluate-live
--max-workers N` calls a live target for several cases at once, but async
evaluator APIs are roadmap work.

### `max_turns` requires explicit metadata

`max_turns` checks require `trace.metadata.turn_count` to be set as a
positive integer. AgenticLens does not infer conversational turns from span
types.

---

## Live OTLP receiver (`serve-otlp`)

### No authentication

The receiver ships with no authentication. It must not be exposed to untrusted
networks. Always bind to localhost (`127.0.0.1`) in development environments.

### Plain polling, not websockets

The real-time dashboard refreshes by polling. It does not use WebSockets
or Server-Sent Events.

### In-memory store eviction

The default in-memory trace store evicts the oldest traces (FIFO) when the
cap (default 200) is reached. Use `--db PATH` for persistent storage.

---

## Enterprise artifact service

The optional artifact service (`agenticlens[api]`) uses SQLite as a trusted
single-node boundary: run one worker on local block storage. Horizontal
scaling, OIDC/SSO and high availability are outside this release. Deleting data
does not erase SQLite free pages or backups, and registry and audit records are
not removed by trace retention. See [Production readiness](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/production-readiness.md).

---

## Payload redaction

### Built-in patterns are not exhaustive

The built-in redactor strips secrets, bearer tokens, and email addresses.
It is not a comprehensive PII scrubber. For production environments with
strict data handling requirements, supply a custom `redactor=` function.

---

## AIOS conformance

### Draft specification

The `ai-operations-spec` is a draft. Conformance reports say "draft alignment"
rather than "stable conformance." Schema and semantic checks will evolve as
the spec matures.

---

## Schemas

### Trace and evaluation APIs are experimental

The trace, comparison, and evaluation report schemas may evolve in future
minor versions. Breaking changes will be documented in
[CHANGELOG.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/CHANGELOG.md)
and accompanied by a version bump.

---

## Platform

### Python 3.10+ required

AgenticLens supports Python 3.10 to 3.14. Older Python versions are not
supported.

---

## Historical integration note: AIOS v0.6.1 compatibility

Source: [docs/aios-0.6.1.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/aios-0.6.1.md)

AI Operations Specification repository v0.6.1 adds the first v0.6.x drafts:

- [provenance records](https://github.com/DeepAgentLabs/ai-operations-spec/blob/v0.6.1/specification/v0.6/provenance.md): a
  `spec_version: "0.6-draft"`, `artifact_type: "provenance"` companion artifact
  with subjects, source references, derived findings and evidence lineage;
- a [portable conformance suite](https://github.com/DeepAgentLabs/ai-operations-spec/tree/v0.6.1/specification/v0.6/conformance-suite)
  with expected outcomes and rule citations;
- [naming conventions](https://github.com/DeepAgentLabs/ai-operations-spec/blob/v0.6.1/specification/v0.6/naming-conventions.md).

Run and Workflow artifacts stay `0.4-draft`; the v0.4 schemas and
`AIOS-0.4-*` rule catalog are unchanged, so existing exports remain valid.
Consumers that do not check `0.6-draft` must reject provenance records under
`AIOS-0.5-V03` rather than validate them against v0.4.

## AgenticLens

The AIOS exporter and `agenticlens conformance` stay on `0.4-draft`; their rule-cited checks were re-run against the v0.6.1 specification and still pass. Running the portable suite from `agenticlens conformance` and exporting Lens findings or optimization evidence as provenance records are roadmap candidates, not shipped features.

## Dependencies

No runtime dependency floor changes and no package release are needed for
this documentation alignment. Independent review is still pending; passing the
suite or holding a verified provenance record is not stable conformance and
does not show that any artifact or finding is true. See the
[AIOS ecosystem guide](https://github.com/DeepAgentLabs/ai-operations-spec/blob/v0.6.1/docs/v0.6.1-ecosystem.md).

---

## Historical integration note: AIOS repository v0.7.0 compatibility

Source: [docs/aios-0.7.0.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/aios-0.7.0.md)

AIOS v0.7.0 adds non-normative migration guidance, an OpenTelemetry companion
profile pinned to upstream semantic conventions 1.37.0, tested retry examples,
and a strict MkDocs publishing pipeline. Run/Workflow remain `0.4-draft`;
provenance remains `0.6-draft`. Independent-review gates remain open.

Existing trace exports and conformance checks keep their current meaning. Lens already supports [OTLP/HTTP export](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/aios-validation-and-otel.md);
this release does not change it or claim that it implements the new companion profile.

No runtime dependency floor changes or package patch release are required.
This is documentation alignment; it does not add an automatic exporter or
migration adapter. The paired telemetry example is illustrative, not OTLP JSON.

For an offline example, clone AIOS at tag `v0.7.0`, run `uv sync --extra dev`,
then `uv run pytest tests/test_otel_binding.py tests/test_v06_conformance_suite.py`.
Use `make docs` to build its browsable documentation. These are specification
repository checks, not commands supplied by this package.

See the [migration guide](https://github.com/DeepAgentLabs/ai-operations-spec/blob/v0.7.0/specification/v0.6/migration-guide.md),
[OTel profile](https://github.com/DeepAgentLabs/ai-operations-spec/blob/v0.7.0/specification/v0.6/otel-binding.md)
and [dependency matrix](https://github.com/DeepAgentLabs/ai-operations-spec/blob/v0.7.0/docs/v0.7.0-ecosystem.md).

Repository v0.7.0 corrects the next-phase release number; the incorrect
v0.6.2 publication and tag have been removed. Artifact markers and independent-review gates do not change.

---

## Historical integration note: AIOS operational-artifact compatibility

Source: [docs/aios-0.8-operational-artifacts.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/aios-0.8-operational-artifacts.md)

AIOS repository v0.8.1 distributes the v0.8.0 schema snapshot under MIT.
Run/Workflow remain **0.4-draft**, provenance **0.6-draft**, and operational
companions **0.8-draft**. Independent acceptance and coordinated v1.0 gates remain open.

## Structured judges and diagnosis evidence

AgenticLens 0.14.0 ships marker-routed schema and semantic validation for 0.4-draft Run/Workflow, 0.6-draft provenance and 0.8-draft operational companions, plus held-byte provenance resolution. `export_verification_signal` projects native judge Scores with explicit source, subject and evidence. Unavailable judgments retain null verdict/confidence, and safety stays not_checked. Native findings remain evidence, not proof of execution or recovery.

## Adoption and validation

See [coordinated readiness and examples](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/coordinated-v1-readiness.md) for the
public API and migration path. The [canonical schemas and rules](https://github.com/DeepAgentLabs/ai-operations-spec/tree/v0.8.1/specification/v0.8)
define the projection contract. Source and citation presence do not authenticate
a producer or verify its conclusion. Reference URIs are not instructions to
fetch or execute anything. Use Lens or MCP for optional schema and semantic
checks; source/native identity and unavailable/unknown states remain explicit.

## Dependencies and rollback

The implementation is released in the owning package's minor version, with no
AIOS Python runtime dependency. Native contracts retain their own versions.
Disable optional companion emission or pin the preceding package version to
roll back; do not relabel a companion as an older artifact family.

---

## Historical integration note: AIOS v0.6 compatibility

Source: [docs/aios-v0.6.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/aios-v0.6.md)

AI Operations Specification repository v0.6.0 delivers the exploratory
[canonical examples and extension model](https://github.com/DeepAgentLabs/ai-operations-spec/tree/v0.6.0/specification/v0.6).
Artifacts still declare `spec_version: "0.4-draft"`; the existing schemas,
conformance rules and compatibility catalog are unchanged. Independent review
remains pending; the repository release does not establish stable conformance.

Existing AIOS export and validation continue using v0.4 schemas and rules. Suite, ModelFit and routing artifacts retain their Lens-local contracts.

## Dependencies and examples

No runtime dependency floor changes or package patch release is needed for this
documentation alignment. The AIOS layer adds no Python runtime API.

To inspect the canonical artifacts, check out AIOS `v0.6.0`, run
`uv sync --extra dev` and `make check` there, then read
`specification/v0.6/examples/manifest.json`. It distinguishes valid fixtures
from schema-invalid and semantic-invalid controls. These checks need no sibling
package and do not constitute independent implementation evidence.

Producer metadata belongs only in permitted `attributes` or reverse-domain
`extensions` entries; it cannot redefine core vocabulary. Consumers that
re-emit an artifact must preserve unknown extension JSON values. Extension
contract validation is separate from core validation. A namespace does not
certify the payload, safety, authority or successful execution.

---

## Historical integration note: Chaos 0.11 ChaosHub compatibility

Source: [docs/chaos-0.11-chaoshub.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/chaos-0.11-chaoshub.md)

Lens 0.13.0 continues reading native Chaos reports and caller-created span markers. Instrument target spans explicitly; recipe names do not establish ground truth for quality or containment. Chaos's existing optional Lens range admits Lens 0.13.0; Lens core has no
Chaos dependency and no Lens release is needed.

Chaos 0.11.0 adds six offline framework-neutral starter recipes, explicit
commit-pinned GitHub registry exchange and opt-in installed fault plugins.
Downloads and catalog listing never execute recipe targets. JSON recipes are
also valid YAML and need no YAML extra. `hub push` stages a contribution in a
caller-owned registry checkout for an ordinary reviewed pull request.

## Offline operator example

Run from an agentic-chaos checkout with its instrumented offline target:

```bash
agentic-chaos hub search rag
agentic-chaos hub pull rag-context-poisoning recipe.json
agentic-chaos chaos run examples/chaoshub_app.py --experiment rag-context-poisoning --save hub-report.json
```

The example deliberately emits a synthetic wrong answer. Availability can pass
while resilience stays inconclusive without quality probes or a fidelity judge.
Review target, probe and workflow paths before running downloaded recipes.
Remote access needs an explicit repository and full commit SHA; plugin loading
executes trusted installed code only when explicitly requested. The native
Chaos report and AIOS export formats are unchanged.

See the [ChaosHub guide](https://github.com/DeepAgentLabs/agentic-chaos/blob/4b60f2e8deb7b68a469a10d3219e60fdc3f3c562/docs/v0.11.md)
and [offline app](https://github.com/DeepAgentLabs/agentic-chaos/blob/4b60f2e8deb7b68a469a10d3219e60fdc3f3c562/examples/chaoshub_app.py).
Coordinated ecosystem v1.0 acceptance remains open.

---

## Historical integration note: Chaos 0.7 compatibility

Source: [docs/chaos-0.7.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/chaos-0.7.md)

## Chaos 0.7.0 interoperability

Chaos 0.7.0 adds sequential fault cascades, deterministic monotonic breaking-point
search, synthetic response poisoning (including prompt/tool-response instruction
and policy-bypass payloads), and explicit-price retry cost estimates. Native
child event IDs and fault types remain intact; cascade IDs/stages and poisoning
strategy/payload/seed are additive event detail. Existing report readers and
AIOS exports remain compatible.

See the [v0.7 guide and offline synthetic example](https://github.com/DeepAgentLabs/agentic-chaos/blob/v0.7.0/docs/v0.7.md).
The example includes observed synthetic dispatches and a bypassed negative
control. Injection or recovery alone does not prove containment. No new shared
schema, automatic adapter, hosted execution capability or containment guarantee
is introduced.

Lens continues to read chaos_events and diagnose marked spans through existing Chaos span adapters. Suite conversion rules are unchanged. No dependency bump or Lens patch release is needed.

---

## Historical integration note: Chaos 0.8 compatibility

Source: [docs/chaos-0.8.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/chaos-0.8.md)

## Chaos 0.8.0 interoperability

Chaos 0.8.0 adds:

- multi-stage chaos workflows: steps, steady-state health checks, parallel
  branches, approval gates that can be resumed, and reusable templates
- declarative YAML/JSON/TOML experiments, with validation that never executes
  targets and cron schedule previews
- `Scope` explosion-radius control (steps, providers and exclusions) on every
  built-in fault and `cascade()`; custom faults get it by calling
  `BaseFault.__init__`, setting `scope` or overriding `in_scope()`
- a topology fuzzer that weights fault placement by fan-out

Native event IDs and fault types are unchanged. Workflow provenance
(`detail.workflow`) and an optional `ChaosReport.workflow` summary are
additive. A workflow's steps merge into one native report for contracts and
AIOS export.

See the [v0.8 guide](https://github.com/DeepAgentLabs/agentic-chaos/blob/v0.8.0/docs/v0.8.md)
and the [offline examples](https://github.com/DeepAgentLabs/agentic-chaos/tree/v0.8.0/examples/workflows).
Workflow statuses, health checks and fuzz outcomes are resilience evidence.
They are not scores, release gates or proof of containment. No new shared
schema, automatic adapter or hosted execution capability is introduced.

Lens reads workflow reports and merged reports as `Workflow` JSON and analyzes their `chaos_events` as before. `detail.workflow` is producer-specific event detail under schema v1.1. Suite conversion rules are unchanged. Chaos's optional `agenticlens>=0.7.0` extra is unchanged, so no dependency bump or Lens patch release is needed.

---

## Historical integration note: Chaos 0.9 compatibility

Source: [docs/chaos-0.9.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/chaos-0.9.md)

## Chaos 0.9.0 interoperability

Chaos 0.9.0 adds:

- resilience probes: `HttpProbe`, `ResponseQualityProbe`, `LatencyProbe` and
  `FunctionProbe` check steady state before chaos, while faults are active and
  after recovery. By default no fault is injected when a pre-chaos probe
  fails; `require_steady_state=False` runs the chaos anyway and leaves the
  score inconclusive
- a 0-100 resilience score built from recovery, probe, latency,
  retry-efficiency and cost evidence, with per-fault verdicts. Components a
  run cannot show (for example latency without a baseline) are left out and
  the remaining weights renormalized. The score is inconclusive (`null`) after
  a failed pre-chaos probe, for dry runs, when no fault fired, or when no
  component can be computed
- a local run-history store for score trends, with `max_runs` and
  `max_age_days` retention, and a `--min-score` CI gate
- probes and scoring on chaos workflows, experiment files and the pytest marker

Native event IDs and fault types are unchanged. `ChaosReport.probes`,
`ChaosReport.resilience` and the matching `WorkflowReport` fields are optional
and additive. When a score was computed, AIOS exports add a derived
`resilience_score` measurement; inconclusive runs export none. Probe results
and the score breakdown stay in the `io.deepagentlabs.agentic-chaos`
producer extension.

See the [v0.9 guide](https://github.com/DeepAgentLabs/agentic-chaos/blob/v0.9.0/docs/v0.9.md)
and the [offline demo](https://github.com/DeepAgentLabs/agentic-chaos/blob/v0.9.0/examples/chaos_resilience_demo.py).
The resilience score summarizes the evidence of one chaos run. It is not an
Evals score, a release-gate decision, a deployment health signal or proof of
containment. No new shared schema, automatic adapter or hosted execution
capability is introduced.

Lens reads scored reports as `Workflow` JSON and analyzes their `chaos_events` as before. The chaos-impact recommender does not consume `probes` or `resilience`, so Lens cost, latency and diagnosis findings do not change. Suite conversion rules are unchanged. Chaos's optional `agenticlens>=0.7.0` extra is unchanged, so no dependency bump or Lens patch release is needed.

---

## Historical integration note: Control Tower 0.6.0 compatibility

Source: [docs/control-tower-0.6.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/control-tower-0.6.md)

Tower combines Phase 6 (local MCP connector and investigation) and Phase 6A
(approved staging incident-to-recovery) in a single **0.6.0** release, paired with
MCP **0.3.6**. Sibling packages remain optional; no producer dependency floor or
runtime behavior changes in this documentation alignment.

Lens 0.7.1 supplies native failed/successful Run artifacts and diagnosis reports.
Tower preserves trace IDs, failed spans, tool names and dependency error types;
Lens retains analysis and producer attribution. Prompt versions are unavailable
in the native run contract and remain explicitly missing in investigations.

The first supported remediation target is Tower's deterministic local SQLite
staging dependency runtime. Exact-preview approval binds target, dependency,
impact, rollback and recovery criteria. Tower commits a consumed execution claim
before dispatch; duplicates and interrupted actions cannot automatically replay.
A successful command only awaits verification: fresh Lens success, a correlated
passing Evals gate and an independent successful probe determine resolution.
Failed recovery escalates. Production runtime adapters, hosted MCP tenant
credential binding, bulk operations and incident console views remain planned.

## Example and dependency matrix

From a sibling workspace, create a versioned Tower checkout (omit clone if
already present). The example first ships in `v0.6.0`; it is absent from 0.5.x:

```bash
git clone --branch v0.6.0 https://github.com/DeepAgentLabs/agenticops-control-tower.git ../tower-0.6.0
cd ../tower-0.6.0
uv run --with ../agenticlens --with ../agentic-evals python examples/incident_recovery.py
uv run --with ../agenticlens --with ../agentic-evals python examples/incident_recovery.py --fail-verification
make test-ecosystem
```

The two walkthrough outputs are `resolved` and `escalated`. The actual producer
matrix is Lens 0.7.1, Evals 0.7.1, Sidecar 0.8.0 and Chaos 0.5.3; MCP 0.3.6
exposes the real authenticated Tower 0.6.0 API. Native artifact readers do not
require those packages at Tower startup. MCP uses HTTP and does not import Tower.
`ai-operations-spec` 0.5.1 is a repository/catalog release, not an AIOS
schema version. Lens supports AIOS v0.4-draft only; Tower-local incident
contracts make no AIOS conformance claim.

See [the operator guide](https://github.com/DeepAgentLabs/agenticops-control-tower/blob/v0.6.0/docs/incident-recovery.md)
and [MCP setup](https://github.com/DeepAgentLabs/agenticops-control-tower/blob/v0.6.0/docs/mcp-connector.md)
for API requests, credentials, supported scope and recovery limits.

---

## Historical integration note: Evals 0.10.0 evaluation evidence compatibility

Source: [docs/evals-0.10-aios-evidence.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/evals-0.10-aios-evidence.md)

[Agentic Evals 0.10.0](https://github.com/DeepAgentLabs/agentic-evals/releases/tag/v0.10.0)
delivers its roadmap v0.10: `to_aios_evidence()` exports an evaluation report
as AI Operations Specification `0.4-draft` `evaluation` evidence, and
`attach_aios_evidence()` merges it into an existing `run` artifact. The CLI
path is `agentic-evals aios export`.

## Validating with Lens

Lens's own AIOS validator accepts the merged Run. The Evals example
(`examples/aios/run-with-evaluations.json`) reports `schema_valid`,
`semantic_valid` and `aligned` as true with no issues:

```bash
agenticlens validate run-with-evaluations.json --spec-root ../ai-operations-spec
```

Each evaluation has an `evaluates` target that resolves in the Run (rule
`AIOS-0.4-P08`). Evals refuses to export without a mapping and refuses to
attach to a target that is not in the Run.

## Ownership

- Lens still owns traces, calibration, experiments, diagnosis and its AIOS
  conformance tooling. Evals derives evidence only from its native report and
  never reads Lens traces.
- To attach Evals evidence to a Run that Lens exported, map each Evals case to
  the Step or occurrence whose output it scored. Use `external: true` for a
  Lens trace that is not in the Run. Evals never infers the mapping.
- Judge usage keys (`judge_*`) ride in each evaluation's attributes as score
  metadata. They are not added to the Run's `measurements`, so judge spend is
  never counted as the run's own cost.
- Unavailable judgments are exported as `unavailable` with no score, and cases
  with no observed output are reported in `unobserved_cases`. Neither reads as
  a pass.

Native report schema 1.0 is unchanged. Lens 0.10.0's full test suite passes
against Evals 0.10.0 (723 tests), and `agentic-evals>=0.7.1,<1` already allows
it. No Lens change or release is needed.
See the [Evals guide](https://github.com/DeepAgentLabs/agentic-evals/blob/v0.10.0/docs/aios-evidence.md).

---

## Historical integration note: Evals 0.11 containment compatibility

Source: [docs/evals-0.11-containment.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/evals-0.11-containment.md)

Evals 0.11.0 supplies `ContainmentEvaluator` and the six-scenario
`adversarial-containment` pack. It scores actual dispatch/completion and denial
observations separately from task success. Missing evidence, missing policy or
configuration versions, incomplete coverage and bypassed enforcement fail.

Lens 0.12.0 authenticates the exact ordered snapshot. Coverage remains
producer-declared. Chaos 0.10.0 supplies attacks and native scenario assertions;
Sidecar 0.9.2 owns authority, enforcement and effective stop receipts. MCP 0.6.1
pins Evals 0.11.0 and validates scores against the Phase 6 real-adapter harness.
Already-running calls can complete after acknowledgement and remain separately
reported. A BLOCK decision or safe answer alone cannot pass containment.

Use the [Evals guide and passing/failing example](https://github.com/DeepAgentLabs/agentic-evals/blob/main/docs/containment.md):

From an **agentic-evals v0.11.0 checkout**, run:

```bash
uv run --extra integrity python examples/containment/generate.py
uv run --extra integrity agentic-evals evaluate examples/containment/suite.json \
  examples/containment/passing.samples.json \
  --registry examples.containment.registry:registry --out /tmp/containment.json
uv run agentic-evals gate /tmp/containment.json --config examples/containment/gate.json
```

Run those commands from an Evals checkout. Substitute
`post-stop-dispatch.samples.json` or `incomplete.samples.json` to get a failing
gate. The fixture key is public synthetic test material; production trust keys
and expected scope belong to the host, never the evaluated sample.

Native report/gate schema 1.0 is unchanged. Existing optional ranges remain
sufficient except MCP's exact pin, which requires its 0.6.1 patch release.
Lens 0.12.1 also updates report schemas, examples and live-target failure handling.

Lens 0.12.1 requires agentic-evals>=0.11.0,<1. Its integrity verifier remains optional to Evals and supplies verified/failed/unknown/incomplete status. Snapshot authentication does not establish exhaustive capture or runtime enforcement.

Lens 0.12.1 refreshes embedded Evals schemas/examples and preserves native
reports for failed live-target trials. Wrong answers remain completed trials.
The runtime Evals floor becomes 0.11.0; Lens integrity semantics are unchanged.

---

## Historical integration note: Evals 0.12 API and report readiness

Source: [docs/evals-0.12.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/evals-0.12.md)

Evals 0.12.0 captures its public root API candidate and current report/gate
schemas in compatibility fixtures, executes all registered offline Python
examples, and publishes its CPython 3.10-3.14 support policy. The downstream
workflow pins Lens 0.12.1, Tower 0.9.1 and MCP 0.6.1 and installs the candidate
distribution over each consumer's locked environment before testing it.

Native report/gate schema 1.0, immutable schema IDs and AIOS `0.4-draft`
exports are unchanged. Existing public imports and compatible dependency ranges
continue to work. No runtime, schema or normative AIOS change is required here.
Scoring and release-gate computation remain Evals-owned; deployment health,
resilience, supervision and artifact conformance retain their own meanings.

The public/private module and deprecation policies are candidate readiness work.
The `agentic-evals>=1.0,<2` matrix and coordinated ecosystem release-candidate
acceptance gates remain open until that launch. No independent stable API or
AIOS conformance is claimed.

For an offline producer example, run in a clean Evals checkout at the released tag:

```bash
git clone --branch v0.12.0 --depth 1 https://github.com/DeepAgentLabs/agentic-evals.git evals-0.12
cd evals-0.12
uv sync --extra dev
uv run python examples/report-contract/generate.py
uv run pytest tests/test_public_api.py tests/test_report_contract.py --no-cov
```

Consumers must preserve a failed `GateDecision.passed` and unknown future fields;
schema validation does not recompute gates. See the
[public API policy](https://github.com/DeepAgentLabs/agentic-evals/blob/v0.12.0/docs/public-api.md),
[support and reproducible matrix](https://github.com/DeepAgentLabs/agentic-evals/blob/v0.12.0/docs/support-policy.md)
and [executable examples](https://github.com/DeepAgentLabs/agentic-evals/blob/v0.12.0/examples/README.md).

---

## Historical integration note: Evals 0.8.0 CLI interoperability

Source: [docs/evals-0.8-cli.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/evals-0.8-cli.md)

Evals 0.8.0 runs Lens 0.8.0 approved suite exports directly with `agentic-evals evaluate` or `live`, then applies release policy with `gate`. Lens retains dataset curation, approval, lineage and diagnosis. The existing `agentic-evals>=0.7.1,<1` dependency admits 0.8.0; no floor increase is needed.

```bash
agentic-evals evaluate suite.yaml samples.jsonl --out report.json
agentic-evals gate report.json --config gate.yaml --out gate.json
```

`evaluate`/`live` exit 0 when a report is produced, even if cases fail.
`gate` exits 0 on pass, 1 on failed policy, and 2 on invalid input or usage.
Use Evals 0.8.0 for these commands; see the [CLI guide and CI example](https://github.com/DeepAgentLabs/agentic-evals/blob/v0.8.0/docs/cli.md).

This is compatibility documentation only: no sibling runtime change,
dependency-floor increase or patch release is required.

---

## Historical integration note: Evals 0.9.0 judge reliability compatibility

Source: [docs/evals-0.9-judge-reliability.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/evals-0.9-judge-reliability.md)

[Agentic Evals 0.9.0](https://github.com/DeepAgentLabs/agentic-evals/releases/tag/v0.9.0) delivers its roadmap v0.9: judge cost and
latency on every judge score, bounded judge retries with an explicit
*unavailable* outcome, repeated judging with agreement, live-target retries
and per-case timeouts, and async evaluators and targets.

## One judge-usage contract

Evals now records the judge usage keys that Lens's `structured_judge()` already
writes and `analyze_scores()` already reads: `judge_cost_usd`,
`judge_cost_source`, `judge_input_tokens`, `judge_output_tokens`,
`judge_latency_ms`, `judge_model` and `judge_provider`. Evals' own
`LLMRubricEvaluator` and `LLMJudgeEvaluator` now produce them too, so
`analyze_scores()` prices Evals rubric judges without any change in Lens.
Evals also totals them in the report's new `summary.judge`. Lens keeps its own
per-evaluator breakdown, pricing estimates and disagreement analysis.

When `structured_judge()` records `judge_latency_ms` itself, Evals keeps that
value. Every judge score also gains `judge_status` (`ok` or `unavailable`) and
`judge_attempts`. With `samples=N` it also gains `judge_verdicts` and
`judge_agreement`, a judge-stability signal. Lens's `calibrate_judge()` does
not read it today: it still consumes `Score.value` and `Score.passed`. Using
agreement in calibration would be future Lens work.

## Behavior to know

- A judge function that raises no longer aborts `evaluate_suite`. This includes
  one wrapped by `structured_judge()`. It becomes an unavailable score: value 0,
  never passing, `judge_status: "unavailable"`. `analyze_scores()` counts it as
  a failed model-based score, and the Evals default gate fails on it and names
  the case.
- Experiment trial reports embed native reports. They may now carry
  `summary.judge`, `summary.live` and `cases[].target_status`, all optional and
  `null` for offline or judge-free runs. ModelFit and routing read the same
  per-case fields as before.
- Lens report consumers and approved-suite exports work unchanged with
  `evaluate`, `live` and `gate`.

## Dependencies

`agentic-evals>=0.7.1,<1` already admits 0.9.0. Lens 0.10.0's full test
suite (722 tests) passes against Evals 0.9.0 unchanged. No floor increase or
Lens release is needed. Scoring and gate computation stay in Evals;
datasets, calibration, experiments and diagnosis stay in Lens.

See the [Evals guide](https://github.com/DeepAgentLabs/agentic-evals/blob/v0.9.0/docs/judge-reliability.md).

---

## Historical integration note: Evals native contract compatibility

Source: [docs/evals-report-contract.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/evals-report-contract.md)

Agentic Evals 0.7.2 publishes native report (`schema_version: "1.0"`) and
gate-decision JSON Schemas, with offline `report_schema()` and
`gate_decision_schema()` accessors. Contract 1.x evolves additively; readers
should tolerate unknown fields. Lens continues to consume the same native report fields through its existing Evals dependency. Trace capture, calibration, score analysis and diagnosis remain Lens-owned.

See the [contract, examples and compatibility policy](https://github.com/DeepAgentLabs/agentic-evals/blob/main/docs/report-contract.md). Existing dependency
ranges remain sufficient; using the new accessors directly requires
`agentic-evals>=0.7.2`. This documentation alignment needs no sibling patch release.

These schemas validate native Evals output; they do not establish AIOS
conformance. See [AIOS validation and OpenTelemetry](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/aios-validation-and-otel.md)
for the separate specification validation surface.

---

## Historical integration note: Lens 0.13 ecosystem compatibility

Source: [docs/lens-0.13-compatibility.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/lens-0.13-compatibility.md)

The production-readiness candidate adds optional project artifact storage. It
changes no existing native report, Run/Span or integrity-verification semantics.
No automatic adapter turns the new audit/compliance artifacts into native
Sidecar, Tower, MCP or AIOS evidence.

| Consumer | Dependency / tested boundary | Impact |
| --- | --- | --- |
| agentic-evals 0.12.0 | Lens integrity extra `>=0.12.0,<1`; Lens requires Evals `>=0.11.0,<1` | Existing native reports, gates and optional verifier stay compatible; no floor increase |
| agentic-chaos 0.11.0 | Lens analysis extra `>=0.7.0`; containment extra `>=0.12.0,<1` | Chaos reports/containment remain producer-owned; no range change |
| agentic-sidecar 0.10.1 | Lens extra `>=0.7.1,<1` | Existing decisions/correlation remain native; new service policy controls stored artifacts only |
| Control Tower 0.10.0 | Lens extra `>=0.12,<1` | Native evidence reader and health semantics unchanged; no project/audit ingestion implied |
| MCP 0.6.6 | Hosted recipes pair Lens 0.13.0, Evals 0.12.0, Sidecar 0.10.1 and Chaos 0.11.0 | Patch refreshes the Chaos/Sidecar pins; no new enterprise routes exposed as MCP tools |
| AIOS repository 0.7.0 | No Lens runtime dependency | Native exports retain `0.4-draft`; enterprise artifacts are Lens-local candidates |
| Organization profile | Documentation only | Readiness scope and open security/stability gates recorded |

For the Lens 0.13 delivery, only MCP needed a package patch for its hosted
image pin. The subsequent ChaosHub alignment also releases Sidecar 0.10.1 to
admit Chaos 0.11 and MCP 0.6.6 to refresh both pins. Other siblings' existing
ranges already admit Lens 0.13; their docs need no package release. Existing installed
optional extras can update Lens normally. Hosting a new enterprise service is an
explicit operator action, never an automatic effect of a sibling upgrade.

## Offline operator example

```python
from agenticlens.enterprise import Project
from agenticlens.models.trace import Run

project = Project(organization="demo", name="support")
run = Run(application_name="support", trace_id="recorded-trace")
assert project.key == "demo/support"
assert run.schema_version == "1.0"  # Existing native trace contract
```

Run `uv run python examples/enterprise_demo.py` for isolated storage, redaction,
registry and metadata export. Run `make check` for Lens acceptance; sibling CI
retains each package's existing producer-specific checks. Package compatibility
is not evidence completeness, runtime containment or a deployment health verdict.

---

## Historical integration note: MCP 0.4.0 unified workflows

Source: [docs/mcp-0.4-unified-workflows.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/mcp-0.4-unified-workflows.md)

[MCP 0.4.0](https://github.com/DeepAgentLabs/mcp-server/releases/tag/v0.4.0) completes Phase 4 with its unified workflows: `core.compare_runs`, a fail-closed `core.release_check`, `core.incident_summary` and `core.export_report`. MCP judges nothing itself; it composes Lens comparisons, the Evals release gate and Chaos run reports. Malformed or failed-call evidence always blocks readiness, and so does missing evidence of a required kind; all three kinds are required by default and `required_evidence` narrows that.

## What MCP reads

- `core.compare_runs` and `lens.compare_runs` share one path and store the Lens
  comparison in the MCP session.
- `core.release_check` re-validates a supplied comparison with
  `agenticlens.comparison.models.ComparisonReport`; anything that does not
  validate, or a failed call (`ok: false`), is an `invalid` gate.
- Evaluation reports go through `agenticlens.evaluation.evaluate_gate` with a
  `GateConfig`, as `lens.slo_summary` does.

## What blocks a release

Lens-related conditions:

- Any entry in `regressions`.
- A comparison that does not validate as a `ComparisonReport`, or a failed call.
- An evaluation report that fails the Evals gate or is not a valid Evals report.

The release check also blocks on chaos crashes or timeouts, malformed chaos
reports, and any kind listed in `required_evidence` (all three by default) that
is missing. Lens-specific notes:

- `sample_size_guidance` is surfaced in the gate's `observed` values but does not
  block on its own. Compare at least five runs per cohort for stable results.

## Compatibility

No Lens API change, dependency bump or release. MCP keeps its existing optional
Lens import; without Lens the comparison and evaluation gates report `invalid`.

See the [MCP unified workflows guide](https://github.com/DeepAgentLabs/mcp-server/blob/v0.4.0/docs/unified-workflows.md).

---

## Historical integration note: MCP 0.5.0 hosted access control

Source: [docs/mcp-0.5-access-control.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/mcp-0.5-access-control.md)

[MCP 0.5.0](https://github.com/DeepAgentLabs/mcp-server/releases/tag/v0.5.0) completes MCP Phase 5 with hosted access control. Each hosted key can carry allow and deny tool globs, an expiry and a task scope. The server enforces them at dispatch, outside the model: before each hosted handler runs, it re-authenticates the key and reloads its policy. Revocation, a narrower policy or expiry therefore stops queued calls, retries and calls on existing connections. Calls already running finish. Allowed calls log a `dispatch` and a `completion` record. Denied calls instead return and log a `denial` or `revocation_acknowledged` record and never reach the handler. Every record uses the MCP-local `mcp.access-decision.v1` shape, and the records of one call share a `correlation_id`. They are not AIOS artifacts. `core.access_status` reports a key's effective policy, and operators use `deep-agentic-core-mcp-admin` to narrow or revoke a key by user ID.

## What changes for Lens

- Hosted `lens.*` tools are subject to a key's policy. For example,
  `"allow": ["lens.*"], "deny": ["lens.suite_*"]` permits analysis but not suite
  management.
- Lens analysis, provenance and suite behaviour are unchanged. MCP still
  delegates every judgement to Lens.
- Access evidence is MCP-local. Lens integrity-protected export and verification
  is still open on the Lens roadmap and is not part of this release.

## Compatibility

No Lens API change, dependency bump or release. MCP's hosted pins stay at
`agenticlens==0.11.0`.

See the [MCP hosted access control guide](https://github.com/DeepAgentLabs/mcp-server/blob/v0.5.0/docs/access-control.md).

---

## Historical integration note: MCP 0.7 integration readiness — Lens 0.13.0

Source: [docs/mcp-0.7-readiness.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/mcp-0.7-readiness.md)

Lens owns analysis and authenticated execution snapshot verification. MCP does not reinterpret snapshot authentication as exhaustive observation or production readiness. Project artifact-service credentials and MCP/Tower credentials remain distinct.

MCP 0.7.0 completes its local integration-readiness milestone: read-only
`core.compatibility`, packaged candidate matrix, standalone installed-wheel MCP
protocol acceptance and released sibling matrix validation. It reports
`baseline_match`, `different_version` or `not_installed` for local distribution
metadata. Those observations do not certify imported workspace sources, adapter
readiness, a remote service version or hosted deployment health. Use `core.verify`
for adapter probes and Tower discovery for the configured remote contract.

The acceptance baseline is MCP 0.7.0, MCP Python SDK 2.0.0, Lens 0.13.0,
Chaos 0.11.0, Evals 0.12.0, Sidecar 0.10.1, Tower 0.10.0 and AIOS repository
0.7.0. Optional package boundaries and native schemas are unchanged. Explicit
workspace checkouts may override installed producer sources.

This companion update changes documentation only; it requires no dependency
floor change, runtime patch or sibling package release. Publishing MCP does not
deploy AWS. Coordinated ecosystem v1.0, independent AIOS review and operator
security/deployment acceptance remain open gates.

See [MCP support, acceptance commands, upgrades and rollback](https://github.com/DeepAgentLabs/mcp-server/blob/fcdf635d522acc8103173d2f7ef56539222d04b5/docs/release-readiness.md)
and [the executable diagnostic example](https://github.com/DeepAgentLabs/mcp-server/blob/fcdf635d522acc8103173d2f7ef56539222d04b5/examples/compatibility_check.py):

```bash
# Run from an MCP 0.7 checkout:
uv run python examples/compatibility_check.py
```

---

## Historical integration note: MCP Phase 6 coordinated containment release

Source: [docs/phase6-containment.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/phase6-containment.md)

MCP 0.6.0 pairs with Chaos 0.10.0 and Sidecar 0.9.2. Lens 0.12.0,
Evals 0.10.0, Tower 0.9.0 and AIOS 0.6.1 remain compatible. See the
[MCP operator guide and tested matrix](https://github.com/DeepAgentLabs/mcp-server/blob/c18f73decdc75aaac3e2e95004ae88589d587e75/docs/phase6-containment.md).

MCP binds hosted Tower credentials per authenticated user; tool policies still
apply and approval remains human-only in Tower. The independent operator stop
endpoint binds an exact owner/task to a live Sidecar runtime. Sidecar owns stop
latching, authority and dispatch enforcement. The MCP revoker waits for its
in-flight transaction before acknowledging task-dedicated credential revocation;
queued calls reauthenticate. Running Sidecar calls and unrelated credentials
remain harness-owned. Bind controls to the process hosting the actual runtime.

Chaos supplies native assertions over observed dispatch/completion and effective
acknowledgements, authenticating the exact ordered snapshot through Lens.
Failed, unknown, incomplete or missing evidence cannot pass. Tests include an
actual handler dispatch through a deliberately bypassed authorizer, which must
fail containment assertions despite valid snapshot authentication. Recovery,
output quality and resilience scores are separate. Evals v0.11 reusable
containment scoring shipped subsequently in Evals 0.11.0; see
[the updated matrix](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/evals-0.11-containment.md).

MCP retains its native access records and adds `io.deepagentlabs.access`, defined
in the spec-owned exploratory `drafts/access-evidence-v1` profile. No new
normative artifact or version marker is introduced. Coverage is producer-declared;
Lens authentication does not prove exhaustive capture. Tower preserves attributed
native outcomes and deployment health remains separate.

Sidecar 0.9.2 widens optional Chaos dependencies to `<0.11`. Other existing
optional ranges remain sufficient, so no other sibling runtime release is needed.
Hosted arbitrary chaos execution stays disabled. Reproduce the isolated seed-601
acceptance suite from the MCP guide; it requires the actual adapters without skips.

AIOS 0.6.1 denotes the existing Run/schema compatibility baseline. The new
exploratory access profile is in the coordinated spec repository revision,
not the historical v0.6.1 tag. It is not promoted to a normative schema family.

Evals 0.11 reusable containment scoring is delivered separately from this
original Phase 6 release. MCP 0.6.1 and Lens 0.12.1 provide coordinated
consumer compatibility. See [the updated matrix](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/evals-0.11-containment.md).

---

## Historical integration note: Sidecar 0.10 contract readiness

Source: [docs/sidecar-0.10.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/sidecar-0.10.md)

Lens 0.12.1 retains sidecar.correlation/1 journal verification and projections; the new wrappers do not replace the native correlation reader.

Sidecar 0.10.0 adds opt-in candidate `sidecar.intent/1`, `sidecar.decision/1`,
`sidecar.audit/1`, `sidecar.scope/1` and `sidecar.transfer/1` contracts. Raw native
artifacts remain supported. Transfer requires a trusted host and live shared
AuthorityRegistry; private configuration is not approval, remote authorization
or a durable grant. Shared and exclusive restrictions all apply; conflicts
fail, readers intersect and earliest expiry wins.

See the [migration and supported-version guide](https://github.com/DeepAgentLabs/agentic-sidecar/blob/main/website/docs/v0.10.md),
[offline propagation example](https://github.com/DeepAgentLabs/agentic-sidecar/blob/main/examples/v0_10_contracts.py)
and [AIOS candidate mapping](https://github.com/DeepAgentLabs/ai-operations-spec/tree/main/drafts/sidecar-contracts-v1).

Operator example: keep existing native readback/dispatch integration; wrap an
existing Decision with `DecisionContract(schema_version="sidecar.decision/1", decision=native)` only when a consumer
explicitly supports that family. Never unwrap an ALLOW as an execution receipt.
Authorize private payload exports; redacted summaries cannot verify journals.
No new sibling runtime dependency is introduced. AIOS draft maturity and the
coordinated ecosystem v1.0 acceptance gates remain open.

---

## Historical integration note: Sidecar 0.9.0 compatibility

Source: [docs/sidecar-0.9.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/sidecar-0.9.md)

Sidecar 0.9.0 adds explicit task-authority tool bindings, narrowed delegation,
ancestor revocation, dispatch-time expiry checks, context reader permissions and
redacted evidence summaries. Private scope goals/values use explicit host delivery.

Lens owns trace capture and analysis. Native Decision and sidecar.correlation/1 remain unchanged. Redacted Sidecar summaries omit arguments/reasons and are not native or hash-verifiable evidence; use authorized native exports when integrity/readback is required.

The core package remains standalone. No new mandatory sibling dependency or
shared schema is introduced. Constraint-only guardians retain expiry WARN;
authority-bearing tasks BLOCK on expiry/revocation. Stop revokes descendants;
restart does not revive grants. Operator intent modification cannot reset a
delegated grant. Reader/actor identities must come from the trusted harness.

The fixed comparison has 24 offline synthetic runs (12 per variant): Agent Alone
dispatches 6/6 unsafe proposals; Sidecar dispatches 0/6, with 2/6 false interventions
on clean gate/provider-outage controls. Zero live inference cost/tokens are
synthetic accounting, not an economic or production-reliability claim. Raw
arguments/journals/operator views remain privileged; redaction is allowlisted,
not arbitrary secret detection or process isolation.

See the [Sidecar v0.9 guide](https://github.com/DeepAgentLabs/agentic-sidecar/blob/v0.9.0/website/docs/v0.9.md)
and [paired evidence](https://github.com/DeepAgentLabs/agentic-sidecar/blob/v0.9.0/tests/validation/v0_9_supervision.json).

---

## Historical integration note: Tower 0.10 capability contract compatibility

Source: [docs/tower-0.10-compatibility.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/tower-0.10-compatibility.md)

Updated 2026-11-04.

Tower 0.10 adds authenticated `GET /contracts/capabilities` and the Python
`ControlTowerAPI.get_capability_contract()` facade. The descriptor publishes
`tower.capabilities.v1` as a candidate, with registration/heartbeat/readback JSON
Schemas, status values and existing merge/replacement semantics. CPython and
Node.js HTTP clients are tested against a live server and durable SQLite
readback. Existing routes and payloads remain compatible.

Lens owns telemetry, analysis and execution verification. Reported capability metadata is not authenticated evidence.

## Operator example

Against a running Tower server with a reader token:

```bash
curl --fail -H "Authorization: Bearer $AGENTICOPS_READ_TOKEN" \
  "$AGENTICOPS_API_URL/contracts/capabilities"
```

Expect `contract_version: tower.capabilities.v1` and `maturity: candidate`.
A writer token can also read this route; readers cannot register workers.
Use Tower's [Python and Node examples](https://github.com/DeepAgentLabs/agenticops-control-tower/tree/v0.10.0/examples/runtimes)
for registration through heartbeat/readback. A duplicate registration replaces
the record; heartbeat merges metadata and replaces reported status. Reported
health does not automatically expire or derive from producer outcomes.

## Dependencies and release boundary

No runtime dependency, optional range, native schema or export marker changes
are required in this repository. No package patch release is needed for this
documentation-only compatibility update. Siblings remain optional to Tower.
The candidate is preparation for the coordinated ecosystem v1.0 release;
independent acceptance and stable freezing remain open. See the
[Tower contract and migration policy](https://github.com/DeepAgentLabs/agenticops-control-tower/blob/v0.10.0/docs/capability-contract.md).

---

## Historical integration note: Tower 0.7.0 integration compatibility

Source: [docs/tower-0.7-fleet-operations.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/tower-0.7-fleet-operations.md)

## Control Tower 0.7.0 fleet operations

Tower 0.7.0 adds frozen environment/capability targeting, bulk desired settings,
separate approval, durable per-target results and bounded stop/MCP-revocation
acknowledgement through Python, HTTP and CLI. No fleet atomicity or automatic
rollback/resume is claimed. Timed-out/requested commands need host reconciliation.

Lens retains trace capture, diagnosis and suite management. Enhanced-tracing fleet settings are desired configuration only until a host explicitly applies them; native evidence and health stay independent.

Existing optional dependency ranges remain sufficient. No sibling runtime or
native evidence schema changes are required; this documentation alignment needs
no patch release. See the [operator guide](https://github.com/DeepAgentLabs/agenticops-control-tower/blob/v0.7.0/docs/fleet-operations.md).

Example operator workflow (against a configured Tower server):

```bash
agenticops-control-tower --token "$WRITER_TOKEN" bulk preview fleet.json
agenticops-control-tower --token "$APPROVER_TOKEN" bulk approve BULK_ID
agenticops-control-tower --token "$WRITER_TOKEN" bulk execute BULK_ID
agenticops-control-tower --token "$READER_TOKEN" bulk get BULK_ID
```

Use the exact request and ownership setup in the operator guide. A successful
desired-setting write does not assert runtime application or incident recovery.

---

## Historical integration note: Control Tower 0.8.0 live operations compatibility

Source: [docs/tower-0.8-live-operations.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/tower-0.8-live-operations.md)

Control Tower 0.8.0 adds periodic local detection over pushed telemetry, durable
deduplicated alerts and acknowledgements, attributed lifecycle audit, and a
read-only incident console joining inventory, evidence, findings, approvals,
commands and recovery checks. Fresh native Lens failures can open recovery
incidents; stale heartbeats and stale/missing evidence produce separate warnings.
Detection never executes recovery, and clearing an alert never resolves an incident.

Fresh failed native Lens runs can create Tower incidents. Tower marks Lens integrity as not verified and coverage as not assessed; runtime routing and ModelFit artifacts are not automatic detection inputs.

The detector uses the latest observation per deployment/producer, with a default
300-second freshness window and 30-second polling interval. It is not lossless
streaming or an external notification service. Same-run correlation stays within
an environment and does not prove causality. Deployment health remains reported;
evidence freshness, integrity and coverage are separate concerns.

No sibling dependency bump, new mandatory import or native artifact change is
needed. This compatibility update is documentation only and needs no patch release.

## Example operator workflow

```bash
agenticops-control-tower --token writer-token alerts evaluate
agenticops-control-tower --token reader-token alerts list --active-only --environment staging
agenticops-control-tower --token reader-token incidents view INCIDENT_ID
```

Use Tower's [operator guide](https://github.com/DeepAgentLabs/agenticops-control-tower/blob/v0.8.0/docs/live-operations.md)
for rules, authorization, persistence, API/CLI commands and operational limits,
and its [standalone example](https://github.com/DeepAgentLabs/agenticops-control-tower/blob/v0.8.0/examples/live_operations.py)
for detection, deduplication and acknowledgement without optional siblings.

---

## Historical integration note: Control Tower 0.9.0 runbooks compatibility

Source: [docs/tower-0.9-runbooks.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/tower-0.9-runbooks.md)

Control Tower 0.9.0 adds versioned runbooks and recovery workflows. Installed
runbook versions are immutable and declare prerequisites, named string parameters
(each constrained by a pattern, length and optional allowed list) and ordered steps with per-step timeouts, retry limits and optional rollback actions.
Recommendations come only from installed versions. A writer previews an exact
digest, a separate human approves it, and Tower claims each step before
dispatching it to a host-installed connector. Clean failures retry within the step
limit and then run declared rollback actions for completed steps; partial,
timed-out or unknown outcomes stop for reconciliation without replay. A runbook
resolves only after a connector probe, a fresh successful Lens run and a passing
Evals gate for the same run. The supported runtime is a deterministic staging
fixture; production runtime connectors are not included.

Tower owns runbooks, approvals and incident coordination. Lens owns analysis; Evals
owns scoring; Sidecar owns runtime enforcement; Chaos owns resilience testing;
MCP owns tool exposure. AIOS remains the draft shared-semantics authority.

Resolving a runbook requires a fresh successful native Lens run whose run ID differs from the detection run, with no failed Lens run recorded for that run ID. Tower does not compute diagnosis, trace integrity or routing decisions.

MCP 0.5.1 adds local `tower.runbook*` tools over the new routes; approval stays
human-only. No sibling dependency bump, new mandatory import or native artifact
change is needed here. This compatibility update is documentation only and needs
no patch release.

## Example operator workflow

```bash
agenticops-control-tower --token reader-token runbooks recommend INCIDENT_ID
agenticops-control-tower --token writer-token runbooks preview INCIDENT_ID preview.json
agenticops-control-tower --token approver-token runbooks approval EXECUTION_ID approval.json
agenticops-control-tower --token writer-token runbooks execute EXECUTION_ID execute.json
agenticops-control-tower --token writer-token runbooks verify EXECUTION_ID verify.json
```

Use Tower's [runbook guide](https://github.com/DeepAgentLabs/agenticops-control-tower/blob/v0.9.0/docs/runbooks.md) for definitions, step outcomes,
authorization, request bodies and limits, and its
[standalone walkthrough](https://github.com/DeepAgentLabs/agenticops-control-tower/blob/v0.9.0/examples/runbook_recovery.py) for recovery,
compensation and escalation without optional siblings.

---

## Source declarations: src/agenticlens/__init__.py

Source: [src/agenticlens/__init__.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/__init__.py)

```python
__all__ = ['Run', 'RunStatus', 'Span', 'SpanHandle', 'SpanType', 'StepHandle', '__version__', 'profile', 'step', 'trace']
```

---

## Source declarations: src/agenticlens/adapters/__init__.py

Source: [src/agenticlens/adapters/__init__.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/adapters/__init__.py)

```python
__all__ = ['load_otlp_export', 'parse_otlp_payload', 'safe_trace_filename']
```

---

## Source declarations: src/agenticlens/adapters/otlp.py

Source: [src/agenticlens/adapters/otlp.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/adapters/otlp.py)

```python
def safe_trace_filename(trace_id: str) -> str: ...
def load_otlp_export(path: Path) -> list[Run]: ...
def parse_otlp_payload(payload: dict[str, Any]) -> list[Run]: ...
```

---

## Source declarations: src/agenticlens/analysis/__init__.py

Source: [src/agenticlens/analysis/__init__.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/analysis/__init__.py)

```python
__all__ = ['analyze_trace', 'next_best_analyses']
```

---

## Source declarations: src/agenticlens/analysis/handoffs.py

Source: [src/agenticlens/analysis/handoffs.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/analysis/handoffs.py)

```python
def count_round_trips(transitions: Sequence[tuple[str, str]]) -> int: ...
```

---

## Source declarations: src/agenticlens/analysis/next_steps.py

Source: [src/agenticlens/analysis/next_steps.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/analysis/next_steps.py)

```python
def next_best_analyses(findings: list[Finding]) -> list[str]: ...
```

---

## Source declarations: src/agenticlens/analysis/trace.py

Source: [src/agenticlens/analysis/trace.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/analysis/trace.py)

```python
def memory_tokens(run: Run) -> int: ...
def memory_share(run: Run) -> float: ...
def retry_tokens(run: Run) -> int: ...
def retry_latency_ms(run: Run) -> float: ...
def retry_cost_usd(run: Run) -> float: ...
def retry_token_share(run: Run) -> float: ...
def retry_latency_share(run: Run) -> float: ...
def retry_attribution(run: Run) -> dict[str, dict[str, str | None]]: ...
def classify_retry_outcomes(run: Run) -> dict[str, int]: ...
def duplicated_context_groups(run: Run) -> list[list[str]]: ...
def analyze_trace(run: Run, *, memory_share_threshold: float=0.5, retry_share_threshold: float=0.2, duplicated_context_threshold: int=2) -> list[Finding]: ...
```

---

## Source declarations: src/agenticlens/analyzers/__init__.py

Source: [src/agenticlens/analyzers/__init__.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/analyzers/__init__.py)

```python
__all__ = ['BaseAnalyzer']
```

---

## Source declarations: src/agenticlens/analyzers/base.py

Source: [src/agenticlens/analyzers/base.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/analyzers/base.py)

```python
class BaseAnalyzer(ABC):
    @abstractmethod
    def analyze(self, workflow: Workflow) -> dict[str, Any]: ...
```

---

## Source declarations: src/agenticlens/api/__init__.py

Source: [src/agenticlens/api/__init__.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/api/__init__.py)

```python
__all__ = ['LiveTraceStore']
```

---

## Source declarations: src/agenticlens/api/http.py

Source: [src/agenticlens/api/http.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/api/http.py)

```python
def create_app(store: TraceStore | None=None, *, save_dir: Path | None=None) -> FastAPI: ...
```

---

## Source declarations: src/agenticlens/api/store.py

Source: [src/agenticlens/api/store.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/api/store.py)

```python
class TraceStore(Protocol):
    def add(self, run: Run) -> None: ...
    def list_recent(self, limit: int | None=None) -> list[Run]: ...
    def get(self, trace_id: str) -> Run | None: ...
class LiveTraceStore():
    def __init__(self, max_traces: int=_DEFAULT_MAX_TRACES) -> None: ...
    def add(self, run: Run) -> None: ...
    def list_recent(self, limit: int | None=None) -> list[Run]: ...
    def get(self, trace_id: str) -> Run | None: ...
class PersistentTraceStore():
    def __init__(self, db_path: Path, max_traces: int | None=None) -> None: ...
    def add(self, run: Run) -> None: ...
    def list_recent(self, limit: int | None=None) -> list[Run]: ...
    def get(self, trace_id: str) -> Run | None: ...
```

---

## Source declarations: src/agenticlens/cli/integrity.py

Source: [src/agenticlens/cli/integrity.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/cli/integrity.py)

```python
@integrity_app.command('verify')
def verify_command(records: Path, manifest: Path, stream_id: str=typer.Option(..., help='Expected stream from trusted caller context.'), key_file: Path=typer.Option(..., help='JSON mapping of trusted key IDs to hex keys.')) -> None: ...
@integrity_app.command('export')
def export_command(run: Path, records: Path, output: Path, key_id: str=typer.Option(...), key_file: Path=typer.Option(...), complete: bool=typer.Option(False, help='Declare supplied capture complete explicitly.')) -> None: ...
@integrity_app.command('replay')
def replay_command(bundle: Path, run_id: str=typer.Option(...), key_file: Path=typer.Option(...)) -> None: ...
```

---

## Source declarations: src/agenticlens/cli/main.py

Source: [src/agenticlens/cli/main.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/cli/main.py)

```python
@app.command()
def profile(script: Path=typer.Argument(..., help='Path to a Python script to profile.'), save: Path | None=typer.Option(None, '--save', help='Export the profiled workflow to this file after running.'), export_format: str=typer.Option('json', '--format', help="Export format for --save: 'json' or 'csv'.")) -> None: ...
@app.command()
def report(report_file: Path=typer.Argument(..., help='Path to a saved workflow report (JSON).')) -> None: ...
@app.command()
def analyze(workflow_file: Path=typer.Argument(..., help='Path to a saved workflow (JSON).'), html: Path | None=typer.Option(None, '--html', help='Also render a standalone HTML dashboard (cost + findings).')) -> None: ...
@app.command('inspect')
def inspect_run(run_file: Path=typer.Argument(..., help='Path to a saved AgenticLens trace (JSON).'), save: Path | None=typer.Option(None, '--save', help='Save a Markdown trace report.'), html: Path | None=typer.Option(None, '--html', help='Also render a standalone HTML dashboard (agent timeline).')) -> None: ...
@app.command()
def validate(artifact_file: Path=typer.Argument(..., help='AIOS artifact JSON, routed by its declared marker.'), version: str | None=typer.Option(None, '--version', help='AI Operations Specification version to validate against.'), spec_root: Path | None=typer.Option(None, '--spec-root', help='Path to the ai-operations-spec repository root.'), save: Path | None=typer.Option(None, '--save', help='Save the machine-readable validation report.')) -> None: ...
@app.command()
def conformance(artifact_file: Path | None=typer.Argument(None, help='AIOS workflow or run artifact JSON.'), version: str | None=typer.Option(None, '--version', help='Optional version assertion; otherwise use the artifact declared marker.'), spec_root: Path | None=typer.Option(None, '--spec-root', help='Path to the ai-operations-spec repository root.'), save: Path | None=typer.Option(None, '--save', help='Save the machine-readable conformance report.'), as_json: bool=typer.Option(False, '--json', help='Print the structured report as JSON instead of tables.'), list_versions: bool=typer.Option(False, '--list-versions', help='List supported AIOS versions and whether schemas are found.')) -> None: ...
@app.command()
def compare(baseline: Path=typer.Argument(..., help='Baseline trace JSON file or directory.'), candidate: Path=typer.Argument(..., help='Candidate trace JSON file or directory.'), threshold: float=typer.Option(0.05, '--regression-threshold', min=0.0, help='Relative degradation that counts as a regression.'), save: Path | None=typer.Option(None, '--save', help='Save the comparison report.'), export_format: str=typer.Option('json', '--format', help="'json', 'csv', or 'md'."), fail_on_regression: bool=typer.Option(False, '--fail-on-regression', help='Return a non-zero exit status when regressions are detected.'), min_samples: int | None=typer.Option(None, '--min-samples', min=1, help='Require at least this many runs in both baseline and candidate cohorts. Returns a non-zero exit status when the comparison is under-sampled.'), html: Path | None=typer.Option(None, '--html', help='Also render a standalone HTML dashboard (comparison strip).')) -> None: ...
@app.command('import-otlp')
def import_otlp(source: Path=typer.Argument(..., help='OTLP/HTTP JSON export file, or a directory of them.'), save_dir: Path | None=typer.Option(None, '--save-dir', help='Write one <trace_id>.json AgenticLens run file per trace here.')) -> None: ...
@app.command('serve-otlp')
def serve_otlp(host: str=typer.Option('127.0.0.1', '--host', help='Bind address. Stays localhost by default: this endpoint has no built-in auth.'), port: int=typer.Option(4318, '--port', help="OTLP/HTTP's conventional port."), save_dir: Path | None=typer.Option(None, '--save-dir', help='Also persist every received trace as <trace_id>.json here.'), max_traces: int=typer.Option(200, '--max-traces', min=1, help='Most recent in-memory traces kept before evicting.'), db: Path | None=typer.Option(None, '--db', help='Persist traces to a SQLite file here instead of memory-only. Traces survive a restart; view them anytime with `agenticlens history`.'), max_persisted: int | None=typer.Option(None, '--max-persisted', min=1, help='Cap on traces kept in --db before evicting the oldest. Unbounded by default.')) -> None: ...
@app.command('history')
def history(source: Path=typer.Argument(..., help='A `--db` SQLite file, or a directory/file of AgenticLens run JSON.'), save: Path | None=typer.Option(None, '--save', help='Write the rendered HTML history page here.')) -> None: ...
@app.command()
def evaluate(suite_file: Path=typer.Argument(..., help='YAML or JSON evaluation suite.'), samples_file: Path=typer.Argument(..., help='YAML or JSON outputs and traces.'), save: Path=typer.Option(Path('agenticlens-evaluation.json'), '--save', help='Save the machine-readable evaluation report.'), html: Path | None=typer.Option(None, '--html', help='Also create a standalone HTML report.'), audit: Path | None=typer.Option(None, '--audit', help='Save an evidence audit (evaluator versions, trace evidence, cost coverage).'), strict_evidence: bool=typer.Option(False, '--strict-evidence', help='Exit with code 3 when the evidence audit finds blocking issues.'), score_analysis: Path | None=typer.Option(None, '--score-analysis', help='Save deterministic vs model-based scores, judge cost, and evaluator disagreement.')) -> None: ...
@dataset_app.command('summary')
def dataset_summary(dataset_file: Path=typer.Argument(..., help='Evaluation dataset JSON or YAML.')) -> None: ...
@dataset_app.command('split')
def dataset_split(dataset_file: Path=typer.Argument(..., help='Evaluation dataset JSON or YAML.'), save: Path=typer.Option(..., '--save', help='Save the updated dataset JSON file.'), train_ratio: float=typer.Option(0.7, min=0.0, max=1.0), validation_ratio: float=typer.Option(0.15, min=0.0, max=1.0), test_ratio: float=typer.Option(0.15, min=0.0, max=1.0), seed: int=typer.Option(0, help='Random seed used for deterministic split assignment.')) -> None: ...
@dataset_app.command('export-samples')
def dataset_export_samples(dataset_file: Path=typer.Argument(..., help='Evaluation dataset JSON or YAML.'), save: Path=typer.Option(..., '--save', help='Save a samples JSON file.'), split: str | None=typer.Option(None, '--split', help='Optional split filter: train, validation, or test.')) -> None: ...
@app.command('evaluate-live')
def evaluate_live(suite_file: Path=typer.Argument(..., help='YAML or JSON evaluation suite.'), target_kind: str=typer.Option(..., '--target-kind', help="'python' or 'http'."), target: str=typer.Option(..., '--target', help='Python target as module:function or HTTP target as a URL.'), save: Path=typer.Option(Path('agenticlens-evaluation-live.json'), '--save', help='Save the machine-readable evaluation report.'), max_workers: int=typer.Option(1, '--max-workers', min=1, help='Call the target for this many cases at once (only for concurrency-safe targets).'), html: Path | None=typer.Option(None, '--html', help='Also create an HTML report.')) -> None: ...
@experiment_app.command('run')
def experiment_run(manifest_file: Path=typer.Argument(..., help='Experiment manifest JSON or YAML.'), suite_file: Path=typer.Argument(..., help='YAML or JSON evaluation suite.'), save: Path=typer.Option(Path('agenticlens-experiment.json'), '--save', help='Save the machine-readable experiment report.'), confidence_level: float=typer.Option(0.95, '--confidence-level', min=0.5, max=0.999), regression_threshold: float=typer.Option(0.05, '--regression-threshold', min=0.0, help='Relative degradation threshold for baseline deltas.'), html: Path | None=typer.Option(None, '--html', help='Also save an HTML report.'), csv_path: Path | None=typer.Option(None, '--csv', help='Also save a per-variant summary CSV.'), cases_csv: Path | None=typer.Option(None, '--cases-csv', help='Also save a per-variant, per-case matrix CSV.')) -> None: ...
@experiment_app.command('report')
def experiment_report(report_file: Path=typer.Argument(..., help='Saved experiment report JSON.'), html: Path | None=typer.Option(None, '--html', help='Save an HTML report.'), csv_path: Path | None=typer.Option(None, '--csv', help='Save a per-variant summary CSV.'), cases_csv: Path | None=typer.Option(None, '--cases-csv', help='Save a per-variant, per-case matrix CSV.')) -> None: ...
@app.command()
def gate(report_file: Path=typer.Argument(..., help='AgenticLens evaluation report JSON.'), min_pass_rate: float=typer.Option(1.0, min=0.0, max=1.0), min_average_score: float=typer.Option(1.0, min=0.0, max=1.0), max_failed_cases: int=typer.Option(0, min=0), max_average_latency_ms: float | None=typer.Option(None, min=0.0), max_total_cost_usd: float | None=typer.Option(None, min=0.0), notify_webhook: str | None=typer.Option(None, '--notify-webhook', envvar='AGENTICLENS_GATE_WEBHOOK', help='POST an alert to this http(s) webhook when the gate fails.'), notify_format: str=typer.Option('generic', '--notify-format', help='Webhook payload: generic, slack, or teams.'), cooldown_minutes: float=typer.Option(60.0, '--cooldown-minutes', min=0.0, help='Suppress repeat alerts for the same breached threshold for this long.'), notify_state: Path=typer.Option(Path('.agenticlens/gate-notifications.json'), '--notify-state', help='JSON file recording when each threshold last alerted.')) -> None: ...
@app.command()
def dashboard(workflow_file: Path | None=typer.Option(None, '--workflow', help='Saved workflow JSON (from `profile --save`).'), run_file: Path | None=typer.Option(None, '--run', help='Saved run trace JSON (from the trace API).'), evaluation_file: Path | None=typer.Option(None, '--evaluation', help='Saved evaluation report JSON (from `evaluate --save`).'), comparison_file: Path | None=typer.Option(None, '--comparison', help='Saved comparison report JSON (from `compare --save --format json`).'), min_pass_rate: float=typer.Option(1.0, min=0.0, max=1.0), min_average_score: float=typer.Option(1.0, min=0.0, max=1.0), max_failed_cases: int=typer.Option(0, min=0), max_average_latency_ms: float | None=typer.Option(None, min=0.0), max_total_cost_usd: float | None=typer.Option(None, min=0.0), save: Path=typer.Option(Path('agenticlens-dashboard.html'), '--save')) -> None: ...
@app.command('calibrate')
def calibrate(report_file: Path=typer.Argument(..., help='Saved evaluation report JSON.'), labels_file: Path=typer.Argument(..., help='Versioned reference labels JSON.'), evaluator: str=typer.Option(..., '--evaluator', help='Exact llm_judge score name.'), save: Path=typer.Option(Path('agenticlens-calibration.json'), '--save'), tune_threshold: Path | None=typer.Option(None, '--tune-threshold', help='Also sweep pass thresholds and save the tuning report to this path.')) -> None: ...
@app.command()
def diagnose(run_file: Path=typer.Argument(..., help='Saved AgenticLens trace (JSON).'), baseline: list[Path]=typer.Option([], '--baseline', help='Baseline trace file or directory for anomaly detection (repeatable).'), save: Path | None=typer.Option(None, '--save', help='Save the diagnosis report JSON.'), markdown: Path | None=typer.Option(None, '--markdown', help='Also save the investigation narrative as Markdown.'), max_cost_usd: float | None=typer.Option(None, '--max-cost-usd', min=0), max_tokens: int | None=typer.Option(None, '--max-tokens', min=1), max_latency_ms: float | None=typer.Option(None, '--max-latency-ms', min=0), loop_threshold: int=typer.Option(3, '--loop-threshold', min=2), max_spans: int=typer.Option(10000, '--max-spans', min=1, help='Analysis span cap.'), max_depth: int=typer.Option(64, '--max-depth', min=1, help='Span-tree depth cap.'), fail_on_unrecovered: bool=typer.Option(False, '--fail-on-unrecovered', help='Exit with code 4 when an unrecovered failure is diagnosed.')) -> None: ...
@app.command()
def explain(artifact_file: Path=typer.Argument(..., help='A saved trace, workflow, or diagnosis report (JSON).'), save: Path | None=typer.Option(None, '--save', help='Save the narrative as Markdown.')) -> None: ...
@trace_app.command('show')
def trace_show(run_file: Path=typer.Argument(..., help='Saved AgenticLens trace (JSON).'), span: str | None=typer.Option(None, '--span', help="Show one span's full record.")) -> None: ...
@trace_app.command('timeline')
def trace_timeline(run_file: Path=typer.Argument(..., help='Saved AgenticLens trace (JSON).'), save: Path | None=typer.Option(None, '--save', help='Save the timeline JSON.')) -> None: ...
@app.command('attribution-accuracy')
def attribution_accuracy(cases_path: Path=typer.Argument(..., help='Directory or JSON file of controlled-failure traces.'), save: Path | None=typer.Option(None, '--save', help='Save the accuracy report JSON.'), min_step_accuracy: float | None=typer.Option(None, '--min-step-accuracy', min=0, max=1, help='Exit with code 5 when top-1 faulty-step accuracy is below this value.')) -> None: ...
```

---

## Source declarations: src/agenticlens/cli/modelfit.py

Source: [src/agenticlens/cli/modelfit.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/cli/modelfit.py)

```python
@modelfit_app.command('recommend')
def modelfit_recommend(reports: list[Path]=typer.Argument(..., help='Experiment report JSON files (experiment run --save).'), config_path: Path | None=typer.Option(None, '--config', help='ModelFit config (YAML or JSON).'), manifests: list[Path]=typer.Option([], '--manifest', help='Experiment manifests whose variant metadata names provider/deployment.'), save: Path | None=typer.Option(None, '--save', help='Write the ModelFit report JSON.'), markdown: Path | None=typer.Option(None, '--markdown', help='Write a Markdown report.'), matrix_csv: Path | None=typer.Option(None, '--csv', help='Write the task-level model matrix as CSV.'), json_output: bool=typer.Option(False, '--json', help='Print the report as JSON.'), fail_on_unfit: bool=typer.Option(False, '--fail-on-unfit', help='Exit 8 when a category has no feasible candidate.'), fail_on_low_confidence: bool=typer.Option(False, '--fail-on-low-confidence', help='Exit 8 when a recommendation is low confidence.')) -> None: ...
@modelfit_app.command('matrix')
def modelfit_matrix(report_path: Path=typer.Argument(..., help='ModelFit report JSON (modelfit recommend --save).'), matrix_csv: Path | None=typer.Option(None, '--csv', help='Write the matrix as CSV.'), markdown: Path | None=typer.Option(None, '--markdown', help='Write the Markdown report.')) -> None: ...
@modelfit_app.command('taxonomy')
def modelfit_taxonomy(reports: list[Path]=typer.Argument(..., help='Experiment report JSON files.'), config_path: Path | None=typer.Option(None, '--config', help='ModelFit config (YAML or JSON).'), json_output: bool=typer.Option(False, '--json', help='Print categories as JSON.')) -> None: ...
```

---

## Source declarations: src/agenticlens/cli/optimize.py

Source: [src/agenticlens/cli/optimize.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/cli/optimize.py)

```python
@optimize_app.command('analyze')
def analyze(traces: list[Path]=typer.Argument(..., help='Trace JSON files or directories of them.'), config: Path | None=typer.Option(None, '--config', help='Thresholds (YAML or JSON).'), baseline_variant: str | None=typer.Option(None, '--baseline-variant', help='Variant to compare trade-offs against.'), ledger: Path | None=typer.Option(None, '--ledger', help='Show decision statuses.'), save: Path | None=typer.Option(None, '--save', help='Write the report JSON.'), markdown: Path | None=typer.Option(None, '--markdown', help='Write a Markdown report.')) -> None: ...
@optimize_app.command('decide')
def decide(report_file: Path=typer.Argument(..., help='Saved optimization report JSON.'), opportunity_id: str=typer.Argument(...), status: str=typer.Option(..., '--status', help='accepted, rejected, adopted, or reverted.'), decided_by: str=typer.Option(..., '--by', help='Person or process deciding.'), ledger: Path=typer.Option(..., '--ledger', help='Append-only JSONL decision ledger.'), reason: str=typer.Option('', '--reason'), change: str | None=typer.Option(None, '--change', help='PR, commit, or config version.')) -> None: ...
@optimize_app.command('status')
def status_command(report_file: Path=typer.Argument(..., help='Saved optimization report JSON.'), ledger: Path=typer.Option(..., '--ledger')) -> None: ...
@optimize_app.command('outcome')
def outcome(report_file: Path=typer.Argument(..., help='Saved optimization report JSON.'), opportunity_id: str=typer.Argument(...), before: list[Path]=typer.Option(..., '--before', help='Traces before adoption.'), after: list[Path]=typer.Option(..., '--after', help='Traces after adoption.'), ledger: Path | None=typer.Option(None, '--ledger'), min_runs: int=typer.Option(3, '--min-runs', min=1), save: Path | None=typer.Option(None, '--save'), markdown: Path | None=typer.Option(None, '--markdown'), fail_on_regression: bool=typer.Option(False, '--fail-on-regression', help=f'Exit {REGRESSION_EXIT} if quality regressed.')) -> None: ...
```

---

## Source declarations: src/agenticlens/cli/render.py

Source: [src/agenticlens/cli/render.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/cli/render.py)

```python
def render_summary(console: Console, workflow: Workflow) -> None: ...
def render_steps(console: Console, workflow: Workflow) -> None: ...
def render_recommendations(console: Console, recommendations: list[Recommendation], estimated_savings_pct: float, workflow: Workflow | None=None, cost_savings: float | None=None) -> None: ...
def render_token_optimization(console: Console, workflow: Workflow, recommendations: list[Recommendation]) -> None: ...
def render_agent_summary(console: Console, workflow: Workflow) -> None: ...
```

---

## Source declarations: src/agenticlens/cli/render_diagnosis.py

Source: [src/agenticlens/cli/render_diagnosis.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/cli/render_diagnosis.py)

```python
def render_diagnosis(console: Console, report: DiagnosisReport) -> None: ...
def render_timeline(console: Console, timeline: IncidentTimeline) -> None: ...
def render_score_analysis(console: Console, analysis: ScoreAnalysis) -> None: ...
def render_accuracy(console: Console, report: AttributionAccuracyReport) -> None: ...
```

---

## Source declarations: src/agenticlens/cli/routing.py

Source: [src/agenticlens/cli/routing.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/cli/routing.py)

```python
@routing_app.command('decide')
def decide(report: Path=typer.Argument(..., help='Saved ModelFit report JSON.'), category: str=typer.Option(..., '--category'), request_id: str=typer.Option(..., '--request-id', help='Opaque allocation/correlation ID.'), policy: Path | None=typer.Option(None, '--policy', help='RoutingPolicy JSON.'), save: Path | None=typer.Option(None, '--save'), audit: Path | None=typer.Option(None, '--audit', help='Append local JSONL audit records.')) -> None: ...
@routing_app.command('summary')
def summary(results: list[Path]=typer.Argument(..., help='RoutingResult JSON files from Router.run.'), save: Path | None=typer.Option(None, '--save')) -> None: ...
```

---

## Source declarations: src/agenticlens/cli/suite.py

Source: [src/agenticlens/cli/suite.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/cli/suite.py)

```python
@suite_app.command('summary')
def suite_summary(suite_file: Path=typer.Argument(..., help='Suite JSON or YAML.'), json_output: bool=typer.Option(False, '--json', help='Print the summary as JSON.')) -> None: ...
@suite_app.command('import')
def suite_import(source: Path=typer.Argument(..., help='CSV, JSON, JSON Lines, or YAML cases.'), save: Path=typer.Option(..., '--save', help='Suite file to write (.json, .yaml).'), name: str | None=typer.Option(None, '--name', help='Suite name (new suites).'), version: str | None=typer.Option(None, '--version', help='Suite version (new suites).'), into: Path | None=_INTO_OPTION, mask: bool=_MASK_OPTION, strategy: str=_STRATEGY_OPTION, salt: str=_SALT_OPTION) -> None: ...
@suite_app.command('from-traces')
def suite_from_traces(traces: list[Path]=typer.Argument(..., help='Trace JSON files or directories of them.'), save: Path=typer.Option(..., '--save', help='Suite file to write.'), name: str | None=typer.Option(None, '--name'), version: str | None=typer.Option(None, '--version'), into: Path | None=_INTO_OPTION, latency_margin: float=typer.Option(1.5, '--latency-margin', min=1.0, help='max_latency_ms = observed x margin.'), cost_margin: float=typer.Option(1.5, '--cost-margin', min=1.0, help='max_cost_usd = observed x margin.'), include_output: bool=typer.Option(False, '--include-output', help='Also expect the recorded output exactly.'), mask: bool=_MASK_OPTION, strategy: str=_STRATEGY_OPTION, salt: str=_SALT_OPTION) -> None: ...
@suite_app.command('from-feedback')
def suite_from_feedback(feedback: Path=typer.Argument(..., help='Feedback JSON, JSON Lines, or YAML.'), save: Path=typer.Option(..., '--save', help='Suite file to write.'), name: str | None=typer.Option(None, '--name'), version: str | None=typer.Option(None, '--version'), into: Path | None=_INTO_OPTION, traces: list[Path]=typer.Option([], '--traces', help='Traces that feedback refers to (fills a missing input).'), mask: bool=_MASK_OPTION, strategy: str=_STRATEGY_OPTION, salt: str=_SALT_OPTION) -> None: ...
@suite_app.command('add-case')
def suite_add_case(suite_file: Path=typer.Argument(..., help='Suite to edit.'), case_id: str=typer.Option(..., '--id'), name: str | None=typer.Option(None, '--name'), input_value: str | None=typer.Option(None, '--input', help='Text, or a JSON object.'), expected_output: str | None=typer.Option(None, '--expected-output'), contains: list[str]=typer.Option([], '--contains', help='Repeatable expected substring.'), required_tools: list[str]=typer.Option([], '--required-tool'), forbidden_tools: list[str]=typer.Option([], '--forbidden-tool'), max_latency_ms: float | None=typer.Option(None, '--max-latency-ms'), max_cost_usd: float | None=typer.Option(None, '--max-cost-usd'), tags: list[str]=typer.Option([], '--tag'), domain: str | None=typer.Option(None, '--domain'), save: Path | None=typer.Option(None, '--save', help='Write here instead of in place.')) -> None: ...
@suite_app.command('remove-case')
def suite_remove_case(suite_file: Path=typer.Argument(..., help='Suite to edit.'), case_ids: list[str]=typer.Argument(..., help='Case IDs to remove.'), save: Path | None=typer.Option(None, '--save')) -> None: ...
@suite_app.command('tag')
def suite_tag(suite_file: Path=typer.Argument(..., help='Suite to edit.'), case_ids: list[str]=typer.Option([], '--case', help='Repeatable; all cases when omitted.'), add: list[str]=typer.Option([], '--add', help='Tag to add (repeatable).'), remove: list[str]=typer.Option([], '--remove', help='Tag to remove (repeatable).'), domain: str | None=typer.Option(None, '--domain', help='Domain category to set.'), save: Path | None=typer.Option(None, '--save')) -> None: ...
@suite_app.command('review')
def suite_review(suite_file: Path=typer.Argument(..., help='Suite to edit.'), status: str=typer.Option(..., '--status', help='accepted, rejected, or needs_review.'), reviewer: str=typer.Option(..., '--reviewer'), case_ids: list[str]=typer.Option([], '--case', help='Repeatable; all cases when omitted.'), notes: str=typer.Option('', '--notes'), save: Path | None=typer.Option(None, '--save')) -> None: ...
@suite_app.command('mask')
def suite_mask(suite_file: Path=typer.Argument(..., help='Suite to mask.'), strategy: str=_STRATEGY_OPTION, salt: str=_SALT_OPTION, check: bool=typer.Option(False, '--check', help='Only scan; exit 7 when unmasked PII is found.'), report: Path | None=typer.Option(None, '--report', help='Save the masking report JSON.'), save: Path | None=typer.Option(None, '--save')) -> None: ...
@suite_app.command('dedupe')
def suite_dedupe(suite_file: Path=typer.Argument(..., help='Suite to check.'), threshold: float=typer.Option(0.85, '--threshold', min=0.01, max=1.0, help='Near-duplicate Jaccard threshold.'), include_variants: bool=typer.Option(False, '--include-variants', help='Also compare variants of the same original.'), drop: bool=typer.Option(False, '--drop', help='Remove duplicates, keeping the first.'), report: Path | None=typer.Option(None, '--report', help='Save the duplicate report JSON.'), save: Path | None=typer.Option(None, '--save')) -> None: ...
@suite_app.command('vary')
def suite_vary(suite_file: Path=typer.Argument(..., help='Suite to extend.'), per_case: int=typer.Option(2, '--per-case', min=1, help='Variants per original case.'), kinds: list[str]=typer.Option([], '--kind', help=f'Repeatable; default all: {', '.join(VARIATIONS)}.'), seed: int=typer.Option(0, '--seed'), save: Path | None=typer.Option(None, '--save')) -> None: ...
@suite_app.command('split')
def suite_split(suite_file: Path=typer.Argument(..., help='Suite to split.'), train_ratio: float=typer.Option(0.7, '--train', min=0.0, max=1.0), validation_ratio: float=typer.Option(0.15, '--validation', min=0.0, max=1.0), test_ratio: float=typer.Option(0.15, '--test', min=0.0, max=1.0), seed: int=typer.Option(0, '--seed'), overwrite: bool=typer.Option(False, '--overwrite', help='Reassign existing splits too.'), save: Path | None=typer.Option(None, '--save')) -> None: ...
@suite_app.command('filter')
def suite_filter(suite_file: Path=typer.Argument(..., help='Suite to filter.'), save: Path=typer.Option(..., '--save'), tags: list[str]=typer.Option([], '--tag', help='Keep cases with any of these tags.'), exclude_tags: list[str]=typer.Option([], '--exclude-tag'), domains: list[str]=typer.Option([], '--domain'), splits: list[str]=typer.Option([], '--split')) -> None: ...
@suite_app.command('approve')
def suite_approve(suite_file: Path=typer.Argument(..., help='Draft suite to approve.'), store: Path=typer.Option(..., '--store', help='Suite store directory.'), approver: str=typer.Option(..., '--approver', help='Who is approving this version.'), notes: str=typer.Option('', '--notes'), parent_version: str | None=typer.Option(None, '--parent-version', help='Approved version this one supersedes.'), allow_unreviewed: bool=typer.Option(False, '--allow-unreviewed', help='Approve cases still marked needs_review.'), allow_pii: bool=typer.Option(False, '--allow-pii', help='Approve unmasked PII as-is.')) -> None: ...
@suite_app.command('versions')
def suite_versions(store: Path=typer.Option(..., '--store', help='Suite store directory.'), name: str | None=typer.Option(None, '--name', help='Only this suite.')) -> None: ...
@suite_app.command('verify')
def suite_verify(refs: list[str]=typer.Argument(None, help='NAME@VERSION refs; all versions when omitted.'), store: Path=typer.Option(..., '--store', help='Suite store directory.'), json_output: bool=typer.Option(False, '--json', help='Print results as JSON.')) -> None: ...
@suite_app.command('export')
def suite_export(ref: str=typer.Argument(..., help='NAME@VERSION of an approved suite.'), store: Path=typer.Option(..., '--store', help='Suite store directory.'), save: Path=typer.Option(..., '--save', help='Suite file for evaluate/evaluate-live.'), tags: list[str]=typer.Option([], '--tag'), exclude_tags: list[str]=typer.Option([], '--exclude-tag'), domains: list[str]=typer.Option([], '--domain'), splits: list[str]=typer.Option([], '--split')) -> None: ...
@suite_app.command('diff')
def suite_diff(old: str=typer.Argument(..., help='Suite file, or NAME@VERSION with --store.'), new: str=typer.Argument(..., help='Suite file, or NAME@VERSION with --store.'), store: Path | None=typer.Option(None, '--store'), json_output: bool=typer.Option(False, '--json')) -> None: ...
```

---

## Source declarations: src/agenticlens/comparison/__init__.py

Source: [src/agenticlens/comparison/__init__.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/comparison/__init__.py)

```python
__all__ = ['ComparisonReport', 'RunGroupSummary', 'compare_runs', 'export_comparison_csv', 'export_comparison_json', 'export_comparison_markdown', 'load_runs', 'render_comparison_markdown']
```

---

## Source declarations: src/agenticlens/comparison/export.py

Source: [src/agenticlens/comparison/export.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/comparison/export.py)

```python
def export_comparison_json(report: ComparisonReport, path: Path) -> None: ...
def export_comparison_csv(report: ComparisonReport, path: Path) -> None: ...
def export_comparison_markdown(report: ComparisonReport, path: Path) -> None: ...
```

---

## Source declarations: src/agenticlens/comparison/markdown.py

Source: [src/agenticlens/comparison/markdown.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/comparison/markdown.py)

```python
def render_comparison_markdown(report: ComparisonReport) -> str: ...
```

---

## Source declarations: src/agenticlens/comparison/models.py

Source: [src/agenticlens/comparison/models.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/comparison/models.py)

```python
class MetricSummary(BaseModel):
    count: int = Field(ge=0)
    mean: float
    median: float
    p95: float
    standard_deviation: float
    coefficient_of_variation: float | None = None
class RunGroupSummary(BaseModel):
    label: str
    run_count: int
    success_rate: float
    tokens: MetricSummary
    latency_ms: MetricSummary
    cost_usd: MetricSummary | None = None
    cost_per_successful_task: float | None = None
class MetricDelta(BaseModel):
    absolute: float
    relative: float | None = None
    regressed: bool
class ComparisonReport(BaseModel):
    schema_version: str = '1.0'
    baseline: RunGroupSummary
    candidate: RunGroupSummary
    success_rate_delta: MetricDelta
    mean_tokens_delta: MetricDelta
    mean_latency_ms_delta: MetricDelta
    mean_cost_usd_delta: MetricDelta | None = None
    regression_threshold: float
    regressions: list[str] = Field(default_factory=list)
    minimum_sample_size: int = 5
    sample_size_guidance: str | None = None
```

---

## Source declarations: src/agenticlens/comparison/runner.py

Source: [src/agenticlens/comparison/runner.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/comparison/runner.py)

```python
def load_runs(path: Path) -> list[Run]: ...
def summarize_runs(label: str, runs: list[Run]) -> RunGroupSummary: ...
def compare_runs(baseline_runs: list[Run], candidate_runs: list[Run], *, baseline_label: str='baseline', candidate_label: str='candidate', regression_threshold: float=0.05) -> ComparisonReport: ...
```

---

## Source declarations: src/agenticlens/comparison/stats.py

Source: [src/agenticlens/comparison/stats.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/comparison/stats.py)

```python
def percentile(values: list[float], percentile_value: float) -> float: ...
def metric_delta(baseline: float, candidate: float, threshold: float, *, lower_is_better: bool) -> MetricDelta: ...
```

---

## Source declarations: src/agenticlens/config/__init__.py

Source: [src/agenticlens/config/__init__.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/config/__init__.py)

```python
__all__ = ['LivePricingConfig', 'ModelPricing', 'RecommenderConfig', 'AgenticLensConfig', 'UnknownModelPricingWarning', 'calculate_cost', 'load_config', 'resolve_live_pricing', 'resolve_pricing']
```

---

## Source declarations: src/agenticlens/config/live_pricing.py

Source: [src/agenticlens/config/live_pricing.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/config/live_pricing.py)

```python
class LivePricingConfig(BaseModel):
    enabled: bool = True
    url: str = LITELLM_PRICING_URL
    cache_path: str = str(DEFAULT_CACHE_PATH)
    ttl_seconds: float = Field(default=DEFAULT_TTL_SECONDS, gt=0)
    timeout_seconds: float = Field(default=DEFAULT_TIMEOUT_SECONDS, gt=0)
def parse_litellm_entry(entry: dict[str, Any]) -> ModelPricing | None: ...
def get_live_pricing_table(config: LivePricingConfig) -> dict[str, Any] | None: ...
def resolve_live_pricing(provider: str, model: str, config: LivePricingConfig) -> ModelPricing | None: ...
```

---

## Source declarations: src/agenticlens/config/pricing.py

Source: [src/agenticlens/config/pricing.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/config/pricing.py)

```python
class UnknownModelPricingWarning(UserWarning):
    ...
class ModelPricing(BaseModel):
    input_per_1k: float
    output_per_1k: float
def bundled_pricing_table() -> dict[str, ModelPricing]: ...
def resolve_pricing(provider: str, model: str, overrides: dict[str, ModelPricing] | None=None, live_pricing: 'LivePricingConfig | None'=None) -> ModelPricing | None: ...
def calculate_cost(provider: str, model: str, prompt_tokens: int, completion_tokens: int, overrides: dict[str, ModelPricing] | None=None, live_pricing: 'LivePricingConfig | None'=None) -> float | None: ...
```

---

## Source declarations: src/agenticlens/config/settings.py

Source: [src/agenticlens/config/settings.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/config/settings.py)

```python
class RecommenderConfig(BaseModel):
    system_prompt_prefix_tokens: int = 50
    max_chunks: int = 8
    history_token_limit: int = 4000
    monthly_runs: int = 1000
    warning_savings_pct: float = 5.0
    critical_savings_pct: float = 20.0
    warning_savings_usd: float = 0.005
    critical_savings_usd: float = 0.05
    rag_min_chunk_utility_score: float = 0.08
    rag_min_low_utility_chunks: int = 2
    handoff_token_limit: int = 3000
    model_swap_min_savings_pct: float = 15.0
    model_swap_providers: list[str] = Field(default_factory=lambda: list(DEFAULT_MODEL_SWAP_PROVIDERS))
class AgenticLensConfig(BaseModel):
    pricing_overrides: dict[str, ModelPricing] = Field(default_factory=dict)
    live_pricing: LivePricingConfig = Field(default_factory=LivePricingConfig)
    recommender: RecommenderConfig = Field(default_factory=RecommenderConfig)
def load_config(path: str | Path | None=None) -> AgenticLensConfig: ...
```

---

## Source declarations: src/agenticlens/diagnosis/__init__.py

Source: [src/agenticlens/diagnosis/__init__.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/diagnosis/__init__.py)

```python
__all__ = ['CHAOS_EVENT_ID_KEY', 'CHAOS_FAULT_TYPE_KEY', 'CHAOS_INJECTED_KEY', 'DEFAULT_RULES', 'DIAGNOSIS_SCHEMA_VERSION', 'ENGINE_VERSION', 'FAILURE_TAXONOMY', 'TAXONOMY_VERSION', 'AccuracyMetric', 'AnalysisBudget', 'AnalysisGuard', 'Anomaly', 'AnomalyReport', 'Attribution', 'AttributionAccuracyReport', 'AttributionCandidate', 'AttributionOutcome', 'CategoryInfo', 'ControlledFailure', 'Diagnosis', 'DiagnosisConfig', 'DiagnosisReport', 'DiagnosisRule', 'DiagnosisSummary', 'FailureCategory', 'GuardrailStatus', 'IncidentTimeline', 'TimelineEvent', 'TraceView', 'controlled_failure_from_run', 'describe', 'detect_anomalies', 'diagnose_run', 'evaluate_attribution', 'explain_recommendations', 'explain_run', 'failure_category', 'load_controlled_failures']
```

---

## Source declarations: src/agenticlens/diagnosis/accuracy.py

Source: [src/agenticlens/diagnosis/accuracy.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/diagnosis/accuracy.py)

```python
class ControlledFailure(BaseModel):
    case_id: str
    run: Run
    expected_span_id: str | None = None
    expected_span_name: str | None = None
    expected_agent: str | None = None
    expected_category: FailureCategory | None = None
    notes: str = ''
    @model_validator(mode='after')
    def require_expected_step(self) -> 'ControlledFailure': ...
def controlled_failure_from_run(run: Run, *, case_id: str | None=None) -> ControlledFailure: ...
def load_controlled_failures(path: Path) -> list[ControlledFailure]: ...
class AttributionOutcome(BaseModel):
    case_id: str
    expected_span: str
    predicted_span_id: str | None
    predicted_span_name: str | None
    predicted_agent: str | None
    predicted_category: FailureCategory | None
    confidence: float
    step_correct: bool
    top3_correct: bool
    agent_correct: bool | None = Field(default=None, description='None when the case names no expected agent.')
    category_correct: bool | None = Field(default=None, description='None when the case names no expected category.')
class AccuracyMetric(BaseModel):
    correct: int
    total: int
    accuracy: float | None
    interval: tuple[float, float] | None = Field(default=None, description="Wilson interval at the report's confidence level.")
class AttributionAccuracyReport(BaseModel):
    schema_version: str = ACCURACY_SCHEMA_VERSION
    total_cases: int
    confidence_level: float
    step: AccuracyMetric
    top3_step: AccuracyMetric
    agent: AccuracyMetric
    category: AccuracyMetric
    mean_confidence: float
    calibration_gap: float = Field(description='Mean attribution confidence minus top-1 step accuracy (positive = overconfident).')
    outcomes: list[AttributionOutcome]
    warnings: list[str] = Field(default_factory=list)
def evaluate_attribution(cases: Sequence[ControlledFailure], *, config: DiagnosisConfig | None=None, confidence_level: float=0.95) -> AttributionAccuracyReport: ...
```

---

## Source declarations: src/agenticlens/diagnosis/anomaly.py

Source: [src/agenticlens/diagnosis/anomaly.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/diagnosis/anomaly.py)

```python
def span_key(span: Span) -> str: ...
def detect_anomalies(run: Run, baseline: Sequence[Run], *, threshold: float=DEFAULT_THRESHOLD, min_baseline_samples: int=DEFAULT_MIN_BASELINE, constant_tolerance: float=DEFAULT_CONSTANT_TOLERANCE) -> AnomalyReport: ...
```

---

## Source declarations: src/agenticlens/diagnosis/attribution.py

Source: [src/agenticlens/diagnosis/attribution.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/diagnosis/attribution.py)

```python
def attribute(view: TraceView, diagnoses: list[Diagnosis]) -> Attribution: ...
```

---

## Source declarations: src/agenticlens/diagnosis/engine.py

Source: [src/agenticlens/diagnosis/engine.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/diagnosis/engine.py)

```python
def diagnose_run(run: Run, *, config: DiagnosisConfig | None=None, rules: Sequence[DiagnosisRule] | None=None, baseline: Sequence[Run] | None=None, budget: AnalysisBudget | None=None, anomaly_threshold: float=DEFAULT_THRESHOLD, min_baseline_samples: int=DEFAULT_MIN_BASELINE) -> DiagnosisReport: ...
```

---

## Source declarations: src/agenticlens/diagnosis/guardrails.py

Source: [src/agenticlens/diagnosis/guardrails.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/diagnosis/guardrails.py)

```python
class AnalysisBudget(BaseModel):
    max_spans: int | None = Field(default=10000, gt=0)
    max_depth: int | None = Field(default=64, gt=0, description='Span-tree recursion cap.')
    max_diagnoses: int | None = Field(default=500, gt=0)
    max_iterations: int | None = Field(default=None, gt=0)
    max_cost_usd: float | None = Field(default=None, ge=0)
    max_seconds: float | None = Field(default=None, gt=0)
    stagnation_limit: int | None = Field(default=3, gt=0, description='Stop after this many consecutive iterations that add nothing new.')
class AnalysisGuard():
    def __init__(self, budget: AnalysisBudget | None=None) -> None: ...
    @property
    def exhausted(self) -> bool: ...
    @property
    def stop_reasons(self) -> list[str]: ...
    @property
    def out_of_time(self) -> bool: ...
    def limit_spans(self, total: int) -> int: ...
    def allow_depth(self, depth: int) -> bool: ...
    def allow_diagnoses(self, count: int) -> int: ...
    def charge(self, *, cost_usd: float=0.0) -> None: ...
    def record(self, fingerprints: Iterable[str]) -> bool: ...
    def status(self) -> GuardrailStatus: ...
```

---

## Source declarations: src/agenticlens/diagnosis/models.py

Source: [src/agenticlens/diagnosis/models.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/diagnosis/models.py)

```python
class Diagnosis(BaseModel):
    diagnosis_id: str
    category: FailureCategory
    title: str
    summary: str
    severity: Severity
    confidence: float = Field(ge=0, le=1)
    rule_id: str
    rule_version: str
    origin_span_id: str | None = Field(default=None, description='Span where the failure started; None when no single span is responsible.')
    span_ids: list[str] = Field(default_factory=list, description='Every span that supports this diagnosis.')
    agent_name: str | None = None
    recovered: bool = Field(default=False, description='True when a later span of the same operation succeeded.')
    evidence: list[Evidence] = Field(default_factory=list)
class AttributionCandidate(BaseModel):
    span_id: str
    span_name: str
    span_type: str
    agent_name: str | None = None
    score: float = Field(ge=0, le=1, description='Share of total blame; candidates sum to 1.')
    categories: list[FailureCategory] = Field(default_factory=list)
    diagnosis_ids: list[str] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)
class Attribution(BaseModel):
    status: AttributionStatus
    faulty_span_id: str | None = None
    faulty_step: str | None = None
    faulty_agent: str | None = None
    category: FailureCategory | None = None
    confidence: float = Field(default=0.0, ge=0, le=1)
    explanation: str
    candidates: list[AttributionCandidate] = Field(default_factory=list)
    agent_scores: dict[str, float] = Field(default_factory=dict, description="Blame share per agent (spans with no agent: '(none)').")
class TimelineEvent(BaseModel):
    offset_ms: float = Field(description='Milliseconds since the run started.')
    timestamp: datetime
    kind: TimelineEventKind
    description: str
    span_id: str | None = None
    span_name: str | None = None
    agent_name: str | None = None
    is_root_cause: bool = False
class IncidentTimeline(BaseModel):
    run_id: str
    events: list[TimelineEvent] = Field(default_factory=list)
    first_failure_offset_ms: float | None = None
    root_cause_offset_ms: float | None = None
    recovered_span_ids: list[str] = Field(default_factory=list)
    truncated: bool = Field(default=False, description='True when max_events cut the timeline.')
class Anomaly(BaseModel):
    scope: Literal['run', 'span']
    key: str = Field(description="'run' or '<span_type>:<span name>'.")
    metric: Literal['latency_ms', 'total_tokens', 'cost_usd']
    observed: float
    baseline_median: float
    baseline_mad: float
    robust_z: float | None = Field(default=None, description='Modified z-score (MAD, or mean absolute deviation when MAD is 0); None when every baseline value is identical.')
    direction: Literal['high', 'low']
    baseline_samples: int
    span_ids: list[str] = Field(default_factory=list)
class AnomalyReport(BaseModel):
    method: str = 'robust_z_mad'
    threshold: float
    min_baseline_samples: int
    baseline_runs: int
    anomalies: list[Anomaly] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
class GuardrailStatus(BaseModel):
    truncated: bool = False
    stop_reasons: list[str] = Field(default_factory=list)
    spans_analyzed: int = 0
    spans_total: int = 0
    max_depth_seen: int = 0
    iterations: int = 0
    stagnant_iterations: int = 0
    cost_usd: float = 0.0
class RuleRef(BaseModel):
    rule_id: str
    version: str
class DiagnosisSummary(BaseModel):
    total_diagnoses: int = 0
    unrecovered: int = 0
    highest_severity: Severity | None = None
    categories: dict[str, int] = Field(default_factory=dict)
    failed_spans: int = 0
    wasted_tokens: int = Field(default=0, description='Tokens spent in failed and retry spans.')
    wasted_latency_ms: float = 0.0
    wasted_cost_usd: float | None = Field(default=None, description='None when any failed or retry span has no cost.')
class DiagnosisReport(BaseModel):
    schema_version: str = DIAGNOSIS_SCHEMA_VERSION
    taxonomy_version: str = TAXONOMY_VERSION
    engine_version: str
    run_id: str
    trace_id: str
    application_name: str
    run_status: str
    task_success: bool | None = None
    rules: list[RuleRef] = Field(default_factory=list)
    summary: DiagnosisSummary
    diagnoses: list[Diagnosis] = Field(default_factory=list)
    attribution: Attribution
    timeline: IncidentTimeline
    anomalies: AnomalyReport | None = None
    efficiency_findings: list[Finding] = Field(default_factory=list, description='Memory, retry, and duplicated-context findings from analyze_trace().')
    guardrails: GuardrailStatus = Field(default_factory=GuardrailStatus)
    limitations: list[str] = Field(default_factory=list)
```

---

## Source declarations: src/agenticlens/diagnosis/narrative.py

Source: [src/agenticlens/diagnosis/narrative.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/diagnosis/narrative.py)

```python
def explain_run(report: DiagnosisReport) -> str: ...
def explain_recommendations(workflow: Workflow, recommendations: Sequence[Recommendation]) -> str: ...
```

---

## Source declarations: src/agenticlens/diagnosis/rules.py

Source: [src/agenticlens/diagnosis/rules.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/diagnosis/rules.py)

```python
class DiagnosisConfig(BaseModel):
    loop_threshold: int = Field(default=3, ge=2, description='Identical consecutive tool calls that count as a loop.')
    handoff_round_trips: int = Field(default=2, ge=1, description='A->B->A round trips that count as a handoff loop.')
    stagnation_threshold: int = Field(default=3, ge=2, description='Identical consecutive model outputs that count as no progress.')
    max_cost_usd: float | None = Field(default=None, ge=0)
    max_total_tokens: int | None = Field(default=None, gt=0)
    max_latency_ms: float | None = Field(default=None, gt=0)
class DiagnosisRule(Protocol):
    rule_id: str
    version: str
    def diagnose(self, view: TraceView, config: DiagnosisConfig) -> list[Diagnosis]: ...
def failure_category(view: TraceView, span: Span) -> FailureCategory: ...
class FailedSpanRule():
    rule_id = 'failed_span'
    version = '1.0'
    def diagnose(self, view: TraceView, config: DiagnosisConfig) -> list[Diagnosis]: ...
class InjectedFaultRule():
    rule_id = 'injected_fault'
    version = '1.0'
    def diagnose(self, view: TraceView, config: DiagnosisConfig) -> list[Diagnosis]: ...
class RetryExhaustionRule():
    rule_id = 'retry_exhaustion'
    version = '1.0'
    def diagnose(self, view: TraceView, config: DiagnosisConfig) -> list[Diagnosis]: ...
class ToolLoopRule():
    rule_id = 'tool_loop'
    version = '1.0'
    def diagnose(self, view: TraceView, config: DiagnosisConfig) -> list[Diagnosis]: ...
class HandoffLoopRule():
    rule_id = 'handoff_loop'
    version = '1.0'
    def diagnose(self, view: TraceView, config: DiagnosisConfig) -> list[Diagnosis]: ...
class StagnationRule():
    rule_id = 'stagnation'
    version = '1.0'
    def diagnose(self, view: TraceView, config: DiagnosisConfig) -> list[Diagnosis]: ...
def retrieval_result_count(span: Span) -> int | None: ...
class EmptyRetrievalRule():
    rule_id = 'empty_retrieval'
    version = '1.0'
    def diagnose(self, view: TraceView, config: DiagnosisConfig) -> list[Diagnosis]: ...
class BudgetRule():
    rule_id = 'budget'
    version = '1.0'
    def diagnose(self, view: TraceView, config: DiagnosisConfig) -> list[Diagnosis]: ...
class IncompleteTaskRule():
    rule_id = 'incomplete_task'
    version = '1.0'
    def diagnose(self, view: TraceView, config: DiagnosisConfig) -> list[Diagnosis]: ...
```

---

## Source declarations: src/agenticlens/diagnosis/taxonomy.py

Source: [src/agenticlens/diagnosis/taxonomy.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/diagnosis/taxonomy.py)

```python
class FailureCategory(str, Enum):
    TOOL_ERROR = 'tool_error'
    MODEL_ERROR = 'model_error'
    RETRIEVAL_ERROR = 'retrieval_error'
    TIMEOUT = 'timeout'
    RETRY_EXHAUSTED = 'retry_exhausted'
    TOOL_LOOP = 'tool_loop'
    HANDOFF_LOOP = 'handoff_loop'
    STAGNATION = 'stagnation'
    EMPTY_RETRIEVAL = 'empty_retrieval'
    VALIDATION_FAILURE = 'validation_failure'
    DELEGATION_FAILURE = 'delegation_failure'
    BUDGET_EXCEEDED = 'budget_exceeded'
    INJECTED_FAULT = 'injected_fault'
    INCOMPLETE_TASK = 'incomplete_task'
@dataclass(frozen=True)
class CategoryInfo():
    category: FailureCategory
    layer: Layer
    description: str
    default_severity: Severity
    attribution_weight: float
    next_step: str
def describe(category: FailureCategory) -> CategoryInfo: ...
def max_severity(values: list[Severity]) -> Severity: ...
```

---

## Source declarations: src/agenticlens/diagnosis/timeline.py

Source: [src/agenticlens/diagnosis/timeline.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/diagnosis/timeline.py)

```python
def build_timeline(view: TraceView, attribution: Attribution, *, max_events: int=DEFAULT_MAX_EVENTS) -> IncidentTimeline: ...
```

---

## Source declarations: src/agenticlens/diagnosis/view.py

Source: [src/agenticlens/diagnosis/view.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/diagnosis/view.py)

```python
def fingerprint(value: Any) -> str: ...
class TraceView():
    def __init__(self, run: Run, guard: AnalysisGuard) -> None: ...
    def descendants(self, span_id: str) -> list[Span]: ...
    def ancestors(self, span: Span) -> list[Span]: ...
    def agent_of(self, span: Span) -> str | None: ...
    @staticmethod
    def failed(span: Span) -> bool: ...
    @staticmethod
    def succeeded(span: Span) -> bool: ...
    @staticmethod
    def injected_fault(span: Span) -> dict[str, Any] | None: ...
    @staticmethod
    def timed_out(span: Span) -> bool: ...
    @staticmethod
    def operation_key(span: Span) -> tuple[str, str, str]: ...
    def recovered_by(self, span: Span) -> Span | None: ...
    @staticmethod
    def input_fingerprint(span: Span) -> str | None: ...
    @staticmethod
    def output_fingerprint(span: Span) -> str | None: ...
    def evidence(self, span: Span, *, source: str='trace.span', reasoning: str | None=None, confidence: float=1.0, **details: Any) -> Evidence: ...
def is_span_type(span: Span, *types: SpanType) -> bool: ...
```

---

## Source declarations: src/agenticlens/enterprise/__init__.py

Source: [src/agenticlens/enterprise/__init__.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/enterprise/__init__.py)

```python
__all__ = ['Credential', 'EnterpriseStore', 'Project', 'RegistryEntry', 'StoragePolicy', 'digest']
```

---

## Source declarations: src/agenticlens/enterprise/gates.py

Source: [src/agenticlens/enterprise/gates.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/enterprise/gates.py)

```python
def release_receipt(report: EvaluationReport, policy: GateConfig) -> dict[str, Any]: ...
```

---

## Source declarations: src/agenticlens/enterprise/http.py

Source: [src/agenticlens/enterprise/http.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/enterprise/http.py)

```python
def create_enterprise_app(store: EnterpriseStore, credentials: Sequence[Credential], *, storage_policy: StoragePolicy | None=None, gate_policy: GateConfig | None=None) -> FastAPI: ...
```

---

## Source declarations: src/agenticlens/enterprise/models.py

Source: [src/agenticlens/enterprise/models.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/enterprise/models.py)

```python
class Project(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True)
    organization: str = Field(min_length=1, max_length=100, pattern='^[a-zA-Z0-9_-]+$')
    name: str = Field(min_length=1, max_length=100, pattern='^[a-zA-Z0-9_-]+$')
    @property
    def key(self) -> str: ...
class Credential(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True)
    subject: str = Field(min_length=1, max_length=100)
    token_sha256: SecretStr
    project: Project
    role: Literal['reader', 'writer', 'admin']
class StoragePolicy(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True)
    max_age_days: int = Field(default=30, ge=1, le=3650)
    max_traces: int = Field(default=1000, ge=1, le=100000)
    redact: Literal[True] = True
class RegistryEntry(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True)
    kind: Literal['model', 'prompt']
    name: str = Field(min_length=1, max_length=100, pattern='^[a-zA-Z0-9_-]+$')
    version: str = Field(min_length=1, max_length=100, pattern='^[a-zA-Z0-9_.-]+$')
    content_sha256: str = Field(pattern='^[a-f0-9]{64}$')
def digest(value: str) -> str: ...
```

---

## Source declarations: src/agenticlens/enterprise/server.py

Source: [src/agenticlens/enterprise/server.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/enterprise/server.py)

```python
class ServiceConfig(BaseModel):
    model_config = ConfigDict(extra='forbid')
    credentials: list[Credential] = Field(min_length=1)
    storage_policy: StoragePolicy = Field(default_factory=StoragePolicy)
    gate_policy: GateConfig = Field(default_factory=GateConfig)
def create_app() -> FastAPI: ...
```

---

## Source declarations: src/agenticlens/enterprise/store.py

Source: [src/agenticlens/enterprise/store.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/enterprise/store.py)

```python
class EnterpriseStore():
    def __init__(self, path: Path) -> None: ...
    def put_run(self, project: Project, subject: str, run: Run, policy: StoragePolicy) -> None: ...
    def iter_runs(self, project: Project, policy: StoragePolicy, *, limit: int=20, offset: int=0) -> Iterator[Run]: ...
    def runs(self, project: Project, policy: StoragePolicy, *, limit: int=20, offset: int=0) -> list[Run]: ...
    def get_run(self, project: Project, trace_id: str, policy: StoragePolicy) -> Run | None: ...
    def prune(self, project: Project, subject: str, policy: StoragePolicy) -> int: ...
    def register(self, project: Project, subject: str, entry: RegistryEntry) -> None: ...
    def registry(self, project: Project, *, limit: int=100, offset: int=0) -> list[RegistryEntry]: ...
    def record(self, project: Project, subject: str, action: str, body: str) -> None: ...
    def export_audit(self, project: Project, *, limit: int=100, offset: int=0) -> dict[str, Any]: ...
    def compliance_export(self, project: Project, policy: StoragePolicy, *, limit: int=100, offset: int=0) -> dict[str, Any]: ...
```

---

## Source declarations: src/agenticlens/evaluation/__init__.py

Source: [src/agenticlens/evaluation/__init__.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/evaluation/__init__.py)

```python
def load_samples(path: Path) -> list[EvaluationSample]: ...
def run_live_suite(suite: TestSuite, target: LiveTarget, *, registry: EvaluatorRegistry | None=None, max_workers: int=1) -> EvaluationReport: ...
__all__ = ['BUILTIN_EVALUATOR', 'DEFAULT_VERDICT_VALUES', 'TRACE_EVALUATORS', 'TRACE_EVALUATOR_VERSION', 'Breach', 'BusinessRuleEvaluator', 'CalibrationCase', 'CalibrationDataset', 'CalibrationReport', 'CallableEvaluator', 'CaseEvaluation', 'ConfidenceInterval', 'CostCoverage', 'DatasetLabel', 'DatasetRecord', 'DatasetSummary', 'Disagreement', 'EvalSpan', 'EvalTrace', 'EvaluationContext', 'EvaluationDataset', 'EvaluationReport', 'EvaluationSample', 'EvaluationSummary', 'Evaluator', 'EvaluatorConfig', 'EvaluatorRegistry', 'EvidenceAudit', 'EvidenceIssue', 'GateConfig', 'GateDecision', 'HTTPTarget', 'JudgeCost', 'JudgeCostSummary', 'JudgeUsage', 'JudgeVerdict', 'KindSummary', 'LLMJudgeEvaluator', 'LiveTarget', 'NotificationResult', 'PairwiseAgreement', 'PythonTarget', 'ReferenceLabel', 'Score', 'ScoreAnalysis', 'TestCase', 'TestSuite', 'ThresholdPoint', 'ThresholdTuningReport', 'analyze_scores', 'audit_report', 'breached_thresholds', 'build_payload', 'calibrate_judge', 'dataset_from_samples', 'dataset_to_samples', 'default_registry', 'evaluate_gate', 'evaluate_suite', 'evaluated_model', 'judge_verdict', 'load_dataset', 'load_samples', 'load_suite', 'notify_gate_breach', 'prompt_fingerprint', 'register_trace_evaluators', 'render_html_report', 'run_live_suite', 'save_dataset', 'save_html_report', 'score_kind', 'split_dataset', 'structured_judge', 'summarize_dataset', 'to_eval_trace', 'trace_evaluators', 'tune_judge_threshold']
```

---

## Source declarations: src/agenticlens/evaluation/_trace_adapter.py

Source: [src/agenticlens/evaluation/_trace_adapter.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/evaluation/_trace_adapter.py)

```python
def to_eval_trace(run: Run) -> EvalTrace: ...
def to_eval_trace_dict(payload: Any) -> Any: ...
```

---

## Source declarations: src/agenticlens/evaluation/calibration.py

Source: [src/agenticlens/evaluation/calibration.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/evaluation/calibration.py)

```python
class ReferenceLabel(BaseModel):
    model_config = ConfigDict(extra='forbid')
    case_id: str = Field(min_length=1)
    passed: StrictBool
class CalibrationDataset(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: str = Field(min_length=1)
    version: str = Field(min_length=1)
    suite_name: str = Field(min_length=1)
    suite_version: str = Field(min_length=1)
    labels: list[ReferenceLabel] = Field(min_length=1)
    @model_validator(mode='after')
    def unique_labels(self) -> 'CalibrationDataset': ...
class CalibrationCase(BaseModel):
    case_id: str
    trace_id: str
    judge_value: float
    judge_passed: bool
    reference_passed: bool
    agreed: bool
class CalibrationReport(BaseModel):
    schema_version: Literal['1.0'] = '1.0'
    dataset_name: str
    dataset_version: str
    suite_name: str
    suite_version: str
    evaluator: str
    evaluator_version: str | None = None
    sample_count: int
    agreement_rate: float
    confidence_level: float = Field(default=0.95, ge=0.95, le=0.95)
    interval_method: Literal['wilson'] = 'wilson'
    agreement_interval: tuple[float, float]
    true_accepts: int
    true_rejects: int
    false_accepts: int
    false_rejects: int
    cases: list[CalibrationCase]
    warnings: list[str]
def calibrate_judge(report: EvaluationReport, dataset: CalibrationDataset, *, evaluator: str) -> CalibrationReport: ...
class ThresholdPoint(BaseModel):
    threshold: float
    agreement_rate: float
    balanced_accuracy: float | None
    false_accepts: int
    false_rejects: int
class ThresholdTuningReport(BaseModel):
    schema_version: Literal['1.0'] = '1.0'
    dataset_name: str
    dataset_version: str
    evaluator: str
    evaluator_version: str | None = None
    sample_count: int
    current_agreement_rate: float
    recommended_threshold: float
    recommended: ThresholdPoint
    objective: Literal['balanced_accuracy', 'agreement_rate']
    points: list[ThresholdPoint]
    warnings: list[str]
def tune_judge_threshold(report: EvaluationReport, dataset: CalibrationDataset, *, evaluator: str, thresholds: list[float] | None=None) -> ThresholdTuningReport: ...
```

---

## Source declarations: src/agenticlens/evaluation/datasets.py

Source: [src/agenticlens/evaluation/datasets.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/evaluation/datasets.py)

```python
def load_dataset(path: Path) -> EvaluationDataset: ...
def save_dataset(dataset: EvaluationDataset, path: Path) -> None: ...
def dataset_from_samples(*, name: str, version: str, samples: list[EvaluationSample], description: str='') -> EvaluationDataset: ...
def dataset_to_samples(dataset: EvaluationDataset, *, split: str | None=None) -> list[EvaluationSample]: ...
def summarize_dataset(dataset: EvaluationDataset) -> DatasetSummary: ...
def split_dataset(dataset: EvaluationDataset, *, train_ratio: float=0.7, validation_ratio: float=0.15, test_ratio: float=0.15, seed: int=0) -> EvaluationDataset: ...
def find_dataset_label(record: DatasetRecord, score_name: str) -> DatasetLabel | None: ...
```

---

## Source declarations: src/agenticlens/evaluation/evidence.py

Source: [src/agenticlens/evaluation/evidence.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/evaluation/evidence.py)

```python
class EvidenceIssue(BaseModel):
    kind: IssueKind
    message: str
    case_id: str | None = None
    score_name: str | None = None
    evaluator: str | None = None
    blocking: bool = True
class CostCoverage(BaseModel):
    total_cases: int
    priced_cases: int
    sources: dict[str, int] = Field(default_factory=dict)
    complete: bool
class EvidenceAudit(BaseModel):
    schema_version: Literal['1.0'] = '1.0'
    suite_name: str
    suite_version: str
    passed: bool
    evaluators: dict[str, list[str]] = Field(default_factory=dict, description="Evaluator name -> sorted declared versions ('unversioned' when none).")
    failed_cases: int
    failed_cases_with_trace: int
    cost: CostCoverage
    issues: list[EvidenceIssue] = Field(default_factory=list)
def audit_report(report: EvaluationReport, *, require_evaluator_versions: bool=True, require_complete_cost: bool=False, require_cost_source: bool=False) -> EvidenceAudit: ...
```

---

## Source declarations: src/agenticlens/evaluation/html_report.py

Source: [src/agenticlens/evaluation/html_report.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/evaluation/html_report.py)

```python
def render_html_report(report: EvaluationReport) -> str: ...
def save_html_report(report: EvaluationReport, path: Path) -> None: ...
```

---

## Source declarations: src/agenticlens/evaluation/judging.py

Source: [src/agenticlens/evaluation/judging.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/evaluation/judging.py)

```python
class JudgeUsage(BaseModel):
    cost_usd: float | None = Field(default=None, ge=0)
    cost_source: Literal['measured', 'estimated'] | None = None
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
class JudgeVerdict(BaseModel):
    verdict: Verdict
    confidence: float = Field(ge=0, le=1)
    rationale: str = ''
    unsupported_claims: list[str] = Field(default_factory=list)
    evidence_missed: list[str] = Field(default_factory=list)
    usage: JudgeUsage | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
def evaluated_model(context: EvaluationContext) -> str | None: ...
def prompt_fingerprint(prompt_template: str) -> str: ...
def structured_judge(name: str, judge: JudgeFunction, *, judge_model: str, version: str, verdict_values: Mapping[Verdict, float] | None=None, allow_self_judging: bool=False, judge_provider: str | None=None, prompt_version: str | None=None, prompt_template: str | None=None) -> LLMJudgeEvaluator: ...
def judge_verdict(score: Score) -> JudgeVerdict | None: ...
```

---

## Source declarations: src/agenticlens/evaluation/models.py

Source: [src/agenticlens/evaluation/models.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/evaluation/models.py)

```python
class DatasetLabel(BaseModel):
    score_name: str = Field(min_length=1)
    expected_value: float | None = Field(default=None, ge=0, le=1)
    expected_passed: bool | None = None
    expected_verdict: str | None = None
    threshold: float | None = Field(default=None, ge=0, le=1)
    notes: str = ''
    metadata: dict[str, Any] = Field(default_factory=dict)
    @model_validator(mode='after')
    def require_reference_judgment(self) -> 'DatasetLabel': ...
class DatasetRecord(BaseModel):
    case_id: str
    output: str
    trace: EvalTrace
    split: str | None = Field(default=None, pattern='^(train|validation|test)$')
    tags: list[str] = Field(default_factory=list)
    labels: list[DatasetLabel] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
class EvaluationDataset(BaseModel):
    schema_version: str = '1.0'
    name: str
    version: str
    description: str = ''
    records: list[DatasetRecord]
    metadata: dict[str, Any] = Field(default_factory=dict)
    @model_validator(mode='after')
    def unique_record_ids(self) -> 'EvaluationDataset': ...
class DatasetSummary(BaseModel):
    total_records: int
    split_counts: dict[str, int] = Field(default_factory=dict)
    labeled_records: int
    total_labels: int
    label_counts: dict[str, int] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
class ConfidenceInterval(BaseModel):
    lower: float
    upper: float
    confidence_level: float = Field(gt=0, lt=1)
    method: str
```

---

## Source declarations: src/agenticlens/evaluation/notifications.py

Source: [src/agenticlens/evaluation/notifications.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/evaluation/notifications.py)

```python
class Breach(BaseModel):
    key: str
    category: Literal['quality', 'latency', 'budget']
    observed: float | int | None
    limit: float | int
class NotificationResult(BaseModel):
    sent: bool
    breaches: list[Breach] = Field(default_factory=list)
    notified_keys: list[str] = Field(default_factory=list)
    suppressed_keys: list[str] = Field(default_factory=list)
    payload: dict[str, Any] | None = None
def breached_thresholds(decision: GateDecision, config: GateConfig) -> list[Breach]: ...
def describe_breach(breach: Breach) -> str: ...
def state_key(report: EvaluationReport, breach_key: str) -> str: ...
def build_payload(report: EvaluationReport, decision: GateDecision, breaches: list[Breach], *, webhook_format: WebhookFormat) -> dict[str, Any]: ...
def notify_gate_breach(report: EvaluationReport, decision: GateDecision, config: GateConfig, *, url: str, webhook_format: WebhookFormat='generic', cooldown: timedelta=timedelta(hours=1), cooldowns: Mapping[str, timedelta] | None=None, state_path: Path | None=None, now: datetime | None=None, timeout_seconds: float=10.0, sender: Sender | None=None) -> NotificationResult: ...
```

---

## Source declarations: src/agenticlens/evaluation/score_analysis.py

Source: [src/agenticlens/evaluation/score_analysis.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/evaluation/score_analysis.py)

```python
def score_kind(score: Score) -> ScoreKind: ...
class KindSummary(BaseModel):
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    pass_rate: float | None = None
    average_score: float | None = None
    evaluators: list[str] = Field(default_factory=list)
class JudgeCost(BaseModel):
    evaluator: str
    judge_models: list[str] = Field(default_factory=list)
    scores: int = 0
    priced_scores: int = 0
    total_cost_usd: float | None = Field(default=None, description='Sum over priced scores; None when no score is priced.')
    cost_sources: dict[str, int] = Field(default_factory=dict)
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: float = 0.0
class JudgeCostSummary(BaseModel):
    judge_scores: int = Field(default=0, description='Judge scores from an actual judge call.')
    skipped_scores: int = Field(default=0, description='Judge scores skipped before any call (e.g. self-judging); not costed.')
    priced_scores: int = 0
    complete: bool = Field(default=True, description='True when every judge score has a known cost.')
    total_cost_usd: float | None = None
    cost_per_case_usd: float | None = None
    evaluators: list[JudgeCost] = Field(default_factory=list)
class Disagreement(BaseModel):
    case_id: str
    passing: list[str]
    failing: list[str]
    deterministic_vs_model: bool = Field(description='True when the deterministic checks and a model judge disagree.')
    details: dict[str, str] = Field(default_factory=dict)
class PairwiseAgreement(BaseModel):
    evaluator_a: str
    evaluator_b: str
    shared_cases: int
    agreements: int
    agreement_rate: float | None
class ScoreAnalysis(BaseModel):
    deterministic: KindSummary
    model_based: KindSummary
    judge_cost: JudgeCostSummary
    agent_cost_usd: float | None = Field(default=None, description='Cost of the evaluated runs, from the report summary.')
    comparable_cases: int = Field(default=0, description='Cases where at least two evaluator units gave a verdict.')
    disagreement_cases: int = 0
    disagreement_rate: float | None = None
    disagreements: list[Disagreement] = Field(default_factory=list)
    pairwise_agreement: list[PairwiseAgreement] = Field(default_factory=list)
def judge_usage(score: Score) -> tuple[float | None, str | None, int, int, float]: ...
def analyze_scores(report: EvaluationReport) -> ScoreAnalysis: ...
```

---

## Source declarations: src/agenticlens/evaluation/trace_evaluators.py

Source: [src/agenticlens/evaluation/trace_evaluators.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/evaluation/trace_evaluators.py)

```python
def tool_trajectory(context: EvaluationContext) -> Score: ...
def agent_goal(context: EvaluationContext) -> Score: ...
def handoff(context: EvaluationContext) -> Score: ...
def loop(context: EvaluationContext) -> Score: ...
def groundedness(context: EvaluationContext) -> Score: ...
def relevance(context: EvaluationContext) -> Score: ...
def completeness(context: EvaluationContext) -> Score: ...
def citation(context: EvaluationContext) -> Score: ...
def safety(context: EvaluationContext) -> Score: ...
def trace_evaluators() -> list[CallableEvaluator]: ...
def register_trace_evaluators(registry: EvaluatorRegistry, *, replace: bool=False) -> None: ...
def default_registry() -> EvaluatorRegistry: ...
```

---

## Source declarations: src/agenticlens/experiments/__init__.py

Source: [src/agenticlens/experiments/__init__.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/experiments/__init__.py)

```python
__all__ = ['KNOWN_FACTORS', 'ExperimentCaseResult', 'ExperimentComparison', 'ExperimentManifest', 'ExperimentMetricSummary', 'ExperimentRandomization', 'ExperimentReport', 'ExperimentTrialResult', 'ExperimentVariant', 'ExperimentVariantResult', 'ExperimentVariantSummary', 'FactorLevelSummary', 'load_experiment_report', 'load_experiment_suite', 'load_manifest', 'load_recorded_trials', 'pass_at_k', 'pass_hat_k', 'render_case_matrix_csv', 'render_experiment_html', 'render_variant_csv', 'run_experiment', 'save_case_matrix_csv', 'save_experiment_html', 'save_variant_csv', 'two_proportion_p_value', 'wilson_interval']
```

---

## Source declarations: src/agenticlens/experiments/export.py

Source: [src/agenticlens/experiments/export.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/experiments/export.py)

```python
def render_variant_csv(report: ExperimentReport) -> str: ...
def render_case_matrix_csv(report: ExperimentReport) -> str: ...
def save_variant_csv(report: ExperimentReport, path: Path) -> None: ...
def save_case_matrix_csv(report: ExperimentReport, path: Path) -> None: ...
```

---

## Source declarations: src/agenticlens/experiments/html_report.py

Source: [src/agenticlens/experiments/html_report.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/experiments/html_report.py)

```python
def render_experiment_html(report: ExperimentReport) -> str: ...
def save_experiment_html(report: ExperimentReport, path: Path) -> None: ...
```

---

## Source declarations: src/agenticlens/experiments/models.py

Source: [src/agenticlens/experiments/models.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/experiments/models.py)

```python
class ExperimentVariant(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    target_kind: str = Field(pattern='^(python|http|recorded)$')
    target: str = Field(min_length=1)
    timeout_seconds: float = Field(default=30.0, gt=0)
    description: str = ''
    factors: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, str] = Field(default_factory=dict)
class ExperimentManifest(BaseModel):
    schema_version: str = '1.1'
    name: str = Field(min_length=1)
    version: str = Field(min_length=1)
    baseline_variant_id: str = Field(min_length=1)
    trial_count: int = Field(default=5, ge=1)
    random_seed: int | None = None
    pass_k: list[int] = Field(default_factory=list, description='k values for pass@k and pass^k; defaults to 1 and trial_count.')
    minimum_trials: int = Field(default=5, ge=1, description='Completed trials per variant below which deltas are flagged exploratory.')
    max_workers: int = Field(default=1, ge=1, description='Cases run concurrently within one live trial.')
    variants: list[ExperimentVariant]
    metadata: dict[str, str] = Field(default_factory=dict)
    @model_validator(mode='after')
    def validate_variants(self) -> 'ExperimentManifest': ...
    def resolved_pass_k(self) -> list[int]: ...
class ExperimentMetricSummary(BaseModel):
    count: int = Field(ge=0)
    mean: float
    median: float
    p95: float
    standard_deviation: float
    coefficient_of_variation: float | None = None
    confidence_interval: ConfidenceInterval | None = None
class ExperimentCaseResult(BaseModel):
    case_id: str
    case_name: str
    attempts: int = Field(ge=0)
    passes: int = Field(ge=0)
    pass_rate: float = Field(ge=0, le=1)
    pass_at_k: dict[str, float] = Field(default_factory=dict)
    pass_hat_k: dict[str, float] = Field(default_factory=dict)
    mean_score: float | None = None
    score_standard_deviation: float | None = None
    consistent: bool = Field(description='Every attempt had the same pass/fail outcome.')
class ExperimentVariantSummary(BaseModel):
    attempted_trials: int = Field(ge=0)
    completed_trials: int = Field(ge=0)
    failed_trials: int = Field(ge=0)
    successful_trials: int = Field(ge=0)
    trial_success_rate: float = Field(ge=0, le=1)
    pass_rate: ExperimentMetricSummary | None = None
    average_score: ExperimentMetricSummary | None = None
    average_latency_ms: ExperimentMetricSummary | None = None
    total_cost_usd: ExperimentMetricSummary | None = None
    case_attempts: int = Field(default=0, ge=0)
    case_passes: int = Field(default=0, ge=0)
    case_pass_rate: float | None = Field(default=None, ge=0, le=1)
    case_pass_rate_interval: ConfidenceInterval | None = None
    pass_at_k: dict[str, float] = Field(default_factory=dict)
    pass_hat_k: dict[str, float] = Field(default_factory=dict)
    consistency_rate: float | None = Field(default=None, ge=0, le=1)
    flaky_case_ids: list[str] = Field(default_factory=list)
    priced_trials: int = Field(default=0, ge=0)
class ExperimentTrialResult(BaseModel):
    trial_index: int = Field(ge=1)
    status: str = Field(pattern='^(succeeded|failed)$')
    report: EvaluationReport | None = None
    error_message: str | None = None
class ExperimentVariantResult(BaseModel):
    variant_id: str
    variant_name: str
    target_kind: str
    factors: dict[str, str] = Field(default_factory=dict)
    pareto_optimal: bool = False
    trials: list[ExperimentTrialResult]
    summary: ExperimentVariantSummary
    cases: list[ExperimentCaseResult] = Field(default_factory=list)
class ExperimentComparison(BaseModel):
    baseline_variant_id: str
    candidate_variant_id: str
    pass_rate_delta: MetricDelta
    average_score_delta: MetricDelta
    average_latency_ms_delta: MetricDelta
    total_cost_usd_delta: MetricDelta | None = None
    changed_factors: dict[str, list[str | None]] = Field(default_factory=dict, description='Factor -> [baseline value, candidate value] for factors that differ.')
    case_pass_rate_delta: float | None = None
    case_pass_rate_p_value: float | None = None
    statistically_significant: bool | None = None
    regressed_case_ids: list[str] = Field(default_factory=list)
    improved_case_ids: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
class FactorLevelSummary(BaseModel):
    factor: str
    value: str
    variant_ids: list[str]
    mean_pass_rate: float | None = None
    mean_average_score: float | None = None
    mean_latency_ms: float | None = None
    mean_cost_usd: float | None = None
    mean_trial_success_rate: float
class ExperimentRandomization(BaseModel):
    random_seed: int | None = None
    shuffled: bool
    execution_order: list[tuple[str, int]] = Field(default_factory=list, description='(variant_id, trial_index) in the order run.')
class ExperimentReport(BaseModel):
    schema_version: str = '1.1'
    experiment_name: str
    experiment_version: str
    suite_name: str
    suite_version: str
    baseline_variant_id: str
    trial_count: int = Field(ge=1)
    random_seed: int | None = None
    confidence_level: float = Field(default=0.95, gt=0, lt=1)
    regression_threshold: float = Field(default=0.05, ge=0)
    pass_k: list[int] = Field(default_factory=list)
    minimum_trials: int = Field(default=5, ge=1)
    randomization: ExperimentRandomization | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    variants: list[ExperimentVariantResult]
    comparisons: list[ExperimentComparison]
    pareto_frontier_variant_ids: list[str] = Field(default_factory=list)
    factor_levels: list[FactorLevelSummary] = Field(default_factory=list)
    case_ids: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
```

---

## Source declarations: src/agenticlens/experiments/runner.py

Source: [src/agenticlens/experiments/runner.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/experiments/runner.py)

```python
def load_manifest(path: Path) -> ExperimentManifest: ...
def load_recorded_trials(path: Path) -> list[list[EvaluationSample]]: ...
def run_experiment(manifest: ExperimentManifest, suite: TestSuite, *, registry: EvaluatorRegistry | None=None, confidence_level: float=0.95, regression_threshold: float=0.05) -> ExperimentReport: ...
def load_experiment_suite(path: Path) -> TestSuite: ...
def load_experiment_report(path: Path) -> ExperimentReport: ...
```

---

## Source declarations: src/agenticlens/experiments/stats.py

Source: [src/agenticlens/experiments/stats.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/experiments/stats.py)

```python
def pass_at_k(trials: int, passes: int, k: int) -> float: ...
def pass_hat_k(trials: int, passes: int, k: int) -> float: ...
def z_value(confidence_level: float) -> float: ...
def wilson_interval(successes: int, total: int, confidence_level: float) -> tuple[float, float]: ...
def mean_interval(values: list[float], confidence_level: float) -> tuple[float, float]: ...
def two_proportion_p_value(successes_a: int, total_a: int, successes_b: int, total_b: int) -> float | None: ...
```

---

## Source declarations: src/agenticlens/exporters/__init__.py

Source: [src/agenticlens/exporters/__init__.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/exporters/__init__.py)

```python
__all__ = ['BaseExporter', 'CSVExporter', 'JiraExporter', 'JSONExporter', 'MarkdownExporter', 'OTLPTraceExporter']
```

---

## Source declarations: src/agenticlens/exporters/_aios.py

Source: [src/agenticlens/exporters/_aios.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/exporters/_aios.py)

```python
def timestamp(value: datetime) -> str: ...
def identifier(value: str) -> str: ...
def reference(value: Mapping[str, Any]) -> dict[str, str]: ...
```

---

## Source declarations: src/agenticlens/exporters/base.py

Source: [src/agenticlens/exporters/base.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/exporters/base.py)

```python
class BaseExporter(ABC):
    @abstractmethod
    def export(self, workflow: Workflow, path: str | Path | None=None, recommendations: list[Recommendation] | None=None) -> None: ...
```

---

## Source declarations: src/agenticlens/exporters/csv_exporter.py

Source: [src/agenticlens/exporters/csv_exporter.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/exporters/csv_exporter.py)

```python
class CSVExporter(BaseExporter):
    def export(self, workflow: Workflow, path: str | Path | None=None, recommendations: list[Recommendation] | None=None) -> None: ...
```

---

## Source declarations: src/agenticlens/exporters/jira_exporter.py

Source: [src/agenticlens/exporters/jira_exporter.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/exporters/jira_exporter.py)

```python
class JiraExporter(BaseExporter):
    def __init__(self, base_url: str, user_email: str, api_token: str, issue_key: str) -> None: ...
    def export(self, workflow: Workflow, path: str | Path | None=None, recommendations: list[Recommendation] | None=None) -> None: ...
```

---

## Source declarations: src/agenticlens/exporters/json_exporter.py

Source: [src/agenticlens/exporters/json_exporter.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/exporters/json_exporter.py)

```python
class JSONExporter(BaseExporter):
    def export(self, workflow: Workflow, path: str | Path | None=None, recommendations: list[Recommendation] | None=None) -> None: ...
```

---

## Source declarations: src/agenticlens/exporters/markdown_exporter.py

Source: [src/agenticlens/exporters/markdown_exporter.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/exporters/markdown_exporter.py)

```python
class MarkdownExporter(BaseExporter):
    def export(self, workflow: Workflow, path: str | Path | None=None, recommendations: list[Recommendation] | None=None) -> None: ...
```

---

## Source declarations: src/agenticlens/exporters/otlp_trace_exporter.py

Source: [src/agenticlens/exporters/otlp_trace_exporter.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/exporters/otlp_trace_exporter.py)

```python
class OTLPTraceExporter():
    def to_payload(self, run: Run) -> dict[str, Any]: ...
    def save(self, run: Run, path: str | Path) -> None: ...
    def export(self, run: Run, endpoint: str, *, headers: dict[str, str] | None=None, timeout: float=_DEFAULT_TIMEOUT_SECONDS) -> None: ...
```

---

## Source declarations: src/agenticlens/exporters/verification.py

Source: [src/agenticlens/exporters/verification.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/exporters/verification.py)

```python
def export_verification_signal(score: Score, *, source_id: str, subject: Mapping[str, Any], evidence: Sequence[Mapping[str, Any]], created_at: datetime, method_version: str) -> dict[str, Any]: ...
```

---

## Source declarations: src/agenticlens/instrumentation/__init__.py

Source: [src/agenticlens/instrumentation/__init__.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/instrumentation/__init__.py)

```python
__all__ = ['Redactor', 'SpanHandle', 'redact_sensitive', 'trace']
```

---

## Source declarations: src/agenticlens/instrumentation/redaction.py

Source: [src/agenticlens/instrumentation/redaction.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/instrumentation/redaction.py)

```python
def redact_sensitive(value: Any) -> Any: ...
```

---

## Source declarations: src/agenticlens/instrumentation/trace.py

Source: [src/agenticlens/instrumentation/trace.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/instrumentation/trace.py)

```python
class SpanHandle():
    def __init__(self, span: Span, redactor: Redactor) -> None: ...
    def record_tokens(self, input_tokens: int=0, output_tokens: int=0) -> None: ...
    def record_cost(self, estimated_cost_usd: float) -> None: ...
    def set_attribute(self, name: str, value: Any) -> None: ...
    def record_io(self, *, input_data: Any=None, output_data: Any=None) -> None: ...
class SpanContext():
    def __init__(self, owner: 'trace', name: str, span_type: SpanType | str, *, agent_name: str | None=None, model_name: str | None=None, provider: str | None=None, tool_name: str | None=None, retry_number: int | None=None, input_reference: str | None=None, output_reference: str | None=None, **attributes: Any): ...
class trace():
    def __init__(self, application_name: str, *, redactor: Redactor=redact_sensitive, framework: str | None=None, framework_version: str | None=None, task_id: str | None=None, task_type: str | None=None, experiment_id: str | None=None, variant_id: str | None=None, otlp_endpoint: str | None=None, otlp_headers: dict[str, str] | None=None, otlp_timeout_seconds: float | None=None, **metadata: Any) -> None: ...
    def span(self, name: str, span_type: SpanType | str=SpanType.CUSTOM, **attributes: Any) -> SpanContext: ...
    def save(self, path: str | Path) -> None: ...
```

---

## Source declarations: src/agenticlens/integrations/sidecar.py

Source: [src/agenticlens/integrations/sidecar.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/integrations/sidecar.py)

```python
def attach_decisions(run: Run, records: list[dict[str, Any]]) -> None: ...
def verify_journal(events: list[dict[str, Any]], *, task_id: str) -> None: ...
```

---

## Source declarations: src/agenticlens/integrity/__init__.py

Source: [src/agenticlens/integrity/__init__.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/integrity/__init__.py)

```python
class Coverage(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    stream_id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    complete: bool
class Manifest(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    format: Literal['lens.evidence-manifest/1'] = 'lens.evidence-manifest/1'
    key_id: str = Field(min_length=1)
    coverage: Coverage
    record_count: int = Field(ge=0)
    root_sha256: str = Field(pattern='^[0-9a-f]{64}$')
    authentication: str = Field(pattern='^[0-9a-f]{64}$')
class Verification(BaseModel):
    status: Literal['verified', 'failed', 'unknown', 'incomplete']
    reason: str
    authenticated: bool = False
    coverage: Coverage | None = None
    record_count: int = 0
def seal(records: list[dict[str, Any]], *, coverage: Coverage, key_id: str, key: bytes) -> Manifest: ...
def verify(records: list[dict[str, Any]], manifest: Manifest, *, trusted_keys: dict[str, bytes], expected_stream_id: str) -> Verification: ...
def replay(records: list[dict[str, Any]], manifest: Manifest, *, trusted_keys: dict[str, bytes], expected_stream_id: str) -> list[dict[str, Any]]: ...
__all__ = ['Coverage', 'Manifest', 'Verification', 'replay', 'seal', 'verify']
```

---

## Source declarations: src/agenticlens/integrity/execution.py

Source: [src/agenticlens/integrity/execution.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/integrity/execution.py)

```python
class ExecutionRecord(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    event_id: str = Field(min_length=1)
    run_id: str = Field(min_length=1)
    span_id: str | None = None
    occurred_at: str
    kind: Literal['proposed', 'allowed', 'denied', 'dispatched', 'completed', 'stop_acknowledged', 'revocation_acknowledged']
    producer: str = Field(min_length=1)
    decision_id: str | None = None
    action_id: str | None = None
    actor: str | None = None
    policy_version: str | None = None
    approval_id: str | None = None
    outcome: str | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)
    @model_validator(mode='after')
    def aware_time(self) -> 'ExecutionRecord': ...
class ExecutionBundle(BaseModel):
    model_config = ConfigDict(extra='forbid')
    artifact: dict[str, Any]
    manifest: Manifest
class ExecutionValidationUnavailableError(ValueError):
    ...
def export_execution(run: Run, records: list[ExecutionRecord]) -> dict[str, Any]: ...
def import_execution(artifact: dict[str, Any]) -> tuple[Run, list[ExecutionRecord]]: ...
def capture_execution(run: Run, records: list[ExecutionRecord], *, coverage: Coverage, key_id: str, key: bytes) -> ExecutionBundle: ...
def verify_execution(bundle: ExecutionBundle, *, trusted_keys: dict[str, bytes], expected_run_id: str) -> Verification: ...
def replay_execution(bundle: ExecutionBundle, *, trusted_keys: dict[str, bytes], expected_run_id: str) -> tuple[Run, list[ExecutionRecord]]: ...
def execution_summary(bundle: ExecutionBundle, *, trusted_keys: dict[str, bytes], expected_run_id: str) -> dict[str, Any]: ...
```

---

## Source declarations: src/agenticlens/metrics/__init__.py

Source: [src/agenticlens/metrics/__init__.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/metrics/__init__.py)

```python
__all__ = ['apply_cost']
```

---

## Source declarations: src/agenticlens/metrics/calculator.py

Source: [src/agenticlens/metrics/calculator.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/metrics/calculator.py)

```python
def apply_cost(step: Step, config: AgenticLensConfig | None=None) -> None: ...
```

---

## Source declarations: src/agenticlens/metrics/trace.py

Source: [src/agenticlens/metrics/trace.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/metrics/trace.py)

```python
def tokens_by_span_type(run: Run) -> dict[SpanType, int]: ...
def latency_by_span_type(run: Run) -> dict[SpanType, float]: ...
def retry_count(run: Run) -> int: ...
def tool_call_count(run: Run) -> int: ...
```

---

## Source declarations: src/agenticlens/modelfit/__init__.py

Source: [src/agenticlens/modelfit/__init__.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/modelfit/__init__.py)

```python
__all__ = ['MODELFIT_SCHEMA_VERSION', 'OVERALL_CATEGORY_ID', 'Alternative', 'CandidateEvidence', 'CandidateMetrics', 'CaseAttempt', 'CaseEvidence', 'CategoryResult', 'EvidenceSource', 'ExperimentEvidence', 'MatrixRow', 'ModelCandidate', 'ModelConstraints', 'ModelFitConfig', 'ModelFitReport', 'ModelFitSummary', 'QualityRisk', 'Recommendation', 'SavingsEstimate', 'ScoringWeights', 'TaskCategory', 'Violation', 'check_constraints', 'collect_candidates', 'cost_per_success_ranking', 'derive_categories', 'load_experiment_evidence', 'load_modelfit_config', 'load_modelfit_report', 'pareto_frontier', 'recommend_models', 'render_markdown', 'render_matrix_csv', 'resolve_taxonomy', 'save_markdown', 'save_matrix_csv', 'save_modelfit_report']
```

---

## Source declarations: src/agenticlens/modelfit/evidence.py

Source: [src/agenticlens/modelfit/evidence.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/modelfit/evidence.py)

```python
@dataclass(frozen=True)
class ExperimentEvidence():
    report: ExperimentReport
    file: str | None = None
    sha256: str | None = None
@dataclass(frozen=True)
class CaseAttempt():
    passed: bool
    completed: bool
    latency_ms: float | None = None
    cost_usd: float | None = None
@dataclass
class CaseEvidence():
    case_id: str
    tags: list[str] = field(default_factory=list)
    domain: str | None = None
    attempts: list[CaseAttempt] = field(default_factory=list)
@dataclass
class CandidateEvidence():
    variant: ExperimentVariantResult
    source_index: int
    model: str
    provider: str | None
    deployment: str | None
    capabilities: list[str]
    cases: dict[str, CaseEvidence]
def load_experiment_evidence(path: Path) -> ExperimentEvidence: ...
def as_evidence(item: ExperimentReport | ExperimentEvidence) -> ExperimentEvidence: ...
def evidence_source(evidence: ExperimentEvidence) -> EvidenceSource: ...
def collect_candidates(evidence: list[ExperimentEvidence], config: ModelFitConfig, variant_metadata: dict[str, dict[str, str]] | None=None) -> tuple[list[CandidateEvidence], list[str]]: ...
```

---

## Source declarations: src/agenticlens/modelfit/io.py

Source: [src/agenticlens/modelfit/io.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/modelfit/io.py)

```python
def load_modelfit_config(path: Path) -> ModelFitConfig: ...
def load_modelfit_report(path: Path) -> ModelFitReport: ...
def save_modelfit_report(report: ModelFitReport, path: Path) -> None: ...
```

---

## Source declarations: src/agenticlens/modelfit/models.py

Source: [src/agenticlens/modelfit/models.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/modelfit/models.py)

```python
class ModelConstraints(BaseModel):
    min_pass_rate: float | None = Field(default=None, ge=0, le=1)
    min_pass_rate_lower_bound: float | None = Field(default=None, ge=0, le=1, description="Minimum lower bound of the pass rate's Wilson confidence interval.")
    max_cost_per_case_usd: float | None = Field(default=None, ge=0)
    max_cost_per_success_usd: float | None = Field(default=None, ge=0)
    max_mean_latency_ms: float | None = Field(default=None, gt=0)
    max_p95_latency_ms: float | None = Field(default=None, gt=0)
    min_consistency: float | None = Field(default=None, ge=0, le=1, description='Minimum share of cases with the same outcome on every attempt.')
    min_safety_pass_rate: float | None = Field(default=None, ge=0, le=1, description='Minimum pass rate over every safety-tagged case in the suite.')
    allowed_providers: list[str] | None = None
    blocked_providers: list[str] | None = Field(default_factory=list, description='`null` in an override clears the default block-list.')
    allowed_deployments: list[str] | None = None
    required_capabilities: list[str] | None = Field(default_factory=list, description='`null` in an override clears the default requirement.')
    def merged(self, override: 'ModelConstraints | None') -> 'ModelConstraints': ...
class ScoringWeights(BaseModel):
    quality: float = Field(default=0.5, ge=0)
    cost: float = Field(default=0.3, ge=0)
    latency: float = Field(default=0.1, ge=0)
    reliability: float = Field(default=0.1, ge=0)
    @model_validator(mode='after')
    def check_total(self) -> 'ScoringWeights': ...
    def as_dict(self) -> dict[str, float]: ...
class TaskCategory(BaseModel):
    id: str = Field(min_length=1, pattern='^[A-Za-z0-9][A-Za-z0-9_.:-]*$')
    name: str = ''
    description: str = ''
    tags: list[str] = Field(default_factory=list)
    domains: list[str] = Field(default_factory=list)
    case_ids: list[str] = Field(default_factory=list)
    constraints: ModelConstraints | None = Field(default=None, description="Overrides for the config's default constraints.")
    weights: ScoringWeights | None = Field(default=None, description="Replaces the config's default weights for this category.")
    monthly_volume: int | None = Field(default=None, ge=0, description='Expected requests per month, for savings projections.')
    @model_validator(mode='after')
    def check_selector(self) -> 'TaskCategory': ...
    @property
    def display_name(self) -> str: ...
class ModelCandidate(BaseModel):
    variant_id: str = Field(min_length=1)
    model: str | None = None
    provider: str | None = None
    deployment: str | None = None
    capabilities: list[str] = Field(default_factory=list)
class ModelFitConfig(BaseModel):
    schema_version: str = MODELFIT_SCHEMA_VERSION
    name: str = Field(default='modelfit', min_length=1)
    model_factor: str = Field(default='model', min_length=1, description='Experiment factor that names the model.')
    reference_variant_id: str | None = Field(default=None, description='Variant that savings and quality risks are measured against; defaults to the experiment baseline.')
    categories: list[TaskCategory] = Field(default_factory=list, description='Task taxonomy. When empty, one category is derived per case tag.')
    include_overall: bool = Field(default=True, description='Add an `all` category covering every case.')
    defaults: ModelConstraints = Field(default_factory=ModelConstraints)
    weights: ScoringWeights = Field(default_factory=ScoringWeights)
    candidates: list[ModelCandidate] = Field(default_factory=list)
    exclude_variant_ids: list[str] = Field(default_factory=list)
    safety_tags: list[str] = Field(default_factory=lambda: ['safety'])
    minimum_attempts: int = Field(default=10, ge=1, description='Case attempts per category below which a recommendation is low confidence.')
    confidence_level: float = Field(default=0.95, gt=0, lt=1)
    significance_level: float = Field(default=0.05, gt=0, lt=1)
    max_alternatives: int = Field(default=2, ge=0)
    metadata: dict[str, str] = Field(default_factory=dict)
    @model_validator(mode='after')
    def check_unique(self) -> 'ModelFitConfig': ...
class EvidenceSource(BaseModel):
    experiment_name: str
    experiment_version: str
    suite_name: str
    suite_version: str
    baseline_variant_id: str
    trial_count: int = Field(ge=1)
    created_at: datetime
    variant_ids: list[str]
    file: str | None = Field(default=None, description='Report file name, without directories.')
    sha256: str | None = Field(default=None, description='SHA-256 of the report file bytes, when loaded from a file.')
class Violation(BaseModel):
    constraint: str
    limit: Any = None
    observed: Any = None
    message: str
class CandidateMetrics(BaseModel):
    variant_id: str
    variant_name: str
    model: str
    provider: str | None = None
    deployment: str | None = None
    capabilities: list[str] = Field(default_factory=list)
    factors: dict[str, str] = Field(default_factory=dict)
    source_index: int = Field(ge=0, description="Index into the report's `sources`.")
    case_ids: list[str]
    attempts: int = Field(ge=0)
    passes: int = Field(ge=0)
    pass_rate: float | None = Field(default=None, ge=0, le=1)
    pass_rate_interval: ConfidenceInterval | None = None
    failed_trial_attempts: int = Field(default=0, ge=0, description='Attempts lost because the whole trial failed.')
    mean_latency_ms: float | None = None
    p95_latency_ms: float | None = None
    cost_complete: bool = Field(description='Every completed attempt reported a cost; otherwise costs are unavailable.')
    total_cost_usd: float | None = None
    cost_per_case_usd: float | None = None
    cost_per_success_usd: float | None = None
    consistency_rate: float | None = Field(default=None, ge=0, le=1)
    flaky_case_ids: list[str] = Field(default_factory=list)
    safety_attempts: int = Field(default=0, ge=0)
    safety_pass_rate: float | None = Field(default=None, ge=0, le=1)
    failed_safety_case_ids: list[str] = Field(default_factory=list)
    feasible: bool = False
    violations: list[Violation] = Field(default_factory=list)
    component_scores: dict[str, float] = Field(default_factory=dict)
    weighted_score: float | None = Field(default=None, description='Only feasible candidates are scored.')
    rank: int | None = Field(default=None, ge=1, description='Rank among feasible candidates.')
    pareto_optimal: bool = False
    cost_per_success_rank: int | None = Field(default=None, ge=1)
class Alternative(BaseModel):
    variant_id: str
    model: str
    provider: str | None = None
    role: Literal['alternative', 'fallback']
    weighted_score: float | None = None
    pass_rate: float | None = None
    cost_per_success_usd: float | None = None
    reason: str
class SavingsEstimate(BaseModel):
    reference_variant_id: str
    recommended_variant_id: str
    available: bool
    reason: str = ''
    reference_cost_per_case_usd: float | None = None
    recommended_cost_per_case_usd: float | None = None
    cost_per_case_savings_usd: float | None = None
    cost_per_case_savings_ratio: float | None = None
    reference_cost_per_success_usd: float | None = None
    recommended_cost_per_success_usd: float | None = None
    cost_per_success_savings_usd: float | None = None
    monthly_volume: int | None = None
    projected_monthly_savings_usd: float | None = None
    reference_pass_rate: float | None = None
    recommended_pass_rate: float | None = None
    pass_rate_delta: float | None = None
    pass_rate_p_value: float | None = None
    reference_attempts: int = Field(default=0, ge=0)
    recommended_attempts: int = Field(default=0, ge=0)
    case_ids: list[str] = Field(default_factory=list)
    source_indexes: list[int] = Field(default_factory=list, description="Indexes into the report's `sources`.")
class QualityRisk(BaseModel):
    kind: RiskKind
    severity: RiskSeverity
    message: str
    case_ids: list[str] = Field(default_factory=list)
class Recommendation(BaseModel):
    category_id: str
    status: RecommendationStatus
    variant_id: str | None = None
    model: str | None = None
    provider: str | None = None
    weighted_score: float | None = None
    confidence: Confidence | None = None
    confidence_reasons: list[str] = Field(default_factory=list)
    explanation: list[str] = Field(default_factory=list)
    alternatives: list[Alternative] = Field(default_factory=list)
    fallback: Alternative | None = None
    savings: SavingsEstimate | None = None
    quality_risks: list[QualityRisk] = Field(default_factory=list)
    rejected_variant_ids: list[str] = Field(default_factory=list)
class CategoryResult(BaseModel):
    category: TaskCategory
    case_ids: list[str]
    constraints: ModelConstraints = Field(description='Effective constraints after overrides.')
    weights: ScoringWeights = Field(description='Effective scoring weights.')
    candidates: list[CandidateMetrics] = Field(description='Feasible candidates by rank, then infeasible ones.')
    pareto_frontier_variant_ids: list[str] = Field(default_factory=list)
    cost_per_success_ranking: list[str] = Field(default_factory=list, description='Candidates with known cost per success, cheapest first.')
    recommendation: Recommendation
class MatrixRow(BaseModel):
    category_id: str
    variant_id: str
    model: str
    provider: str | None = None
    role: Literal['recommended', 'alternative', 'fallback', 'feasible', 'infeasible']
    feasible: bool
    attempts: int
    pass_rate: float | None = None
    cost_per_success_usd: float | None = None
    mean_latency_ms: float | None = None
    weighted_score: float | None = None
    violations: list[str] = Field(default_factory=list)
class ModelFitSummary(BaseModel):
    categories: int = Field(ge=0)
    recommended: int = Field(ge=0)
    unfit_category_ids: list[str] = Field(default_factory=list, description='Categories with no feasible candidate or no evidence.')
    low_confidence_category_ids: list[str] = Field(default_factory=list)
    candidates: int = Field(ge=0)
class ModelFitReport(BaseModel):
    schema_version: str = MODELFIT_SCHEMA_VERSION
    name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    model_factor: str
    reference_variant_id: str
    safety_tags: list[str] = Field(default_factory=list)
    minimum_attempts: int = Field(ge=1)
    confidence_level: float = Field(gt=0, lt=1)
    sources: list[EvidenceSource]
    summary: ModelFitSummary
    categories: list[CategoryResult]
    matrix: list[MatrixRow] = Field(default_factory=list)
    uncategorized_case_ids: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
```

---

## Source declarations: src/agenticlens/modelfit/recommend.py

Source: [src/agenticlens/modelfit/recommend.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/modelfit/recommend.py)

```python
def recommend_models(reports: Sequence[ExperimentReport | ExperimentEvidence], config: ModelFitConfig | None=None, *, variant_metadata: dict[str, dict[str, str]] | None=None) -> ModelFitReport: ...
```

---

## Source declarations: src/agenticlens/modelfit/render.py

Source: [src/agenticlens/modelfit/render.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/modelfit/render.py)

```python
def render_matrix_csv(report: ModelFitReport) -> str: ...
def save_matrix_csv(report: ModelFitReport, path: Path) -> None: ...
def render_markdown(report: ModelFitReport) -> str: ...
def save_markdown(report: ModelFitReport, path: Path) -> None: ...
```

---

## Source declarations: src/agenticlens/modelfit/scoring.py

Source: [src/agenticlens/modelfit/scoring.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/modelfit/scoring.py)

```python
def percentile(values: list[float], fraction: float) -> float: ...
def measure(candidate: CandidateEvidence, case_ids: list[str], safety_case_ids: list[str], confidence_level: float) -> CandidateMetrics: ...
def check_constraints(metrics: CandidateMetrics, constraints: ModelConstraints) -> list[Violation]: ...
def score(candidates: list[CandidateMetrics], weights: ScoringWeights) -> None: ...
def sort_key(candidate: CandidateMetrics) -> tuple[int, float, float, float, str]: ...
def pareto_frontier(candidates: list[CandidateMetrics]) -> list[str]: ...
def cost_per_success_ranking(candidates: list[CandidateMetrics]) -> list[str]: ...
```

---

## Source declarations: src/agenticlens/modelfit/taxonomy.py

Source: [src/agenticlens/modelfit/taxonomy.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/modelfit/taxonomy.py)

```python
def case_index(candidates: list[CandidateEvidence]) -> dict[str, CaseEvidence]: ...
def matches(category: TaskCategory, case: CaseEvidence) -> bool: ...
def derive_categories(cases: dict[str, CaseEvidence], reserved: Iterable[str]=()) -> list[TaskCategory]: ...
def resolve_taxonomy(config: ModelFitConfig, cases: dict[str, CaseEvidence]) -> tuple[list[tuple[TaskCategory, list[str]]], list[str], list[str]]: ...
```

---

## Source declarations: src/agenticlens/models/__init__.py

Source: [src/agenticlens/models/__init__.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/models/__init__.py)

```python
__all__ = ['Metrics', 'Recommendation', 'Severity', 'Step', 'StepType', 'Evidence', 'Finding', 'MetricValue', 'Run', 'RunStatus', 'Span', 'SpanType', 'Workflow']
```

---

## Source declarations: src/agenticlens/models/enums.py

Source: [src/agenticlens/models/enums.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/models/enums.py)

```python
class StepType(str, Enum):
    PLANNER = 'planner'
    RETRIEVER = 'retriever'
    TOOL_CALL = 'tool_call'
    LLM_CALL = 'llm_call'
    MEMORY = 'memory'
    FINAL_RESPONSE = 'final_response'
class Severity(str, Enum):
    INFO = 'info'
    WARNING = 'warning'
    CRITICAL = 'critical'
```

---

## Source declarations: src/agenticlens/models/metrics.py

Source: [src/agenticlens/models/metrics.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/models/metrics.py)

```python
class Metrics(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency: float = 0.0
    ttft: float | None = Field(default=None, description='Time To First Token in seconds. Only set for streaming calls.')
    cost: float | None = Field(default=None, description='Total cost for the step. None when pricing is unknown for the model.')
    @property
    def tps(self) -> float | None: ...
```

---

## Source declarations: src/agenticlens/models/recommendation.py

Source: [src/agenticlens/models/recommendation.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/models/recommendation.py)

```python
class Recommendation(BaseModel):
    title: str
    description: str
    optimization_type: str = Field(default='token_optimization', description='Machine-readable optimization category, e.g. rag_chunk_pruning.')
    step_id: str | None = None
    step_name: str | None = None
    step_type: str | None = None
    severity: Severity = Severity.INFO
    tokens_saved: int = 0
    estimated_savings: float | None = None
    estimated_usd_savings: float | None = None
    estimated_monthly_savings: float | None = None
    confidence: float | None = None
    quality_risk: str | None = None
    evidence: list[Evidence] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    cost_savings: float | None = Field(default=None, description='Projected dollar savings for cost-aware recommenders (e.g. model swaps). Distinct from `estimated_savings`, which is a token-reduction percentage.')
```

---

## Source declarations: src/agenticlens/models/step.py

Source: [src/agenticlens/models/step.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/models/step.py)

```python
class Step(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: StepType
    agent_name: str | None = Field(default=None, description='Name of the agent responsible for this step in a multi-agent workflow.')
    agent_role: str | None = Field(default=None, description='Optional role label such as planner, researcher, critic, or executor.')
    parent_step_id: str | None = Field(default=None, description='Optional parent step id for workflow graph or handoff relationships.')
    handoff_from: str | None = Field(default=None, description='Agent or step that handed context to this step.')
    handoff_to: str | None = Field(default=None, description="Agent or step that receives this step's output.")
    provider: str | None = None
    model: str | None = None
    metrics: Metrics = Field(default_factory=Metrics)
    metadata: dict[str, Any] = Field(default_factory=dict, description="Free-form signals supplied by the developer for recommender rules (e.g. 'prompt', 'chunk_count', 'history_tokens', 'tool_name', 'tool_args').")
```

---

## Source declarations: src/agenticlens/models/trace.py

Source: [src/agenticlens/models/trace.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/models/trace.py)

```python
class SpanType(str, Enum):
    MODEL_CALL = 'model_call'
    PLANNING = 'planning'
    MEMORY_READ = 'memory_read'
    MEMORY_WRITE = 'memory_write'
    RETRIEVAL = 'retrieval'
    TOOL_CALL = 'tool_call'
    VALIDATION = 'validation'
    RETRY = 'retry'
    DELEGATION = 'delegation'
    FINAL_RESPONSE = 'final_response'
    CUSTOM = 'custom'
class RunStatus(str, Enum):
    RUNNING = 'running'
    SUCCEEDED = 'succeeded'
    FAILED = 'failed'
class Span(BaseModel):
    span_id: str = Field(default_factory=_uuid)
    parent_span_id: str | None = None
    name: str
    span_type: SpanType
    agent_name: str | None = None
    model_name: str | None = None
    provider: str | None = None
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    latency_ms: float = Field(default=0.0, ge=0)
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    estimated_cost_usd: float | None = Field(default=None, ge=0)
    tool_name: str | None = None
    retry_number: int | None = Field(default=None, ge=0)
    status: RunStatus = RunStatus.RUNNING
    error_type: str | None = None
    error_message: str | None = None
    input_reference: str | None = None
    output_reference: str | None = None
    input_data: Any | None = Field(default=None, description='Optional captured input after configured redaction.')
    output_data: Any | None = Field(default=None, description='Optional captured output after configured redaction.')
    attributes: dict[str, Any] = Field(default_factory=dict)
    @property
    def total_tokens(self) -> int: ...
class Run(BaseModel):
    schema_version: str = '1.0'
    run_id: str = Field(default_factory=_uuid)
    trace_id: str = Field(default_factory=_uuid)
    application_name: str
    framework: str | None = None
    framework_version: str | None = None
    task_id: str | None = None
    task_type: str | None = None
    experiment_id: str | None = None
    variant_id: str | None = None
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    status: RunStatus = RunStatus.RUNNING
    spans: list[Span] = Field(default_factory=list)
    task_success: bool | None = None
    error_type: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    @model_validator(mode='after')
    def validate_span_tree(self) -> 'Run': ...
    @property
    def total_input_tokens(self) -> int: ...
    @property
    def total_output_tokens(self) -> int: ...
    @property
    def total_tokens(self) -> int: ...
    @property
    def total_latency_ms(self) -> float: ...
    @property
    def estimated_cost_usd(self) -> float | None: ...
class MetricValue(BaseModel):
    name: str
    value: float
    unit: str
    estimated: bool = False
    attributes: dict[str, Any] = Field(default_factory=dict)
class Evidence(BaseModel):
    source: str
    span_id: str | None = None
    timestamp: datetime | None = None
    confidence: float = Field(default=1.0, ge=0, le=1)
    reasoning: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)
class Finding(BaseModel):
    finding_id: str = Field(default_factory=_uuid)
    category: str
    title: str
    description: str
    severity: str
    confidence: float = Field(ge=0, le=1)
    span_ids: list[str] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
```

---

## Source declarations: src/agenticlens/models/workflow.py

Source: [src/agenticlens/models/workflow.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/models/workflow.py)

```python
class Workflow(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    start_time: datetime
    end_time: datetime | None = None
    steps: list[Step] = Field(default_factory=list)
    chaos_events: list[dict[str, Any]] = Field(default_factory=list, description="Additive workflow.json extension (schema v1.1, see docs/workflow-schema-spec.md). Populated by fault-injection tools such as agentic-chaos; each entry is expected to carry at least 'fault_type', 'outcome', and (when correlated to a step) 'step_id'/'step_name'. Left loosely typed here so AgenticLens has no hard dependency on the producer.")
    @property
    def total_tokens(self) -> int: ...
    @property
    def total_cost(self) -> float | None: ...
    @property
    def latency(self) -> float: ...
```

---

## Source declarations: src/agenticlens/optimization/__init__.py

Source: [src/agenticlens/optimization/__init__.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/optimization/__init__.py)

```python
__all__ = ['DEFAULT_RULES', 'MemoryRule', 'MetricChange', 'ObservedOutcome', 'Opportunity', 'OpportunityEvidence', 'OptimizationConfig', 'OptimizationReport', 'OptimizationRule', 'OutcomeEvaluation', 'ProjectedBenefit', 'PromptCachingRule', 'PromptCompressionRule', 'QualityCostTradeoffRule', 'QualityRisk', 'RecommendationDecision', 'RecommendationLedger', 'RedundantStepRule', 'RetrievalRule', 'RetryPolicyRule', 'ToolCachingRule', 'TradeoffAnalysis', 'UnnecessaryHandoffRule', 'VariantTradeoff', 'analyze_optimizations', 'analyze_tradeoffs', 'evaluate_outcome', 'load_optimization_config', 'load_optimization_report', 'load_traces', 'render_optimization_markdown', 'render_outcome_markdown', 'report_sha256', 'save_optimization_report']
```

---

## Source declarations: src/agenticlens/optimization/engine.py

Source: [src/agenticlens/optimization/engine.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/optimization/engine.py)

```python
def analyze_optimizations(runs: Sequence[Run], config: OptimizationConfig | None=None, *, rules: Sequence[OptimizationRule] | None=None, baseline_variant_id: str | None=None) -> OptimizationReport: ...
```

---

## Source declarations: src/agenticlens/optimization/io.py

Source: [src/agenticlens/optimization/io.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/optimization/io.py)

```python
def load_traces(paths: Sequence[Path]) -> list[Run]: ...
def load_optimization_config(path: Path) -> OptimizationConfig: ...
def save_optimization_report(report: OptimizationReport, path: Path) -> None: ...
def load_optimization_report(path: Path) -> OptimizationReport: ...
```

---

## Source declarations: src/agenticlens/optimization/models.py

Source: [src/agenticlens/optimization/models.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/optimization/models.py)

```python
class OptimizationModel(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)
class OptimizationConfig(OptimizationModel):
    prompt_cache_min_prefix_tokens: int = Field(default=512, ge=1)
    prompt_cache_min_repeats: int = Field(default=2, ge=2)
    prompt_cache_read_price_ratio: float = Field(default=0.1, ge=0, le=1, description='Cached-read price as a fraction of the uncached input price.')
    prompt_compression_min_input_tokens: int = Field(default=4000, ge=1)
    prompt_compression_min_ratio: float = Field(default=20.0, gt=0)
    prompt_compression_target_reduction: float = Field(default=0.3, gt=0, lt=1)
    retrieval_min_chunks: int = Field(default=4, ge=1)
    retrieval_max_utility: float = Field(default=0.5, ge=0, le=1)
    retrieval_rerank_min_rank: int = Field(default=4, ge=2, description='A used chunk ranked at or below this position suggests reranking.')
    memory_max_share: float = Field(default=0.4, gt=0, lt=1)
    memory_token_budget: int = Field(default=2000, ge=0)
    tool_cache_min_repeats: int = Field(default=2, ge=2)
    retry_min_unrecovered: int = Field(default=2, ge=1)
    redundant_step_min_repeats: int = Field(default=2, ge=2)
    handoff_min_occurrences: int = Field(default=1, ge=1)
    tradeoff_min_runs: int = Field(default=3, ge=1)
    tradeoff_max_success_rate_drop: float = Field(default=0.05, ge=0, le=1)
    tradeoff_min_cost_reduction: float = Field(default=0.1, gt=0, lt=1)
    confidence_level: float = Field(default=0.95, gt=0, lt=1)
    high_confidence_min_runs: int = Field(default=3, ge=1)
    high_confidence_min_share: float = Field(default=0.5, gt=0, le=1)
    monthly_runs: int | None = Field(default=None, ge=1)
class OpportunityEvidence(OptimizationModel):
    run_id: str
    span_ids: list[str] = Field(default_factory=list)
    measurements: dict[str, Any] = Field(default_factory=dict)
    reasoning: str
class ProjectedBenefit(OptimizationModel):
    tokens_per_run: float = Field(ge=0)
    cost_usd_per_run: float | None = Field(default=None, ge=0)
    latency_ms_per_run: float = Field(default=0.0, ge=0)
    monthly_cost_usd: float | None = Field(default=None, ge=0)
    cost_available: bool
    basis: str
class QualityRisk(OptimizationModel):
    kind: str
    severity: RiskSeverity
    description: str
class Opportunity(OptimizationModel):
    opportunity_id: str = Field(description='Stable hash of rule and subject.')
    rule_id: str
    rule_version: str
    area: OptimizationArea
    kind: str
    title: str
    summary: str
    action: str
    subject: dict[str, Any] = Field(default_factory=dict)
    thresholds: dict[str, Any] = Field(default_factory=dict)
    runs_observed: int = Field(ge=0)
    runs_affected: int = Field(ge=0)
    evidence: list[OpportunityEvidence]
    benefit: ProjectedBenefit
    confidence: Confidence
    confidence_reasons: list[str] = Field(default_factory=list)
    risks: list[QualityRisk] = Field(default_factory=list)
class VariantTradeoff(OptimizationModel):
    variant_id: str
    runs: int
    successes: int
    success_rate: float
    success_interval: tuple[float, float]
    mean_cost_usd: float | None = None
    cost_per_success_usd: float | None = None
    mean_latency_ms: float
    mean_tokens: float
    pareto_optimal: bool = False
    success_rate_delta: float | None = Field(default=None, description='Versus the baseline variant; negative is worse.')
    cost_delta_usd: float | None = Field(default=None, description='Versus the baseline variant; negative is cheaper.')
    p_value: float | None = None
class TradeoffAnalysis(OptimizationModel):
    baseline_variant_id: str | None = None
    variants: list[VariantTradeoff] = Field(default_factory=list)
    excluded: dict[str, str] = Field(default_factory=dict, description='Variant ID to the reason it was not compared.')
class RunSource(OptimizationModel):
    run_id: str
    variant_id: str | None = None
    spans: int
    tokens: int
    cost_usd: float | None = None
    task_success: bool | None = None
class OptimizationReport(OptimizationModel):
    schema_version: Literal['1.0'] = '1.0'
    runs: list[RunSource]
    total_tokens: int
    total_cost_usd: float | None = None
    config: OptimizationConfig
    opportunities: list[Opportunity] = Field(default_factory=list)
    tradeoffs: TradeoffAnalysis = Field(default_factory=TradeoffAnalysis)
    def opportunity(self, opportunity_id: str) -> Opportunity: ...
class RecommendationDecision(OptimizationModel):
    schema_version: Literal['1.0'] = '1.0'
    opportunity_id: str = Field(min_length=1)
    report_sha256: str = Field(min_length=64, max_length=64)
    status: DecisionStatus
    decided_by: str = Field(min_length=1)
    decided_at: datetime
    reason: str = ''
    change_reference: str | None = Field(default=None, description='PR, commit, or config version that adopted the change.')
class MetricChange(OptimizationModel):
    before: float | None = None
    after: float | None = None
    delta: float | None = None
class ObservedOutcome(OptimizationModel):
    before_runs: int
    after_runs: int
    tokens_per_run: MetricChange
    cost_usd_per_run: MetricChange
    latency_ms_per_run: MetricChange
    success_rate: MetricChange
    success_p_value: float | None = None
    still_detected: bool = Field(description='The same rule still finds this opportunity in the after runs.')
class OutcomeEvaluation(OptimizationModel):
    schema_version: Literal['1.0'] = '1.0'
    opportunity_id: str
    report_sha256: str
    decision_status: DecisionStatus | None = None
    projected: ProjectedBenefit
    observed: ObservedOutcome
    realized_basis: Literal['tokens', 'cost_usd'] | None = Field(default=None, description='Which per-run metric the realized ratio compares.')
    realized_ratio: float | None = Field(default=None, description='Observed per-run saving divided by the projected saving.')
    status: OutcomeStatus
    reasons: list[str] = Field(default_factory=list)
```

---

## Source declarations: src/agenticlens/optimization/outcomes.py

Source: [src/agenticlens/optimization/outcomes.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/optimization/outcomes.py)

```python
def evaluate_outcome(report: OptimizationReport, opportunity_id: str, before: Sequence[Run], after: Sequence[Run], *, ledger: RecommendationLedger | None=None, min_runs: int=3) -> OutcomeEvaluation: ...
```

---

## Source declarations: src/agenticlens/optimization/render.py

Source: [src/agenticlens/optimization/render.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/optimization/render.py)

```python
def render_optimization_markdown(report: OptimizationReport, statuses: dict[str, DecisionStatus] | None=None) -> str: ...
def render_outcome_markdown(outcome: OutcomeEvaluation) -> str: ...
```

---

## Source declarations: src/agenticlens/optimization/rules.py

Source: [src/agenticlens/optimization/rules.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/optimization/rules.py)

```python
class OptimizationRule(Protocol):
    rule_id: str
    version: str
    def analyze(self, runs: Sequence[Run], config: OptimizationConfig) -> list[Opportunity]: ...
def fingerprint(value: Any) -> str: ...
def opportunity_id(rule_id: str, subject: dict[str, Any]) -> str: ...
def input_fingerprint(span: Span) -> str | None: ...
def output_fingerprint(span: Span) -> str | None: ...
def subtree(run: Run, root: Span) -> list[Span]: ...
def run_cost(run: Run) -> float | None: ...
def run_cost_per_token(run: Run) -> float | None: ...
@dataclass
class Savings():
    tokens: float = 0.0
    cost: float | None = 0.0
    latency_ms: float = 0.0
    evidence: list[OpportunityEvidence] = field(default_factory=list)
    def add(self, tokens: float, cost: float | None, latency_ms: float=0.0) -> None: ...
    def add_spans(self, spans: Iterable[Span]) -> None: ...
def grade_confidence(runs_affected: int, runs_observed: int, cost_available: bool, config: OptimizationConfig, *, cap: Confidence | None=None, reasons: Sequence[str]=()) -> tuple[Confidence, list[str]]: ...
def build_opportunity(rule: OptimizationRule, *, area: OptimizationArea, kind: str, title: str, summary: str, action: str, subject: dict[str, Any], thresholds: dict[str, Any], runs: Sequence[Run], savings: Savings, basis: str, config: OptimizationConfig, risks: list[QualityRisk], confidence_cap: Confidence | None=None, confidence_reasons: Sequence[str]=()) -> Opportunity: ...
class PromptCachingRule():
    rule_id = 'prompt_caching'
    version = '1'
    def analyze(self, runs: Sequence[Run], config: OptimizationConfig) -> list[Opportunity]: ...
class PromptCompressionRule():
    rule_id = 'prompt_compression'
    version = '1'
    def analyze(self, runs: Sequence[Run], config: OptimizationConfig) -> list[Opportunity]: ...
class RetrievalRule():
    rule_id = 'retrieval'
    version = '1'
    def analyze(self, runs: Sequence[Run], config: OptimizationConfig) -> list[Opportunity]: ...
class MemoryRule():
    rule_id = 'memory'
    version = '1'
    def analyze(self, runs: Sequence[Run], config: OptimizationConfig) -> list[Opportunity]: ...
class ToolCachingRule():
    rule_id = 'tool_caching'
    version = '1'
    def analyze(self, runs: Sequence[Run], config: OptimizationConfig) -> list[Opportunity]: ...
class RetryPolicyRule():
    rule_id = 'retry_policy'
    version = '1'
    def analyze(self, runs: Sequence[Run], config: OptimizationConfig) -> list[Opportunity]: ...
class RedundantStepRule():
    rule_id = 'redundant_step'
    version = '1'
    span_types = frozenset({SpanType.MODEL_CALL, SpanType.RETRIEVAL, SpanType.PLANNING, SpanType.VALIDATION, SpanType.MEMORY_READ})
    def analyze(self, runs: Sequence[Run], config: OptimizationConfig) -> list[Opportunity]: ...
class UnnecessaryHandoffRule():
    rule_id = 'unnecessary_handoff'
    version = '1'
    def analyze(self, runs: Sequence[Run], config: OptimizationConfig) -> list[Opportunity]: ...
```

---

## Source declarations: src/agenticlens/optimization/tracking.py

Source: [src/agenticlens/optimization/tracking.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/optimization/tracking.py)

```python
def report_sha256(report: OptimizationReport) -> str: ...
class RecommendationLedger():
    def __init__(self, path: str | Path): ...
    def decisions(self) -> list[RecommendationDecision]: ...
    def status(self, opportunity_id: str, report_digest: str | None=None) -> DecisionStatus: ...
    def record(self, report: OptimizationReport, decision: RecommendationDecision) -> RecommendationDecision: ...
    def summary(self, report: OptimizationReport) -> dict[str, DecisionStatus]: ...
```

---

## Source declarations: src/agenticlens/optimization/tradeoffs.py

Source: [src/agenticlens/optimization/tradeoffs.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/optimization/tradeoffs.py)

```python
def analyze_tradeoffs(runs: Sequence[Run], config: OptimizationConfig, *, baseline_variant_id: str | None=None) -> TradeoffAnalysis: ...
class QualityCostTradeoffRule():
    rule_id = 'quality_cost_tradeoff'
    version = '1'
    def __init__(self, baseline_variant_id: str | None=None) -> None: ...
    def analyze(self, runs: Sequence[Run], config: OptimizationConfig) -> list[Opportunity]: ...
```

---

## Source declarations: src/agenticlens/profiler/__init__.py

Source: [src/agenticlens/profiler/__init__.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/profiler/__init__.py)

```python
__all__ = ['StepHandle', 'profile', 'step']
```

---

## Source declarations: src/agenticlens/profiler/context.py

Source: [src/agenticlens/profiler/context.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/profiler/context.py)

```python
def get_active_workflow() -> Workflow: ...
```

---

## Source declarations: src/agenticlens/profiler/profile.py

Source: [src/agenticlens/profiler/profile.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/profiler/profile.py)

```python
class profile():
    def __init__(self, name: str, config: AgenticLensConfig | None=None) -> None: ...
```

---

## Source declarations: src/agenticlens/profiler/step.py

Source: [src/agenticlens/profiler/step.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/profiler/step.py)

```python
class StepHandle():
    def __init__(self, step: Step) -> None: ...
    def record(self, response: Any, ttft: float | None=None) -> None: ...
class step():
    def __init__(self, name: str, type: StepType | str, provider: str | None=None, model: str | None=None, agent_name: str | None=None, agent_role: str | None=None, parent_step_id: str | None=None, handoff_from: str | None=None, handoff_to: str | None=None, **metadata: Any) -> None: ...
```

---

## Source declarations: src/agenticlens/providers/__init__.py

Source: [src/agenticlens/providers/__init__.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/providers/__init__.py)

```python
__all__ = ['AnthropicProvider', 'BaseProvider', 'OpenAIProvider', 'TokenUsage', 'detect_provider', 'get_provider']
```

---

## Source declarations: src/agenticlens/providers/anthropic.py

Source: [src/agenticlens/providers/anthropic.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/providers/anthropic.py)

```python
class AnthropicProvider(BaseProvider):
    name = 'anthropic'
    def supports(self, response: Any) -> bool: ...
    def extract_usage(self, response: Any) -> TokenUsage: ...
```

---

## Source declarations: src/agenticlens/providers/base.py

Source: [src/agenticlens/providers/base.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/providers/base.py)

```python
class TokenUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
class BaseProvider(ABC):
    name: str
    @abstractmethod
    def extract_usage(self, response: Any) -> TokenUsage: ...
    @abstractmethod
    def supports(self, response: Any) -> bool: ...
```

---

## Source declarations: src/agenticlens/providers/openai.py

Source: [src/agenticlens/providers/openai.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/providers/openai.py)

```python
class OpenAIProvider(BaseProvider):
    name = 'openai'
    def supports(self, response: Any) -> bool: ...
    def extract_usage(self, response: Any) -> TokenUsage: ...
```

---

## Source declarations: src/agenticlens/providers/registry.py

Source: [src/agenticlens/providers/registry.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/providers/registry.py)

```python
def get_provider(name: str) -> BaseProvider: ...
def detect_provider(response: object) -> BaseProvider | None: ...
```

---

## Source declarations: src/agenticlens/recommenders/__init__.py

Source: [src/agenticlens/recommenders/__init__.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/recommenders/__init__.py)

```python
__all__ = ['BaseRecommender', 'ChaosImpactRecommender', 'DuplicateToolCallsRecommender', 'ExcessiveChunksRecommender', 'HandoffBloatRecommender', 'LongHistoryRecommender', 'RAGChunkUtilityRecommender', 'ModelSwapRecommender', 'RecommendationEngine', 'RepeatedSystemPromptRecommender']
```

---

## Source declarations: src/agenticlens/recommenders/base.py

Source: [src/agenticlens/recommenders/base.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/recommenders/base.py)

```python
class BaseRecommender(ABC):
    @abstractmethod
    def evaluate(self, workflow: Workflow, config: RecommenderConfig) -> list[Recommendation]: ...
```

---

## Source declarations: src/agenticlens/recommenders/chaos_impact.py

Source: [src/agenticlens/recommenders/chaos_impact.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/recommenders/chaos_impact.py)

```python
class ChaosImpactRecommender(BaseRecommender):
    def evaluate(self, workflow: Workflow, config: RecommenderConfig) -> list[Recommendation]: ...
```

---

## Source declarations: src/agenticlens/recommenders/duplicate_tool_calls.py

Source: [src/agenticlens/recommenders/duplicate_tool_calls.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/recommenders/duplicate_tool_calls.py)

```python
class DuplicateToolCallsRecommender(BaseRecommender):
    def evaluate(self, workflow: Workflow, config: RecommenderConfig) -> list[Recommendation]: ...
```

---

## Source declarations: src/agenticlens/recommenders/engine.py

Source: [src/agenticlens/recommenders/engine.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/recommenders/engine.py)

```python
class RecommendationEngine():
    def __init__(self, recommenders: list[BaseRecommender] | None=None, config: RecommenderConfig | None=None) -> None: ...
    def run(self, workflow: Workflow) -> list[Recommendation]: ...
    @staticmethod
    def estimated_savings_pct(workflow: Workflow, recommendations: list[Recommendation]) -> float: ...
    @staticmethod
    def estimated_cost_savings(recommendations: list[Recommendation]) -> float | None: ...
```

---

## Source declarations: src/agenticlens/recommenders/excessive_chunks.py

Source: [src/agenticlens/recommenders/excessive_chunks.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/recommenders/excessive_chunks.py)

```python
class ExcessiveChunksRecommender(BaseRecommender):
    def evaluate(self, workflow: Workflow, config: RecommenderConfig) -> list[Recommendation]: ...
```

---

## Source declarations: src/agenticlens/recommenders/handoff_bloat.py

Source: [src/agenticlens/recommenders/handoff_bloat.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/recommenders/handoff_bloat.py)

```python
class HandoffBloatRecommender(BaseRecommender):
    def evaluate(self, workflow: Workflow, config: RecommenderConfig) -> list[Recommendation]: ...
```

---

## Source declarations: src/agenticlens/recommenders/long_history.py

Source: [src/agenticlens/recommenders/long_history.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/recommenders/long_history.py)

```python
class LongHistoryRecommender(BaseRecommender):
    def evaluate(self, workflow: Workflow, config: RecommenderConfig) -> list[Recommendation]: ...
```

---

## Source declarations: src/agenticlens/recommenders/model_swap.py

Source: [src/agenticlens/recommenders/model_swap.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/recommenders/model_swap.py)

```python
class ModelSwapRecommender(BaseRecommender):
    def __init__(self, candidates: list[str] | None=None, pricing_overrides: dict[str, ModelPricing] | None=None, live_pricing: LivePricingConfig | None=None) -> None: ...
    def evaluate(self, workflow: Workflow, config: RecommenderConfig) -> list[Recommendation]: ...
```

---

## Source declarations: src/agenticlens/recommenders/rag_chunk_utility.py

Source: [src/agenticlens/recommenders/rag_chunk_utility.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/recommenders/rag_chunk_utility.py)

```python
class RAGChunkUtilityRecommender(BaseRecommender):
    def evaluate(self, workflow: Workflow, config: RecommenderConfig) -> list[Recommendation]: ...
```

---

## Source declarations: src/agenticlens/recommenders/repeated_prompt.py

Source: [src/agenticlens/recommenders/repeated_prompt.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/recommenders/repeated_prompt.py)

```python
class RepeatedSystemPromptRecommender(BaseRecommender):
    def evaluate(self, workflow: Workflow, config: RecommenderConfig) -> list[Recommendation]: ...
```

---

## Source declarations: src/agenticlens/recommenders/utils.py

Source: [src/agenticlens/recommenders/utils.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/recommenders/utils.py)

```python
def prefix_hash(text: str, n_words: int) -> str: ...
```

---

## Source declarations: src/agenticlens/reports/__init__.py

Source: [src/agenticlens/reports/__init__.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/reports/__init__.py)

```python
__all__ = ['render_dashboard_html', 'render_history_html', 'render_trace', 'render_trace_markdown', 'save_dashboard_html']
```

---

## Source declarations: src/agenticlens/reports/dashboard.py

Source: [src/agenticlens/reports/dashboard.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/reports/dashboard.py)

```python
def render_dashboard_html(*, workflow: Workflow | None=None, recommendations: list[Recommendation] | None=None, run: Run | None=None, evaluation: EvaluationReport | None=None, gate: GateDecision | None=None, comparison: ComparisonReport | None=None, title: str | None=None, extra_header_html: str | None=None) -> str: ...
def render_history_html(runs: list[Run], *, title: str | None=None, trace_link_base: str | None=None) -> str: ...
def save_dashboard_html(path: Path, *, workflow: Workflow | None=None, recommendations: list[Recommendation] | None=None, run: Run | None=None, evaluation: EvaluationReport | None=None, gate: GateDecision | None=None, comparison: ComparisonReport | None=None, title: str | None=None) -> None: ...
```

---

## Source declarations: src/agenticlens/reports/trace.py

Source: [src/agenticlens/reports/trace.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/reports/trace.py)

```python
def render_trace(console: Console, run: Run) -> None: ...
def render_trace_markdown(run: Run) -> str: ...
```

---

## Source declarations: src/agenticlens/routing/__init__.py

Source: [src/agenticlens/routing/__init__.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/routing/__init__.py)

```python
__all__ = ['RetryableRouteError', 'RouteAttempt', 'RouteCallback', 'RouteDecision', 'RouteOutcome', 'RouteRequest', 'RouteTarget', 'Router', 'RoutingAuditLog', 'RoutingConstraints', 'RoutingPolicy', 'RoutingResult', 'RoutingSummary', 'artifact_sha256', 'summarize_routing']
```

---

## Source declarations: src/agenticlens/routing/audit.py

Source: [src/agenticlens/routing/audit.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/routing/audit.py)

```python
def artifact_sha256(model: BaseModel) -> str: ...
class RoutingAuditLog():
    def __init__(self, path: str | Path): ...
    def append(self, event: str, decision_id: str, record: BaseModel) -> None: ...
```

---

## Source declarations: src/agenticlens/routing/metrics.py

Source: [src/agenticlens/routing/metrics.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/routing/metrics.py)

```python
def summarize_routing(results: list[RoutingResult]) -> RoutingSummary: ...
```

---

## Source declarations: src/agenticlens/routing/models.py

Source: [src/agenticlens/routing/models.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/routing/models.py)

```python
class RoutingModel(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)
class RoutingConstraints(ModelConstraints):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)
class RoutingPolicy(RoutingModel):
    name: str = Field(default='routing', min_length=1)
    version: str = Field(default='1', min_length=1)
    mode: Literal['advisory', 'enforce', 'shadow', 'canary'] = 'advisory'
    strategy: Literal['score', 'rule'] = 'score'
    rules: dict[str, list[str]] = Field(default_factory=dict)
    constraints: RoutingConstraints = Field(default_factory=RoutingConstraints)
    minimum_confidence: Confidence = 'medium'
    on_unroutable: Literal['block', 'escalate'] = 'escalate'
    baseline_variant_id: str | None = None
    canary_fraction: float = Field(default=0.1, ge=0, le=1)
    allocation_salt: str = 'lens-routing-v1'
    max_attempts: int = Field(default=3, ge=1, le=20)
    @field_validator('constraints', mode='before')
    @classmethod
    def parse_constraints(cls, value: object) -> object: ...
    @model_validator(mode='after')
    def check_modes(self) -> 'RoutingPolicy': ...
class RouteRequest(RoutingModel):
    request_id: str = Field(min_length=1)
    category_id: str = Field(min_length=1)
class RouteTarget(RoutingModel):
    variant_id: str
    model: str
    provider: str | None = None
    deployment: str | None = None
    source_index: int
    weighted_score: float | None = None
class RouteDecision(RoutingModel):
    schema_version: Literal['1.0'] = '1.0'
    decision_id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    request: RouteRequest
    policy_name: str
    policy_version: str
    policy_sha256: str
    report_sha256: str
    mode: Literal['advisory', 'enforce', 'shadow', 'canary']
    status: Literal['selected', 'blocked', 'escalated']
    confidence: Confidence | None = None
    reasons: list[str] = Field(default_factory=list)
    rejected: dict[str, list[str]] = Field(default_factory=dict)
    targets: list[RouteTarget] = Field(default_factory=list)
    shadow_target: RouteTarget | None = None
    cohort: Literal['baseline', 'canary'] | None = None
class RouteOutcome(RoutingModel):
    success: bool
    cost_usd: float | None = Field(default=None, ge=0)
class RouteAttempt(RoutingModel):
    target: RouteTarget
    role: Literal['primary', 'fallback', 'shadow']
    status: Literal['succeeded', 'unsuccessful', 'retryable_error', 'error']
    latency_ms: float = Field(ge=0)
    cost_usd: float | None = Field(default=None, ge=0)
class RoutingResult(RoutingModel):
    decision: RouteDecision
    attempts: list[RouteAttempt] = Field(default_factory=list)
    served_variant_id: str | None = None
    status: Literal['advisory', 'blocked', 'escalated', 'succeeded', 'failed']
class RoutingSummary(RoutingModel):
    results: int
    served: int
    shadow_attempts: int
    shadow_pairs: int
    mean_shadow_latency_delta_ms: float | None = None
    mean_shadow_cost_delta_usd: float | None = None
    shadow_success_rate: float | None = None
    primary_success_rate: float | None = None
```

---

## Source declarations: src/agenticlens/routing/router.py

Source: [src/agenticlens/routing/router.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/routing/router.py)

```python
class RetryableRouteError(Exception):
    ...
class Router():
    def __init__(self, report: ModelFitReport, policy: RoutingPolicy | None=None, *, audit: RoutingAuditLog | None=None): ...
    def decide(self, request: RouteRequest) -> RouteDecision: ...
    def run(self, request: RouteRequest, callbacks: Mapping[str, RouteCallback], *, shadow_callbacks: Mapping[str, RouteCallback] | None=None) -> RoutingResult: ...
```

---

## Source declarations: src/agenticlens/suites/__init__.py

Source: [src/agenticlens/suites/__init__.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/suites/__init__.py)

```python
__all__ = ['DEFAULT_SENSITIVE_KEYS', 'DOMAIN_KEY', 'PROVENANCE_KEY', 'REVIEW_STATUS_KEY', 'SOURCE_KEY', 'SPLIT_KEY', 'SUITE_VERSION_SCHEMA_VERSION', 'VARIATIONS', 'ApprovalCheck', 'ApprovalError', 'ApprovalRecord', 'CaseChange', 'CaseSource', 'ConversionResult', 'DuplicateGroup', 'DuplicateReport', 'FeedbackBatch', 'FeedbackRecord', 'ImmutableVersionError', 'IntegrityError', 'MaskedLocation', 'MaskingReport', 'PIIMasker', 'SkippedItem', 'SuiteDiff', 'SuiteImportError', 'SuiteStore', 'SuiteStoreError', 'SuiteSummary', 'SuiteVersion', 'VerificationResult', 'add_case', 'approval_checks', 'assign_splits', 'canonical_json', 'case_from_feedback', 'case_from_run', 'case_lineage', 'case_review_status', 'case_source_kind', 'cases_from_feedback', 'cases_from_runs', 'content_sha256', 'diff_suites', 'drop_duplicates', 'filter_suite', 'find_duplicates', 'generate_variations', 'import_cases', 'import_csv', 'import_json', 'import_suite', 'load_feedback', 'load_suite_file', 'mask_case', 'mask_suite', 'merge_suites', 'new_suite', 'normalize_input', 'parse_ref', 'record_sha256', 'remove_cases', 'review_cases', 'save_suite_file', 'scan_suite', 'summarize_suite', 'tag_cases', 'update_case', 'vary_case']
```

---

## Source declarations: src/agenticlens/suites/conversion.py

Source: [src/agenticlens/suites/conversion.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/suites/conversion.py)

```python
def case_from_run(run: Run, *, latency_margin: float | None=1.5, cost_margin: float | None=1.5, include_output: bool=False, case_id: str | None=None) -> TestCase: ...
def cases_from_runs(runs: Iterable[Run], *, latency_margin: float | None=1.5, cost_margin: float | None=1.5, include_output: bool=False) -> ConversionResult: ...
def load_feedback(path: Path) -> list[FeedbackRecord]: ...
def case_from_feedback(record: FeedbackRecord, *, runs: Mapping[str, Run] | None=None) -> TestCase: ...
def cases_from_feedback(records: Iterable[FeedbackRecord], *, runs: Iterable[Run]=()) -> ConversionResult: ...
```

---

## Source declarations: src/agenticlens/suites/duplicates.py

Source: [src/agenticlens/suites/duplicates.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/suites/duplicates.py)

```python
def normalize_input(value: Any) -> str: ...
def find_duplicates(suite: TestSuite, *, threshold: float=0.85, include_variants: bool=False) -> DuplicateReport: ...
def drop_duplicates(suite: TestSuite, report: DuplicateReport) -> TestSuite: ...
```

---

## Source declarations: src/agenticlens/suites/editing.py

Source: [src/agenticlens/suites/editing.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/suites/editing.py)

```python
def load_suite_file(path: Path) -> TestSuite: ...
def suite_to_data(suite: TestSuite) -> dict[str, Any]: ...
def save_suite_file(suite: TestSuite, path: Path) -> None: ...
def new_suite(*, name: str, version: str, cases: list[TestCase], description: str='') -> TestSuite: ...
def add_case(suite: TestSuite, case: TestCase | dict[str, Any]) -> TestSuite: ...
def update_case(suite: TestSuite, case_id: str, **changes: Any) -> TestSuite: ...
def remove_cases(suite: TestSuite, case_ids: Iterable[str]) -> TestSuite: ...
def tag_cases(suite: TestSuite, *, case_ids: Iterable[str] | None=None, add: Iterable[str]=(), remove: Iterable[str]=(), domain: str | None=None) -> TestSuite: ...
def review_cases(suite: TestSuite, *, status: ReviewStatus, reviewer: str, case_ids: Iterable[str] | None=None, notes: str='') -> TestSuite: ...
def merge_suites(base: TestSuite, *others: TestSuite, on_conflict: str='error') -> TestSuite: ...
def case_review_status(case: TestCase) -> str: ...
def case_source_kind(case: TestCase) -> str: ...
def case_lineage(case: TestCase) -> str: ...
def filter_suite(suite: TestSuite, *, tags: Iterable[str]=(), exclude_tags: Iterable[str]=(), domains: Iterable[str]=(), splits: Iterable[str]=(), review_statuses: Iterable[str]=()) -> TestSuite: ...
def summarize_suite(suite: TestSuite) -> SuiteSummary: ...
def diff_suites(old: TestSuite, new: TestSuite) -> SuiteDiff: ...
```

---

## Source declarations: src/agenticlens/suites/importers.py

Source: [src/agenticlens/suites/importers.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/suites/importers.py)

```python
class SuiteImportError(ValueError):
    ...
def import_csv(path: Path) -> list[TestCase]: ...
def import_json(path: Path) -> list[TestCase]: ...
def import_cases(path: Path) -> list[TestCase]: ...
def import_suite(path: Path, *, name: str, version: str, description: str='') -> TestSuite: ...
```

---

## Source declarations: src/agenticlens/suites/models.py

Source: [src/agenticlens/suites/models.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/suites/models.py)

```python
class CaseSource(BaseModel):
    kind: SourceKind
    trace_id: str | None = None
    run_id: str | None = None
    feedback_id: str | None = None
    parent_case_id: str | None = Field(default=None, description='Case this synthetic variation was derived from.')
    variation: str | None = None
    seed: int | None = None
    file: str | None = Field(default=None, description='Import file name, without directories.')
    row: int | None = Field(default=None, description='1-based data row or record in the file.')
class SkippedItem(BaseModel):
    source_id: str
    reason: str
class FeedbackRecord(BaseModel):
    feedback_id: str = Field(min_length=1)
    input: Any = None
    output: str | None = None
    rating: Literal['positive', 'negative'] | None = None
    score: float | None = Field(default=None, ge=0, le=1)
    corrected_output: str | None = None
    comment: str = ''
    trace_id: str | None = None
    run_id: str | None = None
    submitted_by: str | None = None
    tags: list[str] = Field(default_factory=list)
    domain: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    @model_validator(mode='after')
    def require_signal(self) -> 'FeedbackRecord': ...
class FeedbackBatch(BaseModel):
    schema_version: str = '1.0'
    feedback: list[FeedbackRecord]
    @model_validator(mode='after')
    def unique_ids(self) -> 'FeedbackBatch': ...
class ApprovalCheck(BaseModel):
    name: str
    passed: bool
    detail: str
class ApprovalRecord(BaseModel):
    approved_by: str = Field(min_length=1)
    approved_at: datetime
    notes: str = ''
    checks: list[ApprovalCheck] = Field(default_factory=list)
class SuiteVersion(BaseModel):
    schema_version: str = SUITE_VERSION_SCHEMA_VERSION
    name: str
    version: str
    status: Literal['approved'] = 'approved'
    content_sha256: str = Field(pattern='^[0-9a-f]{64}$')
    record_sha256: str = Field(default='', description='SHA-256 of the canonical envelope without this field.')
    case_count: int = Field(ge=1)
    parent_version: str | None = None
    approval: ApprovalRecord
    suite: dict[str, Any]
class VerificationResult(BaseModel):
    name: str
    version: str
    path: str
    ok: bool
    expected_sha256: str | None = None
    actual_sha256: str | None = None
    error: str | None = None
class SuiteSummary(BaseModel):
    name: str
    version: str
    total_cases: int
    by_split: dict[str, int] = Field(default_factory=dict)
    by_domain: dict[str, int] = Field(default_factory=dict)
    by_tag: dict[str, int] = Field(default_factory=dict)
    by_source: dict[str, int] = Field(default_factory=dict)
    by_review_status: dict[str, int] = Field(default_factory=dict)
class CaseChange(BaseModel):
    case_id: str
    fields: list[str]
class SuiteDiff(BaseModel):
    old: str
    new: str
    added: list[str] = Field(default_factory=list)
    removed: list[str] = Field(default_factory=list)
    changed: list[CaseChange] = Field(default_factory=list)
    unchanged: int = 0
    @property
    def is_empty(self) -> bool: ...
class DuplicateGroup(BaseModel):
    kind: Literal['exact', 'near']
    case_ids: list[str] = Field(min_length=2)
    keep: str = Field(description='Case kept when duplicates are dropped (the first one).')
    similarity: float = Field(ge=0, le=1, description='Lowest pairwise similarity in the group.')
    conflicting: bool = Field(description='True when the cases share an input but expect different results.')
class DuplicateReport(BaseModel):
    schema_version: str = '1.0'
    suite_name: str
    threshold: float = Field(ge=0, le=1)
    total_cases: int
    groups: list[DuplicateGroup] = Field(default_factory=list)
    duplicate_case_ids: list[str] = Field(default_factory=list, description='Every grouped case except the one kept.')
    conflicting_groups: int = 0
class MaskedLocation(BaseModel):
    case_id: str
    field: str = Field(description='Dotted path to the masked value, e.g. input.customer.email.')
    pii_type: PIIType
class MaskingReport(BaseModel):
    schema_version: str = '1.0'
    suite_name: str
    strategy: MaskingStrategy
    applied: bool = Field(description='False for a scan that reported but changed nothing.')
    total: int = 0
    counts: dict[str, int] = Field(default_factory=dict)
    locations: list[MaskedLocation] = Field(default_factory=list)
class ConversionResult(BaseModel):
    cases: list[TestCase] = Field(default_factory=list)
    skipped: list[SkippedItem] = Field(default_factory=list)
```

---

## Source declarations: src/agenticlens/suites/pii.py

Source: [src/agenticlens/suites/pii.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/suites/pii.py)

```python
def is_placeholder(value: str) -> bool: ...
def preserve_placeholders(text: str, transform: Callable[[str], str]) -> str: ...
class PIIMasker():
    def __init__(self, *, strategy: MaskingStrategy='redact', salt: str='', sensitive_keys: Iterable[str]=DEFAULT_SENSITIVE_KEYS) -> None: ...
    def placeholder(self, pii_type: PIIType, value: str) -> str: ...
    def mask_text(self, text: str) -> tuple[str, list[PIIType]]: ...
    def is_sensitive_key(self, key: str) -> bool: ...
    def mask_value(self, value: Any, path: str='') -> tuple[Any, list[tuple[str, PIIType]]]: ...
def mask_case(case: TestCase, masker: PIIMasker) -> tuple[TestCase, list[MaskedLocation]]: ...
def mask_suite(suite: TestSuite, masker: PIIMasker | None=None, *, apply: bool=True) -> tuple[TestSuite, MaskingReport]: ...
def scan_suite(suite: TestSuite, masker: PIIMasker | None=None) -> MaskingReport: ...
```

---

## Source declarations: src/agenticlens/suites/splits.py

Source: [src/agenticlens/suites/splits.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/suites/splits.py)

```python
def assign_splits(suite: TestSuite, *, train_ratio: float=0.7, validation_ratio: float=0.15, test_ratio: float=0.15, seed: int=0, overwrite: bool=False) -> TestSuite: ...
```

---

## Source declarations: src/agenticlens/suites/store.py

Source: [src/agenticlens/suites/store.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/suites/store.py)

```python
class SuiteStoreError(ValueError):
    ...
class ApprovalError(SuiteStoreError):
    def __init__(self, checks: list[ApprovalCheck]) -> None: ...
class ImmutableVersionError(SuiteStoreError):
    ...
class IntegrityError(SuiteStoreError):
    ...
def canonical_json(data: Any) -> str: ...
def content_sha256(suite_data: dict[str, Any]) -> str: ...
def record_sha256(envelope: dict[str, Any]) -> str: ...
def parse_ref(ref: str) -> tuple[str, str]: ...
def approval_checks(suite: TestSuite, *, allow_unreviewed: bool=False, allow_pii: bool=False, masker: PIIMasker | None=None) -> list[ApprovalCheck]: ...
class SuiteStore():
    def __init__(self, root: Path) -> None: ...
    def path_for(self, name: str, version: str) -> Path: ...
    def approve(self, suite: TestSuite, *, approved_by: str, notes: str='', approved_at: datetime | None=None, parent_version: str | None=None, allow_unreviewed: bool=False, allow_pii: bool=False, masker: PIIMasker | None=None) -> SuiteVersion: ...
    def get(self, name: str, version: str) -> SuiteVersion: ...
    def load_suite(self, name: str, version: str) -> TestSuite: ...
    def versions(self, name: str | None=None) -> list[SuiteVersion]: ...
    def latest(self, name: str) -> SuiteVersion: ...
    def verify(self, refs: list[tuple[str, str]] | None=None) -> list[VerificationResult]: ...
```

---

## Source declarations: src/agenticlens/suites/variation.py

Source: [src/agenticlens/suites/variation.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/suites/variation.py)

```python
def vary_case(case: TestCase, kind: str, *, seed: int=0) -> TestCase | None: ...
def generate_variations(suite: TestSuite, *, per_case: int=2, kinds: Iterable[str] | None=None, seed: int=0, include_synthetic: bool=False) -> list[TestCase]: ...
```

---

## Source declarations: src/agenticlens/validation/__init__.py

Source: [src/agenticlens/validation/__init__.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/validation/__init__.py)

```python
__all__ = ['ISSUE_RULES', 'SUPPORTED_SPEC_VERSIONS', 'ConformanceReport', 'ConformanceSummary', 'RuleResult', 'ValidationIssue', 'available_spec_versions', 'normalize_spec_version', 'resolve_provenance', 'validate_aios_artifact']
```

---

## Source declarations: src/agenticlens/validation/aios.py

Source: [src/agenticlens/validation/aios.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/validation/aios.py)

```python
class ValidationIssue(BaseModel):
    code: str
    level: str = 'error'
    source: str
    message: str
    location: str | None = None
    rule_id: str | None = Field(default=None, description='AIOS conformance rule this issue violates, when known.')
class RuleResult(BaseModel):
    rule_id: str
    role: str
    level: str
    check: str
    requirement: str
    result: Literal['pass', 'fail', 'not_checked']
    issues: int = 0
class ConformanceSummary(BaseModel):
    status: Literal['aligned', 'schema_valid', 'schema_invalid', 'semantic_invalid']
    schema_issues: int = 0
    semantic_issues: int = 0
    issue_codes: dict[str, int] = Field(default_factory=dict)
    rules_passed: int = 0
    rules_failed: int = 0
    rules_not_checked: int = 0
    failed_rules: list[str] = Field(default_factory=list)
class ConformanceReport(BaseModel):
    spec_version: str
    artifact_type: str
    artifact_path: str
    mode: str
    draft_alignment_claim: str
    schema_valid: bool
    semantic_valid: bool
    aligned: bool
    semantic_checked: bool = False
    issues: list[ValidationIssue] = Field(default_factory=list)
    declared_spec_version: str | None = Field(default=None, description="The artifact's own spec_version marker, if any.")
    rules_catalog: str | None = Field(default=None, description='Path of the conformance-rules.json catalog used, if found.')
    rules: list[RuleResult] = Field(default_factory=list)
    summary: ConformanceSummary | None = None
class SpecUnavailableError(ValueError):
    ...
def validate_aios_artifact(artifact_path: Path, *, spec_version: str | None=None, mode: str='conformance', spec_root: Path | None=None) -> ConformanceReport: ...
def normalize_spec_version(version: str) -> str: ...
def available_spec_versions(spec_root: Path | None=None) -> list[str]: ...
def resolve_provenance(record: dict[str, Any], subjects: dict[str, bytes], *, spec_root: Path | None=None) -> dict[str, Any]: ...
```

---

## Source declarations: src/agenticlens/validation/companions.py

Source: [src/agenticlens/validation/companions.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/validation/companions.py)

```python
def instant(value: str) -> datetime: ...
def cyclic(edges: list[tuple[str, str]]) -> bool: ...
def issues(document: dict[str, Any]) -> list[Issue]: ...
def provenance_issues(record: dict[str, Any]) -> list[Issue]: ...
def operational_issues(document: dict[str, Any]) -> list[Issue]: ...
def object_index(artifact: dict[str, Any]) -> dict[str, str]: ...
def resolve(record: dict[str, Any], held: dict[str, bytes], validate: Callable[[dict[str, Any]], bool]) -> dict[str, Any]: ...
```

---

## Data contract: schemas/aios/specification/v0.4/schemas/common.schema.json

Source: [schemas/aios/specification/v0.4/schemas/common.schema.json](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/aios/specification/v0.4/schemas/common.schema.json)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://deepagentlabs.github.io/ai-operations-spec/v0.4/common.schema.json",
  "$defs": {
    "id": {
      "type": "string",
      "minLength": 1,
      "pattern": ".*\\S.*"
    },
    "time": {
      "type": "string",
      "format": "date-time"
    },
    "extension_name": {
      "type": "string",
      "pattern": "^(?!aiops(?:\\.|$))[a-z0-9]+(?:[_-][a-z0-9]+)*(?:\\.[a-z0-9]+(?:[_-][a-z0-9]+)*){2,}$"
    },
    "extensions": {
      "type": "object",
      "propertyNames": {
        "$ref": "#/$defs/extension_name"
      }
    },
    "reference": {
      "type": "object",
      "required": [
        "id",
        "type"
      ],
      "properties": {
        "id": {
          "$ref": "#/$defs/id"
        },
        "type": {
          "enum": [
            "workflow",
            "run",
            "request",
            "step",
            "agent",
            "model_interaction",
            "prompt",
            "context",
            "tool_invocation",
            "rag_retrieval",
            "memory_operation",
            "evaluation",
            "safety_signal",
            "reliability_event",
            "incident"
          ]
        },
        "external": {
          "type": "boolean",
          "default": false
        }
      },
      "additionalProperties": false
    },
    "relationship": {
      "type": "object",
      "required": [
        "id",
        "type",
        "source",
        "target"
      ],
      "properties": {
        "id": {
          "$ref": "#/$defs/id"
        },
        "type": {
          "enum": [
            "run-of",
            "contains",
            "parent-of",
            "caused",
            "follows",
            "depends-on",
            "performed-by",
            "delegated-to",
            "handed-off-to",
            "observed-in",
            "evaluates",
            "signals-on",
            "evidence-for"
          ]
        },
        "source": {
          "$ref": "#/$defs/reference"
        },
        "target": {
          "$ref": "#/$defs/reference"
        },
        "extensions": {
          "$ref": "#/$defs/extensions"
        }
      },
      "additionalProperties": false
    },
    "measurement": {
      "type": "object",
      "required": [
        "name",
        "value",
        "kind"
      ],
      "properties": {
        "name": {
          "type": "string",
          "minLength": 1
        },
        "value": {
          "type": "number",
          "minimum": 0
        },
        "unit": {
          "type": "string",
          "minLength": 1
        },
        "currency": {
          "type": "string",
          "pattern": "^[A-Z]{3}$"
        },
        "kind": {
          "enum": [
            "observed",
            "estimated",
            "derived"
          ]
        }
      },
      "allOf": [
        {
          "if": {
            "properties": {
              "name": {
                "const": "cost"
              }
            },
            "required": [
              "name"
            ]
          },
          "then": {
            "required": [
              "currency"
            ]
          }
        }
      ],
      "additionalProperties": false
    },
    "canonical_event_name": {
      "enum": [
        "aiops.run.started",
        "aiops.run.completed",
        "aiops.run.failed",
        "aiops.run.cancelled",
        "aiops.request.received",
        "aiops.request.completed",
        "aiops.request.rejected",
        "aiops.step.started",
        "aiops.step.completed",
        "aiops.step.failed",
        "aiops.step.cancelled",
        "aiops.agent.started",
        "aiops.agent.waiting",
        "aiops.agent.completed",
        "aiops.agent.failed",
        "aiops.model.requested",
        "aiops.model.responded",
        "aiops.model.failed",
        "aiops.prompt.rendered",
        "aiops.context.assembled",
        "aiops.tool.requested",
        "aiops.tool.authorized",
        "aiops.tool.completed",
        "aiops.tool.failed",
        "aiops.retrieval.started",
        "aiops.retrieval.completed",
        "aiops.retrieval.failed",
        "aiops.memory.read",
        "aiops.memory.written",
        "aiops.memory.updated",
        "aiops.memory.deleted",
        "aiops.memory.failed",
        "aiops.evaluation.completed",
        "aiops.evaluation.failed",
        "aiops.safety.detected",
        "aiops.safety.reviewed",
        "aiops.safety.mitigated",
        "aiops.reliability.detected",
        "aiops.reliability.recovered",
        "aiops.incident.opened",
        "aiops.incident.updated",
        "aiops.incident.mitigated",
        "aiops.incident.resolved"
      ]
    },
    "event": {
      "type": "object",
      "required": [
        "event_id",
        "event_name",
        "occurred_at",
        "object_id",
        "object_type"
      ],
      "properties": {
        "event_id": {
          "$ref": "#/$defs/id"
        },
        "event_name": {
          "description": "Either a canonical aiops.* name from the draft catalog, or a reverse-domain namespaced extension event (e.g. io.deepagentlabs.agenticlens.custom_event). Extension names MUST NOT start with the aiops namespace.",
          "anyOf": [
            {
              "$ref": "#/$defs/canonical_event_name"
            },
            {
              "$ref": "#/$defs/extension_name"
            }
          ]
        },
        "occurred_at": {
          "$ref": "#/$defs/time"
        },
        "object_id": {
          "$ref": "#/$defs/id"
        },
        "object_type": {
          "enum": [
            "run",
            "request",
            "step",
            "agent",
            "model_interaction",
            "prompt",
            "context",
            "tool_invocation",
            "rag_retrieval",
            "memory_operation",
            "evaluation",
            "safety_signal",
            "reliability_event",
            "incident"
          ]
        },
        "attributes": {
          "type": "object"
        },
        "extensions": {
          "$ref": "#/$defs/extensions"
        }
      },
      "additionalProperties": false
    }
  }
}
```

---

## Data contract: schemas/aios/specification/v0.4/schemas/run.schema.json

Source: [schemas/aios/specification/v0.4/schemas/run.schema.json](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/aios/specification/v0.4/schemas/run.schema.json)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://deepagentlabs.github.io/ai-operations-spec/v0.4/run.schema.json",
  "title": "AI Operations Run Artifact",
  "type": "object",
  "required": [
    "spec_version",
    "artifact_type",
    "id",
    "started_at",
    "status",
    "requests",
    "steps",
    "relationships"
  ],
  "properties": {
    "spec_version": {
      "const": "0.4-draft"
    },
    "artifact_type": {
      "const": "run"
    },
    "id": {
      "$ref": "common.schema.json#/$defs/id"
    },
    "workflow_id": {
      "$ref": "common.schema.json#/$defs/id"
    },
    "started_at": {
      "$ref": "common.schema.json#/$defs/time"
    },
    "ended_at": {
      "$ref": "common.schema.json#/$defs/time"
    },
    "status": {
      "enum": [
        "created",
        "running",
        "completed",
        "failed",
        "cancelled"
      ]
    },
    "requests": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/object"
      }
    },
    "steps": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/step"
      }
    },
    "agents": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/object"
      }
    },
    "occurrences": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/occurrence"
      }
    },
    "evidence": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/evidence"
      }
    },
    "incidents": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/object"
      }
    },
    "relationships": {
      "type": "array",
      "items": {
        "$ref": "common.schema.json#/$defs/relationship"
      }
    },
    "events": {
      "type": "array",
      "items": {
        "$ref": "common.schema.json#/$defs/event"
      }
    },
    "measurements": {
      "type": "array",
      "items": {
        "$ref": "common.schema.json#/$defs/measurement"
      }
    },
    "extensions": {
      "$ref": "common.schema.json#/$defs/extensions"
    }
  },
  "additionalProperties": false,
  "$defs": {
    "object": {
      "type": "object",
      "required": [
        "id"
      ],
      "properties": {
        "id": {
          "$ref": "common.schema.json#/$defs/id"
        },
        "name": {
          "type": "string"
        },
        "status": {
          "type": "string"
        },
        "attributes": {
          "type": "object"
        },
        "extensions": {
          "$ref": "common.schema.json#/$defs/extensions"
        }
      },
      "additionalProperties": false
    },
    "step": {
      "type": "object",
      "required": [
        "id",
        "category"
      ],
      "properties": {
        "id": {
          "$ref": "common.schema.json#/$defs/id"
        },
        "category": {
          "type": "string",
          "minLength": 1
        },
        "name": {
          "type": "string"
        },
        "status": {
          "type": "string"
        },
        "started_at": {
          "$ref": "common.schema.json#/$defs/time"
        },
        "ended_at": {
          "$ref": "common.schema.json#/$defs/time"
        },
        "attributes": {
          "type": "object"
        },
        "extensions": {
          "$ref": "common.schema.json#/$defs/extensions"
        }
      },
      "additionalProperties": false
    },
    "occurrence": {
      "type": "object",
      "required": [
        "id",
        "type"
      ],
      "properties": {
        "id": {
          "$ref": "common.schema.json#/$defs/id"
        },
        "type": {
          "enum": [
            "model_interaction",
            "prompt",
            "context",
            "tool_invocation",
            "rag_retrieval",
            "memory_operation"
          ]
        },
        "name": {
          "type": "string"
        },
        "status": {
          "type": "string"
        },
        "attributes": {
          "type": "object"
        },
        "extensions": {
          "$ref": "common.schema.json#/$defs/extensions"
        }
      },
      "additionalProperties": false
    },
    "evidence": {
      "type": "object",
      "required": [
        "id",
        "type"
      ],
      "properties": {
        "id": {
          "$ref": "common.schema.json#/$defs/id"
        },
        "type": {
          "enum": [
            "evaluation",
            "safety_signal",
            "reliability_event"
          ]
        },
        "name": {
          "type": "string"
        },
        "status": {
          "type": "string"
        },
        "attributes": {
          "type": "object"
        },
        "extensions": {
          "$ref": "common.schema.json#/$defs/extensions"
        }
      },
      "additionalProperties": false
    }
  }
}
```

---

## Data contract: schemas/aios/specification/v0.4/schemas/workflow.schema.json

Source: [schemas/aios/specification/v0.4/schemas/workflow.schema.json](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/aios/specification/v0.4/schemas/workflow.schema.json)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://deepagentlabs.github.io/ai-operations-spec/v0.4/workflow.schema.json",
  "title": "AI Operations Workflow Definition",
  "type": "object",
  "required": [
    "spec_version",
    "artifact_type",
    "id",
    "name"
  ],
  "properties": {
    "spec_version": {
      "const": "0.4-draft"
    },
    "artifact_type": {
      "const": "workflow"
    },
    "id": {
      "$ref": "common.schema.json#/$defs/id"
    },
    "name": {
      "type": "string",
      "minLength": 1
    },
    "description": {
      "type": "string"
    },
    "revision": {
      "type": "string",
      "minLength": 1
    },
    "status": {
      "enum": [
        "draft",
        "active",
        "retired"
      ]
    },
    "declared_structure": {
      "type": "object"
    },
    "references": {
      "type": "array",
      "items": {
        "$ref": "common.schema.json#/$defs/reference"
      }
    },
    "extensions": {
      "$ref": "common.schema.json#/$defs/extensions"
    }
  },
  "additionalProperties": false
}
```

---

## Data contract: schemas/aios/specification/v0.6/schemas/provenance.schema.json

Source: [schemas/aios/specification/v0.6/schemas/provenance.schema.json](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/aios/specification/v0.6/schemas/provenance.schema.json)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://deepagentlabs.github.io/ai-operations-spec/v0.6/provenance.schema.json",
  "title": "AI Operations Provenance Record",
  "description": "Exploratory 0.6-draft companion artifact recording the sources and evidence lineage behind derived findings about AIOS artifacts. Shared definitions come from the 0.4-draft common schema.",
  "type": "object",
  "required": [
    "spec_version",
    "artifact_type",
    "id",
    "created_at",
    "producer",
    "subjects",
    "sources",
    "findings",
    "lineage"
  ],
  "properties": {
    "spec_version": {
      "const": "0.6-draft"
    },
    "artifact_type": {
      "const": "provenance"
    },
    "id": {
      "$ref": "https://deepagentlabs.github.io/ai-operations-spec/v0.4/common.schema.json#/$defs/id"
    },
    "created_at": {
      "$ref": "https://deepagentlabs.github.io/ai-operations-spec/v0.4/common.schema.json#/$defs/time"
    },
    "producer": {
      "$ref": "#/$defs/producer"
    },
    "subjects": {
      "type": "array",
      "minItems": 1,
      "items": {
        "$ref": "#/$defs/subject"
      }
    },
    "sources": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/source"
      }
    },
    "findings": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/finding"
      }
    },
    "lineage": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/lineage_edge"
      }
    },
    "attributes": {
      "type": "object"
    },
    "extensions": {
      "$ref": "https://deepagentlabs.github.io/ai-operations-spec/v0.4/common.schema.json#/$defs/extensions"
    }
  },
  "additionalProperties": false,
  "$defs": {
    "id": {
      "$ref": "https://deepagentlabs.github.io/ai-operations-spec/v0.4/common.schema.json#/$defs/id"
    },
    "subject_object": {
      "description": "A v0.4 reference to an object inside the subject artifact; it can never be external.",
      "allOf": [
        {
          "$ref": "https://deepagentlabs.github.io/ai-operations-spec/v0.4/common.schema.json#/$defs/reference"
        }
      ],
      "properties": {
        "external": {
          "const": false
        }
      }
    },
    "producer": {
      "type": "object",
      "required": [
        "name"
      ],
      "properties": {
        "name": {
          "type": "string",
          "minLength": 1
        },
        "version": {
          "type": "string",
          "minLength": 1
        },
        "uri": {
          "type": "string",
          "format": "uri"
        }
      },
      "additionalProperties": false
    },
    "digest": {
      "type": "object",
      "required": [
        "algorithm",
        "value"
      ],
      "properties": {
        "algorithm": {
          "enum": [
            "sha-256",
            "sha-384",
            "sha-512"
          ]
        },
        "value": {
          "type": "string",
          "pattern": "^[0-9a-f]+$"
        }
      },
      "allOf": [
        {
          "if": {
            "properties": {
              "algorithm": {
                "const": "sha-256"
              }
            }
          },
          "then": {
            "properties": {
              "value": {
                "minLength": 64,
                "maxLength": 64
              }
            }
          }
        },
        {
          "if": {
            "properties": {
              "algorithm": {
                "const": "sha-384"
              }
            }
          },
          "then": {
            "properties": {
              "value": {
                "minLength": 96,
                "maxLength": 96
              }
            }
          }
        },
        {
          "if": {
            "properties": {
              "algorithm": {
                "const": "sha-512"
              }
            }
          },
          "then": {
            "properties": {
              "value": {
                "minLength": 128,
                "maxLength": 128
              }
            }
          }
        }
      ],
      "additionalProperties": false
    },
    "subject": {
      "type": "object",
      "required": [
        "id",
        "artifact_id",
        "artifact_type",
        "spec_version"
      ],
      "properties": {
        "id": {
          "$ref": "#/$defs/id"
        },
        "artifact_id": {
          "$ref": "#/$defs/id"
        },
        "artifact_type": {
          "enum": [
            "workflow",
            "run"
          ]
        },
        "spec_version": {
          "type": "string",
          "pattern": "^(0\\.[1-9][0-9]*|[1-9][0-9]*\\.(0|[1-9][0-9]*))(-draft)?$"
        },
        "uri": {
          "type": "string",
          "format": "uri"
        },
        "digest": {
          "$ref": "#/$defs/digest"
        }
      },
      "additionalProperties": false
    },
    "source": {
      "type": "object",
      "required": [
        "id",
        "kind"
      ],
      "properties": {
        "id": {
          "$ref": "#/$defs/id"
        },
        "kind": {
          "enum": [
            "aios_object",
            "artifact",
            "document",
            "dataset",
            "log",
            "tool_output",
            "human_input"
          ]
        },
        "description": {
          "type": "string",
          "minLength": 1
        },
        "subject": {
          "$ref": "#/$defs/id"
        },
        "object": {
          "$ref": "#/$defs/subject_object"
        },
        "uri": {
          "type": "string",
          "format": "uri"
        },
        "digest": {
          "$ref": "#/$defs/digest"
        },
        "captured_at": {
          "$ref": "https://deepagentlabs.github.io/ai-operations-spec/v0.4/common.schema.json#/$defs/time"
        },
        "attributes": {
          "type": "object"
        },
        "extensions": {
          "$ref": "https://deepagentlabs.github.io/ai-operations-spec/v0.4/common.schema.json#/$defs/extensions"
        }
      },
      "allOf": [
        {
          "if": {
            "properties": {
              "kind": {
                "const": "aios_object"
              }
            }
          },
          "then": {
            "required": [
              "subject",
              "object"
            ]
          }
        },
        {
          "if": {
            "properties": {
              "kind": {
                "const": "artifact"
              }
            }
          },
          "then": {
            "required": [
              "subject"
            ],
            "not": {
              "required": [
                "object"
              ]
            }
          }
        },
        {
          "if": {
            "properties": {
              "kind": {
                "enum": [
                  "document",
                  "dataset",
                  "log",
                  "tool_output",
                  "human_input"
                ]
              }
            }
          },
          "then": {
            "anyOf": [
              {
                "required": [
                  "uri"
                ]
              },
              {
                "required": [
                  "description"
                ]
              }
            ],
            "not": {
              "required": [
                "object"
              ]
            }
          }
        }
      ],
      "additionalProperties": false
    },
    "method": {
      "type": "object",
      "required": [
        "kind",
        "name"
      ],
      "properties": {
        "kind": {
          "enum": [
            "rule",
            "model",
            "human",
            "statistical",
            "heuristic"
          ]
        },
        "name": {
          "type": "string",
          "minLength": 1
        },
        "version": {
          "type": "string",
          "minLength": 1
        }
      },
      "additionalProperties": false
    },
    "finding_target": {
      "type": "object",
      "required": [
        "subject",
        "object"
      ],
      "properties": {
        "subject": {
          "$ref": "#/$defs/id"
        },
        "object": {
          "$ref": "#/$defs/subject_object"
        }
      },
      "additionalProperties": false
    },
    "finding": {
      "type": "object",
      "required": [
        "id",
        "statement",
        "status",
        "method"
      ],
      "properties": {
        "id": {
          "$ref": "#/$defs/id"
        },
        "statement": {
          "type": "string",
          "minLength": 1
        },
        "category": {
          "type": "string",
          "minLength": 1
        },
        "status": {
          "enum": [
            "open",
            "confirmed",
            "disputed",
            "retracted"
          ]
        },
        "severity": {
          "enum": [
            "info",
            "low",
            "medium",
            "high",
            "critical"
          ]
        },
        "confidence": {
          "type": "number",
          "minimum": 0,
          "maximum": 1
        },
        "method": {
          "$ref": "#/$defs/method"
        },
        "targets": {
          "type": "array",
          "items": {
            "$ref": "#/$defs/finding_target"
          }
        },
        "attributes": {
          "type": "object"
        },
        "extensions": {
          "$ref": "https://deepagentlabs.github.io/ai-operations-spec/v0.4/common.schema.json#/$defs/extensions"
        }
      },
      "additionalProperties": false
    },
    "lineage_edge": {
      "type": "object",
      "required": [
        "id",
        "type",
        "source",
        "target"
      ],
      "properties": {
        "id": {
          "$ref": "#/$defs/id"
        },
        "type": {
          "enum": [
            "derived-from",
            "supports",
            "contradicts",
            "supersedes"
          ]
        },
        "source": {
          "$ref": "#/$defs/id"
        },
        "target": {
          "$ref": "#/$defs/id"
        },
        "extensions": {
          "$ref": "https://deepagentlabs.github.io/ai-operations-spec/v0.4/common.schema.json#/$defs/extensions"
        }
      },
      "additionalProperties": false
    }
  }
}
```

---

## Data contract: schemas/aios/specification/v0.8/schemas/audit_event.schema.json

Source: [schemas/aios/specification/v0.8/schemas/audit_event.schema.json](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/aios/specification/v0.8/schemas/audit_event.schema.json)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://deepagentlabs.github.io/ai-operations-spec/v0.8/audit_event.schema.json",
  "type": "object",
  "required": [
    "spec_version",
    "artifact_type",
    "id",
    "created_at",
    "producer",
    "occurred_at",
    "actor",
    "action",
    "target",
    "outcome",
    "native_outcome",
    "source"
  ],
  "properties": {
    "spec_version": {
      "const": "0.8-draft"
    },
    "artifact_type": {
      "const": "audit_event"
    },
    "id": {
      "type": "string",
      "minLength": 1
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    },
    "producer": {
      "$ref": "https://deepagentlabs.github.io/ai-operations-spec/v0.8/common.schema.json#/$defs/producer"
    },
    "occurred_at": {
      "type": "string",
      "format": "date-time"
    },
    "actor": {
      "$ref": "https://deepagentlabs.github.io/ai-operations-spec/v0.8/common.schema.json#/$defs/actor"
    },
    "action": {
      "type": "string",
      "minLength": 1
    },
    "target": {
      "$ref": "https://deepagentlabs.github.io/ai-operations-spec/v0.8/common.schema.json#/$defs/reference"
    },
    "outcome": {
      "enum": [
        "requested",
        "denied",
        "started",
        "succeeded",
        "failed",
        "partial",
        "unknown"
      ]
    },
    "native_outcome": {
      "$ref": "https://deepagentlabs.github.io/ai-operations-spec/v0.8/common.schema.json#/$defs/native_outcome"
    },
    "correlation_id": {
      "type": "string",
      "minLength": 1
    },
    "causal_event_ids": {
      "type": "array",
      "items": {
        "type": "string",
        "minLength": 1
      },
      "minItems": 0,
      "uniqueItems": true
    },
    "attributes": {
      "type": "object"
    },
    "extensions": {
      "$ref": "https://deepagentlabs.github.io/ai-operations-spec/v0.8/common.schema.json#/$defs/extensions"
    },
    "source": {
      "$ref": "https://deepagentlabs.github.io/ai-operations-spec/v0.8/common.schema.json#/$defs/reference"
    }
  },
  "additionalProperties": false
}
```

---

## Data contract: schemas/aios/specification/v0.8/schemas/common.schema.json

Source: [schemas/aios/specification/v0.8/schemas/common.schema.json](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/aios/specification/v0.8/schemas/common.schema.json)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://deepagentlabs.github.io/ai-operations-spec/v0.8/common.schema.json",
  "$defs": {
    "producer": {
      "type": "object",
      "required": [
        "name",
        "version"
      ],
      "properties": {
        "name": {
          "type": "string",
          "minLength": 1
        },
        "version": {
          "type": "string",
          "minLength": 1
        }
      },
      "additionalProperties": false
    },
    "reference": {
      "type": "object",
      "required": [
        "id",
        "producer",
        "artifact_id",
        "format"
      ],
      "properties": {
        "id": {
          "type": "string",
          "minLength": 1
        },
        "producer": {
          "type": "string",
          "minLength": 1
        },
        "artifact_id": {
          "type": "string",
          "minLength": 1
        },
        "format": {
          "type": "string",
          "minLength": 1
        },
        "object_id": {
          "type": "string",
          "minLength": 1
        },
        "uri": {
          "type": "string",
          "format": "uri"
        }
      },
      "additionalProperties": false
    },
    "method": {
      "type": "object",
      "required": [
        "kind",
        "name",
        "version"
      ],
      "properties": {
        "kind": {
          "enum": [
            "rule",
            "model",
            "human",
            "statistical",
            "heuristic"
          ]
        },
        "name": {
          "type": "string",
          "minLength": 1
        },
        "version": {
          "type": "string",
          "minLength": 1
        }
      },
      "additionalProperties": false
    },
    "native_outcome": {
      "type": "object",
      "required": [
        "format",
        "value"
      ],
      "properties": {
        "format": {
          "type": "string",
          "minLength": 1
        },
        "value": {
          "type": "string",
          "minLength": 1
        }
      },
      "additionalProperties": false
    },
    "actor": {
      "type": "object",
      "required": [
        "kind"
      ],
      "properties": {
        "kind": {
          "enum": [
            "human",
            "service",
            "agent",
            "unknown"
          ]
        },
        "id": {
          "type": "string",
          "minLength": 1
        }
      },
      "additionalProperties": false,
      "allOf": [
        {
          "if": {
            "properties": {
              "kind": {
                "enum": [
                  "human",
                  "service",
                  "agent"
                ]
              }
            }
          },
          "then": {
            "required": [
              "id"
            ]
          }
        }
      ]
    },
    "extensions": {
      "$ref": "https://deepagentlabs.github.io/ai-operations-spec/v0.4/common.schema.json#/$defs/extensions"
    },
    "certainty": {
      "enum": [
        "observed",
        "hypothesis",
        "contradictory",
        "inconclusive"
      ]
    }
  }
}
```

---

## Data contract: schemas/aios/specification/v0.8/schemas/investigation_report.schema.json

Source: [schemas/aios/specification/v0.8/schemas/investigation_report.schema.json](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/aios/specification/v0.8/schemas/investigation_report.schema.json)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://deepagentlabs.github.io/ai-operations-spec/v0.8/investigation_report.schema.json",
  "type": "object",
  "required": [
    "spec_version",
    "artifact_type",
    "id",
    "created_at",
    "producer",
    "incident",
    "summary",
    "evidence",
    "timeline_entries",
    "findings",
    "missing_evidence_items",
    "recovery",
    "source"
  ],
  "properties": {
    "spec_version": {
      "const": "0.8-draft"
    },
    "artifact_type": {
      "const": "investigation_report"
    },
    "id": {
      "type": "string",
      "minLength": 1
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    },
    "producer": {
      "$ref": "https://deepagentlabs.github.io/ai-operations-spec/v0.8/common.schema.json#/$defs/producer"
    },
    "incident": {
      "type": "object",
      "required": [
        "id",
        "status",
        "native_state",
        "detected_at",
        "affected_targets"
      ],
      "properties": {
        "id": {
          "type": "string",
          "minLength": 1
        },
        "status": {
          "enum": [
            "open",
            "investigating",
            "resolved",
            "escalated",
            "unknown"
          ]
        },
        "native_state": {
          "type": "string",
          "minLength": 1
        },
        "detected_at": {
          "type": "string",
          "format": "date-time"
        },
        "affected_targets": {
          "type": "array",
          "items": {
            "$ref": "https://deepagentlabs.github.io/ai-operations-spec/v0.8/common.schema.json#/$defs/reference"
          },
          "minItems": 1
        }
      },
      "additionalProperties": false
    },
    "summary": {
      "type": "object",
      "required": [
        "statement",
        "certainty",
        "evidence_ids"
      ],
      "properties": {
        "statement": {
          "type": "string",
          "minLength": 1
        },
        "certainty": {
          "$ref": "https://deepagentlabs.github.io/ai-operations-spec/v0.8/common.schema.json#/$defs/certainty"
        },
        "evidence_ids": {
          "type": "array",
          "items": {
            "type": "string",
            "minLength": 1
          },
          "minItems": 0,
          "uniqueItems": true
        }
      },
      "additionalProperties": false
    },
    "evidence": {
      "type": "array",
      "items": {
        "$ref": "https://deepagentlabs.github.io/ai-operations-spec/v0.8/common.schema.json#/$defs/reference"
      },
      "minItems": 0
    },
    "timeline_entries": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "id",
          "occurred_at",
          "evidence_ids"
        ],
        "properties": {
          "id": {
            "type": "string",
            "minLength": 1
          },
          "occurred_at": {
            "type": "string",
            "format": "date-time"
          },
          "evidence_ids": {
            "type": "array",
            "items": {
              "type": "string",
              "minLength": 1
            },
            "minItems": 0,
            "uniqueItems": true
          }
        },
        "additionalProperties": false
      },
      "minItems": 0
    },
    "findings": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "id",
          "statement",
          "certainty",
          "evidence_ids"
        ],
        "properties": {
          "id": {
            "type": "string",
            "minLength": 1
          },
          "statement": {
            "type": "string",
            "minLength": 1
          },
          "certainty": {
            "$ref": "https://deepagentlabs.github.io/ai-operations-spec/v0.8/common.schema.json#/$defs/certainty"
          },
          "evidence_ids": {
            "type": "array",
            "items": {
              "type": "string",
              "minLength": 1
            },
            "minItems": 0,
            "uniqueItems": true
          }
        },
        "additionalProperties": false
      },
      "minItems": 0
    },
    "missing_evidence_items": {
      "type": "array",
      "items": {
        "type": "string",
        "minLength": 1
      },
      "minItems": 0
    },
    "recovery": {
      "type": "object",
      "required": [
        "status",
        "evidence_ids"
      ],
      "properties": {
        "status": {
          "enum": [
            "not_attempted",
            "pending",
            "verified",
            "failed",
            "unknown"
          ]
        },
        "evidence_ids": {
          "type": "array",
          "items": {
            "type": "string",
            "minLength": 1
          },
          "minItems": 0,
          "uniqueItems": true
        }
      },
      "additionalProperties": false
    },
    "attributes": {
      "type": "object"
    },
    "extensions": {
      "$ref": "https://deepagentlabs.github.io/ai-operations-spec/v0.8/common.schema.json#/$defs/extensions"
    },
    "source": {
      "$ref": "https://deepagentlabs.github.io/ai-operations-spec/v0.8/common.schema.json#/$defs/reference"
    }
  },
  "additionalProperties": false
}
```

---

## Data contract: schemas/aios/specification/v0.8/schemas/verification_signal.schema.json

Source: [schemas/aios/specification/v0.8/schemas/verification_signal.schema.json](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/aios/specification/v0.8/schemas/verification_signal.schema.json)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://deepagentlabs.github.io/ai-operations-spec/v0.8/verification_signal.schema.json",
  "type": "object",
  "required": [
    "spec_version",
    "artifact_type",
    "id",
    "created_at",
    "producer",
    "subject",
    "method",
    "status",
    "verdict",
    "confidence",
    "rationale",
    "evidence",
    "grounding",
    "safety",
    "native_outcome",
    "source"
  ],
  "properties": {
    "spec_version": {
      "const": "0.8-draft"
    },
    "artifact_type": {
      "const": "verification_signal"
    },
    "id": {
      "type": "string",
      "minLength": 1
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    },
    "producer": {
      "$ref": "https://deepagentlabs.github.io/ai-operations-spec/v0.8/common.schema.json#/$defs/producer"
    },
    "subject": {
      "$ref": "https://deepagentlabs.github.io/ai-operations-spec/v0.8/common.schema.json#/$defs/reference"
    },
    "method": {
      "$ref": "https://deepagentlabs.github.io/ai-operations-spec/v0.8/common.schema.json#/$defs/method"
    },
    "status": {
      "enum": [
        "completed",
        "unavailable",
        "error",
        "skipped"
      ]
    },
    "verdict": {
      "enum": [
        "supports",
        "partially_supports",
        "contradicts",
        "inconclusive",
        null
      ]
    },
    "confidence": {
      "type": [
        "number",
        "null"
      ],
      "minimum": 0,
      "maximum": 1
    },
    "rationale": {
      "type": "string",
      "minLength": 1
    },
    "evidence": {
      "type": "array",
      "items": {
        "$ref": "https://deepagentlabs.github.io/ai-operations-spec/v0.8/common.schema.json#/$defs/reference"
      },
      "minItems": 0
    },
    "grounding": {
      "type": "object",
      "required": [
        "status",
        "unsupported_claims",
        "missed_evidence_items"
      ],
      "properties": {
        "status": {
          "enum": [
            "grounded",
            "partial",
            "ungrounded",
            "not_checked"
          ]
        },
        "unsupported_claims": {
          "type": "array",
          "items": {
            "type": "string",
            "minLength": 1
          },
          "minItems": 0
        },
        "missed_evidence_items": {
          "type": "array",
          "items": {
            "type": "string",
            "minLength": 1
          },
          "minItems": 0
        }
      },
      "additionalProperties": false
    },
    "safety": {
      "type": "object",
      "required": [
        "status",
        "concerns"
      ],
      "properties": {
        "status": {
          "enum": [
            "concerns",
            "no_concerns",
            "not_checked"
          ]
        },
        "concerns": {
          "type": "array",
          "items": {
            "type": "string",
            "minLength": 1
          },
          "minItems": 0
        }
      },
      "additionalProperties": false
    },
    "native_outcome": {
      "$ref": "https://deepagentlabs.github.io/ai-operations-spec/v0.8/common.schema.json#/$defs/native_outcome"
    },
    "attributes": {
      "type": "object"
    },
    "extensions": {
      "$ref": "https://deepagentlabs.github.io/ai-operations-spec/v0.8/common.schema.json#/$defs/extensions"
    },
    "source": {
      "$ref": "https://deepagentlabs.github.io/ai-operations-spec/v0.8/common.schema.json#/$defs/reference"
    }
  },
  "additionalProperties": false,
  "allOf": [
    {
      "if": {
        "properties": {
          "status": {
            "const": "completed"
          }
        }
      },
      "then": {
        "properties": {
          "verdict": {
            "type": "string"
          }
        }
      },
      "else": {
        "properties": {
          "verdict": {
            "type": "null"
          },
          "confidence": {
            "type": "null"
          },
          "grounding": {
            "properties": {
              "status": {
                "const": "not_checked"
              },
              "unsupported_claims": {
                "maxItems": 0,
                "type": "array"
              },
              "missed_evidence_items": {
                "maxItems": 0,
                "type": "array"
              }
            }
          },
          "safety": {
            "properties": {
              "status": {
                "const": "not_checked"
              },
              "concerns": {
                "maxItems": 0,
                "type": "array"
              }
            }
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "safety": {
            "properties": {
              "status": {
                "const": "concerns"
              }
            }
          }
        }
      },
      "then": {
        "properties": {
          "safety": {
            "properties": {
              "concerns": {
                "minItems": 1,
                "type": "array"
              }
            }
          }
        }
      },
      "else": {
        "properties": {
          "safety": {
            "properties": {
              "concerns": {
                "maxItems": 0,
                "type": "array"
              }
            }
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "grounding": {
            "properties": {
              "status": {
                "const": "grounded"
              }
            }
          }
        }
      },
      "then": {
        "properties": {
          "grounding": {
            "properties": {
              "unsupported_claims": {
                "maxItems": 0,
                "type": "array"
              },
              "missed_evidence_items": {
                "maxItems": 0,
                "type": "array"
              }
            }
          }
        }
      }
    }
  ]
}
```

---

## Data contract: schemas/diagnosis/attribution-accuracy-report.schema.json

Source: [schemas/diagnosis/attribution-accuracy-report.schema.json](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/diagnosis/attribution-accuracy-report.schema.json)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://deepagentlabs.github.io/agenticlens/schemas/diagnosis/attribution-accuracy-report.schema.json",
  "$defs": {
    "AccuracyMetric": {
      "properties": {
        "correct": {
          "title": "Correct",
          "type": "integer"
        },
        "total": {
          "title": "Total",
          "type": "integer"
        },
        "accuracy": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "title": "Accuracy"
        },
        "interval": {
          "anyOf": [
            {
              "maxItems": 2,
              "minItems": 2,
              "prefixItems": [
                {
                  "type": "number"
                },
                {
                  "type": "number"
                }
              ],
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Wilson interval at the report's confidence level.",
          "title": "Interval"
        }
      },
      "required": [
        "correct",
        "total",
        "accuracy"
      ],
      "title": "AccuracyMetric",
      "type": "object"
    },
    "AttributionOutcome": {
      "properties": {
        "case_id": {
          "title": "Case Id",
          "type": "string"
        },
        "expected_span": {
          "title": "Expected Span",
          "type": "string"
        },
        "predicted_span_id": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Predicted Span Id"
        },
        "predicted_span_name": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Predicted Span Name"
        },
        "predicted_agent": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "title": "Predicted Agent"
        },
        "predicted_category": {
          "anyOf": [
            {
              "$ref": "#/$defs/FailureCategory"
            },
            {
              "type": "null"
            }
          ]
        },
        "confidence": {
          "title": "Confidence",
          "type": "number"
        },
        "step_correct": {
          "title": "Step Correct",
          "type": "boolean"
        },
        "top3_correct": {
          "title": "Top3 Correct",
          "type": "boolean"
        },
        "agent_correct": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "None when the case names no expected agent.",
          "title": "Agent Correct"
        },
        "category_correct": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "None when the case names no expected category.",
          "title": "Category Correct"
        }
      },
      "required": [
        "case_id",
        "expected_span",
        "predicted_span_id",
        "predicted_span_name",
        "predicted_agent",
        "predicted_category",
        "confidence",
        "step_correct",
        "top3_correct"
      ],
      "title": "AttributionOutcome",
      "type": "object"
    },
    "FailureCategory": {
      "enum": [
        "tool_error",
        "model_error",
        "retrieval_error",
        "timeout",
        "retry_exhausted",
        "tool_loop",
        "handoff_loop",
        "stagnation",
        "empty_retrieval",
        "validation_failure",
        "delegation_failure",
        "budget_exceeded",
        "injected_fault",
        "incomplete_task"
      ],
      "title": "FailureCategory",
      "type": "string"
    }
  },
  "properties": {
    "schema_version": {
      "default": "1.0",
      "title": "Schema Version",
      "type": "string"
    },
    "total_cases": {
      "title": "Total Cases",
      "type": "integer"
    },
    "confidence_level": {
      "title": "Confidence Level",
      "type": "number"
    },
    "step": {
      "$ref": "#/$defs/AccuracyMetric"
    },
    "top3_step": {
      "$ref": "#/$defs/AccuracyMetric"
    },
    "agent": {
      "$ref": "#/$defs/AccuracyMetric"
    },
    "category": {
      "$ref": "#/$defs/AccuracyMetric"
    },
    "mean_confidence": {
      "title": "Mean Confidence",
      "type": "number"
    },
    "calibration_gap": {
      "description": "Mean attribution confidence minus top-1 step accuracy (positive = overconfident).",
      "title": "Calibration Gap",
      "type": "number"
    },
    "outcomes": {
      "items": {
        "$ref": "#/$defs/AttributionOutcome"
      },
      "title": "Outcomes",
      "type": "array"
    },
    "warnings": {
      "items": {
        "type": "string"
      },
      "title": "Warnings",
      "type": "array"
    }
  },
  "required": [
    "total_cases",
    "confidence_level",
    "step",
    "top3_step",
    "agent",
    "category",
    "mean_confidence",
    "calibration_gap",
    "outcomes"
  ],
  "title": "AttributionAccuracyReport",
  "type": "object"
}
```

---

## Data contract: schemas/diagnosis/diagnosis-report.schema.json

Source: [schemas/diagnosis/diagnosis-report.schema.json](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/diagnosis/diagnosis-report.schema.json)

```json
{
  "$defs": {
    "Anomaly": {
      "description": "A metric far outside the baseline runs' distribution.",
      "properties": {
        "scope": {
          "enum": [
            "run",
            "span"
          ],
          "title": "Scope",
          "type": "string"
        },
        "key": {
          "description": "'run' or '<span_type>:<span name>'.",
          "title": "Key",
          "type": "string"
        },
        "metric": {
          "enum": [
            "latency_ms",
            "total_tokens",
            "cost_usd"
          ],
          "title": "Metric",
          "type": "string"
        },
        "observed": {
          "title": "Observed",
          "type": "number"
        },
        "baseline_median": {
          "title": "Baseline Median",
          "type": "number"
        },
        "baseline_mad": {
          "title": "Baseline Mad",
          "type": "number"
        },
        "robust_z": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Modified z-score (MAD, or mean absolute deviation when MAD is 0); None when every baseline value is identical.",
          "title": "Robust Z"
        },
        "direction": {
          "enum": [
            "high",
            "low"
          ],
          "title": "Direction",
          "type": "string"
        },
        "baseline_samples": {
          "title": "Baseline Samples",
          "type": "integer"
        },
        "span_ids": {
          "items": {
            "type": "string"
          },
          "title": "Span Ids",
          "type": "array"
        }
      },
      "required": [
        "scope",
        "key",
        "metric",
        "observed",
        "baseline_median",
        "baseline_mad",
        "direction",
        "baseline_samples"
      ],
      "title": "Anomaly",
      "type": "object"
    },
    "AnomalyReport": {
      "properties": {
        "method": {
          "default": "robust_z_mad",
          "title": "Method",
          "type": "string"
        },
        "threshold": {
          "title": "Threshold",
          "type": "number"
        },
        "min_baseline_samples": {
          "title": "Min Baseline Samples",
          "type": "integer"
        },
        "baseline_runs": {
          "title": "Baseline Runs",
          "type": "integer"
        },
        "anomalies": {
          "items": {
            "$ref": "#/$defs/Anomaly"
          },
          "title": "Anomalies",
          "type": "array"
        },
        "warnings": {
          "items": {
            "type": "string"
          },
          "title": "Warnings",
          "type": "array"
        }
      },
      "required": [
        "threshold",
        "min_baseline_samples",
        "baseline_runs"
      ],
      "title": "AnomalyReport",
      "type": "object"
    },
    "Attribution": {
      "description": "Which step and agent most likely caused the run's failure.\n\n- ``attributed``: an unrecovered failure was traced to a span.\n- ``recovered``: failures happened but were all recovered and the run did\n  not fail; candidates are still listed.\n- ``unattributed``: the run failed but no span explains it.\n- ``no_failure``: nothing failed.",
      "properties": {
        "status": {
          "enum": [
            "attributed",
            "recovered",
            "unattributed",
            "no_failure"
          ],
          "title": "Status",
          "type": "string"
        },
        "faulty_span_id": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Faulty Span Id"
        },
        "faulty_step": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Faulty Step"
        },
        "faulty_agent": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Faulty Agent"
        },
        "category": {
          "anyOf": [
            {
              "$ref": "#/$defs/FailureCategory"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "confidence": {
          "default": 0.0,
          "maximum": 1,
          "minimum": 0,
          "title": "Confidence",
          "type": "number"
        },
        "explanation": {
          "title": "Explanation",
          "type": "string"
        },
        "candidates": {
          "items": {
            "$ref": "#/$defs/AttributionCandidate"
          },
          "title": "Candidates",
          "type": "array"
        },
        "agent_scores": {
          "additionalProperties": {
            "type": "number"
          },
          "description": "Blame share per agent (spans with no agent: '(none)').",
          "title": "Agent Scores",
          "type": "object"
        }
      },
      "required": [
        "status",
        "explanation"
      ],
      "title": "Attribution",
      "type": "object"
    },
    "AttributionCandidate": {
      "description": "A span that may be responsible for the run's failure, with its share of blame.",
      "properties": {
        "span_id": {
          "title": "Span Id",
          "type": "string"
        },
        "span_name": {
          "title": "Span Name",
          "type": "string"
        },
        "span_type": {
          "title": "Span Type",
          "type": "string"
        },
        "agent_name": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Agent Name"
        },
        "score": {
          "description": "Share of total blame; candidates sum to 1.",
          "maximum": 1,
          "minimum": 0,
          "title": "Score",
          "type": "number"
        },
        "categories": {
          "items": {
            "$ref": "#/$defs/FailureCategory"
          },
          "title": "Categories",
          "type": "array"
        },
        "diagnosis_ids": {
          "items": {
            "type": "string"
          },
          "title": "Diagnosis Ids",
          "type": "array"
        },
        "reasons": {
          "items": {
            "type": "string"
          },
          "title": "Reasons",
          "type": "array"
        }
      },
      "required": [
        "span_id",
        "span_name",
        "span_type",
        "score"
      ],
      "title": "AttributionCandidate",
      "type": "object"
    },
    "Diagnosis": {
      "description": "One failure explained by a deterministic rule.",
      "properties": {
        "diagnosis_id": {
          "title": "Diagnosis Id",
          "type": "string"
        },
        "category": {
          "$ref": "#/$defs/FailureCategory"
        },
        "title": {
          "title": "Title",
          "type": "string"
        },
        "summary": {
          "title": "Summary",
          "type": "string"
        },
        "severity": {
          "enum": [
            "low",
            "medium",
            "high",
            "critical"
          ],
          "title": "Severity",
          "type": "string"
        },
        "confidence": {
          "maximum": 1,
          "minimum": 0,
          "title": "Confidence",
          "type": "number"
        },
        "rule_id": {
          "title": "Rule Id",
          "type": "string"
        },
        "rule_version": {
          "title": "Rule Version",
          "type": "string"
        },
        "origin_span_id": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Span where the failure started; None when no single span is responsible.",
          "title": "Origin Span Id"
        },
        "span_ids": {
          "description": "Every span that supports this diagnosis.",
          "items": {
            "type": "string"
          },
          "title": "Span Ids",
          "type": "array"
        },
        "agent_name": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Agent Name"
        },
        "recovered": {
          "default": false,
          "description": "True when a later span of the same operation succeeded.",
          "title": "Recovered",
          "type": "boolean"
        },
        "evidence": {
          "items": {
            "$ref": "#/$defs/Evidence"
          },
          "title": "Evidence",
          "type": "array"
        }
      },
      "required": [
        "diagnosis_id",
        "category",
        "title",
        "summary",
        "severity",
        "confidence",
        "rule_id",
        "rule_version"
      ],
      "title": "Diagnosis",
      "type": "object"
    },
    "DiagnosisSummary": {
      "properties": {
        "total_diagnoses": {
          "default": 0,
          "title": "Total Diagnoses",
          "type": "integer"
        },
        "unrecovered": {
          "default": 0,
          "title": "Unrecovered",
          "type": "integer"
        },
        "highest_severity": {
          "anyOf": [
            {
              "enum": [
                "low",
                "medium",
                "high",
                "critical"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Highest Severity"
        },
        "categories": {
          "additionalProperties": {
            "type": "integer"
          },
          "title": "Categories",
          "type": "object"
        },
        "failed_spans": {
          "default": 0,
          "title": "Failed Spans",
          "type": "integer"
        },
        "wasted_tokens": {
          "default": 0,
          "description": "Tokens spent in failed and retry spans.",
          "title": "Wasted Tokens",
          "type": "integer"
        },
        "wasted_latency_ms": {
          "default": 0.0,
          "title": "Wasted Latency Ms",
          "type": "number"
        },
        "wasted_cost_usd": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "None when any failed or retry span has no cost.",
          "title": "Wasted Cost Usd"
        }
      },
      "title": "DiagnosisSummary",
      "type": "object"
    },
    "Evidence": {
      "properties": {
        "source": {
          "title": "Source",
          "type": "string"
        },
        "span_id": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Span Id"
        },
        "timestamp": {
          "anyOf": [
            {
              "format": "date-time",
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Timestamp"
        },
        "confidence": {
          "default": 1.0,
          "maximum": 1,
          "minimum": 0,
          "title": "Confidence",
          "type": "number"
        },
        "reasoning": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Reasoning"
        },
        "details": {
          "additionalProperties": true,
          "title": "Details",
          "type": "object"
        }
      },
      "required": [
        "source"
      ],
      "title": "Evidence",
      "type": "object"
    },
    "FailureCategory": {
      "enum": [
        "tool_error",
        "model_error",
        "retrieval_error",
        "timeout",
        "retry_exhausted",
        "tool_loop",
        "handoff_loop",
        "stagnation",
        "empty_retrieval",
        "validation_failure",
        "delegation_failure",
        "budget_exceeded",
        "injected_fault",
        "incomplete_task"
      ],
      "title": "FailureCategory",
      "type": "string"
    },
    "Finding": {
      "properties": {
        "finding_id": {
          "title": "Finding Id",
          "type": "string"
        },
        "category": {
          "title": "Category",
          "type": "string"
        },
        "title": {
          "title": "Title",
          "type": "string"
        },
        "description": {
          "title": "Description",
          "type": "string"
        },
        "severity": {
          "title": "Severity",
          "type": "string"
        },
        "confidence": {
          "maximum": 1,
          "minimum": 0,
          "title": "Confidence",
          "type": "number"
        },
        "span_ids": {
          "items": {
            "type": "string"
          },
          "title": "Span Ids",
          "type": "array"
        },
        "evidence": {
          "items": {
            "$ref": "#/$defs/Evidence"
          },
          "title": "Evidence",
          "type": "array"
        }
      },
      "required": [
        "category",
        "title",
        "description",
        "severity",
        "confidence"
      ],
      "title": "Finding",
      "type": "object"
    },
    "GuardrailStatus": {
      "description": "What the analysis budget allowed, and whether anything was cut short.",
      "properties": {
        "truncated": {
          "default": false,
          "title": "Truncated",
          "type": "boolean"
        },
        "stop_reasons": {
          "items": {
            "type": "string"
          },
          "title": "Stop Reasons",
          "type": "array"
        },
        "spans_analyzed": {
          "default": 0,
          "title": "Spans Analyzed",
          "type": "integer"
        },
        "spans_total": {
          "default": 0,
          "title": "Spans Total",
          "type": "integer"
        },
        "max_depth_seen": {
          "default": 0,
          "title": "Max Depth Seen",
          "type": "integer"
        },
        "iterations": {
          "default": 0,
          "title": "Iterations",
          "type": "integer"
        },
        "stagnant_iterations": {
          "default": 0,
          "title": "Stagnant Iterations",
          "type": "integer"
        },
        "cost_usd": {
          "default": 0.0,
          "title": "Cost Usd",
          "type": "number"
        }
      },
      "title": "GuardrailStatus",
      "type": "object"
    },
    "IncidentTimeline": {
      "description": "Ordered events reconstructed from span timestamps and statuses.",
      "properties": {
        "run_id": {
          "title": "Run Id",
          "type": "string"
        },
        "events": {
          "items": {
            "$ref": "#/$defs/TimelineEvent"
          },
          "title": "Events",
          "type": "array"
        },
        "first_failure_offset_ms": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "First Failure Offset Ms"
        },
        "root_cause_offset_ms": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Root Cause Offset Ms"
        },
        "recovered_span_ids": {
          "items": {
            "type": "string"
          },
          "title": "Recovered Span Ids",
          "type": "array"
        },
        "truncated": {
          "default": false,
          "description": "True when max_events cut the timeline.",
          "title": "Truncated",
          "type": "boolean"
        }
      },
      "required": [
        "run_id"
      ],
      "title": "IncidentTimeline",
      "type": "object"
    },
    "RuleRef": {
      "properties": {
        "rule_id": {
          "title": "Rule Id",
          "type": "string"
        },
        "version": {
          "title": "Version",
          "type": "string"
        }
      },
      "required": [
        "rule_id",
        "version"
      ],
      "title": "RuleRef",
      "type": "object"
    },
    "TimelineEvent": {
      "properties": {
        "offset_ms": {
          "description": "Milliseconds since the run started.",
          "title": "Offset Ms",
          "type": "number"
        },
        "timestamp": {
          "format": "date-time",
          "title": "Timestamp",
          "type": "string"
        },
        "kind": {
          "enum": [
            "supervision_decision",
            "run_started",
            "span_started",
            "span_completed",
            "span_failed",
            "retry",
            "handoff",
            "fault_injected",
            "recovered",
            "run_completed"
          ],
          "title": "Kind",
          "type": "string"
        },
        "description": {
          "title": "Description",
          "type": "string"
        },
        "span_id": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Span Id"
        },
        "span_name": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Span Name"
        },
        "agent_name": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Agent Name"
        },
        "is_root_cause": {
          "default": false,
          "title": "Is Root Cause",
          "type": "boolean"
        }
      },
      "required": [
        "offset_ms",
        "timestamp",
        "kind",
        "description"
      ],
      "title": "TimelineEvent",
      "type": "object"
    }
  },
  "properties": {
    "schema_version": {
      "default": "1.1",
      "title": "Schema Version",
      "type": "string"
    },
    "taxonomy_version": {
      "default": "1.0",
      "title": "Taxonomy Version",
      "type": "string"
    },
    "engine_version": {
      "title": "Engine Version",
      "type": "string"
    },
    "run_id": {
      "title": "Run Id",
      "type": "string"
    },
    "trace_id": {
      "title": "Trace Id",
      "type": "string"
    },
    "application_name": {
      "title": "Application Name",
      "type": "string"
    },
    "run_status": {
      "title": "Run Status",
      "type": "string"
    },
    "task_success": {
      "anyOf": [
        {
          "type": "boolean"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Task Success"
    },
    "rules": {
      "items": {
        "$ref": "#/$defs/RuleRef"
      },
      "title": "Rules",
      "type": "array"
    },
    "summary": {
      "$ref": "#/$defs/DiagnosisSummary"
    },
    "diagnoses": {
      "items": {
        "$ref": "#/$defs/Diagnosis"
      },
      "title": "Diagnoses",
      "type": "array"
    },
    "attribution": {
      "$ref": "#/$defs/Attribution"
    },
    "timeline": {
      "$ref": "#/$defs/IncidentTimeline"
    },
    "anomalies": {
      "anyOf": [
        {
          "$ref": "#/$defs/AnomalyReport"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "efficiency_findings": {
      "description": "Memory, retry, and duplicated-context findings from analyze_trace().",
      "items": {
        "$ref": "#/$defs/Finding"
      },
      "title": "Efficiency Findings",
      "type": "array"
    },
    "guardrails": {
      "$ref": "#/$defs/GuardrailStatus"
    },
    "limitations": {
      "items": {
        "type": "string"
      },
      "title": "Limitations",
      "type": "array"
    }
  },
  "required": [
    "engine_version",
    "run_id",
    "trace_id",
    "application_name",
    "run_status",
    "summary",
    "attribution",
    "timeline"
  ],
  "title": "DiagnosisReport",
  "type": "object",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://deepagentlabs.github.io/agenticlens/schemas/diagnosis/diagnosis-report.schema.json"
}
```

---

## Data contract: schemas/evaluation/score-analysis.schema.json

Source: [schemas/evaluation/score-analysis.schema.json](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/evaluation/score-analysis.schema.json)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://deepagentlabs.github.io/agenticlens/schemas/evaluation/score-analysis.schema.json",
  "$defs": {
    "Disagreement": {
      "properties": {
        "case_id": {
          "title": "Case Id",
          "type": "string"
        },
        "passing": {
          "items": {
            "type": "string"
          },
          "title": "Passing",
          "type": "array"
        },
        "failing": {
          "items": {
            "type": "string"
          },
          "title": "Failing",
          "type": "array"
        },
        "deterministic_vs_model": {
          "description": "True when the deterministic checks and a model judge disagree.",
          "title": "Deterministic Vs Model",
          "type": "boolean"
        },
        "details": {
          "additionalProperties": {
            "type": "string"
          },
          "title": "Details",
          "type": "object"
        }
      },
      "required": [
        "case_id",
        "passing",
        "failing",
        "deterministic_vs_model"
      ],
      "title": "Disagreement",
      "type": "object"
    },
    "JudgeCost": {
      "properties": {
        "evaluator": {
          "title": "Evaluator",
          "type": "string"
        },
        "judge_models": {
          "items": {
            "type": "string"
          },
          "title": "Judge Models",
          "type": "array"
        },
        "scores": {
          "default": 0,
          "title": "Scores",
          "type": "integer"
        },
        "priced_scores": {
          "default": 0,
          "title": "Priced Scores",
          "type": "integer"
        },
        "total_cost_usd": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Sum over priced scores; None when no score is priced.",
          "title": "Total Cost Usd"
        },
        "cost_sources": {
          "additionalProperties": {
            "type": "integer"
          },
          "title": "Cost Sources",
          "type": "object"
        },
        "input_tokens": {
          "default": 0,
          "title": "Input Tokens",
          "type": "integer"
        },
        "output_tokens": {
          "default": 0,
          "title": "Output Tokens",
          "type": "integer"
        },
        "latency_ms": {
          "default": 0.0,
          "title": "Latency Ms",
          "type": "number"
        }
      },
      "required": [
        "evaluator"
      ],
      "title": "JudgeCost",
      "type": "object"
    },
    "JudgeCostSummary": {
      "properties": {
        "judge_scores": {
          "default": 0,
          "description": "Judge scores from an actual judge call.",
          "title": "Judge Scores",
          "type": "integer"
        },
        "skipped_scores": {
          "default": 0,
          "description": "Judge scores skipped before any call (e.g. self-judging); not costed.",
          "title": "Skipped Scores",
          "type": "integer"
        },
        "priced_scores": {
          "default": 0,
          "title": "Priced Scores",
          "type": "integer"
        },
        "complete": {
          "default": true,
          "description": "True when every judge score has a known cost.",
          "title": "Complete",
          "type": "boolean"
        },
        "total_cost_usd": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Total Cost Usd"
        },
        "cost_per_case_usd": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Cost Per Case Usd"
        },
        "evaluators": {
          "items": {
            "$ref": "#/$defs/JudgeCost"
          },
          "title": "Evaluators",
          "type": "array"
        }
      },
      "title": "JudgeCostSummary",
      "type": "object"
    },
    "KindSummary": {
      "properties": {
        "total": {
          "default": 0,
          "title": "Total",
          "type": "integer"
        },
        "passed": {
          "default": 0,
          "title": "Passed",
          "type": "integer"
        },
        "failed": {
          "default": 0,
          "title": "Failed",
          "type": "integer"
        },
        "skipped": {
          "default": 0,
          "title": "Skipped",
          "type": "integer"
        },
        "pass_rate": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Pass Rate"
        },
        "average_score": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Average Score"
        },
        "evaluators": {
          "items": {
            "type": "string"
          },
          "title": "Evaluators",
          "type": "array"
        }
      },
      "title": "KindSummary",
      "type": "object"
    },
    "PairwiseAgreement": {
      "properties": {
        "evaluator_a": {
          "title": "Evaluator A",
          "type": "string"
        },
        "evaluator_b": {
          "title": "Evaluator B",
          "type": "string"
        },
        "shared_cases": {
          "title": "Shared Cases",
          "type": "integer"
        },
        "agreements": {
          "title": "Agreements",
          "type": "integer"
        },
        "agreement_rate": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "title": "Agreement Rate"
        }
      },
      "required": [
        "evaluator_a",
        "evaluator_b",
        "shared_cases",
        "agreements",
        "agreement_rate"
      ],
      "title": "PairwiseAgreement",
      "type": "object"
    }
  },
  "properties": {
    "deterministic": {
      "$ref": "#/$defs/KindSummary"
    },
    "model_based": {
      "$ref": "#/$defs/KindSummary"
    },
    "judge_cost": {
      "$ref": "#/$defs/JudgeCostSummary"
    },
    "agent_cost_usd": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Cost of the evaluated runs, from the report summary.",
      "title": "Agent Cost Usd"
    },
    "comparable_cases": {
      "default": 0,
      "description": "Cases where at least two evaluator units gave a verdict.",
      "title": "Comparable Cases",
      "type": "integer"
    },
    "disagreement_cases": {
      "default": 0,
      "title": "Disagreement Cases",
      "type": "integer"
    },
    "disagreement_rate": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Disagreement Rate"
    },
    "disagreements": {
      "items": {
        "$ref": "#/$defs/Disagreement"
      },
      "title": "Disagreements",
      "type": "array"
    },
    "pairwise_agreement": {
      "items": {
        "$ref": "#/$defs/PairwiseAgreement"
      },
      "title": "Pairwise Agreement",
      "type": "array"
    }
  },
  "required": [
    "deterministic",
    "model_based",
    "judge_cost"
  ],
  "title": "ScoreAnalysis",
  "type": "object"
}
```

---

## Data contract: schemas/experiments/experiment-manifest.schema.json

Source: [schemas/experiments/experiment-manifest.schema.json](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/experiments/experiment-manifest.schema.json)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://deepagentlabs.github.io/agenticlens/schemas/experiments/experiment-manifest.schema.json",
  "$defs": {
    "ExperimentVariant": {
      "description": "One configuration under test.\n\n`target_kind` is `python` (a trusted `module:function` or `path.py:function`),\n`http` (a URL), or `recorded` (a JSON/YAML file of saved per-trial samples,\nreplayed without calling any agent). `factors` names what this variant\nsets for each compared dimension, such as `{\"model\": \"gpt-4o-mini\",\n\"prompt\": \"v2\"}`.",
      "properties": {
        "id": {
          "minLength": 1,
          "title": "Id",
          "type": "string"
        },
        "name": {
          "minLength": 1,
          "title": "Name",
          "type": "string"
        },
        "target_kind": {
          "pattern": "^(python|http|recorded)$",
          "title": "Target Kind",
          "type": "string"
        },
        "target": {
          "minLength": 1,
          "title": "Target",
          "type": "string"
        },
        "timeout_seconds": {
          "default": 30.0,
          "exclusiveMinimum": 0,
          "title": "Timeout Seconds",
          "type": "number"
        },
        "description": {
          "default": "",
          "title": "Description",
          "type": "string"
        },
        "factors": {
          "additionalProperties": {
            "type": "string"
          },
          "title": "Factors",
          "type": "object"
        },
        "metadata": {
          "additionalProperties": {
            "type": "string"
          },
          "title": "Metadata",
          "type": "object"
        }
      },
      "required": [
        "id",
        "name",
        "target_kind",
        "target"
      ],
      "title": "ExperimentVariant",
      "type": "object"
    }
  },
  "properties": {
    "schema_version": {
      "default": "1.1",
      "title": "Schema Version",
      "type": "string"
    },
    "name": {
      "minLength": 1,
      "title": "Name",
      "type": "string"
    },
    "version": {
      "minLength": 1,
      "title": "Version",
      "type": "string"
    },
    "baseline_variant_id": {
      "minLength": 1,
      "title": "Baseline Variant Id",
      "type": "string"
    },
    "trial_count": {
      "default": 5,
      "minimum": 1,
      "title": "Trial Count",
      "type": "integer"
    },
    "random_seed": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Random Seed"
    },
    "pass_k": {
      "description": "k values for pass@k and pass^k; defaults to 1 and trial_count.",
      "items": {
        "type": "integer"
      },
      "title": "Pass K",
      "type": "array"
    },
    "minimum_trials": {
      "default": 5,
      "description": "Completed trials per variant below which deltas are flagged exploratory.",
      "minimum": 1,
      "title": "Minimum Trials",
      "type": "integer"
    },
    "max_workers": {
      "default": 1,
      "description": "Cases run concurrently within one live trial.",
      "minimum": 1,
      "title": "Max Workers",
      "type": "integer"
    },
    "variants": {
      "items": {
        "$ref": "#/$defs/ExperimentVariant"
      },
      "title": "Variants",
      "type": "array"
    },
    "metadata": {
      "additionalProperties": {
        "type": "string"
      },
      "title": "Metadata",
      "type": "object"
    }
  },
  "required": [
    "name",
    "version",
    "baseline_variant_id",
    "variants"
  ],
  "title": "AgenticLens Experiment Manifest",
  "type": "object"
}
```

---

## Data contract: schemas/experiments/experiment-report.schema.json

Source: [schemas/experiments/experiment-report.schema.json](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/experiments/experiment-report.schema.json)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://deepagentlabs.github.io/agenticlens/schemas/experiments/experiment-report.schema.json",
  "$defs": {
    "CaseEvaluation": {
      "description": "One case's result.\n\n`sample_available` is `False` when no sample was supplied for the case;\nits empty `trace_id` then means \"no trace exists\", not \"trace ID lost\".\n\n`target_status` is set only by live runs: `ok` when the target answered,\n`timed_out` when every attempt exceeded the case timeout, and `error`\nwhen the target raised or failed otherwise. A timed-out or errored case\nnever passes, and is distinguishable from a case that answered wrongly.\n`target_attempts` counts the calls made, including retries, and\n`target_error` records the last failure.",
      "properties": {
        "case_id": {
          "title": "Case Id",
          "type": "string"
        },
        "case_name": {
          "title": "Case Name",
          "type": "string"
        },
        "passed": {
          "title": "Passed",
          "type": "boolean"
        },
        "scores": {
          "items": {
            "$ref": "#/$defs/Score"
          },
          "title": "Scores",
          "type": "array"
        },
        "output": {
          "title": "Output",
          "type": "string"
        },
        "trace_id": {
          "title": "Trace Id",
          "type": "string"
        },
        "latency_ms": {
          "title": "Latency Ms",
          "type": "number"
        },
        "cost_usd": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Cost Usd"
        },
        "cost_source": {
          "anyOf": [
            {
              "enum": [
                "measured",
                "estimated"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Cost Source"
        },
        "sample_available": {
          "default": true,
          "title": "Sample Available",
          "type": "boolean"
        },
        "target_status": {
          "anyOf": [
            {
              "enum": [
                "ok",
                "error",
                "timed_out"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Target Status"
        },
        "target_attempts": {
          "anyOf": [
            {
              "minimum": 1,
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Target Attempts"
        },
        "target_error": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Target Error"
        },
        "tags": {
          "items": {
            "type": "string"
          },
          "title": "Tags",
          "type": "array"
        },
        "metadata": {
          "additionalProperties": true,
          "title": "Metadata",
          "type": "object"
        }
      },
      "required": [
        "case_id",
        "case_name",
        "passed",
        "scores",
        "output",
        "trace_id",
        "latency_ms"
      ],
      "title": "CaseEvaluation",
      "type": "object"
    },
    "ConfidenceInterval": {
      "properties": {
        "lower": {
          "title": "Lower",
          "type": "number"
        },
        "upper": {
          "title": "Upper",
          "type": "number"
        },
        "confidence_level": {
          "exclusiveMaximum": 1,
          "exclusiveMinimum": 0,
          "title": "Confidence Level",
          "type": "number"
        },
        "method": {
          "title": "Method",
          "type": "string"
        }
      },
      "required": [
        "lower",
        "upper",
        "confidence_level",
        "method"
      ],
      "title": "ConfidenceInterval",
      "type": "object"
    },
    "EvaluationReport": {
      "properties": {
        "schema_version": {
          "default": "1.0",
          "title": "Schema Version",
          "type": "string"
        },
        "suite_name": {
          "title": "Suite Name",
          "type": "string"
        },
        "suite_version": {
          "title": "Suite Version",
          "type": "string"
        },
        "created_at": {
          "format": "date-time",
          "title": "Created At",
          "type": "string"
        },
        "summary": {
          "$ref": "#/$defs/EvaluationSummary"
        },
        "cases": {
          "items": {
            "$ref": "#/$defs/CaseEvaluation"
          },
          "title": "Cases",
          "type": "array"
        }
      },
      "required": [
        "suite_name",
        "suite_version",
        "summary",
        "cases"
      ],
      "title": "EvaluationReport",
      "type": "object"
    },
    "EvaluationSummary": {
      "properties": {
        "total_cases": {
          "title": "Total Cases",
          "type": "integer"
        },
        "passed_cases": {
          "title": "Passed Cases",
          "type": "integer"
        },
        "failed_cases": {
          "title": "Failed Cases",
          "type": "integer"
        },
        "pass_rate": {
          "maximum": 1,
          "minimum": 0,
          "title": "Pass Rate",
          "type": "number"
        },
        "average_score": {
          "maximum": 1,
          "minimum": 0,
          "title": "Average Score",
          "type": "number"
        },
        "total_cost_usd": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Total Cost Usd"
        },
        "priced_cases": {
          "default": 0,
          "minimum": 0,
          "title": "Priced Cases",
          "type": "integer"
        },
        "cost_sources": {
          "additionalProperties": {
            "type": "integer"
          },
          "title": "Cost Sources",
          "type": "object"
        },
        "average_latency_ms": {
          "title": "Average Latency Ms",
          "type": "number"
        },
        "metrics": {
          "additionalProperties": {
            "$ref": "#/$defs/MetricSummary"
          },
          "title": "Metrics",
          "type": "object"
        },
        "tags": {
          "additionalProperties": {
            "$ref": "#/$defs/TagSummary"
          },
          "title": "Tags",
          "type": "object"
        },
        "judge": {
          "anyOf": [
            {
              "$ref": "#/$defs/JudgeSummary"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "live": {
          "anyOf": [
            {
              "$ref": "#/$defs/LiveSummary"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        }
      },
      "required": [
        "total_cases",
        "passed_cases",
        "failed_cases",
        "pass_rate",
        "average_score",
        "average_latency_ms"
      ],
      "title": "EvaluationSummary",
      "type": "object"
    },
    "ExperimentCaseResult": {
      "description": "One variant's results on one test case across all trials.\n\nA trial whose target call failed counts as a failed attempt on every\ncase: the agent did not deliver an output.",
      "properties": {
        "case_id": {
          "title": "Case Id",
          "type": "string"
        },
        "case_name": {
          "title": "Case Name",
          "type": "string"
        },
        "attempts": {
          "minimum": 0,
          "title": "Attempts",
          "type": "integer"
        },
        "passes": {
          "minimum": 0,
          "title": "Passes",
          "type": "integer"
        },
        "pass_rate": {
          "maximum": 1,
          "minimum": 0,
          "title": "Pass Rate",
          "type": "number"
        },
        "pass_at_k": {
          "additionalProperties": {
            "type": "number"
          },
          "title": "Pass At K",
          "type": "object"
        },
        "pass_hat_k": {
          "additionalProperties": {
            "type": "number"
          },
          "title": "Pass Hat K",
          "type": "object"
        },
        "mean_score": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Mean Score"
        },
        "score_standard_deviation": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Score Standard Deviation"
        },
        "consistent": {
          "description": "Every attempt had the same pass/fail outcome.",
          "title": "Consistent",
          "type": "boolean"
        }
      },
      "required": [
        "case_id",
        "case_name",
        "attempts",
        "passes",
        "pass_rate",
        "consistent"
      ],
      "title": "ExperimentCaseResult",
      "type": "object"
    },
    "ExperimentComparison": {
      "properties": {
        "baseline_variant_id": {
          "title": "Baseline Variant Id",
          "type": "string"
        },
        "candidate_variant_id": {
          "title": "Candidate Variant Id",
          "type": "string"
        },
        "pass_rate_delta": {
          "$ref": "#/$defs/MetricDelta"
        },
        "average_score_delta": {
          "$ref": "#/$defs/MetricDelta"
        },
        "average_latency_ms_delta": {
          "$ref": "#/$defs/MetricDelta"
        },
        "total_cost_usd_delta": {
          "anyOf": [
            {
              "$ref": "#/$defs/MetricDelta"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "changed_factors": {
          "additionalProperties": {
            "items": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ]
            },
            "type": "array"
          },
          "description": "Factor -> [baseline value, candidate value] for factors that differ.",
          "title": "Changed Factors",
          "type": "object"
        },
        "case_pass_rate_delta": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Case Pass Rate Delta"
        },
        "case_pass_rate_p_value": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Case Pass Rate P Value"
        },
        "statistically_significant": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Statistically Significant"
        },
        "regressed_case_ids": {
          "items": {
            "type": "string"
          },
          "title": "Regressed Case Ids",
          "type": "array"
        },
        "improved_case_ids": {
          "items": {
            "type": "string"
          },
          "title": "Improved Case Ids",
          "type": "array"
        },
        "warnings": {
          "items": {
            "type": "string"
          },
          "title": "Warnings",
          "type": "array"
        }
      },
      "required": [
        "baseline_variant_id",
        "candidate_variant_id",
        "pass_rate_delta",
        "average_score_delta",
        "average_latency_ms_delta"
      ],
      "title": "ExperimentComparison",
      "type": "object"
    },
    "ExperimentMetricSummary": {
      "properties": {
        "count": {
          "minimum": 0,
          "title": "Count",
          "type": "integer"
        },
        "mean": {
          "title": "Mean",
          "type": "number"
        },
        "median": {
          "title": "Median",
          "type": "number"
        },
        "p95": {
          "title": "P95",
          "type": "number"
        },
        "standard_deviation": {
          "title": "Standard Deviation",
          "type": "number"
        },
        "coefficient_of_variation": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Coefficient Of Variation"
        },
        "confidence_interval": {
          "anyOf": [
            {
              "$ref": "#/$defs/ConfidenceInterval"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        }
      },
      "required": [
        "count",
        "mean",
        "median",
        "p95",
        "standard_deviation"
      ],
      "title": "ExperimentMetricSummary",
      "type": "object"
    },
    "ExperimentRandomization": {
      "properties": {
        "random_seed": {
          "anyOf": [
            {
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Random Seed"
        },
        "shuffled": {
          "title": "Shuffled",
          "type": "boolean"
        },
        "execution_order": {
          "description": "(variant_id, trial_index) in the order run.",
          "items": {
            "maxItems": 2,
            "minItems": 2,
            "prefixItems": [
              {
                "type": "string"
              },
              {
                "type": "integer"
              }
            ],
            "type": "array"
          },
          "title": "Execution Order",
          "type": "array"
        }
      },
      "required": [
        "shuffled"
      ],
      "title": "ExperimentRandomization",
      "type": "object"
    },
    "ExperimentTrialResult": {
      "properties": {
        "trial_index": {
          "minimum": 1,
          "title": "Trial Index",
          "type": "integer"
        },
        "status": {
          "pattern": "^(succeeded|failed)$",
          "title": "Status",
          "type": "string"
        },
        "report": {
          "anyOf": [
            {
              "$ref": "#/$defs/EvaluationReport"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "error_message": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Error Message"
        }
      },
      "required": [
        "trial_index",
        "status"
      ],
      "title": "ExperimentTrialResult",
      "type": "object"
    },
    "ExperimentVariantResult": {
      "properties": {
        "variant_id": {
          "title": "Variant Id",
          "type": "string"
        },
        "variant_name": {
          "title": "Variant Name",
          "type": "string"
        },
        "target_kind": {
          "title": "Target Kind",
          "type": "string"
        },
        "factors": {
          "additionalProperties": {
            "type": "string"
          },
          "title": "Factors",
          "type": "object"
        },
        "pareto_optimal": {
          "default": false,
          "title": "Pareto Optimal",
          "type": "boolean"
        },
        "trials": {
          "items": {
            "$ref": "#/$defs/ExperimentTrialResult"
          },
          "title": "Trials",
          "type": "array"
        },
        "summary": {
          "$ref": "#/$defs/ExperimentVariantSummary"
        },
        "cases": {
          "items": {
            "$ref": "#/$defs/ExperimentCaseResult"
          },
          "title": "Cases",
          "type": "array"
        }
      },
      "required": [
        "variant_id",
        "variant_name",
        "target_kind",
        "trials",
        "summary"
      ],
      "title": "ExperimentVariantResult",
      "type": "object"
    },
    "ExperimentVariantSummary": {
      "properties": {
        "attempted_trials": {
          "minimum": 0,
          "title": "Attempted Trials",
          "type": "integer"
        },
        "completed_trials": {
          "minimum": 0,
          "title": "Completed Trials",
          "type": "integer"
        },
        "failed_trials": {
          "minimum": 0,
          "title": "Failed Trials",
          "type": "integer"
        },
        "successful_trials": {
          "minimum": 0,
          "title": "Successful Trials",
          "type": "integer"
        },
        "trial_success_rate": {
          "maximum": 1,
          "minimum": 0,
          "title": "Trial Success Rate",
          "type": "number"
        },
        "pass_rate": {
          "anyOf": [
            {
              "$ref": "#/$defs/ExperimentMetricSummary"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "average_score": {
          "anyOf": [
            {
              "$ref": "#/$defs/ExperimentMetricSummary"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "average_latency_ms": {
          "anyOf": [
            {
              "$ref": "#/$defs/ExperimentMetricSummary"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "total_cost_usd": {
          "anyOf": [
            {
              "$ref": "#/$defs/ExperimentMetricSummary"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "case_attempts": {
          "default": 0,
          "minimum": 0,
          "title": "Case Attempts",
          "type": "integer"
        },
        "case_passes": {
          "default": 0,
          "minimum": 0,
          "title": "Case Passes",
          "type": "integer"
        },
        "case_pass_rate": {
          "anyOf": [
            {
              "maximum": 1,
              "minimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Case Pass Rate"
        },
        "case_pass_rate_interval": {
          "anyOf": [
            {
              "$ref": "#/$defs/ConfidenceInterval"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "pass_at_k": {
          "additionalProperties": {
            "type": "number"
          },
          "title": "Pass At K",
          "type": "object"
        },
        "pass_hat_k": {
          "additionalProperties": {
            "type": "number"
          },
          "title": "Pass Hat K",
          "type": "object"
        },
        "consistency_rate": {
          "anyOf": [
            {
              "maximum": 1,
              "minimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Consistency Rate"
        },
        "flaky_case_ids": {
          "items": {
            "type": "string"
          },
          "title": "Flaky Case Ids",
          "type": "array"
        },
        "priced_trials": {
          "default": 0,
          "minimum": 0,
          "title": "Priced Trials",
          "type": "integer"
        }
      },
      "required": [
        "attempted_trials",
        "completed_trials",
        "failed_trials",
        "successful_trials",
        "trial_success_rate"
      ],
      "title": "ExperimentVariantSummary",
      "type": "object"
    },
    "FactorLevelSummary": {
      "description": "Variants that share one value of one factor, averaged together.",
      "properties": {
        "factor": {
          "title": "Factor",
          "type": "string"
        },
        "value": {
          "title": "Value",
          "type": "string"
        },
        "variant_ids": {
          "items": {
            "type": "string"
          },
          "title": "Variant Ids",
          "type": "array"
        },
        "mean_pass_rate": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Mean Pass Rate"
        },
        "mean_average_score": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Mean Average Score"
        },
        "mean_latency_ms": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Mean Latency Ms"
        },
        "mean_cost_usd": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Mean Cost Usd"
        },
        "mean_trial_success_rate": {
          "title": "Mean Trial Success Rate",
          "type": "number"
        }
      },
      "required": [
        "factor",
        "value",
        "variant_ids",
        "mean_trial_success_rate"
      ],
      "title": "FactorLevelSummary",
      "type": "object"
    },
    "JudgeSummary": {
      "description": "What the suite's LLM judges cost, and how dependable they were.\n\nCounts cover evaluated (non-skipped) scores from `llm_judge` and\n`llm_rubric` evaluators. `unavailable_scores` are judgments the judge\ncould not deliver after its retries; they never count as passes and\n`unavailable_cases` names the cases they belong to.\n\n`total_cost_usd` is the sum of `judge_cost_usd` over every judge score,\nand is `None` unless all of them recorded a cost (`priced_scores`\nsays how many did). Judge cost is kept apart from the cost of the system\nunder evaluation in `EvaluationSummary.total_cost_usd`.\n\n`sampled_scores` were judged more than once (`samples=N`).\n`case_agreement` holds, per case, the lowest agreement among its sampled\njudge scores: the share of samples that returned the most common verdict.",
      "properties": {
        "judge_scores": {
          "default": 0,
          "minimum": 0,
          "title": "Judge Scores",
          "type": "integer"
        },
        "unavailable_scores": {
          "default": 0,
          "minimum": 0,
          "title": "Unavailable Scores",
          "type": "integer"
        },
        "unavailable_cases": {
          "items": {
            "type": "string"
          },
          "title": "Unavailable Cases",
          "type": "array"
        },
        "retried_scores": {
          "default": 0,
          "minimum": 0,
          "title": "Retried Scores",
          "type": "integer"
        },
        "priced_scores": {
          "default": 0,
          "minimum": 0,
          "title": "Priced Scores",
          "type": "integer"
        },
        "total_cost_usd": {
          "anyOf": [
            {
              "minimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Total Cost Usd"
        },
        "cost_sources": {
          "additionalProperties": {
            "type": "integer"
          },
          "title": "Cost Sources",
          "type": "object"
        },
        "input_tokens": {
          "default": 0,
          "minimum": 0,
          "title": "Input Tokens",
          "type": "integer"
        },
        "output_tokens": {
          "default": 0,
          "minimum": 0,
          "title": "Output Tokens",
          "type": "integer"
        },
        "total_latency_ms": {
          "default": 0.0,
          "minimum": 0,
          "title": "Total Latency Ms",
          "type": "number"
        },
        "sampled_scores": {
          "default": 0,
          "minimum": 0,
          "title": "Sampled Scores",
          "type": "integer"
        },
        "min_agreement": {
          "anyOf": [
            {
              "maximum": 1,
              "minimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Min Agreement"
        },
        "average_agreement": {
          "anyOf": [
            {
              "maximum": 1,
              "minimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Average Agreement"
        },
        "case_agreement": {
          "additionalProperties": {
            "type": "number"
          },
          "title": "Case Agreement",
          "type": "object"
        }
      },
      "title": "JudgeSummary",
      "type": "object"
    },
    "LiveSummary": {
      "description": "How a live target behaved across the suite (live runs only).",
      "properties": {
        "total_cases": {
          "minimum": 0,
          "title": "Total Cases",
          "type": "integer"
        },
        "ok_cases": {
          "minimum": 0,
          "title": "Ok Cases",
          "type": "integer"
        },
        "retried_cases": {
          "default": 0,
          "minimum": 0,
          "title": "Retried Cases",
          "type": "integer"
        },
        "timed_out_cases": {
          "default": 0,
          "minimum": 0,
          "title": "Timed Out Cases",
          "type": "integer"
        },
        "error_cases": {
          "default": 0,
          "minimum": 0,
          "title": "Error Cases",
          "type": "integer"
        },
        "timed_out_case_ids": {
          "items": {
            "type": "string"
          },
          "title": "Timed Out Case Ids",
          "type": "array"
        },
        "error_case_ids": {
          "items": {
            "type": "string"
          },
          "title": "Error Case Ids",
          "type": "array"
        }
      },
      "required": [
        "total_cases",
        "ok_cases"
      ],
      "title": "LiveSummary",
      "type": "object"
    },
    "MetricDelta": {
      "properties": {
        "absolute": {
          "title": "Absolute",
          "type": "number"
        },
        "relative": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Relative"
        },
        "regressed": {
          "title": "Regressed",
          "type": "boolean"
        }
      },
      "required": [
        "absolute",
        "regressed"
      ],
      "title": "MetricDelta",
      "type": "object"
    },
    "MetricSummary": {
      "description": "How one metric did across the suite. Skipped scores are counted apart.",
      "properties": {
        "total": {
          "title": "Total",
          "type": "integer"
        },
        "passed": {
          "title": "Passed",
          "type": "integer"
        },
        "failed": {
          "title": "Failed",
          "type": "integer"
        },
        "skipped": {
          "default": 0,
          "title": "Skipped",
          "type": "integer"
        },
        "pass_rate": {
          "anyOf": [
            {
              "maximum": 1,
              "minimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Pass Rate"
        },
        "average_score": {
          "anyOf": [
            {
              "maximum": 1,
              "minimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Average Score"
        }
      },
      "required": [
        "total",
        "passed",
        "failed"
      ],
      "title": "MetricSummary",
      "type": "object"
    },
    "Score": {
      "description": "A single named judgment.\n\n`metric` is the stable key reports group by. It defaults to `name`;\nchecks whose name carries a per-case detail (`contains:42`,\n`required_tool:lookup`) share one metric (`contains`, `required_tool`).\n\nA `skipped` score records that a check did not apply to a case. It\nnever fails the case and is left out of averages and pass rates --\nbuild one with `Score.skip(...)`.\n\n`evaluator` and `evaluator_version` identify what produced the score.\n`evaluate_suite` stamps them: built-in checks are attributed to\n`BUILTIN_EVALUATOR` at this package's version, and registered\nevaluators to their registry name and their `version` attribute, if\nany. A `None` version means the evaluator did not declare one.",
      "properties": {
        "name": {
          "title": "Name",
          "type": "string"
        },
        "metric": {
          "default": "",
          "title": "Metric",
          "type": "string"
        },
        "value": {
          "maximum": 1,
          "minimum": 0,
          "title": "Value",
          "type": "number"
        },
        "passed": {
          "title": "Passed",
          "type": "boolean"
        },
        "required": {
          "default": true,
          "title": "Required",
          "type": "boolean"
        },
        "skipped": {
          "default": false,
          "title": "Skipped",
          "type": "boolean"
        },
        "explanation": {
          "title": "Explanation",
          "type": "string"
        },
        "evaluator_type": {
          "default": "deterministic",
          "title": "Evaluator Type",
          "type": "string"
        },
        "evaluator": {
          "default": "",
          "title": "Evaluator",
          "type": "string"
        },
        "evaluator_version": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Evaluator Version"
        },
        "metadata": {
          "additionalProperties": true,
          "title": "Metadata",
          "type": "object"
        }
      },
      "required": [
        "name",
        "value",
        "passed",
        "explanation"
      ],
      "title": "Score",
      "type": "object"
    },
    "TagSummary": {
      "description": "How the cases carrying one tag did.",
      "properties": {
        "total_cases": {
          "title": "Total Cases",
          "type": "integer"
        },
        "passed_cases": {
          "title": "Passed Cases",
          "type": "integer"
        },
        "failed_cases": {
          "title": "Failed Cases",
          "type": "integer"
        },
        "pass_rate": {
          "maximum": 1,
          "minimum": 0,
          "title": "Pass Rate",
          "type": "number"
        },
        "average_score": {
          "anyOf": [
            {
              "maximum": 1,
              "minimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Average Score"
        }
      },
      "required": [
        "total_cases",
        "passed_cases",
        "failed_cases",
        "pass_rate"
      ],
      "title": "TagSummary",
      "type": "object"
    }
  },
  "properties": {
    "schema_version": {
      "default": "1.1",
      "title": "Schema Version",
      "type": "string"
    },
    "experiment_name": {
      "title": "Experiment Name",
      "type": "string"
    },
    "experiment_version": {
      "title": "Experiment Version",
      "type": "string"
    },
    "suite_name": {
      "title": "Suite Name",
      "type": "string"
    },
    "suite_version": {
      "title": "Suite Version",
      "type": "string"
    },
    "baseline_variant_id": {
      "title": "Baseline Variant Id",
      "type": "string"
    },
    "trial_count": {
      "minimum": 1,
      "title": "Trial Count",
      "type": "integer"
    },
    "random_seed": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Random Seed"
    },
    "confidence_level": {
      "default": 0.95,
      "exclusiveMaximum": 1,
      "exclusiveMinimum": 0,
      "title": "Confidence Level",
      "type": "number"
    },
    "regression_threshold": {
      "default": 0.05,
      "minimum": 0,
      "title": "Regression Threshold",
      "type": "number"
    },
    "pass_k": {
      "items": {
        "type": "integer"
      },
      "title": "Pass K",
      "type": "array"
    },
    "minimum_trials": {
      "default": 5,
      "minimum": 1,
      "title": "Minimum Trials",
      "type": "integer"
    },
    "randomization": {
      "anyOf": [
        {
          "$ref": "#/$defs/ExperimentRandomization"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "created_at": {
      "format": "date-time",
      "title": "Created At",
      "type": "string"
    },
    "variants": {
      "items": {
        "$ref": "#/$defs/ExperimentVariantResult"
      },
      "title": "Variants",
      "type": "array"
    },
    "comparisons": {
      "items": {
        "$ref": "#/$defs/ExperimentComparison"
      },
      "title": "Comparisons",
      "type": "array"
    },
    "pareto_frontier_variant_ids": {
      "items": {
        "type": "string"
      },
      "title": "Pareto Frontier Variant Ids",
      "type": "array"
    },
    "factor_levels": {
      "items": {
        "$ref": "#/$defs/FactorLevelSummary"
      },
      "title": "Factor Levels",
      "type": "array"
    },
    "case_ids": {
      "items": {
        "type": "string"
      },
      "title": "Case Ids",
      "type": "array"
    },
    "warnings": {
      "items": {
        "type": "string"
      },
      "title": "Warnings",
      "type": "array"
    }
  },
  "required": [
    "experiment_name",
    "experiment_version",
    "suite_name",
    "suite_version",
    "baseline_variant_id",
    "trial_count",
    "variants",
    "comparisons"
  ],
  "title": "ExperimentReport",
  "type": "object"
}
```

---

## Data contract: schemas/finding.schema.json

Source: [schemas/finding.schema.json](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/finding.schema.json)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://deepagentlabs.github.io/agenticlens/schemas/finding.schema.json",
  "title": "AgenticLens Finding",
  "type": "object",
  "required": [
    "finding_id",
    "category",
    "title",
    "description",
    "severity",
    "confidence",
    "span_ids",
    "evidence"
  ],
  "properties": {
    "finding_id": {
      "type": "string",
      "minLength": 1
    },
    "category": {
      "type": "string",
      "minLength": 1
    },
    "title": {
      "type": "string",
      "minLength": 1
    },
    "description": {
      "type": "string"
    },
    "severity": {
      "type": "string"
    },
    "confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1
    },
    "span_ids": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "evidence": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "source",
          "confidence",
          "details"
        ],
        "properties": {
          "source": {
            "type": "string",
            "minLength": 1
          },
          "span_id": {
            "type": [
              "string",
              "null"
            ]
          },
          "timestamp": {
            "type": [
              "string",
              "null"
            ],
            "format": "date-time"
          },
          "confidence": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
          },
          "reasoning": {
            "type": [
              "string",
              "null"
            ]
          },
          "details": {
            "type": "object"
          }
        },
        "additionalProperties": false
      }
    }
  }
}
```

---

## Data contract: schemas/integrity/execution-bundle.schema.json

Source: [schemas/integrity/execution-bundle.schema.json](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/integrity/execution-bundle.schema.json)

```json
{
  "$defs": {
    "Coverage": {
      "additionalProperties": false,
      "description": "Caller-declared snapshot boundary; not proof of complete execution.",
      "properties": {
        "stream_id": {
          "minLength": 1,
          "title": "Stream Id",
          "type": "string"
        },
        "description": {
          "minLength": 1,
          "title": "Description",
          "type": "string"
        },
        "complete": {
          "title": "Complete",
          "type": "boolean"
        }
      },
      "required": [
        "stream_id",
        "description",
        "complete"
      ],
      "title": "Coverage",
      "type": "object"
    },
    "Manifest": {
      "additionalProperties": false,
      "properties": {
        "format": {
          "const": "lens.evidence-manifest/1",
          "default": "lens.evidence-manifest/1",
          "title": "Format",
          "type": "string"
        },
        "key_id": {
          "minLength": 1,
          "title": "Key Id",
          "type": "string"
        },
        "coverage": {
          "$ref": "#/$defs/Coverage"
        },
        "record_count": {
          "minimum": 0,
          "title": "Record Count",
          "type": "integer"
        },
        "root_sha256": {
          "pattern": "^[0-9a-f]{64}$",
          "title": "Root Sha256",
          "type": "string"
        },
        "authentication": {
          "pattern": "^[0-9a-f]{64}$",
          "title": "Authentication",
          "type": "string"
        }
      },
      "required": [
        "key_id",
        "coverage",
        "record_count",
        "root_sha256",
        "authentication"
      ],
      "title": "Manifest",
      "type": "object"
    }
  },
  "additionalProperties": false,
  "properties": {
    "artifact": {
      "additionalProperties": true,
      "title": "Artifact",
      "type": "object"
    },
    "manifest": {
      "$ref": "#/$defs/Manifest"
    }
  },
  "required": [
    "artifact",
    "manifest"
  ],
  "title": "ExecutionBundle",
  "type": "object"
}
```

---

## Data contract: schemas/integrity/execution-record.schema.json

Source: [schemas/integrity/execution-record.schema.json](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/integrity/execution-record.schema.json)

```json
{
  "additionalProperties": false,
  "description": "Explicit producer observations, never inferred from supervision verdicts.",
  "properties": {
    "event_id": {
      "minLength": 1,
      "title": "Event Id",
      "type": "string"
    },
    "run_id": {
      "minLength": 1,
      "title": "Run Id",
      "type": "string"
    },
    "span_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Span Id"
    },
    "occurred_at": {
      "title": "Occurred At",
      "type": "string"
    },
    "kind": {
      "enum": [
        "proposed",
        "allowed",
        "denied",
        "dispatched",
        "completed",
        "stop_acknowledged",
        "revocation_acknowledged"
      ],
      "title": "Kind",
      "type": "string"
    },
    "producer": {
      "minLength": 1,
      "title": "Producer",
      "type": "string"
    },
    "decision_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Decision Id"
    },
    "action_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Action Id"
    },
    "actor": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Actor"
    },
    "policy_version": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Policy Version"
    },
    "approval_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Approval Id"
    },
    "outcome": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Outcome"
    },
    "attributes": {
      "additionalProperties": true,
      "title": "Attributes",
      "type": "object"
    }
  },
  "required": [
    "event_id",
    "run_id",
    "occurred_at",
    "kind",
    "producer"
  ],
  "title": "ExecutionRecord",
  "type": "object"
}
```

---

## Data contract: schemas/integrity/manifest.schema.json

Source: [schemas/integrity/manifest.schema.json](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/integrity/manifest.schema.json)

```json
{
  "$defs": {
    "Coverage": {
      "additionalProperties": false,
      "description": "Caller-declared snapshot boundary; not proof of complete execution.",
      "properties": {
        "stream_id": {
          "minLength": 1,
          "title": "Stream Id",
          "type": "string"
        },
        "description": {
          "minLength": 1,
          "title": "Description",
          "type": "string"
        },
        "complete": {
          "title": "Complete",
          "type": "boolean"
        }
      },
      "required": [
        "stream_id",
        "description",
        "complete"
      ],
      "title": "Coverage",
      "type": "object"
    }
  },
  "additionalProperties": false,
  "properties": {
    "format": {
      "const": "lens.evidence-manifest/1",
      "default": "lens.evidence-manifest/1",
      "title": "Format",
      "type": "string"
    },
    "key_id": {
      "minLength": 1,
      "title": "Key Id",
      "type": "string"
    },
    "coverage": {
      "$ref": "#/$defs/Coverage"
    },
    "record_count": {
      "minimum": 0,
      "title": "Record Count",
      "type": "integer"
    },
    "root_sha256": {
      "pattern": "^[0-9a-f]{64}$",
      "title": "Root Sha256",
      "type": "string"
    },
    "authentication": {
      "pattern": "^[0-9a-f]{64}$",
      "title": "Authentication",
      "type": "string"
    }
  },
  "required": [
    "key_id",
    "coverage",
    "record_count",
    "root_sha256",
    "authentication"
  ],
  "title": "Manifest",
  "type": "object"
}
```

---

## Data contract: schemas/integrity/verification.schema.json

Source: [schemas/integrity/verification.schema.json](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/integrity/verification.schema.json)

```json
{
  "$defs": {
    "Coverage": {
      "additionalProperties": false,
      "description": "Caller-declared snapshot boundary; not proof of complete execution.",
      "properties": {
        "stream_id": {
          "minLength": 1,
          "title": "Stream Id",
          "type": "string"
        },
        "description": {
          "minLength": 1,
          "title": "Description",
          "type": "string"
        },
        "complete": {
          "title": "Complete",
          "type": "boolean"
        }
      },
      "required": [
        "stream_id",
        "description",
        "complete"
      ],
      "title": "Coverage",
      "type": "object"
    }
  },
  "description": "Consumers must require verified; other statuses never establish coverage.",
  "properties": {
    "status": {
      "enum": [
        "verified",
        "failed",
        "unknown",
        "incomplete"
      ],
      "title": "Status",
      "type": "string"
    },
    "reason": {
      "title": "Reason",
      "type": "string"
    },
    "authenticated": {
      "default": false,
      "title": "Authenticated",
      "type": "boolean"
    },
    "coverage": {
      "anyOf": [
        {
          "$ref": "#/$defs/Coverage"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "record_count": {
      "default": 0,
      "title": "Record Count",
      "type": "integer"
    }
  },
  "required": [
    "status",
    "reason"
  ],
  "title": "Verification",
  "type": "object"
}
```

---

## Data contract: schemas/modelfit/modelfit-config.schema.json

Source: [schemas/modelfit/modelfit-config.schema.json](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/modelfit/modelfit-config.schema.json)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://deepagentlabs.github.io/agenticlens/schemas/modelfit/modelfit-config.schema.json",
  "$defs": {
    "ModelCandidate": {
      "description": "Deployment facts about one experiment variant.\n\nValues here take precedence over the variant's `metadata` keys of the same\nname (`model`, `provider`, `deployment`, comma-separated `capabilities`).",
      "properties": {
        "variant_id": {
          "minLength": 1,
          "title": "Variant Id",
          "type": "string"
        },
        "model": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Model"
        },
        "provider": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Provider"
        },
        "deployment": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Deployment"
        },
        "capabilities": {
          "items": {
            "type": "string"
          },
          "title": "Capabilities",
          "type": "array"
        }
      },
      "required": [
        "variant_id"
      ],
      "title": "ModelCandidate",
      "type": "object"
    },
    "ModelConstraints": {
      "description": "Hard constraints a candidate must satisfy to be recommended.\n\nEvery limit is optional. A limit that cannot be checked because the\nevidence is missing (for example an unpriced trial under a cost limit, or\nan unknown provider under a provider allow-list) is a violation: ModelFit\nnever assumes a candidate passes a constraint it has no evidence for.",
      "properties": {
        "min_pass_rate": {
          "anyOf": [
            {
              "maximum": 1,
              "minimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Min Pass Rate"
        },
        "min_pass_rate_lower_bound": {
          "anyOf": [
            {
              "maximum": 1,
              "minimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Minimum lower bound of the pass rate's Wilson confidence interval.",
          "title": "Min Pass Rate Lower Bound"
        },
        "max_cost_per_case_usd": {
          "anyOf": [
            {
              "minimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Max Cost Per Case Usd"
        },
        "max_cost_per_success_usd": {
          "anyOf": [
            {
              "minimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Max Cost Per Success Usd"
        },
        "max_mean_latency_ms": {
          "anyOf": [
            {
              "exclusiveMinimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Max Mean Latency Ms"
        },
        "max_p95_latency_ms": {
          "anyOf": [
            {
              "exclusiveMinimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Max P95 Latency Ms"
        },
        "min_consistency": {
          "anyOf": [
            {
              "maximum": 1,
              "minimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Minimum share of cases with the same outcome on every attempt.",
          "title": "Min Consistency"
        },
        "min_safety_pass_rate": {
          "anyOf": [
            {
              "maximum": 1,
              "minimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Minimum pass rate over every safety-tagged case in the suite.",
          "title": "Min Safety Pass Rate"
        },
        "allowed_providers": {
          "anyOf": [
            {
              "items": {
                "type": "string"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Allowed Providers"
        },
        "blocked_providers": {
          "anyOf": [
            {
              "items": {
                "type": "string"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "description": "`null` in an override clears the default block-list.",
          "title": "Blocked Providers"
        },
        "allowed_deployments": {
          "anyOf": [
            {
              "items": {
                "type": "string"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Allowed Deployments"
        },
        "required_capabilities": {
          "anyOf": [
            {
              "items": {
                "type": "string"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "description": "`null` in an override clears the default requirement.",
          "title": "Required Capabilities"
        }
      },
      "title": "ModelConstraints",
      "type": "object"
    },
    "ScoringWeights": {
      "description": "Relative weights of the four normalised components of a candidate's score.\n\nComponents are each in [0, 1]: `quality` is the pass rate; `cost` and\n`latency` are the cheapest (fastest) feasible candidate's cost per success\n(mean latency) divided by this candidate's; `reliability` is the share of\ncases with a consistent outcome across attempts.",
      "properties": {
        "quality": {
          "default": 0.5,
          "minimum": 0,
          "title": "Quality",
          "type": "number"
        },
        "cost": {
          "default": 0.3,
          "minimum": 0,
          "title": "Cost",
          "type": "number"
        },
        "latency": {
          "default": 0.1,
          "minimum": 0,
          "title": "Latency",
          "type": "number"
        },
        "reliability": {
          "default": 0.1,
          "minimum": 0,
          "title": "Reliability",
          "type": "number"
        }
      },
      "title": "ScoringWeights",
      "type": "object"
    },
    "TaskCategory": {
      "description": "A task category and the suite cases that belong to it.\n\nA case belongs to the category when its ID is listed in `case_ids`, it\ncarries any of `tags`, or its `metadata[\"domain\"]` is in `domains`. A\ncase can belong to several categories.",
      "properties": {
        "id": {
          "minLength": 1,
          "pattern": "^[A-Za-z0-9][A-Za-z0-9_.:-]*$",
          "title": "Id",
          "type": "string"
        },
        "name": {
          "default": "",
          "title": "Name",
          "type": "string"
        },
        "description": {
          "default": "",
          "title": "Description",
          "type": "string"
        },
        "tags": {
          "items": {
            "type": "string"
          },
          "title": "Tags",
          "type": "array"
        },
        "domains": {
          "items": {
            "type": "string"
          },
          "title": "Domains",
          "type": "array"
        },
        "case_ids": {
          "items": {
            "type": "string"
          },
          "title": "Case Ids",
          "type": "array"
        },
        "constraints": {
          "anyOf": [
            {
              "$ref": "#/$defs/ModelConstraints"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Overrides for the config's default constraints."
        },
        "weights": {
          "anyOf": [
            {
              "$ref": "#/$defs/ScoringWeights"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Replaces the config's default weights for this category."
        },
        "monthly_volume": {
          "anyOf": [
            {
              "minimum": 0,
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Expected requests per month, for savings projections.",
          "title": "Monthly Volume"
        }
      },
      "required": [
        "id"
      ],
      "title": "TaskCategory",
      "type": "object"
    }
  },
  "properties": {
    "schema_version": {
      "default": "1.0",
      "title": "Schema Version",
      "type": "string"
    },
    "name": {
      "default": "modelfit",
      "minLength": 1,
      "title": "Name",
      "type": "string"
    },
    "model_factor": {
      "default": "model",
      "description": "Experiment factor that names the model.",
      "minLength": 1,
      "title": "Model Factor",
      "type": "string"
    },
    "reference_variant_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Variant that savings and quality risks are measured against; defaults to the experiment baseline.",
      "title": "Reference Variant Id"
    },
    "categories": {
      "description": "Task taxonomy. When empty, one category is derived per case tag.",
      "items": {
        "$ref": "#/$defs/TaskCategory"
      },
      "title": "Categories",
      "type": "array"
    },
    "include_overall": {
      "default": true,
      "description": "Add an `all` category covering every case.",
      "title": "Include Overall",
      "type": "boolean"
    },
    "defaults": {
      "$ref": "#/$defs/ModelConstraints"
    },
    "weights": {
      "$ref": "#/$defs/ScoringWeights"
    },
    "candidates": {
      "items": {
        "$ref": "#/$defs/ModelCandidate"
      },
      "title": "Candidates",
      "type": "array"
    },
    "exclude_variant_ids": {
      "items": {
        "type": "string"
      },
      "title": "Exclude Variant Ids",
      "type": "array"
    },
    "safety_tags": {
      "items": {
        "type": "string"
      },
      "title": "Safety Tags",
      "type": "array"
    },
    "minimum_attempts": {
      "default": 10,
      "description": "Case attempts per category below which a recommendation is low confidence.",
      "minimum": 1,
      "title": "Minimum Attempts",
      "type": "integer"
    },
    "confidence_level": {
      "default": 0.95,
      "exclusiveMaximum": 1,
      "exclusiveMinimum": 0,
      "title": "Confidence Level",
      "type": "number"
    },
    "significance_level": {
      "default": 0.05,
      "exclusiveMaximum": 1,
      "exclusiveMinimum": 0,
      "title": "Significance Level",
      "type": "number"
    },
    "max_alternatives": {
      "default": 2,
      "minimum": 0,
      "title": "Max Alternatives",
      "type": "integer"
    },
    "metadata": {
      "additionalProperties": {
        "type": "string"
      },
      "title": "Metadata",
      "type": "object"
    }
  },
  "title": "AgenticLens ModelFit Config",
  "type": "object"
}
```

---

## Data contract: schemas/modelfit/modelfit-report.schema.json

Source: [schemas/modelfit/modelfit-report.schema.json](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/modelfit/modelfit-report.schema.json)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://deepagentlabs.github.io/agenticlens/schemas/modelfit/modelfit-report.schema.json",
  "$defs": {
    "Alternative": {
      "properties": {
        "variant_id": {
          "title": "Variant Id",
          "type": "string"
        },
        "model": {
          "title": "Model",
          "type": "string"
        },
        "provider": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Provider"
        },
        "role": {
          "enum": [
            "alternative",
            "fallback"
          ],
          "title": "Role",
          "type": "string"
        },
        "weighted_score": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Weighted Score"
        },
        "pass_rate": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Pass Rate"
        },
        "cost_per_success_usd": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Cost Per Success Usd"
        },
        "reason": {
          "title": "Reason",
          "type": "string"
        }
      },
      "required": [
        "variant_id",
        "model",
        "role",
        "reason"
      ],
      "title": "Alternative",
      "type": "object"
    },
    "CandidateMetrics": {
      "description": "One candidate's measured evidence on one task category.",
      "properties": {
        "variant_id": {
          "title": "Variant Id",
          "type": "string"
        },
        "variant_name": {
          "title": "Variant Name",
          "type": "string"
        },
        "model": {
          "title": "Model",
          "type": "string"
        },
        "provider": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Provider"
        },
        "deployment": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Deployment"
        },
        "capabilities": {
          "items": {
            "type": "string"
          },
          "title": "Capabilities",
          "type": "array"
        },
        "factors": {
          "additionalProperties": {
            "type": "string"
          },
          "title": "Factors",
          "type": "object"
        },
        "source_index": {
          "description": "Index into the report's `sources`.",
          "minimum": 0,
          "title": "Source Index",
          "type": "integer"
        },
        "case_ids": {
          "items": {
            "type": "string"
          },
          "title": "Case Ids",
          "type": "array"
        },
        "attempts": {
          "minimum": 0,
          "title": "Attempts",
          "type": "integer"
        },
        "passes": {
          "minimum": 0,
          "title": "Passes",
          "type": "integer"
        },
        "pass_rate": {
          "anyOf": [
            {
              "maximum": 1,
              "minimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Pass Rate"
        },
        "pass_rate_interval": {
          "anyOf": [
            {
              "$ref": "#/$defs/ConfidenceInterval"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "failed_trial_attempts": {
          "default": 0,
          "description": "Attempts lost because the whole trial failed.",
          "minimum": 0,
          "title": "Failed Trial Attempts",
          "type": "integer"
        },
        "mean_latency_ms": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Mean Latency Ms"
        },
        "p95_latency_ms": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "P95 Latency Ms"
        },
        "cost_complete": {
          "description": "Every completed attempt reported a cost; otherwise costs are unavailable.",
          "title": "Cost Complete",
          "type": "boolean"
        },
        "total_cost_usd": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Total Cost Usd"
        },
        "cost_per_case_usd": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Cost Per Case Usd"
        },
        "cost_per_success_usd": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Cost Per Success Usd"
        },
        "consistency_rate": {
          "anyOf": [
            {
              "maximum": 1,
              "minimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Consistency Rate"
        },
        "flaky_case_ids": {
          "items": {
            "type": "string"
          },
          "title": "Flaky Case Ids",
          "type": "array"
        },
        "safety_attempts": {
          "default": 0,
          "minimum": 0,
          "title": "Safety Attempts",
          "type": "integer"
        },
        "safety_pass_rate": {
          "anyOf": [
            {
              "maximum": 1,
              "minimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Safety Pass Rate"
        },
        "failed_safety_case_ids": {
          "items": {
            "type": "string"
          },
          "title": "Failed Safety Case Ids",
          "type": "array"
        },
        "feasible": {
          "default": false,
          "title": "Feasible",
          "type": "boolean"
        },
        "violations": {
          "items": {
            "$ref": "#/$defs/Violation"
          },
          "title": "Violations",
          "type": "array"
        },
        "component_scores": {
          "additionalProperties": {
            "type": "number"
          },
          "title": "Component Scores",
          "type": "object"
        },
        "weighted_score": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Only feasible candidates are scored.",
          "title": "Weighted Score"
        },
        "rank": {
          "anyOf": [
            {
              "minimum": 1,
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Rank among feasible candidates.",
          "title": "Rank"
        },
        "pareto_optimal": {
          "default": false,
          "title": "Pareto Optimal",
          "type": "boolean"
        },
        "cost_per_success_rank": {
          "anyOf": [
            {
              "minimum": 1,
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Cost Per Success Rank"
        }
      },
      "required": [
        "variant_id",
        "variant_name",
        "model",
        "source_index",
        "case_ids",
        "attempts",
        "passes",
        "cost_complete"
      ],
      "title": "CandidateMetrics",
      "type": "object"
    },
    "CategoryResult": {
      "properties": {
        "category": {
          "$ref": "#/$defs/TaskCategory"
        },
        "case_ids": {
          "items": {
            "type": "string"
          },
          "title": "Case Ids",
          "type": "array"
        },
        "constraints": {
          "$ref": "#/$defs/ModelConstraints",
          "description": "Effective constraints after overrides."
        },
        "weights": {
          "$ref": "#/$defs/ScoringWeights",
          "description": "Effective scoring weights."
        },
        "candidates": {
          "description": "Feasible candidates by rank, then infeasible ones.",
          "items": {
            "$ref": "#/$defs/CandidateMetrics"
          },
          "title": "Candidates",
          "type": "array"
        },
        "pareto_frontier_variant_ids": {
          "items": {
            "type": "string"
          },
          "title": "Pareto Frontier Variant Ids",
          "type": "array"
        },
        "cost_per_success_ranking": {
          "description": "Candidates with known cost per success, cheapest first.",
          "items": {
            "type": "string"
          },
          "title": "Cost Per Success Ranking",
          "type": "array"
        },
        "recommendation": {
          "$ref": "#/$defs/Recommendation"
        }
      },
      "required": [
        "category",
        "case_ids",
        "constraints",
        "weights",
        "candidates",
        "recommendation"
      ],
      "title": "CategoryResult",
      "type": "object"
    },
    "ConfidenceInterval": {
      "properties": {
        "lower": {
          "title": "Lower",
          "type": "number"
        },
        "upper": {
          "title": "Upper",
          "type": "number"
        },
        "confidence_level": {
          "exclusiveMaximum": 1,
          "exclusiveMinimum": 0,
          "title": "Confidence Level",
          "type": "number"
        },
        "method": {
          "title": "Method",
          "type": "string"
        }
      },
      "required": [
        "lower",
        "upper",
        "confidence_level",
        "method"
      ],
      "title": "ConfidenceInterval",
      "type": "object"
    },
    "EvidenceSource": {
      "description": "One experiment report the recommendations were computed from.",
      "properties": {
        "experiment_name": {
          "title": "Experiment Name",
          "type": "string"
        },
        "experiment_version": {
          "title": "Experiment Version",
          "type": "string"
        },
        "suite_name": {
          "title": "Suite Name",
          "type": "string"
        },
        "suite_version": {
          "title": "Suite Version",
          "type": "string"
        },
        "baseline_variant_id": {
          "title": "Baseline Variant Id",
          "type": "string"
        },
        "trial_count": {
          "minimum": 1,
          "title": "Trial Count",
          "type": "integer"
        },
        "created_at": {
          "format": "date-time",
          "title": "Created At",
          "type": "string"
        },
        "variant_ids": {
          "items": {
            "type": "string"
          },
          "title": "Variant Ids",
          "type": "array"
        },
        "file": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Report file name, without directories.",
          "title": "File"
        },
        "sha256": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "SHA-256 of the report file bytes, when loaded from a file.",
          "title": "Sha256"
        }
      },
      "required": [
        "experiment_name",
        "experiment_version",
        "suite_name",
        "suite_version",
        "baseline_variant_id",
        "trial_count",
        "created_at",
        "variant_ids"
      ],
      "title": "EvidenceSource",
      "type": "object"
    },
    "MatrixRow": {
      "description": "One cell of the task-level model matrix: a category x candidate pair.",
      "properties": {
        "category_id": {
          "title": "Category Id",
          "type": "string"
        },
        "variant_id": {
          "title": "Variant Id",
          "type": "string"
        },
        "model": {
          "title": "Model",
          "type": "string"
        },
        "provider": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Provider"
        },
        "role": {
          "enum": [
            "recommended",
            "alternative",
            "fallback",
            "feasible",
            "infeasible"
          ],
          "title": "Role",
          "type": "string"
        },
        "feasible": {
          "title": "Feasible",
          "type": "boolean"
        },
        "attempts": {
          "title": "Attempts",
          "type": "integer"
        },
        "pass_rate": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Pass Rate"
        },
        "cost_per_success_usd": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Cost Per Success Usd"
        },
        "mean_latency_ms": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Mean Latency Ms"
        },
        "weighted_score": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Weighted Score"
        },
        "violations": {
          "items": {
            "type": "string"
          },
          "title": "Violations",
          "type": "array"
        }
      },
      "required": [
        "category_id",
        "variant_id",
        "model",
        "role",
        "feasible",
        "attempts"
      ],
      "title": "MatrixRow",
      "type": "object"
    },
    "ModelConstraints": {
      "description": "Hard constraints a candidate must satisfy to be recommended.\n\nEvery limit is optional. A limit that cannot be checked because the\nevidence is missing (for example an unpriced trial under a cost limit, or\nan unknown provider under a provider allow-list) is a violation: ModelFit\nnever assumes a candidate passes a constraint it has no evidence for.",
      "properties": {
        "min_pass_rate": {
          "anyOf": [
            {
              "maximum": 1,
              "minimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Min Pass Rate"
        },
        "min_pass_rate_lower_bound": {
          "anyOf": [
            {
              "maximum": 1,
              "minimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Minimum lower bound of the pass rate's Wilson confidence interval.",
          "title": "Min Pass Rate Lower Bound"
        },
        "max_cost_per_case_usd": {
          "anyOf": [
            {
              "minimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Max Cost Per Case Usd"
        },
        "max_cost_per_success_usd": {
          "anyOf": [
            {
              "minimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Max Cost Per Success Usd"
        },
        "max_mean_latency_ms": {
          "anyOf": [
            {
              "exclusiveMinimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Max Mean Latency Ms"
        },
        "max_p95_latency_ms": {
          "anyOf": [
            {
              "exclusiveMinimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Max P95 Latency Ms"
        },
        "min_consistency": {
          "anyOf": [
            {
              "maximum": 1,
              "minimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Minimum share of cases with the same outcome on every attempt.",
          "title": "Min Consistency"
        },
        "min_safety_pass_rate": {
          "anyOf": [
            {
              "maximum": 1,
              "minimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Minimum pass rate over every safety-tagged case in the suite.",
          "title": "Min Safety Pass Rate"
        },
        "allowed_providers": {
          "anyOf": [
            {
              "items": {
                "type": "string"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Allowed Providers"
        },
        "blocked_providers": {
          "anyOf": [
            {
              "items": {
                "type": "string"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "description": "`null` in an override clears the default block-list.",
          "title": "Blocked Providers"
        },
        "allowed_deployments": {
          "anyOf": [
            {
              "items": {
                "type": "string"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Allowed Deployments"
        },
        "required_capabilities": {
          "anyOf": [
            {
              "items": {
                "type": "string"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "description": "`null` in an override clears the default requirement.",
          "title": "Required Capabilities"
        }
      },
      "title": "ModelConstraints",
      "type": "object"
    },
    "ModelFitSummary": {
      "properties": {
        "categories": {
          "minimum": 0,
          "title": "Categories",
          "type": "integer"
        },
        "recommended": {
          "minimum": 0,
          "title": "Recommended",
          "type": "integer"
        },
        "unfit_category_ids": {
          "description": "Categories with no feasible candidate or no evidence.",
          "items": {
            "type": "string"
          },
          "title": "Unfit Category Ids",
          "type": "array"
        },
        "low_confidence_category_ids": {
          "items": {
            "type": "string"
          },
          "title": "Low Confidence Category Ids",
          "type": "array"
        },
        "candidates": {
          "minimum": 0,
          "title": "Candidates",
          "type": "integer"
        }
      },
      "required": [
        "categories",
        "recommended",
        "candidates"
      ],
      "title": "ModelFitSummary",
      "type": "object"
    },
    "QualityRisk": {
      "properties": {
        "kind": {
          "enum": [
            "quality_regression",
            "regressed_cases",
            "flaky_cases",
            "safety_failures",
            "low_evidence",
            "cost_unavailable",
            "failed_trials",
            "no_fallback"
          ],
          "title": "Kind",
          "type": "string"
        },
        "severity": {
          "enum": [
            "high",
            "medium",
            "low"
          ],
          "title": "Severity",
          "type": "string"
        },
        "message": {
          "title": "Message",
          "type": "string"
        },
        "case_ids": {
          "items": {
            "type": "string"
          },
          "title": "Case Ids",
          "type": "array"
        }
      },
      "required": [
        "kind",
        "severity",
        "message"
      ],
      "title": "QualityRisk",
      "type": "object"
    },
    "Recommendation": {
      "properties": {
        "category_id": {
          "title": "Category Id",
          "type": "string"
        },
        "status": {
          "enum": [
            "recommended",
            "no_feasible_model",
            "no_evidence"
          ],
          "title": "Status",
          "type": "string"
        },
        "variant_id": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Variant Id"
        },
        "model": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Model"
        },
        "provider": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Provider"
        },
        "weighted_score": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Weighted Score"
        },
        "confidence": {
          "anyOf": [
            {
              "enum": [
                "high",
                "medium",
                "low"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Confidence"
        },
        "confidence_reasons": {
          "items": {
            "type": "string"
          },
          "title": "Confidence Reasons",
          "type": "array"
        },
        "explanation": {
          "items": {
            "type": "string"
          },
          "title": "Explanation",
          "type": "array"
        },
        "alternatives": {
          "items": {
            "$ref": "#/$defs/Alternative"
          },
          "title": "Alternatives",
          "type": "array"
        },
        "fallback": {
          "anyOf": [
            {
              "$ref": "#/$defs/Alternative"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "savings": {
          "anyOf": [
            {
              "$ref": "#/$defs/SavingsEstimate"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "quality_risks": {
          "items": {
            "$ref": "#/$defs/QualityRisk"
          },
          "title": "Quality Risks",
          "type": "array"
        },
        "rejected_variant_ids": {
          "items": {
            "type": "string"
          },
          "title": "Rejected Variant Ids",
          "type": "array"
        }
      },
      "required": [
        "category_id",
        "status"
      ],
      "title": "Recommendation",
      "type": "object"
    },
    "SavingsEstimate": {
      "description": "Cost of the recommendation relative to the reference, from the same evidence.\n\nPositive `cost_per_case_savings_usd` means the recommendation is cheaper.\nSavings are only stated when both candidates' costs are complete.",
      "properties": {
        "reference_variant_id": {
          "title": "Reference Variant Id",
          "type": "string"
        },
        "recommended_variant_id": {
          "title": "Recommended Variant Id",
          "type": "string"
        },
        "available": {
          "title": "Available",
          "type": "boolean"
        },
        "reason": {
          "default": "",
          "title": "Reason",
          "type": "string"
        },
        "reference_cost_per_case_usd": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Reference Cost Per Case Usd"
        },
        "recommended_cost_per_case_usd": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Recommended Cost Per Case Usd"
        },
        "cost_per_case_savings_usd": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Cost Per Case Savings Usd"
        },
        "cost_per_case_savings_ratio": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Cost Per Case Savings Ratio"
        },
        "reference_cost_per_success_usd": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Reference Cost Per Success Usd"
        },
        "recommended_cost_per_success_usd": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Recommended Cost Per Success Usd"
        },
        "cost_per_success_savings_usd": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Cost Per Success Savings Usd"
        },
        "monthly_volume": {
          "anyOf": [
            {
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Monthly Volume"
        },
        "projected_monthly_savings_usd": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Projected Monthly Savings Usd"
        },
        "reference_pass_rate": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Reference Pass Rate"
        },
        "recommended_pass_rate": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Recommended Pass Rate"
        },
        "pass_rate_delta": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Pass Rate Delta"
        },
        "pass_rate_p_value": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Pass Rate P Value"
        },
        "reference_attempts": {
          "default": 0,
          "minimum": 0,
          "title": "Reference Attempts",
          "type": "integer"
        },
        "recommended_attempts": {
          "default": 0,
          "minimum": 0,
          "title": "Recommended Attempts",
          "type": "integer"
        },
        "case_ids": {
          "items": {
            "type": "string"
          },
          "title": "Case Ids",
          "type": "array"
        },
        "source_indexes": {
          "description": "Indexes into the report's `sources`.",
          "items": {
            "type": "integer"
          },
          "title": "Source Indexes",
          "type": "array"
        }
      },
      "required": [
        "reference_variant_id",
        "recommended_variant_id",
        "available"
      ],
      "title": "SavingsEstimate",
      "type": "object"
    },
    "ScoringWeights": {
      "description": "Relative weights of the four normalised components of a candidate's score.\n\nComponents are each in [0, 1]: `quality` is the pass rate; `cost` and\n`latency` are the cheapest (fastest) feasible candidate's cost per success\n(mean latency) divided by this candidate's; `reliability` is the share of\ncases with a consistent outcome across attempts.",
      "properties": {
        "quality": {
          "default": 0.5,
          "minimum": 0,
          "title": "Quality",
          "type": "number"
        },
        "cost": {
          "default": 0.3,
          "minimum": 0,
          "title": "Cost",
          "type": "number"
        },
        "latency": {
          "default": 0.1,
          "minimum": 0,
          "title": "Latency",
          "type": "number"
        },
        "reliability": {
          "default": 0.1,
          "minimum": 0,
          "title": "Reliability",
          "type": "number"
        }
      },
      "title": "ScoringWeights",
      "type": "object"
    },
    "TaskCategory": {
      "description": "A task category and the suite cases that belong to it.\n\nA case belongs to the category when its ID is listed in `case_ids`, it\ncarries any of `tags`, or its `metadata[\"domain\"]` is in `domains`. A\ncase can belong to several categories.",
      "properties": {
        "id": {
          "minLength": 1,
          "pattern": "^[A-Za-z0-9][A-Za-z0-9_.:-]*$",
          "title": "Id",
          "type": "string"
        },
        "name": {
          "default": "",
          "title": "Name",
          "type": "string"
        },
        "description": {
          "default": "",
          "title": "Description",
          "type": "string"
        },
        "tags": {
          "items": {
            "type": "string"
          },
          "title": "Tags",
          "type": "array"
        },
        "domains": {
          "items": {
            "type": "string"
          },
          "title": "Domains",
          "type": "array"
        },
        "case_ids": {
          "items": {
            "type": "string"
          },
          "title": "Case Ids",
          "type": "array"
        },
        "constraints": {
          "anyOf": [
            {
              "$ref": "#/$defs/ModelConstraints"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Overrides for the config's default constraints."
        },
        "weights": {
          "anyOf": [
            {
              "$ref": "#/$defs/ScoringWeights"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Replaces the config's default weights for this category."
        },
        "monthly_volume": {
          "anyOf": [
            {
              "minimum": 0,
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Expected requests per month, for savings projections.",
          "title": "Monthly Volume"
        }
      },
      "required": [
        "id"
      ],
      "title": "TaskCategory",
      "type": "object"
    },
    "Violation": {
      "properties": {
        "constraint": {
          "title": "Constraint",
          "type": "string"
        },
        "limit": {
          "default": null,
          "title": "Limit"
        },
        "observed": {
          "default": null,
          "title": "Observed"
        },
        "message": {
          "title": "Message",
          "type": "string"
        }
      },
      "required": [
        "constraint",
        "message"
      ],
      "title": "Violation",
      "type": "object"
    }
  },
  "properties": {
    "schema_version": {
      "default": "1.0",
      "title": "Schema Version",
      "type": "string"
    },
    "name": {
      "title": "Name",
      "type": "string"
    },
    "created_at": {
      "format": "date-time",
      "title": "Created At",
      "type": "string"
    },
    "model_factor": {
      "title": "Model Factor",
      "type": "string"
    },
    "reference_variant_id": {
      "title": "Reference Variant Id",
      "type": "string"
    },
    "safety_tags": {
      "items": {
        "type": "string"
      },
      "title": "Safety Tags",
      "type": "array"
    },
    "minimum_attempts": {
      "minimum": 1,
      "title": "Minimum Attempts",
      "type": "integer"
    },
    "confidence_level": {
      "exclusiveMaximum": 1,
      "exclusiveMinimum": 0,
      "title": "Confidence Level",
      "type": "number"
    },
    "sources": {
      "items": {
        "$ref": "#/$defs/EvidenceSource"
      },
      "title": "Sources",
      "type": "array"
    },
    "summary": {
      "$ref": "#/$defs/ModelFitSummary"
    },
    "categories": {
      "items": {
        "$ref": "#/$defs/CategoryResult"
      },
      "title": "Categories",
      "type": "array"
    },
    "matrix": {
      "items": {
        "$ref": "#/$defs/MatrixRow"
      },
      "title": "Matrix",
      "type": "array"
    },
    "uncategorized_case_ids": {
      "items": {
        "type": "string"
      },
      "title": "Uncategorized Case Ids",
      "type": "array"
    },
    "warnings": {
      "items": {
        "type": "string"
      },
      "title": "Warnings",
      "type": "array"
    }
  },
  "required": [
    "name",
    "model_factor",
    "reference_variant_id",
    "minimum_attempts",
    "confidence_level",
    "sources",
    "summary",
    "categories"
  ],
  "title": "AgenticLens ModelFit Report",
  "type": "object"
}
```

---

## Data contract: schemas/optimization/optimization-config.schema.json

Source: [schemas/optimization/optimization-config.schema.json](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/optimization/optimization-config.schema.json)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://deepagentlabs.github.io/agenticlens/schemas/optimization/optimization-config.schema.json",
  "additionalProperties": false,
  "description": "Thresholds for every rule. Each finding records the thresholds it used.",
  "properties": {
    "prompt_cache_min_prefix_tokens": {
      "default": 512,
      "minimum": 1,
      "title": "Prompt Cache Min Prefix Tokens",
      "type": "integer"
    },
    "prompt_cache_min_repeats": {
      "default": 2,
      "minimum": 2,
      "title": "Prompt Cache Min Repeats",
      "type": "integer"
    },
    "prompt_cache_read_price_ratio": {
      "default": 0.1,
      "description": "Cached-read price as a fraction of the uncached input price.",
      "maximum": 1,
      "minimum": 0,
      "title": "Prompt Cache Read Price Ratio",
      "type": "number"
    },
    "prompt_compression_min_input_tokens": {
      "default": 4000,
      "minimum": 1,
      "title": "Prompt Compression Min Input Tokens",
      "type": "integer"
    },
    "prompt_compression_min_ratio": {
      "default": 20.0,
      "exclusiveMinimum": 0,
      "title": "Prompt Compression Min Ratio",
      "type": "number"
    },
    "prompt_compression_target_reduction": {
      "default": 0.3,
      "exclusiveMaximum": 1,
      "exclusiveMinimum": 0,
      "title": "Prompt Compression Target Reduction",
      "type": "number"
    },
    "retrieval_min_chunks": {
      "default": 4,
      "minimum": 1,
      "title": "Retrieval Min Chunks",
      "type": "integer"
    },
    "retrieval_max_utility": {
      "default": 0.5,
      "maximum": 1,
      "minimum": 0,
      "title": "Retrieval Max Utility",
      "type": "number"
    },
    "retrieval_rerank_min_rank": {
      "default": 4,
      "description": "A used chunk ranked at or below this position suggests reranking.",
      "minimum": 2,
      "title": "Retrieval Rerank Min Rank",
      "type": "integer"
    },
    "memory_max_share": {
      "default": 0.4,
      "exclusiveMaximum": 1,
      "exclusiveMinimum": 0,
      "title": "Memory Max Share",
      "type": "number"
    },
    "memory_token_budget": {
      "default": 2000,
      "minimum": 0,
      "title": "Memory Token Budget",
      "type": "integer"
    },
    "tool_cache_min_repeats": {
      "default": 2,
      "minimum": 2,
      "title": "Tool Cache Min Repeats",
      "type": "integer"
    },
    "retry_min_unrecovered": {
      "default": 2,
      "minimum": 1,
      "title": "Retry Min Unrecovered",
      "type": "integer"
    },
    "redundant_step_min_repeats": {
      "default": 2,
      "minimum": 2,
      "title": "Redundant Step Min Repeats",
      "type": "integer"
    },
    "handoff_min_occurrences": {
      "default": 1,
      "minimum": 1,
      "title": "Handoff Min Occurrences",
      "type": "integer"
    },
    "tradeoff_min_runs": {
      "default": 3,
      "minimum": 1,
      "title": "Tradeoff Min Runs",
      "type": "integer"
    },
    "tradeoff_max_success_rate_drop": {
      "default": 0.05,
      "maximum": 1,
      "minimum": 0,
      "title": "Tradeoff Max Success Rate Drop",
      "type": "number"
    },
    "tradeoff_min_cost_reduction": {
      "default": 0.1,
      "exclusiveMaximum": 1,
      "exclusiveMinimum": 0,
      "title": "Tradeoff Min Cost Reduction",
      "type": "number"
    },
    "confidence_level": {
      "default": 0.95,
      "exclusiveMaximum": 1,
      "exclusiveMinimum": 0,
      "title": "Confidence Level",
      "type": "number"
    },
    "high_confidence_min_runs": {
      "default": 3,
      "minimum": 1,
      "title": "High Confidence Min Runs",
      "type": "integer"
    },
    "high_confidence_min_share": {
      "default": 0.5,
      "exclusiveMinimum": 0,
      "maximum": 1,
      "title": "High Confidence Min Share",
      "type": "number"
    },
    "monthly_runs": {
      "anyOf": [
        {
          "minimum": 1,
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Monthly Runs"
    }
  },
  "title": "OptimizationConfig",
  "type": "object"
}
```

---

## Data contract: schemas/optimization/optimization-report.schema.json

Source: [schemas/optimization/optimization-report.schema.json](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/optimization/optimization-report.schema.json)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://deepagentlabs.github.io/agenticlens/schemas/optimization/optimization-report.schema.json",
  "$defs": {
    "Opportunity": {
      "additionalProperties": false,
      "properties": {
        "opportunity_id": {
          "description": "Stable hash of rule and subject.",
          "title": "Opportunity Id",
          "type": "string"
        },
        "rule_id": {
          "title": "Rule Id",
          "type": "string"
        },
        "rule_version": {
          "title": "Rule Version",
          "type": "string"
        },
        "area": {
          "enum": [
            "prompt",
            "retrieval",
            "memory",
            "tool",
            "workflow",
            "model"
          ],
          "title": "Area",
          "type": "string"
        },
        "kind": {
          "title": "Kind",
          "type": "string"
        },
        "title": {
          "title": "Title",
          "type": "string"
        },
        "summary": {
          "title": "Summary",
          "type": "string"
        },
        "action": {
          "title": "Action",
          "type": "string"
        },
        "subject": {
          "additionalProperties": true,
          "title": "Subject",
          "type": "object"
        },
        "thresholds": {
          "additionalProperties": true,
          "title": "Thresholds",
          "type": "object"
        },
        "runs_observed": {
          "minimum": 0,
          "title": "Runs Observed",
          "type": "integer"
        },
        "runs_affected": {
          "minimum": 0,
          "title": "Runs Affected",
          "type": "integer"
        },
        "evidence": {
          "items": {
            "$ref": "#/$defs/OpportunityEvidence"
          },
          "title": "Evidence",
          "type": "array"
        },
        "benefit": {
          "$ref": "#/$defs/ProjectedBenefit"
        },
        "confidence": {
          "enum": [
            "high",
            "medium",
            "low"
          ],
          "title": "Confidence",
          "type": "string"
        },
        "confidence_reasons": {
          "items": {
            "type": "string"
          },
          "title": "Confidence Reasons",
          "type": "array"
        },
        "risks": {
          "items": {
            "$ref": "#/$defs/QualityRisk"
          },
          "title": "Risks",
          "type": "array"
        }
      },
      "required": [
        "opportunity_id",
        "rule_id",
        "rule_version",
        "area",
        "kind",
        "title",
        "summary",
        "action",
        "runs_observed",
        "runs_affected",
        "evidence",
        "benefit",
        "confidence"
      ],
      "title": "Opportunity",
      "type": "object"
    },
    "OpportunityEvidence": {
      "additionalProperties": false,
      "description": "One measured observation backing an opportunity.",
      "properties": {
        "run_id": {
          "title": "Run Id",
          "type": "string"
        },
        "span_ids": {
          "items": {
            "type": "string"
          },
          "title": "Span Ids",
          "type": "array"
        },
        "measurements": {
          "additionalProperties": true,
          "title": "Measurements",
          "type": "object"
        },
        "reasoning": {
          "title": "Reasoning",
          "type": "string"
        }
      },
      "required": [
        "run_id",
        "reasoning"
      ],
      "title": "OpportunityEvidence",
      "type": "object"
    },
    "OptimizationConfig": {
      "additionalProperties": false,
      "description": "Thresholds for every rule. Each finding records the thresholds it used.",
      "properties": {
        "prompt_cache_min_prefix_tokens": {
          "default": 512,
          "minimum": 1,
          "title": "Prompt Cache Min Prefix Tokens",
          "type": "integer"
        },
        "prompt_cache_min_repeats": {
          "default": 2,
          "minimum": 2,
          "title": "Prompt Cache Min Repeats",
          "type": "integer"
        },
        "prompt_cache_read_price_ratio": {
          "default": 0.1,
          "description": "Cached-read price as a fraction of the uncached input price.",
          "maximum": 1,
          "minimum": 0,
          "title": "Prompt Cache Read Price Ratio",
          "type": "number"
        },
        "prompt_compression_min_input_tokens": {
          "default": 4000,
          "minimum": 1,
          "title": "Prompt Compression Min Input Tokens",
          "type": "integer"
        },
        "prompt_compression_min_ratio": {
          "default": 20.0,
          "exclusiveMinimum": 0,
          "title": "Prompt Compression Min Ratio",
          "type": "number"
        },
        "prompt_compression_target_reduction": {
          "default": 0.3,
          "exclusiveMaximum": 1,
          "exclusiveMinimum": 0,
          "title": "Prompt Compression Target Reduction",
          "type": "number"
        },
        "retrieval_min_chunks": {
          "default": 4,
          "minimum": 1,
          "title": "Retrieval Min Chunks",
          "type": "integer"
        },
        "retrieval_max_utility": {
          "default": 0.5,
          "maximum": 1,
          "minimum": 0,
          "title": "Retrieval Max Utility",
          "type": "number"
        },
        "retrieval_rerank_min_rank": {
          "default": 4,
          "description": "A used chunk ranked at or below this position suggests reranking.",
          "minimum": 2,
          "title": "Retrieval Rerank Min Rank",
          "type": "integer"
        },
        "memory_max_share": {
          "default": 0.4,
          "exclusiveMaximum": 1,
          "exclusiveMinimum": 0,
          "title": "Memory Max Share",
          "type": "number"
        },
        "memory_token_budget": {
          "default": 2000,
          "minimum": 0,
          "title": "Memory Token Budget",
          "type": "integer"
        },
        "tool_cache_min_repeats": {
          "default": 2,
          "minimum": 2,
          "title": "Tool Cache Min Repeats",
          "type": "integer"
        },
        "retry_min_unrecovered": {
          "default": 2,
          "minimum": 1,
          "title": "Retry Min Unrecovered",
          "type": "integer"
        },
        "redundant_step_min_repeats": {
          "default": 2,
          "minimum": 2,
          "title": "Redundant Step Min Repeats",
          "type": "integer"
        },
        "handoff_min_occurrences": {
          "default": 1,
          "minimum": 1,
          "title": "Handoff Min Occurrences",
          "type": "integer"
        },
        "tradeoff_min_runs": {
          "default": 3,
          "minimum": 1,
          "title": "Tradeoff Min Runs",
          "type": "integer"
        },
        "tradeoff_max_success_rate_drop": {
          "default": 0.05,
          "maximum": 1,
          "minimum": 0,
          "title": "Tradeoff Max Success Rate Drop",
          "type": "number"
        },
        "tradeoff_min_cost_reduction": {
          "default": 0.1,
          "exclusiveMaximum": 1,
          "exclusiveMinimum": 0,
          "title": "Tradeoff Min Cost Reduction",
          "type": "number"
        },
        "confidence_level": {
          "default": 0.95,
          "exclusiveMaximum": 1,
          "exclusiveMinimum": 0,
          "title": "Confidence Level",
          "type": "number"
        },
        "high_confidence_min_runs": {
          "default": 3,
          "minimum": 1,
          "title": "High Confidence Min Runs",
          "type": "integer"
        },
        "high_confidence_min_share": {
          "default": 0.5,
          "exclusiveMinimum": 0,
          "maximum": 1,
          "title": "High Confidence Min Share",
          "type": "number"
        },
        "monthly_runs": {
          "anyOf": [
            {
              "minimum": 1,
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Monthly Runs"
        }
      },
      "title": "OptimizationConfig",
      "type": "object"
    },
    "ProjectedBenefit": {
      "additionalProperties": false,
      "description": "Expected per-run savings derived from measured spans and a stated basis.\n\nCost is `None` whenever any affected span lacks a recorded cost; it is never\nestimated from list prices. Values are projections, not measurements.",
      "properties": {
        "tokens_per_run": {
          "minimum": 0,
          "title": "Tokens Per Run",
          "type": "number"
        },
        "cost_usd_per_run": {
          "anyOf": [
            {
              "minimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Cost Usd Per Run"
        },
        "latency_ms_per_run": {
          "default": 0.0,
          "minimum": 0,
          "title": "Latency Ms Per Run",
          "type": "number"
        },
        "monthly_cost_usd": {
          "anyOf": [
            {
              "minimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Monthly Cost Usd"
        },
        "cost_available": {
          "title": "Cost Available",
          "type": "boolean"
        },
        "basis": {
          "title": "Basis",
          "type": "string"
        }
      },
      "required": [
        "tokens_per_run",
        "cost_available",
        "basis"
      ],
      "title": "ProjectedBenefit",
      "type": "object"
    },
    "QualityRisk": {
      "additionalProperties": false,
      "properties": {
        "kind": {
          "title": "Kind",
          "type": "string"
        },
        "severity": {
          "enum": [
            "low",
            "medium",
            "high"
          ],
          "title": "Severity",
          "type": "string"
        },
        "description": {
          "title": "Description",
          "type": "string"
        }
      },
      "required": [
        "kind",
        "severity",
        "description"
      ],
      "title": "QualityRisk",
      "type": "object"
    },
    "RunSource": {
      "additionalProperties": false,
      "properties": {
        "run_id": {
          "title": "Run Id",
          "type": "string"
        },
        "variant_id": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Variant Id"
        },
        "spans": {
          "title": "Spans",
          "type": "integer"
        },
        "tokens": {
          "title": "Tokens",
          "type": "integer"
        },
        "cost_usd": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Cost Usd"
        },
        "task_success": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Task Success"
        }
      },
      "required": [
        "run_id",
        "spans",
        "tokens"
      ],
      "title": "RunSource",
      "type": "object"
    },
    "TradeoffAnalysis": {
      "additionalProperties": false,
      "properties": {
        "baseline_variant_id": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Baseline Variant Id"
        },
        "variants": {
          "items": {
            "$ref": "#/$defs/VariantTradeoff"
          },
          "title": "Variants",
          "type": "array"
        },
        "excluded": {
          "additionalProperties": {
            "type": "string"
          },
          "description": "Variant ID to the reason it was not compared.",
          "title": "Excluded",
          "type": "object"
        }
      },
      "title": "TradeoffAnalysis",
      "type": "object"
    },
    "VariantTradeoff": {
      "additionalProperties": false,
      "description": "Measured quality and cost of one experiment variant across its runs.",
      "properties": {
        "variant_id": {
          "title": "Variant Id",
          "type": "string"
        },
        "runs": {
          "title": "Runs",
          "type": "integer"
        },
        "successes": {
          "title": "Successes",
          "type": "integer"
        },
        "success_rate": {
          "title": "Success Rate",
          "type": "number"
        },
        "success_interval": {
          "maxItems": 2,
          "minItems": 2,
          "prefixItems": [
            {
              "type": "number"
            },
            {
              "type": "number"
            }
          ],
          "title": "Success Interval",
          "type": "array"
        },
        "mean_cost_usd": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Mean Cost Usd"
        },
        "cost_per_success_usd": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Cost Per Success Usd"
        },
        "mean_latency_ms": {
          "title": "Mean Latency Ms",
          "type": "number"
        },
        "mean_tokens": {
          "title": "Mean Tokens",
          "type": "number"
        },
        "pareto_optimal": {
          "default": false,
          "title": "Pareto Optimal",
          "type": "boolean"
        },
        "success_rate_delta": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Versus the baseline variant; negative is worse.",
          "title": "Success Rate Delta"
        },
        "cost_delta_usd": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Versus the baseline variant; negative is cheaper.",
          "title": "Cost Delta Usd"
        },
        "p_value": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "P Value"
        }
      },
      "required": [
        "variant_id",
        "runs",
        "successes",
        "success_rate",
        "success_interval",
        "mean_latency_ms",
        "mean_tokens"
      ],
      "title": "VariantTradeoff",
      "type": "object"
    }
  },
  "additionalProperties": false,
  "description": "Reproducible: no wall-clock values, ordered deterministically.",
  "properties": {
    "schema_version": {
      "const": "1.0",
      "default": "1.0",
      "title": "Schema Version",
      "type": "string"
    },
    "runs": {
      "items": {
        "$ref": "#/$defs/RunSource"
      },
      "title": "Runs",
      "type": "array"
    },
    "total_tokens": {
      "title": "Total Tokens",
      "type": "integer"
    },
    "total_cost_usd": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Total Cost Usd"
    },
    "config": {
      "$ref": "#/$defs/OptimizationConfig"
    },
    "opportunities": {
      "items": {
        "$ref": "#/$defs/Opportunity"
      },
      "title": "Opportunities",
      "type": "array"
    },
    "tradeoffs": {
      "$ref": "#/$defs/TradeoffAnalysis"
    }
  },
  "required": [
    "runs",
    "total_tokens",
    "config"
  ],
  "title": "OptimizationReport",
  "type": "object"
}
```

---

## Data contract: schemas/optimization/outcome-evaluation.schema.json

Source: [schemas/optimization/outcome-evaluation.schema.json](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/optimization/outcome-evaluation.schema.json)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://deepagentlabs.github.io/agenticlens/schemas/optimization/outcome-evaluation.schema.json",
  "$defs": {
    "MetricChange": {
      "additionalProperties": false,
      "description": "Per-run means before and after adoption; `None` when not measurable.",
      "properties": {
        "before": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Before"
        },
        "after": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "After"
        },
        "delta": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Delta"
        }
      },
      "title": "MetricChange",
      "type": "object"
    },
    "ObservedOutcome": {
      "additionalProperties": false,
      "properties": {
        "before_runs": {
          "title": "Before Runs",
          "type": "integer"
        },
        "after_runs": {
          "title": "After Runs",
          "type": "integer"
        },
        "tokens_per_run": {
          "$ref": "#/$defs/MetricChange"
        },
        "cost_usd_per_run": {
          "$ref": "#/$defs/MetricChange"
        },
        "latency_ms_per_run": {
          "$ref": "#/$defs/MetricChange"
        },
        "success_rate": {
          "$ref": "#/$defs/MetricChange"
        },
        "success_p_value": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Success P Value"
        },
        "still_detected": {
          "description": "The same rule still finds this opportunity in the after runs.",
          "title": "Still Detected",
          "type": "boolean"
        }
      },
      "required": [
        "before_runs",
        "after_runs",
        "tokens_per_run",
        "cost_usd_per_run",
        "latency_ms_per_run",
        "success_rate",
        "still_detected"
      ],
      "title": "ObservedOutcome",
      "type": "object"
    },
    "ProjectedBenefit": {
      "additionalProperties": false,
      "description": "Expected per-run savings derived from measured spans and a stated basis.\n\nCost is `None` whenever any affected span lacks a recorded cost; it is never\nestimated from list prices. Values are projections, not measurements.",
      "properties": {
        "tokens_per_run": {
          "minimum": 0,
          "title": "Tokens Per Run",
          "type": "number"
        },
        "cost_usd_per_run": {
          "anyOf": [
            {
              "minimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Cost Usd Per Run"
        },
        "latency_ms_per_run": {
          "default": 0.0,
          "minimum": 0,
          "title": "Latency Ms Per Run",
          "type": "number"
        },
        "monthly_cost_usd": {
          "anyOf": [
            {
              "minimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Monthly Cost Usd"
        },
        "cost_available": {
          "title": "Cost Available",
          "type": "boolean"
        },
        "basis": {
          "title": "Basis",
          "type": "string"
        }
      },
      "required": [
        "tokens_per_run",
        "cost_available",
        "basis"
      ],
      "title": "ProjectedBenefit",
      "type": "object"
    }
  },
  "additionalProperties": false,
  "description": "Projected and observed values side by side, never blended.",
  "properties": {
    "schema_version": {
      "const": "1.0",
      "default": "1.0",
      "title": "Schema Version",
      "type": "string"
    },
    "opportunity_id": {
      "title": "Opportunity Id",
      "type": "string"
    },
    "report_sha256": {
      "title": "Report Sha256",
      "type": "string"
    },
    "decision_status": {
      "anyOf": [
        {
          "enum": [
            "proposed",
            "accepted",
            "rejected",
            "adopted",
            "reverted"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Decision Status"
    },
    "projected": {
      "$ref": "#/$defs/ProjectedBenefit"
    },
    "observed": {
      "$ref": "#/$defs/ObservedOutcome"
    },
    "realized_basis": {
      "anyOf": [
        {
          "enum": [
            "tokens",
            "cost_usd"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Which per-run metric the realized ratio compares.",
      "title": "Realized Basis"
    },
    "realized_ratio": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Observed per-run saving divided by the projected saving.",
      "title": "Realized Ratio"
    },
    "status": {
      "enum": [
        "realized",
        "partially_realized",
        "not_realized",
        "quality_regressed",
        "insufficient_evidence"
      ],
      "title": "Status",
      "type": "string"
    },
    "reasons": {
      "items": {
        "type": "string"
      },
      "title": "Reasons",
      "type": "array"
    }
  },
  "required": [
    "opportunity_id",
    "report_sha256",
    "projected",
    "observed",
    "status"
  ],
  "title": "OutcomeEvaluation",
  "type": "object"
}
```

---

## Data contract: schemas/optimization/recommendation-decision.schema.json

Source: [schemas/optimization/recommendation-decision.schema.json](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/optimization/recommendation-decision.schema.json)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://deepagentlabs.github.io/agenticlens/schemas/optimization/recommendation-decision.schema.json",
  "additionalProperties": false,
  "description": "One ledger entry: a person or process deciding on an opportunity.",
  "properties": {
    "schema_version": {
      "const": "1.0",
      "default": "1.0",
      "title": "Schema Version",
      "type": "string"
    },
    "opportunity_id": {
      "minLength": 1,
      "title": "Opportunity Id",
      "type": "string"
    },
    "report_sha256": {
      "maxLength": 64,
      "minLength": 64,
      "title": "Report Sha256",
      "type": "string"
    },
    "status": {
      "enum": [
        "proposed",
        "accepted",
        "rejected",
        "adopted",
        "reverted"
      ],
      "title": "Status",
      "type": "string"
    },
    "decided_by": {
      "minLength": 1,
      "title": "Decided By",
      "type": "string"
    },
    "decided_at": {
      "format": "date-time",
      "title": "Decided At",
      "type": "string"
    },
    "reason": {
      "default": "",
      "title": "Reason",
      "type": "string"
    },
    "change_reference": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "PR, commit, or config version that adopted the change.",
      "title": "Change Reference"
    }
  },
  "required": [
    "opportunity_id",
    "report_sha256",
    "status",
    "decided_by",
    "decided_at"
  ],
  "title": "RecommendationDecision",
  "type": "object"
}
```

---

## Data contract: schemas/report.schema.json

Source: [schemas/report.schema.json](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/report.schema.json)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://deepagentlabs.github.io/agenticlens/schemas/v1/report.schema.json",
  "title": "AgenticLens Comparison Report",
  "type": "object",
  "required": [
    "schema_version",
    "baseline",
    "candidate",
    "regression_threshold",
    "regressions"
  ],
  "properties": {
    "schema_version": {
      "const": "1.0"
    },
    "baseline": {
      "type": "object"
    },
    "candidate": {
      "type": "object"
    },
    "regression_threshold": {
      "type": "number",
      "minimum": 0
    },
    "regressions": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  }
}
```

---

## Data contract: schemas/routing/decision.schema.json

Source: [schemas/routing/decision.schema.json](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/routing/decision.schema.json)

```json
{
  "$defs": {
    "RouteRequest": {
      "additionalProperties": false,
      "properties": {
        "request_id": {
          "minLength": 1,
          "title": "Request Id",
          "type": "string"
        },
        "category_id": {
          "minLength": 1,
          "title": "Category Id",
          "type": "string"
        }
      },
      "required": [
        "request_id",
        "category_id"
      ],
      "title": "RouteRequest",
      "type": "object"
    },
    "RouteTarget": {
      "additionalProperties": false,
      "properties": {
        "variant_id": {
          "title": "Variant Id",
          "type": "string"
        },
        "model": {
          "title": "Model",
          "type": "string"
        },
        "provider": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Provider"
        },
        "deployment": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Deployment"
        },
        "source_index": {
          "title": "Source Index",
          "type": "integer"
        },
        "weighted_score": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Weighted Score"
        }
      },
      "required": [
        "variant_id",
        "model",
        "source_index"
      ],
      "title": "RouteTarget",
      "type": "object"
    }
  },
  "additionalProperties": false,
  "properties": {
    "schema_version": {
      "const": "1.0",
      "default": "1.0",
      "title": "Schema Version",
      "type": "string"
    },
    "decision_id": {
      "title": "Decision Id",
      "type": "string"
    },
    "created_at": {
      "format": "date-time",
      "title": "Created At",
      "type": "string"
    },
    "request": {
      "$ref": "#/$defs/RouteRequest"
    },
    "policy_name": {
      "title": "Policy Name",
      "type": "string"
    },
    "policy_version": {
      "title": "Policy Version",
      "type": "string"
    },
    "policy_sha256": {
      "title": "Policy Sha256",
      "type": "string"
    },
    "report_sha256": {
      "title": "Report Sha256",
      "type": "string"
    },
    "mode": {
      "enum": [
        "advisory",
        "enforce",
        "shadow",
        "canary"
      ],
      "title": "Mode",
      "type": "string"
    },
    "status": {
      "enum": [
        "selected",
        "blocked",
        "escalated"
      ],
      "title": "Status",
      "type": "string"
    },
    "confidence": {
      "anyOf": [
        {
          "enum": [
            "high",
            "medium",
            "low"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Confidence"
    },
    "reasons": {
      "items": {
        "type": "string"
      },
      "title": "Reasons",
      "type": "array"
    },
    "rejected": {
      "additionalProperties": {
        "items": {
          "type": "string"
        },
        "type": "array"
      },
      "title": "Rejected",
      "type": "object"
    },
    "targets": {
      "items": {
        "$ref": "#/$defs/RouteTarget"
      },
      "title": "Targets",
      "type": "array"
    },
    "shadow_target": {
      "anyOf": [
        {
          "$ref": "#/$defs/RouteTarget"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "cohort": {
      "anyOf": [
        {
          "enum": [
            "baseline",
            "canary"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Cohort"
    }
  },
  "required": [
    "request",
    "policy_name",
    "policy_version",
    "policy_sha256",
    "report_sha256",
    "mode",
    "status"
  ],
  "title": "RouteDecision",
  "type": "object"
}
```

---

## Data contract: schemas/routing/policy.schema.json

Source: [schemas/routing/policy.schema.json](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/routing/policy.schema.json)

```json
{
  "$defs": {
    "RoutingConstraints": {
      "additionalProperties": false,
      "description": "Routing policies reject unknown constraint names instead of dropping limits.",
      "properties": {
        "min_pass_rate": {
          "anyOf": [
            {
              "maximum": 1,
              "minimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Min Pass Rate"
        },
        "min_pass_rate_lower_bound": {
          "anyOf": [
            {
              "maximum": 1,
              "minimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Minimum lower bound of the pass rate's Wilson confidence interval.",
          "title": "Min Pass Rate Lower Bound"
        },
        "max_cost_per_case_usd": {
          "anyOf": [
            {
              "minimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Max Cost Per Case Usd"
        },
        "max_cost_per_success_usd": {
          "anyOf": [
            {
              "minimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Max Cost Per Success Usd"
        },
        "max_mean_latency_ms": {
          "anyOf": [
            {
              "exclusiveMinimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Max Mean Latency Ms"
        },
        "max_p95_latency_ms": {
          "anyOf": [
            {
              "exclusiveMinimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Max P95 Latency Ms"
        },
        "min_consistency": {
          "anyOf": [
            {
              "maximum": 1,
              "minimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Minimum share of cases with the same outcome on every attempt.",
          "title": "Min Consistency"
        },
        "min_safety_pass_rate": {
          "anyOf": [
            {
              "maximum": 1,
              "minimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Minimum pass rate over every safety-tagged case in the suite.",
          "title": "Min Safety Pass Rate"
        },
        "allowed_providers": {
          "anyOf": [
            {
              "items": {
                "type": "string"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Allowed Providers"
        },
        "blocked_providers": {
          "anyOf": [
            {
              "items": {
                "type": "string"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "description": "`null` in an override clears the default block-list.",
          "title": "Blocked Providers"
        },
        "allowed_deployments": {
          "anyOf": [
            {
              "items": {
                "type": "string"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Allowed Deployments"
        },
        "required_capabilities": {
          "anyOf": [
            {
              "items": {
                "type": "string"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "description": "`null` in an override clears the default requirement.",
          "title": "Required Capabilities"
        }
      },
      "title": "RoutingConstraints",
      "type": "object"
    }
  },
  "additionalProperties": false,
  "properties": {
    "name": {
      "default": "routing",
      "minLength": 1,
      "title": "Name",
      "type": "string"
    },
    "version": {
      "default": "1",
      "minLength": 1,
      "title": "Version",
      "type": "string"
    },
    "mode": {
      "default": "advisory",
      "enum": [
        "advisory",
        "enforce",
        "shadow",
        "canary"
      ],
      "title": "Mode",
      "type": "string"
    },
    "strategy": {
      "default": "score",
      "enum": [
        "score",
        "rule"
      ],
      "title": "Strategy",
      "type": "string"
    },
    "rules": {
      "additionalProperties": {
        "items": {
          "type": "string"
        },
        "type": "array"
      },
      "title": "Rules",
      "type": "object"
    },
    "constraints": {
      "$ref": "#/$defs/RoutingConstraints"
    },
    "minimum_confidence": {
      "default": "medium",
      "enum": [
        "high",
        "medium",
        "low"
      ],
      "title": "Minimum Confidence",
      "type": "string"
    },
    "on_unroutable": {
      "default": "escalate",
      "enum": [
        "block",
        "escalate"
      ],
      "title": "On Unroutable",
      "type": "string"
    },
    "baseline_variant_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Baseline Variant Id"
    },
    "canary_fraction": {
      "default": 0.1,
      "maximum": 1,
      "minimum": 0,
      "title": "Canary Fraction",
      "type": "number"
    },
    "allocation_salt": {
      "default": "lens-routing-v1",
      "title": "Allocation Salt",
      "type": "string"
    },
    "max_attempts": {
      "default": 3,
      "maximum": 20,
      "minimum": 1,
      "title": "Max Attempts",
      "type": "integer"
    }
  },
  "title": "RoutingPolicy",
  "type": "object"
}
```

---

## Data contract: schemas/routing/result.schema.json

Source: [schemas/routing/result.schema.json](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/routing/result.schema.json)

```json
{
  "$defs": {
    "RouteAttempt": {
      "additionalProperties": false,
      "properties": {
        "target": {
          "$ref": "#/$defs/RouteTarget"
        },
        "role": {
          "enum": [
            "primary",
            "fallback",
            "shadow"
          ],
          "title": "Role",
          "type": "string"
        },
        "status": {
          "enum": [
            "succeeded",
            "unsuccessful",
            "retryable_error",
            "error"
          ],
          "title": "Status",
          "type": "string"
        },
        "latency_ms": {
          "minimum": 0,
          "title": "Latency Ms",
          "type": "number"
        },
        "cost_usd": {
          "anyOf": [
            {
              "minimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Cost Usd"
        }
      },
      "required": [
        "target",
        "role",
        "status",
        "latency_ms"
      ],
      "title": "RouteAttempt",
      "type": "object"
    },
    "RouteDecision": {
      "additionalProperties": false,
      "properties": {
        "schema_version": {
          "const": "1.0",
          "default": "1.0",
          "title": "Schema Version",
          "type": "string"
        },
        "decision_id": {
          "title": "Decision Id",
          "type": "string"
        },
        "created_at": {
          "format": "date-time",
          "title": "Created At",
          "type": "string"
        },
        "request": {
          "$ref": "#/$defs/RouteRequest"
        },
        "policy_name": {
          "title": "Policy Name",
          "type": "string"
        },
        "policy_version": {
          "title": "Policy Version",
          "type": "string"
        },
        "policy_sha256": {
          "title": "Policy Sha256",
          "type": "string"
        },
        "report_sha256": {
          "title": "Report Sha256",
          "type": "string"
        },
        "mode": {
          "enum": [
            "advisory",
            "enforce",
            "shadow",
            "canary"
          ],
          "title": "Mode",
          "type": "string"
        },
        "status": {
          "enum": [
            "selected",
            "blocked",
            "escalated"
          ],
          "title": "Status",
          "type": "string"
        },
        "confidence": {
          "anyOf": [
            {
              "enum": [
                "high",
                "medium",
                "low"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Confidence"
        },
        "reasons": {
          "items": {
            "type": "string"
          },
          "title": "Reasons",
          "type": "array"
        },
        "rejected": {
          "additionalProperties": {
            "items": {
              "type": "string"
            },
            "type": "array"
          },
          "title": "Rejected",
          "type": "object"
        },
        "targets": {
          "items": {
            "$ref": "#/$defs/RouteTarget"
          },
          "title": "Targets",
          "type": "array"
        },
        "shadow_target": {
          "anyOf": [
            {
              "$ref": "#/$defs/RouteTarget"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "cohort": {
          "anyOf": [
            {
              "enum": [
                "baseline",
                "canary"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Cohort"
        }
      },
      "required": [
        "request",
        "policy_name",
        "policy_version",
        "policy_sha256",
        "report_sha256",
        "mode",
        "status"
      ],
      "title": "RouteDecision",
      "type": "object"
    },
    "RouteRequest": {
      "additionalProperties": false,
      "properties": {
        "request_id": {
          "minLength": 1,
          "title": "Request Id",
          "type": "string"
        },
        "category_id": {
          "minLength": 1,
          "title": "Category Id",
          "type": "string"
        }
      },
      "required": [
        "request_id",
        "category_id"
      ],
      "title": "RouteRequest",
      "type": "object"
    },
    "RouteTarget": {
      "additionalProperties": false,
      "properties": {
        "variant_id": {
          "title": "Variant Id",
          "type": "string"
        },
        "model": {
          "title": "Model",
          "type": "string"
        },
        "provider": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Provider"
        },
        "deployment": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Deployment"
        },
        "source_index": {
          "title": "Source Index",
          "type": "integer"
        },
        "weighted_score": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Weighted Score"
        }
      },
      "required": [
        "variant_id",
        "model",
        "source_index"
      ],
      "title": "RouteTarget",
      "type": "object"
    }
  },
  "additionalProperties": false,
  "properties": {
    "decision": {
      "$ref": "#/$defs/RouteDecision"
    },
    "attempts": {
      "items": {
        "$ref": "#/$defs/RouteAttempt"
      },
      "title": "Attempts",
      "type": "array"
    },
    "served_variant_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Served Variant Id"
    },
    "status": {
      "enum": [
        "advisory",
        "blocked",
        "escalated",
        "succeeded",
        "failed"
      ],
      "title": "Status",
      "type": "string"
    }
  },
  "required": [
    "decision",
    "status"
  ],
  "title": "RoutingResult",
  "type": "object"
}
```

---

## Data contract: schemas/suites/duplicate-report.schema.json

Source: [schemas/suites/duplicate-report.schema.json](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/suites/duplicate-report.schema.json)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://deepagentlabs.github.io/agenticlens/schemas/suites/duplicate-report.schema.json",
  "$defs": {
    "DuplicateGroup": {
      "properties": {
        "kind": {
          "enum": [
            "exact",
            "near"
          ],
          "title": "Kind",
          "type": "string"
        },
        "case_ids": {
          "items": {
            "type": "string"
          },
          "minItems": 2,
          "title": "Case Ids",
          "type": "array"
        },
        "keep": {
          "description": "Case kept when duplicates are dropped (the first one).",
          "title": "Keep",
          "type": "string"
        },
        "similarity": {
          "description": "Lowest pairwise similarity in the group.",
          "maximum": 1,
          "minimum": 0,
          "title": "Similarity",
          "type": "number"
        },
        "conflicting": {
          "description": "True when the cases share an input but expect different results.",
          "title": "Conflicting",
          "type": "boolean"
        }
      },
      "required": [
        "kind",
        "case_ids",
        "keep",
        "similarity",
        "conflicting"
      ],
      "title": "DuplicateGroup",
      "type": "object"
    }
  },
  "properties": {
    "schema_version": {
      "default": "1.0",
      "title": "Schema Version",
      "type": "string"
    },
    "suite_name": {
      "title": "Suite Name",
      "type": "string"
    },
    "threshold": {
      "maximum": 1,
      "minimum": 0,
      "title": "Threshold",
      "type": "number"
    },
    "total_cases": {
      "title": "Total Cases",
      "type": "integer"
    },
    "groups": {
      "items": {
        "$ref": "#/$defs/DuplicateGroup"
      },
      "title": "Groups",
      "type": "array"
    },
    "duplicate_case_ids": {
      "description": "Every grouped case except the one kept.",
      "items": {
        "type": "string"
      },
      "title": "Duplicate Case Ids",
      "type": "array"
    },
    "conflicting_groups": {
      "default": 0,
      "title": "Conflicting Groups",
      "type": "integer"
    }
  },
  "required": [
    "suite_name",
    "threshold",
    "total_cases"
  ],
  "title": "AgenticLens Duplicate Report",
  "type": "object"
}
```

---

## Data contract: schemas/suites/feedback-batch.schema.json

Source: [schemas/suites/feedback-batch.schema.json](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/suites/feedback-batch.schema.json)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://deepagentlabs.github.io/agenticlens/schemas/suites/feedback-batch.schema.json",
  "$defs": {
    "FeedbackRecord": {
      "description": "User feedback about one agent response.\n\nPositive feedback confirms `output`; negative feedback needs a\n`corrected_output` to become a test case. `score` (0-1) is used only when\n`rating` is absent, with 0.5 and above counting as positive.",
      "properties": {
        "feedback_id": {
          "minLength": 1,
          "title": "Feedback Id",
          "type": "string"
        },
        "input": {
          "default": null,
          "title": "Input"
        },
        "output": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Output"
        },
        "rating": {
          "anyOf": [
            {
              "enum": [
                "positive",
                "negative"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Rating"
        },
        "score": {
          "anyOf": [
            {
              "maximum": 1,
              "minimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Score"
        },
        "corrected_output": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Corrected Output"
        },
        "comment": {
          "default": "",
          "title": "Comment",
          "type": "string"
        },
        "trace_id": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Trace Id"
        },
        "run_id": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Run Id"
        },
        "submitted_by": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Submitted By"
        },
        "tags": {
          "items": {
            "type": "string"
          },
          "title": "Tags",
          "type": "array"
        },
        "domain": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Domain"
        },
        "metadata": {
          "additionalProperties": true,
          "title": "Metadata",
          "type": "object"
        }
      },
      "required": [
        "feedback_id"
      ],
      "title": "FeedbackRecord",
      "type": "object"
    }
  },
  "properties": {
    "schema_version": {
      "default": "1.0",
      "title": "Schema Version",
      "type": "string"
    },
    "feedback": {
      "items": {
        "$ref": "#/$defs/FeedbackRecord"
      },
      "title": "Feedback",
      "type": "array"
    }
  },
  "required": [
    "feedback"
  ],
  "title": "AgenticLens Feedback Batch",
  "type": "object"
}
```

---

## Data contract: schemas/suites/masking-report.schema.json

Source: [schemas/suites/masking-report.schema.json](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/suites/masking-report.schema.json)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://deepagentlabs.github.io/agenticlens/schemas/suites/masking-report.schema.json",
  "$defs": {
    "MaskedLocation": {
      "properties": {
        "case_id": {
          "title": "Case Id",
          "type": "string"
        },
        "field": {
          "description": "Dotted path to the masked value, e.g. input.customer.email.",
          "title": "Field",
          "type": "string"
        },
        "pii_type": {
          "enum": [
            "email",
            "phone",
            "credit_card",
            "us_ssn",
            "ipv4",
            "secret",
            "sensitive_field"
          ],
          "title": "Pii Type",
          "type": "string"
        }
      },
      "required": [
        "case_id",
        "field",
        "pii_type"
      ],
      "title": "MaskedLocation",
      "type": "object"
    }
  },
  "properties": {
    "schema_version": {
      "default": "1.0",
      "title": "Schema Version",
      "type": "string"
    },
    "suite_name": {
      "title": "Suite Name",
      "type": "string"
    },
    "strategy": {
      "enum": [
        "redact",
        "hash"
      ],
      "title": "Strategy",
      "type": "string"
    },
    "applied": {
      "description": "False for a scan that reported but changed nothing.",
      "title": "Applied",
      "type": "boolean"
    },
    "total": {
      "default": 0,
      "title": "Total",
      "type": "integer"
    },
    "counts": {
      "additionalProperties": {
        "type": "integer"
      },
      "title": "Counts",
      "type": "object"
    },
    "locations": {
      "items": {
        "$ref": "#/$defs/MaskedLocation"
      },
      "title": "Locations",
      "type": "array"
    }
  },
  "required": [
    "suite_name",
    "strategy",
    "applied"
  ],
  "title": "AgenticLens Masking Report",
  "type": "object"
}
```

---

## Data contract: schemas/suites/suite-version.schema.json

Source: [schemas/suites/suite-version.schema.json](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/suites/suite-version.schema.json)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://deepagentlabs.github.io/agenticlens/schemas/suites/suite-version.schema.json",
  "$defs": {
    "ApprovalCheck": {
      "description": "One check run before a suite version was approved.",
      "properties": {
        "name": {
          "title": "Name",
          "type": "string"
        },
        "passed": {
          "title": "Passed",
          "type": "boolean"
        },
        "detail": {
          "title": "Detail",
          "type": "string"
        }
      },
      "required": [
        "name",
        "passed",
        "detail"
      ],
      "title": "ApprovalCheck",
      "type": "object"
    },
    "ApprovalRecord": {
      "properties": {
        "approved_by": {
          "minLength": 1,
          "title": "Approved By",
          "type": "string"
        },
        "approved_at": {
          "format": "date-time",
          "title": "Approved At",
          "type": "string"
        },
        "notes": {
          "default": "",
          "title": "Notes",
          "type": "string"
        },
        "checks": {
          "items": {
            "$ref": "#/$defs/ApprovalCheck"
          },
          "title": "Checks",
          "type": "array"
        }
      },
      "required": [
        "approved_by",
        "approved_at"
      ],
      "title": "ApprovalRecord",
      "type": "object"
    }
  },
  "description": "An approved, immutable suite version.\n\n`suite` is the agentic-evals `TestSuite` JSON exactly as approved;\n`content_sha256` is computed over its canonical JSON (sorted keys, no\nwhitespace). `record_sha256` covers the whole envelope except itself, so\nlater edits to the approval record, case count, or parent version are\ndetected as well as edits to the suite.",
  "properties": {
    "schema_version": {
      "default": "1.0",
      "title": "Schema Version",
      "type": "string"
    },
    "name": {
      "title": "Name",
      "type": "string"
    },
    "version": {
      "title": "Version",
      "type": "string"
    },
    "status": {
      "const": "approved",
      "default": "approved",
      "title": "Status",
      "type": "string"
    },
    "content_sha256": {
      "pattern": "^[0-9a-f]{64}$",
      "title": "Content Sha256",
      "type": "string"
    },
    "record_sha256": {
      "default": "",
      "description": "SHA-256 of the canonical envelope without this field.",
      "title": "Record Sha256",
      "type": "string"
    },
    "case_count": {
      "minimum": 1,
      "title": "Case Count",
      "type": "integer"
    },
    "parent_version": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Parent Version"
    },
    "approval": {
      "$ref": "#/$defs/ApprovalRecord"
    },
    "suite": {
      "additionalProperties": true,
      "title": "Suite",
      "type": "object"
    }
  },
  "required": [
    "name",
    "version",
    "content_sha256",
    "case_count",
    "approval",
    "suite"
  ],
  "title": "AgenticLens Suite Version",
  "type": "object"
}
```

---

## Data contract: schemas/trace.schema.json

Source: [schemas/trace.schema.json](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/trace.schema.json)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://deepagentlabs.github.io/agenticlens/schemas/v1/trace.schema.json",
  "title": "AgenticLens Run Trace",
  "type": "object",
  "required": [
    "schema_version",
    "run_id",
    "trace_id",
    "application_name",
    "started_at",
    "status",
    "spans"
  ],
  "properties": {
    "schema_version": {
      "const": "1.0"
    },
    "run_id": {
      "type": "string",
      "minLength": 1
    },
    "trace_id": {
      "type": "string",
      "minLength": 1
    },
    "application_name": {
      "type": "string",
      "minLength": 1
    },
    "started_at": {
      "type": "string",
      "format": "date-time"
    },
    "completed_at": {
      "type": [
        "string",
        "null"
      ],
      "format": "date-time"
    },
    "status": {
      "enum": [
        "running",
        "succeeded",
        "failed"
      ]
    },
    "spans": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/span"
      }
    },
    "metadata": {
      "type": "object"
    }
  },
  "$defs": {
    "span": {
      "type": "object",
      "required": [
        "span_id",
        "name",
        "span_type",
        "started_at",
        "status"
      ],
      "properties": {
        "span_id": {
          "type": "string",
          "minLength": 1
        },
        "parent_span_id": {
          "type": [
            "string",
            "null"
          ]
        },
        "name": {
          "type": "string",
          "minLength": 1
        },
        "span_type": {
          "enum": [
            "model_call",
            "planning",
            "memory_read",
            "memory_write",
            "retrieval",
            "tool_call",
            "validation",
            "retry",
            "delegation",
            "final_response",
            "custom"
          ]
        },
        "started_at": {
          "type": "string",
          "format": "date-time"
        },
        "completed_at": {
          "type": [
            "string",
            "null"
          ],
          "format": "date-time"
        },
        "latency_ms": {
          "type": "number",
          "minimum": 0
        },
        "input_tokens": {
          "type": "integer",
          "minimum": 0
        },
        "output_tokens": {
          "type": "integer",
          "minimum": 0
        },
        "status": {
          "enum": [
            "running",
            "succeeded",
            "failed"
          ]
        },
        "attributes": {
          "type": "object"
        }
      }
    }
  }
}
```

---

## Data contract: schemas/v2/finding.schema.json

Source: [schemas/v2/finding.schema.json](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/v2/finding.schema.json)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://deepagentlabs.github.io/agenticlens/schemas/v2/finding.schema.json",
  "title": "AgenticLens Finding",
  "type": "object",
  "required": [
    "finding_id",
    "category",
    "title",
    "description",
    "severity",
    "confidence",
    "span_ids",
    "evidence"
  ],
  "properties": {
    "finding_id": {
      "type": "string",
      "minLength": 1
    },
    "category": {
      "type": "string",
      "minLength": 1
    },
    "title": {
      "type": "string",
      "minLength": 1
    },
    "description": {
      "type": "string"
    },
    "severity": {
      "type": "string"
    },
    "confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1
    },
    "span_ids": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "evidence": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "source",
          "confidence",
          "details"
        ],
        "properties": {
          "source": {
            "type": "string",
            "minLength": 1
          },
          "span_id": {
            "type": [
              "string",
              "null"
            ]
          },
          "timestamp": {
            "type": [
              "string",
              "null"
            ],
            "format": "date-time"
          },
          "confidence": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
          },
          "reasoning": {
            "type": [
              "string",
              "null"
            ]
          },
          "details": {
            "type": "object"
          }
        },
        "additionalProperties": false
      }
    }
  }
}
```

---

## Data contract: schemas/enterprise/project.json

Source: [schemas/enterprise/project.json](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/enterprise/project.json)

```json
{
  "additionalProperties": false,
  "properties": {
    "organization": {
      "maxLength": 100,
      "minLength": 1,
      "pattern": "^[a-zA-Z0-9_-]+$",
      "title": "Organization",
      "type": "string"
    },
    "name": {
      "maxLength": 100,
      "minLength": 1,
      "pattern": "^[a-zA-Z0-9_-]+$",
      "title": "Name",
      "type": "string"
    }
  },
  "required": [
    "organization",
    "name"
  ],
  "title": "Project",
  "type": "object",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://deepagentlabs.io/agenticlens/enterprise/1-candidate/project.json"
}
```

---

## Data contract: schemas/enterprise/registry-entry.json

Source: [schemas/enterprise/registry-entry.json](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/enterprise/registry-entry.json)

```json
{
  "additionalProperties": false,
  "description": "Immutable metadata; prompt bodies and executable evaluators stay outside the registry.",
  "properties": {
    "kind": {
      "enum": [
        "model",
        "prompt"
      ],
      "title": "Kind",
      "type": "string"
    },
    "name": {
      "maxLength": 100,
      "minLength": 1,
      "pattern": "^[a-zA-Z0-9_-]+$",
      "title": "Name",
      "type": "string"
    },
    "version": {
      "maxLength": 100,
      "minLength": 1,
      "pattern": "^[a-zA-Z0-9_.-]+$",
      "title": "Version",
      "type": "string"
    },
    "content_sha256": {
      "pattern": "^[a-f0-9]{64}$",
      "title": "Content Sha256",
      "type": "string"
    }
  },
  "required": [
    "kind",
    "name",
    "version",
    "content_sha256"
  ],
  "title": "RegistryEntry",
  "type": "object",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://deepagentlabs.io/agenticlens/enterprise/1-candidate/registry-entry.json"
}
```

---

## Data contract: schemas/enterprise/service-config.json

Source: [schemas/enterprise/service-config.json](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/enterprise/service-config.json)

```json
{
  "$defs": {
    "Credential": {
      "additionalProperties": false,
      "description": "Configure SHA-256 digests of random bearer tokens, never plaintext tokens.",
      "properties": {
        "subject": {
          "maxLength": 100,
          "minLength": 1,
          "title": "Subject",
          "type": "string"
        },
        "token_sha256": {
          "format": "password",
          "title": "Token Sha256",
          "type": "string",
          "writeOnly": true
        },
        "project": {
          "$ref": "#/$defs/Project"
        },
        "role": {
          "enum": [
            "reader",
            "writer",
            "admin"
          ],
          "title": "Role",
          "type": "string"
        }
      },
      "required": [
        "subject",
        "token_sha256",
        "project",
        "role"
      ],
      "title": "Credential",
      "type": "object"
    },
    "GateConfig": {
      "description": "Release thresholds. The default is strict: every case must pass.\n\n`min_average_score` and `max_failed_cases` are extra checks, skipped\nwhen left `None` -- so `min_pass_rate` alone decides how many failures\nare tolerated, and a graded score below 1.0 on a passing case does not\nfail the gate unless an average-score floor is set explicitly.\n\n`min_tag_pass_rate` and `min_metric_pass_rate` set a floor for one\nslice of the report, keyed by tag or by `Score.metric`. They apply on\ntop of `min_pass_rate`, so a single tag or metric can be held to a\nstricter bar than the suite as a whole. A tag or metric named here but\nabsent from the report fails the gate rather than passing unchecked.\n\nJudge and live-target checks read `summary.judge` and `summary.live`.\n`max_judge_unavailable_scores` defaults to 0: a judgment the judge could\nnot deliver fails the gate even when its score was optional, and the\nreason names the affected cases. Set it to `None` to tolerate them.\n`max_judge_cost_usd` fails when any judge score lacks a cost, and\n`min_judge_agreement` fails when any case judged with `samples=N` has\nlower agreement than the floor, or no case was sampled at all.\n`max_timed_out_cases` and `max_target_error_cases` bound live-target\nfailures separately from wrong answers; both are unchecked by default,\nthough such cases already count as failed for `min_pass_rate`.",
      "properties": {
        "min_pass_rate": {
          "default": 1.0,
          "maximum": 1,
          "minimum": 0,
          "title": "Min Pass Rate",
          "type": "number"
        },
        "min_average_score": {
          "anyOf": [
            {
              "maximum": 1,
              "minimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Min Average Score"
        },
        "max_failed_cases": {
          "anyOf": [
            {
              "minimum": 0,
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Max Failed Cases"
        },
        "min_tag_pass_rate": {
          "additionalProperties": {
            "maximum": 1,
            "minimum": 0,
            "type": "number"
          },
          "title": "Min Tag Pass Rate",
          "type": "object"
        },
        "min_metric_pass_rate": {
          "additionalProperties": {
            "maximum": 1,
            "minimum": 0,
            "type": "number"
          },
          "title": "Min Metric Pass Rate",
          "type": "object"
        },
        "max_average_latency_ms": {
          "anyOf": [
            {
              "exclusiveMinimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Max Average Latency Ms"
        },
        "max_total_cost_usd": {
          "anyOf": [
            {
              "minimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Max Total Cost Usd"
        },
        "max_judge_unavailable_scores": {
          "anyOf": [
            {
              "minimum": 0,
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": 0,
          "title": "Max Judge Unavailable Scores"
        },
        "max_judge_cost_usd": {
          "anyOf": [
            {
              "minimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Max Judge Cost Usd"
        },
        "min_judge_agreement": {
          "anyOf": [
            {
              "maximum": 1,
              "minimum": 0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Min Judge Agreement"
        },
        "max_timed_out_cases": {
          "anyOf": [
            {
              "minimum": 0,
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Max Timed Out Cases"
        },
        "max_target_error_cases": {
          "anyOf": [
            {
              "minimum": 0,
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Max Target Error Cases"
        }
      },
      "title": "GateConfig",
      "type": "object"
    },
    "Project": {
      "additionalProperties": false,
      "properties": {
        "organization": {
          "maxLength": 100,
          "minLength": 1,
          "pattern": "^[a-zA-Z0-9_-]+$",
          "title": "Organization",
          "type": "string"
        },
        "name": {
          "maxLength": 100,
          "minLength": 1,
          "pattern": "^[a-zA-Z0-9_-]+$",
          "title": "Name",
          "type": "string"
        }
      },
      "required": [
        "organization",
        "name"
      ],
      "title": "Project",
      "type": "object"
    },
    "StoragePolicy": {
      "additionalProperties": false,
      "properties": {
        "max_age_days": {
          "default": 30,
          "maximum": 3650,
          "minimum": 1,
          "title": "Max Age Days",
          "type": "integer"
        },
        "max_traces": {
          "default": 1000,
          "maximum": 100000,
          "minimum": 1,
          "title": "Max Traces",
          "type": "integer"
        },
        "redact": {
          "const": true,
          "default": true,
          "title": "Redact",
          "type": "boolean"
        }
      },
      "title": "StoragePolicy",
      "type": "object"
    }
  },
  "additionalProperties": false,
  "properties": {
    "credentials": {
      "items": {
        "$ref": "#/$defs/Credential"
      },
      "minItems": 1,
      "title": "Credentials",
      "type": "array"
    },
    "storage_policy": {
      "$ref": "#/$defs/StoragePolicy"
    },
    "gate_policy": {
      "$ref": "#/$defs/GateConfig"
    }
  },
  "required": [
    "credentials"
  ],
  "title": "ServiceConfig",
  "type": "object",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://deepagentlabs.io/agenticlens/enterprise/1-candidate/service-config.json"
}
```

---

## Data contract: schemas/enterprise/storage-policy.json

Source: [schemas/enterprise/storage-policy.json](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/enterprise/storage-policy.json)

```json
{
  "additionalProperties": false,
  "properties": {
    "max_age_days": {
      "default": 30,
      "maximum": 3650,
      "minimum": 1,
      "title": "Max Age Days",
      "type": "integer"
    },
    "max_traces": {
      "default": 1000,
      "maximum": 100000,
      "minimum": 1,
      "title": "Max Traces",
      "type": "integer"
    },
    "redact": {
      "const": true,
      "default": true,
      "title": "Redact",
      "type": "boolean"
    }
  },
  "title": "StoragePolicy",
  "type": "object",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://deepagentlabs.io/agenticlens/enterprise/1-candidate/storage-policy.json"
}
```
