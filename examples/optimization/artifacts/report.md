# Optimization opportunities

8 runs, 127,600 tokens, total cost $0.203076. Benefits are projections; risks are listed separately and never netted against them.

| # | Opportunity | Area | Projected benefit per run | Confidence | Risks | Status |
|---|---|---|---|---|---|---|
| 1 | Switch from 'large' to 'small' | model | 0 tokens, $0.023075, 0 ms per run; $692.250000 per month | medium | quality_regression (medium), sample_size (medium) | proposed |
| 2 | Bound memory with summarization and retention | memory | 4,700 tokens, $0.007480, 0 ms per run; $224.402163 per month | high | fact_loss (medium) | proposed |
| 3 | Cache a repeated prompt prefix | prompt | 2,025 tokens, $0.005400, 0 ms per run; $162.000000 per month | high | cache_invalidation (low) | accepted |
| 4 | Compress the prompt of 'answer' | prompt | 1,560 tokens, $0.004290, 0 ms per run; $128.700000 per month | medium | instruction_loss (medium) | proposed |
| 5 | Lower top-k for 'kb_search' | retrieval | 450 tokens, $0.001238, 0 ms per run; $37.125000 per month | high | recall_loss (low) | proposed |
| 6 | Skip the handoff triage -> billing | workflow | 420 tokens, $0.001155, 140 ms per run; $34.650000 per month | high | handoff_semantics (medium) | rejected |
| 7 | Stop retrying 'auth_error' | tool | 360 tokens, $0.000990, 500 ms per run; $29.700000 per month | high | transient_error (low) | proposed |
| 8 | Remove the repeated 'policy_check' step | workflow | 310 tokens, $0.000853, 60 ms per run; $25.575000 per month | high | intentional_repeat (low) | proposed |
| 9 | Cache results of tool 'lookup_order' | tool | 300 tokens, $0.000825, 400 ms per run; $24.750000 per month | high | stale_result (low) | adopted |
| 10 | Rerank results of 'kb_search' | retrieval | 112 tokens, $0.000309, 0 ms per run; $9.281250 per month | medium | reranker_overhead (low), reranker_quality (medium) | proposed |

## Switch from 'large' to 'small'

- ID: `quality_cost_tradeoff-7ce924e57bba` (rule `quality_cost_tradeoff` v1)
- Finding: 'small' cost 62% less per run with success 75% vs 100%.
- Action: Trial 'small' behind advisory routing or a canary before replacing the baseline.
- Projected benefit: 0 tokens, $0.023075, 0 ms per run; $692.250000 per month
- Basis: Difference between the variants' measured mean per-run cost. Averaged over every observed run, including unaffected ones.
- Confidence: medium — Observed in 8 of 8 runs (100%). Fewer than 30 runs per variant.
- Evidence: 8 of 8 runs, 0 spans
- Risk (medium, quality_regression): Success rate 75% vs 100% (p=0.285).
- Risk (medium, sample_size): 4 and 4 runs; small samples cannot rule out a quality drop larger than the allowed threshold.

## Bound memory with summarization and retention

- ID: `memory_summarization-4774cb4162b2` (rule `memory` v1)
- Finding: Memory reads took over 40% of tokens in 8 runs; 8 grew on every read.
- Action: Summarize older memory into a digest of about 2000 tokens and add a retention window, since memory grew on every read.
- Projected benefit: 4,700 tokens, $0.007480, 0 ms per run; $224.402163 per month
- Basis: Memory tokens above the configured budget, priced at each run's blended cost per token. Averaged over every observed run, including unaffected ones.
- Confidence: high — Observed in 8 of 8 runs (100%).
- Evidence: 8 of 8 runs, 24 spans
- Risk (medium, fact_loss): Summaries can drop facts that later turns rely on.

## Cache a repeated prompt prefix

- ID: `prompt_caching-103f82ac55d9` (rule `prompt_caching` v1)
- Finding: A 1200-token prompt prefix was sent 16 times without a provider cache hit.
- Action: Move the shared prefix to the start of the prompt and enable provider prompt caching (or a local prefix cache).
- Projected benefit: 2,025 tokens, $0.005400, 0 ms per run; $162.000000 per month
- Basis: Billable-equivalent prefix tokens on every repeat after the first, discounted by the configured cached-read price ratio. Cost is the span cost pro-rated by token share, an upper bound when output tokens are priced above input tokens. Averaged over every observed run, including unaffected ones.
- Confidence: high — Observed in 8 of 8 runs (100%).
- Evidence: 8 of 8 runs, 15 spans
- Risk (low, cache_invalidation): Dynamic content inside the prefix, or calls outside the provider cache lifetime, will miss the cache.

## Compress the prompt of 'answer'

- ID: `prompt_compression-ee01f0be5920` (rule `prompt_compression` v1)
- Finding: 'answer' sent at least 4000 input tokens per call for 8 calls with output 20x smaller.
- Action: Trim boilerplate, deduplicate context, or summarize long inputs; evaluate the compressed prompt on the suite before adopting.
- Projected benefit: 1,560 tokens, $0.004290, 0 ms per run; $128.700000 per month
- Basis: The configured 30% target reduction of measured input tokens; the reduction itself is an assumption until measured. Averaged over every observed run, including unaffected ones.
- Confidence: medium — Observed in 8 of 8 runs (100%). The reduction is a configured target, not measured.
- Evidence: 8 of 8 runs, 8 spans
- Risk (medium, instruction_loss): Compression can drop instructions or facts the model needs; require a passing evaluation before rollout.

## Lower top-k for 'kb_search'

- ID: `retrieval_pruning-0995adc226bf` (rule `retrieval` v1)
- Finding: 'kb_search' retrieved up to 8 chunks, but no answer across 8 retrievals used a chunk ranked below 5.
- Action: Reduce top-k from 8 to 5.
- Projected benefit: 450 tokens, $0.001238, 0 ms per run; $37.125000 per month
- Basis: Tokens of chunks ranked below the deepest used chunk, priced at the next model call's cost per token. Averaged over every observed run, including unaffected ones.
- Confidence: high — Observed in 8 of 8 runs (100%).
- Evidence: 8 of 8 runs, 8 spans
- Risk (low, recall_loss): 8 retrievals were observed; unseen queries may need deeper chunks.

## Skip the handoff triage -> billing

- ID: `unnecessary_handoff-3fb69147c860` (rule `unnecessary_handoff` v1)
- Finding: 8 handoffs from triage to billing added no work.
- Action: Let triage continue directly, or merge billing into it.
- Projected benefit: 420 tokens, $0.001155, 140 ms per run; $34.650000 per month
- Basis: Measured tokens, cost and latency of each handoff and its subtree. Averaged over every observed run, including unaffected ones.
- Confidence: high — Observed in 8 of 8 runs (100%).
- Evidence: 8 of 8 runs, 16 spans
- Risk (medium, handoff_semantics): A handoff can carry authorization, audit, or ownership semantics that tokens do not show.

## Stop retrying 'auth_error'

- ID: `retry_policy-1122fb6d6ba6` (rule `retry_policy` v1)
- Finding: 16 retries after 'auth_error' were observed and none recovered.
- Action: Treat 'auth_error' as non-retryable: fail fast or route to a fallback.
- Projected benefit: 360 tokens, $0.000990, 500 ms per run; $29.700000 per month
- Basis: Measured tokens, cost and latency of the unrecovered retry spans. Averaged over every observed run, including unaffected ones.
- Confidence: high — Observed in 8 of 8 runs (100%).
- Evidence: 8 of 8 runs, 16 spans
- Risk (low, transient_error): 16 retries were observed; the error may be transient on traffic not in these traces.

## Remove the repeated 'policy_check' step

- ID: `redundant_step-f0cff7cb49f8` (rule `redundant_step` v1)
- Finding: 'policy_check' (validation) re-ran with identical input and output in 8 runs.
- Action: Reuse the first 'policy_check' result instead of re-executing it.
- Projected benefit: 310 tokens, $0.000853, 60 ms per run; $25.575000 per month
- Basis: Measured tokens, cost and latency of every identical re-execution. Averaged over every observed run, including unaffected ones.
- Confidence: high — Observed in 8 of 8 runs (100%).
- Evidence: 8 of 8 runs, 16 spans
- Risk (low, intentional_repeat): Repeats can be deliberate (self-consistency sampling, polling); confirm before removing.

## Cache results of tool 'lookup_order'

- ID: `tool_result_caching-412a72bac9f5` (rule `tool_caching` v1)
- Finding: 'lookup_order' was called repeatedly with identical arguments in 8 runs.
- Action: Memoize 'lookup_order' by arguments for the duration of a run.
- Projected benefit: 300 tokens, $0.000825, 400 ms per run; $24.750000 per month
- Basis: Measured tokens, cost and latency of every repeat after the first. Averaged over every observed run, including unaffected ones.
- Confidence: high — Observed in 8 of 8 runs (100%).
- Evidence: 8 of 8 runs, 16 spans
- Risk (low, stale_result): The tool is declared idempotent; cached results can still go stale if they outlive the data.

## Rerank results of 'kb_search'

- ID: `retrieval_reranking-f8904867cad8` (rule `retrieval` v1)
- Finding: In 2 retrievals the answer used a chunk ranked 4 or lower while higher-ranked chunks went unused.
- Action: Add a reranker, then lower top-k to the reranked depth that answers use.
- Projected benefit: 112 tokens, $0.000309, 0 ms per run; $9.281250 per month
- Basis: Upper bound: tokens of unused chunks ranked above the deepest used chunk, which a perfect reranker would drop. Reranker cost and latency excluded. Averaged over every observed run, including unaffected ones.
- Confidence: medium — Observed in 2 of 8 runs (25%). Benefit assumes a perfect reranker.
- Evidence: 2 of 8 runs, 2 spans
- Risk (low, reranker_overhead): A reranker adds its own latency and cost per query.
- Risk (medium, reranker_quality): A reranker can demote chunks answers need; evaluate it.

## Quality-cost trade-offs

Baseline: `large`

| Variant | Runs | Success | Interval | Mean cost | Cost/success | Δ success | Δ cost | Pareto |
|---|---|---|---|---|---|---|---|---|
| large | 4 | 100% | 51%–100% | $0.036922 | $0.036922 | — | — | yes |
| small | 4 | 75% | 30%–95% | $0.013847 | $0.018463 | -25% | $-0.023075 | yes |
