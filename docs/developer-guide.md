# AgenticLens developer guide

Use this simple guide to choose a capability, run a local example, and connect it to your application. The [AI Reference (robust)](https://deepagentlabs.io/agenticlens/docs/llms-full.md) includes the detailed topic guides, declared Python/CLI interfaces and bundled JSON schemas. Package versions and draft/candidate artifact versions are independent.

[Capability index](#capability-index) · [Quickstart](#quickstart) · [Configuration](#settings) · [Troubleshooting](#troubleshooting) · [Reference](#reference)

## Capability index

Every row links to a short workflow below. Each workflow links to its detailed reference.

| Capability | What you can do |
| --- | --- |
| [Workflow profiling](#workflow-profiling) | Profile steps, extract provider usage, and analyze cost and token consumption. |
| [Structured tracing and privacy](#tracing) | Record hierarchical runs, spans, agents, errors, tokens and redacted I/O. |
| [Run comparison](#run-comparison) | Compare repeated baseline/candidate runs and detect descriptive regressions. |
| [Diagnosis and attribution](#diagnosis) | Find failure categories, faulty steps and agents, timelines, anomalies and investigation narratives. |
| [Analysis guardrails and attribution accuracy](#analysis-guardrails) | Bound analysis work and measure attribution on controlled failures. |
| [Evaluation and live targets](#evaluation) | Score recorded outputs or trusted Python/HTTP targets using Evals and Lens evaluators. |
| [Advanced evaluation and judge reliability](#advanced-evaluation) | Use structured verdicts, trace-aware checks, score disagreement, judge cost and threshold calibration. |
| [Release gates and evidence audits](#release-gates) | Check quality thresholds, evaluator provenance, cost coverage and optional gate alerts. |
| [Datasets and suite management](#suites) | Import, convert, edit, mask, deduplicate, vary, split, review, approve and verify cases. |
| [Experiments and statistics](#experiments) | Run repeated model/prompt/retrieval/memory/retry variants with uncertainty and factor summaries. |
| [ModelFit](#modelfit) | Rank models per task with hard constraints, weighted scoring, Pareto analysis, fallbacks and model matrices. |
| [Runtime routing](#routing) | Select eligible models; use SDK callbacks for failover, shadow or canary execution and outcome journals. |
| [Optimization and adoption outcomes](#optimization) | Find prompt, retrieval, memory, tool, retry, handoff and model trade-offs; track decisions and realized savings. |
| [RAG chunk utility](#rag) | Identify low-utility chunks using citations, reranker/similarity scores or lexical fallback. |
| [Dashboards, OTLP and history](#otlp-history) | Render HTML reports, import/export OTLP and receive or retain traces locally. |
| [Exports and AIOS contracts](#exports-aios) | Export JSON/CSV/Markdown/Jira, validate draft artifacts and resolve provenance from held bytes. |
| [Execution evidence verification and replay](#evidence) | Authenticate explicitly scoped snapshots and replay verified execution records offline. |
| [Enterprise artifact operations](#enterprise) | Isolate project artifacts with credentials/roles, storage policy, registries, gate receipts, retention and audit. |
| [Provider and multi-agent integrations](#integrations) | Extract OpenAI/Anthropic usage and instrument framework-neutral or LangGraph multi-agent workflows. |
| [Sidecar, Chaos, Tower and MCP interoperability](#ecosystem) | Consume correlated native evidence while preserving producer identity, authority and health semantics. |
| [Configuration and limitations](#settings) | Configure pricing, thresholds, capture and deployment; preserve unknowns and draft/candidate boundaries. |

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

[Download lens_quickstart.py](guide/examples/lens_quickstart.py)

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

Analysis combines token/cost metrics, provider/model pricing and rule-based recommendations for repeated system prompts, excessive retrieval, low-utility chunks, long history, duplicate tools, handoff bloat, injected faults and model swaps. Latency, tokens per second and explicitly measured time to first token support performance analysis. Unknown prices remain unavailable. See [profiling API](api-reference.md#profiling-api), [features](features.md) and [provider integrations](integrations.md).

<span id="tracing"></span>

### Structured tracing and privacy

Use the quickstart's `trace()` and `recording.span()` for nested model, planning, retrieval, tool, memory, validation, delegation and retry spans. Record tokens, costs, status, agent names and attributes at the actual execution boundary. Input/output capture is opt-in through `record_io()`; default redaction covers common secrets, bearer tokens and emails. Supply `redactor=` for application-specific requirements.

```bash
agenticlens inspect run.json --save trace-report.md
agenticlens trace show run.json
```

Use `trace show run.json --span SPAN_ID` for a recorded span ID. See [tracing and comparison](trace-and-comparison.md) and [tracing API](api-reference.md#tracing-api).

### Run comparison

Put baseline and candidate structured runs in separate directories:

```bash
agenticlens compare results/baseline results/candidate \
  --format md --save comparison.md --min-samples 5 --fail-on-regression
```

Compare success, mean/median/P95 latency, variability, tokens, cost per success and relative regressions. This comparison is descriptive; use repeated experiments for statistical comparisons. See [trace comparison](trace-and-comparison.md).

<span id="diagnosis"></span>

### Diagnosis and attribution

```bash
agenticlens diagnose run.json --save diagnosis.json --markdown investigation.md
agenticlens explain diagnosis.json --save explanation.md
agenticlens trace timeline run.json --save timeline.json
```

Diagnosis cites recorded spans for failure categories, origin versus propagated failures, recovery, faulty-step/agent attribution and incident timelines. Add `--baseline healthy-runs/` for anomaly detection. Budgets, tool/handoff loops, empty retrieval and injected faults have explicit rules. See [diagnosis and failure attribution](diagnosis.md).

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

See [guardrails](diagnosis.md#guardrails-for-automated-analysis) and [attribution accuracy](diagnosis.md#attribution-accuracy-on-controlled-failures). Controlled fixtures do not establish accuracy on arbitrary production traffic.

<span id="evaluation"></span>

### Evaluation and live targets

Prepare a YAML/JSON suite plus recorded samples with matching case IDs:

```bash
agenticlens evaluate suite.yaml samples.json --save evaluation.json --html evaluation.html
```

Evals owns scoring and release-gate computation. Lens adds evidence adaptation, trace-aware evaluators and reporting. `evaluate-live` supports trusted Python callables and HTTP endpoints; the host supplies provider clients and credentials. See [evaluation and release gates](evaluation-and-release-gates.md) for suite contracts and live-target setup.

<span id="advanced-evaluation"></span>

### Advanced evaluation and judge reliability

Use `structured_judge()` with your own judge callback to record verdicts, confidence, unsupported claims, missed evidence, prompt identity, latency and usage. Self-judging is skipped by default. Trace-aware checks cover tool trajectories, agent goals, handoffs, loops, groundedness, relevance, completeness, citations and safety.

```bash
agenticlens evaluate suite.yaml samples.json --save evaluation.json \
  --score-analysis scores.json --html evaluation.html
agenticlens calibrate evaluation.json labels.json --evaluator answer_quality --save calibration.json
```

Score analysis separates deterministic/model-based scores, disagreement and judge cost. Calibration compares human references; the Python API and `calibrate --tune-threshold tuning.json` also tune thresholds. Lexical checks have semantic limits. See [structured judges, score analysis and trace-aware evaluators](evaluation-and-release-gates.md#structured-judge-verdicts) and the [judge reliability contract](evals-0.9-judge-reliability.md).

<span id="release-gates"></span>

### Release gates and evidence audits

```bash
agenticlens evaluate suite.yaml samples.json --save evaluation.json \
  --audit audit.json --strict-evidence
agenticlens gate evaluation.json --min-pass-rate 0.95
```

Audits inspect evaluator versions, trace evidence and cost coverage; strict blocking issues exit 3. Gates check configured quality, latency and cost thresholds. Optional webhook notifications support generic, Slack and Teams payloads when configured; they require an operator-supplied destination. See [gate thresholds and alerts](evaluation-and-release-gates.md#apply-a-release-gate) and [native Evals report boundaries](evals-report-contract.md).

<span id="suites"></span>

### Datasets and suite management

Datasets retain saved samples and labels; `dataset summary`, `dataset split` and `dataset export-samples` inspect and partition them. Suites contain test definitions and review metadata:

```bash
agenticlens suite import cases.csv --name support-regression --version 1.0.0 --save suite.yaml
agenticlens suite summary suite.yaml
```

Continue with trace/feedback conversion, case editing/tagging, PII masking, duplicate checks, synthetic variations, split assignment, filtering and review. Approve reviewed suites into an immutable store, then verify/export the approved version for CI. Editing commands modify their input unless `--save` names another file. See the [full suite lifecycle and commands](suite-management.md) and [dataset API](api-reference.md#dataset-api).

<span id="experiments"></span>

### Experiments and statistics

Run the checkout's offline recorded-output example:

```bash
agenticlens experiment run examples/experiments/support-experiment.yaml \
  examples/experiments/support-suite.yaml --save experiment.json \
  --html experiment.html --csv variants.csv --cases-csv cases.csv
```

Manifests define at least three variants, repeated trials and factors such as model, prompt, retrieval, memory or retry policy. Reports include pass@k/pass^k, confidence intervals, comparisons, consistency and factor summaries. `experiment report` renders saved results without rerunning targets. See [experiments and statistics](experiments.md).

### ModelFit

Use saved experiment evidence to select models by task category:

```bash
agenticlens modelfit taxonomy experiment.json --config modelfit.yaml
agenticlens modelfit recommend experiment.json --config modelfit.yaml \
  --save modelfit.json --markdown modelfit.md --csv matrix.csv
agenticlens modelfit matrix modelfit.json
```

Your config defines categories, hard quality/cost/latency/safety/provider/deployment constraints and scoring weights. Missing evidence fails constraints closed. Reports include Pareto status, cost per success, confidence, fallbacks, projected savings and separate quality risks. ModelFit does not invoke models. See [ModelFit configuration and evidence](modelfit.md).

<span id="routing"></span>

### Runtime routing

Given the saved ModelFit report and a category present in it:

```bash
agenticlens routing decide modelfit.json --category orders --request-id opaque-123 \
  --save decision.json
```

The CLI explains selection without invoking providers in every mode. Python `Router.run()` accepts host-owned callbacks for enforce, shadow and canary execution, bounded failover and local audit journals. `routing summary` consumes saved SDK results, not decision files. Hosts own payloads, credentials, deadlines and quality checks. See [routing modes, constraints and outcomes](routing.md).

<span id="optimization"></span>

### Optimization and adoption outcomes

```bash
agenticlens optimize analyze traces/before --save optimization.json --markdown optimization.md
```

Review opportunities for caching/compression, retrieval pruning/reranking, memory summarization, tools, retries, redundant steps, handoffs and model quality/cost trade-offs. Each keeps evidence, benefit, confidence and risk separate; missing costs remain unknown.

Use `optimize decide` to record acceptance and adoption against the exact report hash, `optimize status` to inspect decisions, and `optimize outcome` to compare before/after traces with the original projection. `--fail-on-regression` on outcome exits 9 if quality regressed. See [optimization rules, decision transitions and outcomes](optimization.md).

<span id="rag"></span>

### RAG chunk utility

Record `retrieved_chunks` on a profiled retriever step. Citation flags take priority over reranker scores, embedding similarity and generic utility scores; word overlap is the fallback. `agenticlens analyze workflow.json` flags low-utility chunks when configured thresholds are met. This workflow signal differs from the structured-trace retrieval optimization rules. See [supported chunk signals and configuration](rag-chunk-utility.md).

<span id="otlp-history"></span>

### Dashboards, OTLP and history

Install the optional HTTP dependencies for the local receiver:

```bash
python -m pip install 'agenticlens[api]'
agenticlens import-otlp otlp.json --save imported-run.json
agenticlens serve-otlp --host 127.0.0.1 --port 4318 --db traces.db
```

Run `agenticlens history --db traces.db` in another terminal. The receiver has no authentication; keep it local or on a trusted network. Use `dashboard` for saved HTML and `trace(..., otlp_endpoint=...)` or OTLP environment variables for export to a collector. See [CLI commands](cli-reference.md), [OTLP mapping](aios-validation-and-otel.md) and [receiver limits](limitations.md).

<span id="exports-aios"></span>

### Exports and AIOS contracts

Workflow exporters support JSON, CSV, Markdown and Jira payloads. Comparison, experiment, evaluation, ModelFit and optimization reports have their own output contracts. Native structured runs are not automatically AIOS artifacts.

```bash
agenticlens conformance --list-versions
agenticlens validate aios-artifact.json --save validation.json
agenticlens conformance aios-artifact.json --save conformance.json
```

Validation routes by declared marker: Run/Workflow `0.4-draft`, provenance `0.6-draft`, and supported operational companions `0.8-draft`. Explicit `--version` asserts a version. Schema validation alone does not establish semantic alignment. Python APIs export findings, provenance and structured-judge verification signals; provenance resolution uses caller-held bytes. See [export formats](export-formats.md), [current validation and companion APIs](coordinated-v1-readiness.md), and [operational artifacts](aios-0.8-operational-artifacts.md).

<span id="evidence"></span>

### Execution evidence verification and replay

Prepare explicit execution observations and an operator-owned trusted key file:

```bash
agenticlens evidence export run.json observations.json bundle.json \
  --key-id capture-key --key-file trusted-keys.json --complete
agenticlens evidence replay bundle.json --run-id EXPECTED_RUN_ID --key-file trusted-keys.json
```

The run ID must match your trusted caller context. `evidence verify` checks standalone records/manifests with an expected stream ID. Verification distinguishes failed, unknown and incomplete evidence; replay refuses untrusted or incomplete bundles and preserves capture order. It does not execute tools or providers. Declare completeness only for an actually complete capture. See [trust setup, coverage and evidence schemas](evidence-verification.md).

<span id="enterprise"></span>

### Enterprise artifact operations

The optional single-node artifact service adds organization/project isolation, hashed bearer credentials with reader/writer/admin roles, SQLite storage, redaction/retention, immutable model/prompt registry metadata, policy-bound gate receipts, audit and compliance metadata. Install `[api]`, prepare the documented credential/storage/gate configuration, then run:

```bash
LENS_CONFIG=/secure/config.json LENS_DATABASE=/data/lens.db \
  uvicorn agenticlens.enterprise.server:create_app --factory \
  --host 127.0.0.1 --port 8000 --workers 1 --no-access-log
```

This is a separate service from the developer OTLP receiver. Use its [configuration, HTTP routes, roles, deployment, backup and rollback guide](production-readiness.md) before operating it. Candidate markers and remaining acceptance work are described in [coordinated readiness](coordinated-v1-readiness.md).

<span id="integrations"></span>

### Provider and multi-agent integrations

Use explicit instrumentation around provider/framework execution. OpenAI/Anthropic usage extraction is supported; other providers supply usage manually. Agent names and delegation spans support per-agent analysis. The optional `agenticlens[langgraph]` or `[multi-agent]` extra supports the checked-in LangGraph supervisor reference workflow. See [providers and frameworks](integrations.md) and [offline supervisor/handoff workflows](multi-agent-reference-workflows.md).

<span id="ecosystem"></span>

### Sidecar, Chaos, Tower and MCP interoperability

`attach_decisions(run, records)` attaches Sidecar decisions only when run, trace and span IDs match, preserving supervision events in diagnosis timelines. Chaos evidence supports analysis of injected faults; Lens does not inject them. Tower consumes attributed native evidence, and the separate MCP package exposes Lens workflows. Producer outcomes, execution proof, authority and deployment health remain distinct.

See [Sidecar correlation](sidecar-integration.md), [Sidecar authority/privacy](sidecar-0.9.md), [ChaosHub](chaos-0.11-chaoshub.md), [Tower contract readiness](tower-0.10-compatibility.md), [MCP readiness](mcp-0.7-readiness.md) and the [historical compatibility matrix](lens-0.13-compatibility.md). Release-specific notes describe their stated versions, not a guarantee for every current installation.

<span id="settings"></span>

## Configuration and limitations

For workflow analysis, load `AgenticLensConfig` from an explicit YAML path or set `AGENTICLENS_CONFIG`. Use `pricing_overrides` (USD per 1,000 tokens), `live_pricing` and `recommender` settings. Set `AGENTICLENS_DISABLE_LIVE_PRICING=1` for offline pricing.

Structured tracing takes `otlp_endpoint`, `otlp_headers`, `otlp_timeout_seconds` and `redactor` arguments; OTLP environment variables supply defaults. Explicit arguments take precedence. ModelFit, routing, optimization and enterprise services use their own documented configurations. See [complete configuration](configuration.md).

Instrument actual boundaries and usage; automatic arbitrary-framework interception and streaming token capture are not provided. Recommendations are heuristic, savings are projections, and comparison windows do not prove causality. Missing prices, traces or evaluator evidence must not be treated as zeros or successful checks. See [limitations](limitations.md) and [compatibility policy](compatibility-policy.md).

## Troubleshooting

Use the environment where the package was installed. Confirm files exist, case IDs match, and the input is the right artifact type. Start with `agenticlens COMMAND --help` for exact flags. Keep original evidence when diagnosing an issue. See [troubleshooting](troubleshooting.md).

## Reference

- [API Reference (Detailed)](api-reference.md) and [CLI reference](cli-reference.md).
- [AI Reference (robust)](https://deepagentlabs.io/agenticlens/docs/llms-full.md) and [capability/source index](ai-reference-index.md).
- [Source manifest and checksums](ai-docs-manifest.json).
