# Evals 0.9.0 judge reliability compatibility

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
