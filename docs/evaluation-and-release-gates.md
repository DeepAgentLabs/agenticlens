# Evaluation and Release Gates

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

Built-in checks are deterministic. Custom evaluators and model-based judges use
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
`LLMJudgeEvaluator` identifies provider-supplied model judgments in reports
while leaving model selection, credentials, prompts, retries, and structured
output handling under application control. See `examples/custom_llm_judge.py`
for a complete, runnable registration example.

`BusinessRuleEvaluator` is a named wrapper around trusted application logic for
organization-specific pass/fail rules that do not need an LLM judge.

## Run an Evaluation

```bash
agenticlens evaluate suite.yaml samples.json \
  --save evaluation.json \
  --html evaluation.html
```

The JSON report is suitable for CI and further analysis. The standalone HTML
report is suitable for demonstrations, release reviews, and team sharing.

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

Live targets are intentionally powerful developer-facing integrations. Python
targets execute local code and HTTP targets can reach arbitrary URLs, so suite
files and target definitions should be treated as trusted inputs.

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

`max_turns` requires `trace.metadata.turn_count` to be recorded as a positive
integer. AgenticLens does not infer conversational turns from lower-level span
types when that metadata is absent.

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

The framework supports deterministic checks and synchronous custom or
model-based evaluators. Built-in provider clients, asynchronous and batched
evaluation, judge calibration, statistical confidence intervals, dataset
management, and automatic framework event adapters remain roadmap
capabilities.
