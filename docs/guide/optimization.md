# Review optimization evidence

Reference examples below show API composition and configuration fragments. Start with the complete quickstart before adapting these to your application.

## What each rule reads

Rules only use what the trace records. A span without the signal a rule

needs is skipped, not estimated.

| Rule (`rule_id`) | Opportunity `kind` | Reads | Fires when |
| --- | --- | --- | --- |
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

## Tracking decisions

`RecommendationLedger` is an append-only JSONL file. Each

`RecommendationDecision` records the opportunity, the SHA-256 of the report

that proposed it, the status, who decided, when, why, and an optional change

reference (PR, commit, config version). Transitions are enforced:

| To | Allowed from |
| --- | --- |
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
| --- | --- |
| `insufficient_evidence` | fewer than `--min-runs` (default 3) runs on either side, or the rule stopped firing but the saving could not be measured |
| `quality_regressed` | success rate fell by more than `tradeoff_max_success_rate_drop`; this takes precedence over savings |
| `realized` | at least 80% of the projected saving appeared and the rule no longer fires |
| `partially_realized` | some saving appeared, or the rule still fires |
| `not_realized` | no saving appeared |

`agenticlens optimize outcome --fail-on-regression` exits **9** on

`quality_regressed`, so CI can block a regression introduced by an adopted

optimization.

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
