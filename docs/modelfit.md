# ModelFit: Task-Level Model Recommendations

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
a safety minimum when no case is safety-tagged, or a provider allow-list for
a candidate with no known provider are all violations with a message that
says the limit cannot be verified.

The safety pass rate always covers every safety-tagged case in the suite,
not just the category's own cases: a model that mishandles a safety case is
a risk wherever it is routed.

## Candidates

Each experiment variant is one candidate. Its model name is the variant's
`model` factor (`model_factor` changes which factor), and its provider,
deployment, and capabilities come from, in order of precedence:

1. the config's `candidates` catalog,
2. the experiment manifest's variant `metadata` (`--manifest`, or
   `variant_metadata=` in Python), with comma-separated `capabilities`,
3. variant factors named `provider` or `deployment`.

Variants that change something other than the model (a prompt or retrieval
change) are still compared, as configurations; ModelFit warns when two
candidates share a model. Use `exclude_variant_ids` to leave variants out.
Several experiment reports can be combined; ModelFit warns when they use
different suites, because the comparison is then not like-for-like.

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
incomplete.

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
