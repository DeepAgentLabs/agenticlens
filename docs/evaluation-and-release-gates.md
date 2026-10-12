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

Experiments (repeated trials across variants, pass@k, significance tests) are
covered in [Experiments and Statistical Comparison](experiments.md).

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

The framework supports deterministic checks, custom or model-based evaluators
with recorded versions, structured judge verdicts, versioned local datasets,
judge calibration and threshold tuning against human labels, evidence audits,
concurrent live targets, and gate alerts. Built-in provider clients, async
evaluator APIs, and automatic framework event adapters remain future roadmap
capabilities.
