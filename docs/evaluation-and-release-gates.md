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
covered in [Experiments and Statistical Comparison](experiments.md).

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
are covered in [Diagnosis and Failure Attribution](diagnosis.md). Built-in
provider clients, async evaluator APIs, and automatic framework event adapters
remain future roadmap capabilities.
