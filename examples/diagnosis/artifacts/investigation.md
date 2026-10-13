# Investigation: refund-support

- Run `incident-0042` (trace `trace-incident-0042`), outcome: failed, task_success=False
- 3 diagnosis(es), 3 unrecovered, 3 failed span(s)
- Taxonomy v1.0, engine v1.0

## Verdict

Most likely faulty step: 'issue_refund' in agent 'refunds' — timeout, 79% of attributed blame. Next candidate: 'write_reply' (21%). Attribution confidence: 71%.

## Root cause

**A span exceeded its time limit or failed with a timeout error: issue_refund** (timeout, environment layer, severity high, rule `failed_span@1.0`)

tool_call span 'issue_refund' failed with TimeoutError: payments API timed out after 5000 ms.

Supporting spans: `incident-0042-pay`

## Contributing factors

- **retry_exhausted**: 1 retry of 'issue_refund' did not succeed. [confidence 90%]
- **model_error**: final_response span 'write_reply' failed with MissingData: no refund confirmation to report. [confidence 95%]

## What happened

- +0 ms — Run of refund-support started.
- +0 ms — Handoff by router: delegation 'route_ticket'.
- +5553 ms — tool_call 'issue_refund' failed (TimeoutError: payments API timed out after 5000 ms). **(root cause)**
- +5557 ms — Retry #1: retry 'retry issue_refund' started.
- +10557 ms — retry 'retry issue_refund' failed (TimeoutError: payments API timed out after 5000 ms).
- +10941 ms — final_response 'write_reply' failed (MissingData: no refund confirmation to report).
- +10945 ms — Run completed (failed, task_success=False).

## Cost of the failure

Failed and retry spans used 1500 tokens, 10380 ms, and $0.000240.

## Anomalies against baseline

- `run` latency_ms: 10945.2 vs median 1757.25 (robust z +317.8, n=6)
- `final_response:write_reply` latency_ms: 380 vs median 533 (robust z -17.2, n=6)
- `tool_call:issue_refund` latency_ms: 5000 vs median 653 (robust z +488.7, n=6)
- Warning: Too few baseline samples to score: retry:retry issue_refund

## Next steps

1. Compare the span's latency with its timeout and with earlier runs; look for slow dependencies or oversized inputs.
2. Look at the original failure the retries targeted; repeating an identical request rarely fixes a non-transient error.
3. Check the provider error type, rate limits, and the prompt size sent to the model.

## Limitations

- Diagnoses come from deterministic rules over recorded spans; behavior the trace did not record cannot be diagnosed.
- Attribution shares are rule-weighted blame, not calibrated probabilities. Check accuracy on controlled failures with evaluate_attribution().
