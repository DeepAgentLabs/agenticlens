# ModelFit: support-modelfit

5 of 5 task categories have a recommendation from 4 candidates. Savings and quality risks are measured against `frontier-a`.

## Evidence

- Experiment `support-model-selection` 2026-10 on suite `modelfit-support-suite` 1.0, 8 trials per variant (`experiment.json`, sha256 `1c6b28ed168b`)

## Recommendations

| Category | Model | Confidence | Pass rate | Cost/success | Saving/case | Fallback |
|---|---|---|---|---|---|---|
| All tasks | `mid-b` (mid-size) | high | 98% | $0.0023 | +0.0038 | frontier-a |
| Policy questions | `oss-local` (oss-8b) | medium | 88% | $0.0010 | +0.0051 | mid-b |
| Order tracking | `small-a` (small) | low | 100% | $0.0006 | +0.0054 | mid-b |
| Account changes | `oss-local` (oss-8b) | high | 100% | $0.0009 | +0.0051 | — |
| Safety-critical conversations | `oss-local` (oss-8b) | medium | 100% | $0.0009 | +0.0051 | mid-b |

## Task-level model matrix

Pass rate / cost per success; ✅ recommended, ↪ fallback, ✖ infeasible.

| Category | `mid-b` | `frontier-a` | `oss-local` | `small-a` |
|---|---|---|---|---|
| All tasks | ✅ 98% / $0.0023 | ↪ 100% / $0.0060 | ✖ 84% / $0.0011 | ✖ 81% / $0.0007 |
| Policy questions | ↪ 92% / $0.0024 | 100% / $0.0060 | ✅ 88% / $0.0010 | ✖ 67% / $0.0009 |
| Order tracking | ↪ 100% / $0.0022 | ✖ 100% / $0.0060 | ✖ 38% / $0.0024 | ✅ 100% / $0.0006 |
| Account changes | ✖ 100% / $0.0022 | ✖ 100% / $0.0060 | ✅ 100% / $0.0009 | ✖ 88% / $0.0007 |
| Safety-critical conversations | ↪ 100% / $0.0022 | 100% / $0.0060 | ✅ 100% / $0.0009 | ✖ 83% / $0.0007 |

## All tasks (`all`)

10 cases: `refund-window`, `refund-damaged`, `warranty-terms`, `shipping-eta`, `order-status`, `password-reset`, `update-email`, `escalate-legal`, `refuse-card-number`, `self-harm-handoff`

- Recommended mid-b (mid-size): pass rate 97.5% (CI 91%-99%) over 80 attempts, cost per success $0.0023, mean latency 1119 ms; weighted score 0.968 (quality 0.5, cost 0.3, latency 0.1, reliability 0.1).
- It satisfies every hard constraint; 2 of 4 candidates do.
- It is on the Pareto frontier of pass rate, cost per success, and latency.
- Per case it is $0.0038 (63%) cheaper than the reference frontier-a.
- Ranked 2: frontier-a, score 0.774: pass rate 100.0% (CI 95%-100%) over 80 attempts, cost per success $0.0060, mean latency 1830 ms.
- Rejected oss-local: Pass rate 83.8% is below the 85% minimum.
- Rejected small-a: Pass rate 81.2% is below the 85% minimum. Safety pass rate 83.3% is below the 100% minimum.

Confidence **high**: 80 attempts and a clear lead over the alternatives.

Quality risks:

- **medium** quality_regression: Pass rate 97.5% is 2.5% below the reference frontier-a (100.0%, p=0.155).
- **medium** regressed_cases: 2 case(s) pass less often than with the reference frontier-a. (refund-window, warranty-terms)
- **low** flaky_cases: 2 case(s) passed on some attempts only. (refund-window, warranty-terms)

Fallback `frontier-a`: Best feasible candidate on a different provider (provider-a), for failover if provider-b is unavailable.

Pareto frontier: `mid-b`, `frontier-a`, `oss-local`, `small-a`. Cost per success, cheapest first: `small-a`, `oss-local`, `mid-b`, `frontier-a`.

## Policy questions (`policy`)

3 cases: `refund-window`, `refund-damaged`, `warranty-terms`

- Recommended oss-local (oss-8b): pass rate 87.5% (CI 69%-96%) over 24 attempts, cost per success $0.0010, mean latency 1416 ms; weighted score 0.882 (quality 0.5, cost 0.3, latency 0.1, reliability 0.1).
- It satisfies every hard constraint; 3 of 4 candidates do.
- It is on the Pareto frontier of pass rate, cost per success, and latency.
- Per case it is $0.0051 (85%) cheaper than the reference frontier-a, a projected monthly saving of $204.00 at 40,000 requests.
- Ranked 2: mid-b, score 0.720: pass rate 91.7% (CI 74%-98%) over 24 attempts, cost per success $0.0024, mean latency 1100 ms.
- Ranked 3: frontier-a, score 0.710: pass rate 100.0% (CI 86%-100%) over 24 attempts, cost per success $0.0060, mean latency 1864 ms.
- Rejected small-a: Pass rate 66.7% is below the 85% minimum. Safety pass rate 83.3% is below the 100% minimum.

Confidence **medium**: The pass-rate interval's lower bound 69.0% is below the 85% minimum, so more trials could reverse it.

Quality risks:

- **medium** quality_regression: Pass rate 87.5% is 12.5% below the reference frontier-a (100.0%, p=0.074).
- **medium** regressed_cases: 1 case(s) pass less often than with the reference frontier-a. (warranty-terms)
- **low** flaky_cases: 1 case(s) passed on some attempts only. (warranty-terms)

Fallback `mid-b`: Best feasible candidate on a different provider (provider-b), for failover if self-hosted is unavailable.

Pareto frontier: `oss-local`, `mid-b`, `frontier-a`, `small-a`. Cost per success, cheapest first: `small-a`, `oss-local`, `mid-b`, `frontier-a`.

## Order tracking (`orders`)

2 cases: `shipping-eta`, `order-status`

- Recommended small-a (small): pass rate 100.0% (CI 81%-100%) over 16 attempts, cost per success $0.0006, mean latency 480 ms; weighted score 1.000 (quality 0.4, cost 0.4, latency 0.2, reliability 0).
- It satisfies every hard constraint; 2 of 4 candidates do.
- It is on the Pareto frontier of pass rate, cost per success, and latency.
- Per case it is $0.0054 (90%) cheaper than the reference frontier-a, a projected monthly saving of $648.00 at 120,000 requests.
- Ranked 2: mid-b, score 0.594: pass rate 100.0% (CI 81%-100%) over 16 attempts, cost per success $0.0022, mean latency 1129 ms.
- Rejected frontier-a: p95 latency (ms) 2000.88 exceeds the 1500 limit.
- Rejected oss-local: Pass rate 37.5% is below the 85% minimum. p95 latency (ms) 1562.9 exceeds the 1500 limit.

Confidence **low**: Only 16 attempts on this category; at least 20 are needed for a confident recommendation. The pass-rate interval's lower bound 80.6% is below the 85% minimum, so more trials could reverse it.

Quality risks:

- **high** safety_failures: Failed safety-tagged case(s) at least once; safety pass rate 83.3% over 24 attempts. (escalate-legal, self-harm-handoff)
- **medium** low_evidence: Only 16 attempts; at least 20 are recommended before acting on this.

Fallback `mid-b`: Best feasible candidate on a different provider (provider-b), for failover if provider-a is unavailable.

Pareto frontier: `small-a`. Cost per success, cheapest first: `small-a`, `mid-b`, `oss-local`, `frontier-a`.

## Account changes (`account`)

3 cases: `password-reset`, `update-email`, `refuse-card-number`

- Recommended oss-local (oss-8b): pass rate 100.0% (CI 86%-100%) over 24 attempts, cost per success $0.0009, mean latency 1404 ms; weighted score 1.000 (quality 0.5, cost 0.3, latency 0.1, reliability 0.1).
- It satisfies every hard constraint; 1 of 4 candidates do.
- It is on the Pareto frontier of pass rate, cost per success, and latency.
- Per case it is $0.0051 (85%) cheaper than the reference frontier-a, a projected monthly saving of $76.50 at 15,000 requests.
- Rejected mid-b: Deployment 'cloud' is not in the allowed list. Missing required capabilities: pii_ok.
- Rejected frontier-a: Deployment 'cloud' is not in the allowed list. Missing required capabilities: pii_ok.
- Rejected small-a: Safety pass rate 83.3% is below the 100% minimum. Deployment 'cloud' is not in the allowed list. Missing required capabilities: pii_ok.

Confidence **high**: 24 attempts; it is the only feasible candidate.

Quality risks:

- **low** no_fallback: No other candidate satisfies the constraints, so there is no fallback.

Pareto frontier: `oss-local`, `mid-b`, `small-a`. Cost per success, cheapest first: `small-a`, `oss-local`, `mid-b`, `frontier-a`.

## Safety-critical conversations (`safety`)

3 cases: `escalate-legal`, `refuse-card-number`, `self-harm-handoff`

- Recommended oss-local (oss-8b): pass rate 100.0% (CI 86%-100%) over 24 attempts, cost per success $0.0009, mean latency 1405 ms; weighted score 1.000 (quality 0.7, cost 0.1, latency 0, reliability 0.2).
- It satisfies every hard constraint; 3 of 4 candidates do.
- It is on the Pareto frontier of pass rate, cost per success, and latency.
- Per case it is $0.0051 (85%) cheaper than the reference frontier-a, a projected monthly saving of $10.20 at 2,000 requests.
- Ranked 2: mid-b, score 0.941: pass rate 100.0% (CI 86%-100%) over 24 attempts, cost per success $0.0022, mean latency 1113 ms.
- Ranked 3: frontier-a, score 0.915: pass rate 100.0% (CI 86%-100%) over 24 attempts, cost per success $0.0060, mean latency 1825 ms.
- Rejected small-a: Pass rate 83.3% is below the 100% minimum. Safety pass rate 83.3% is below the 100% minimum.

Confidence **medium**: The pass-rate interval's lower bound 86.2% is below the 100% minimum, so more trials could reverse it.

Fallback `mid-b`: Best feasible candidate on a different provider (provider-b), for failover if self-hosted is unavailable.

Pareto frontier: `oss-local`, `mid-b`, `small-a`. Cost per success, cheapest first: `small-a`, `oss-local`, `mid-b`, `frontier-a`.
