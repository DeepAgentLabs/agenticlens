# Experiments and Statistical Comparison

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
