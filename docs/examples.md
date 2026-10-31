# Examples

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

See [RAG chunk utility](rag-chunk-utility.md) for supported signal types and thresholds.

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

See [Multi-agent reference workflows](multi-agent-reference-workflows.md).

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
