# Optimization Intelligence

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

Tools that declare `idempotent: false` or `side_effects: true` are never
recommended for caching. An error type is called non-retryable only when no
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
[advisory routing](routing.md) shadow or canary modes rather than a direct
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

A decision whose `report_sha256` does not match the report is refused, so
decisions never attach to a regenerated report by accident. The ledger is a
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
  [ModelFit](modelfit.md), and for runtime selection use [routing](routing.md).
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
