# Advisory runtime routing (0.10.0 / roadmap v0.8)

Route task categories using recorded ModelFit experiment evidence. The Python
SDK supports selection and bounded execution. The CLI and MCP only explain
selection; they never execute models, even if the policy says `enforce`.

## Offline quickstart

```bash
uv run python examples/routing_demo.py
agenticlens routing decide examples/modelfit/artifacts/modelfit.json \
  --category orders --request-id demo-1 \
  --policy examples/routing/artifacts/policy.json --save decision.json
agenticlens routing summary examples/routing/artifacts/shadow.json
```

The synthetic example explicitly allows low-confidence evidence, demonstrates
provider failover and measured shadow operation, and writes results and a JSONL
journal. Its costs are synthetic and its local callback latency is measured;
these are not claims about real providers. The default requires **medium**
confidence and escalates this deliberately small example corpus.

## Python SDK

```python
from pathlib import Path
from agenticlens.modelfit import load_modelfit_report
from agenticlens.routing import (
    RouteOutcome, RouteRequest, Router, RoutingAuditLog, RoutingPolicy,
)

report = load_modelfit_report(Path("modelfit.json"))
router = Router(report, RoutingPolicy(mode="enforce"),
                audit=RoutingAuditLog("routing.jsonl"))

def invoke(target, request):
    # Resolve the original payload by its opaque request_id in your application.
    # Call your provider with your timeout and evaluate the actual outcome.
    # This illustrative callback makes no network call.
    return RouteOutcome(success=True, cost_usd=None)

result = router.run(
    RouteRequest(request_id="opaque-123", category_id="orders"),
    {"small-a": invoke, "mid-b": invoke},
)
```

The host owns payloads, provider SDKs, credentials, deadlines, output storage and
quality checks. Routing records retain outcome, measured elapsed latency and
caller-reported cost, never prompts, responses or exception messages. Use opaque
IDs and non-sensitive model/deployment names. No universal wall-clock timeout,
async provider API or automatic model invocation is claimed.

## Policies and decisions

`RoutingPolicy` has a name/version and canonical SHA-256. A `RouteDecision`
records these plus the canonical hash of the **entire ModelFit model JSON**,
category, confidence, ranked targets, source indexes, rejected candidate reasons,
and selection/allocation explanations. The report hash is independent of file
whitespace; source experiment file hashes remain in the ModelFit report. Keep
that report with the decision to resolve source indexes.

- `advisory` (default): `run` returns a proposal with no callbacks.
- `enforce`: only eligible targets execute, within `max_attempts` (default 3).
- `shadow`: an eligible baseline serves. A separately supplied `shadow_callbacks`
  map enables a second, explicitly safe call to the proposed candidate. Shadow
  output never serves; its failure never changes the serving result. Shadow
  execution is sequential, adds work/cost, and needs side-effect-safe callbacks.
- `canary`: SHA-256 of salt, category and opaque request ID assigns a stable
  baseline/canary cohort. `canary_fraction` is in [0, 1]. Use stable distinct IDs;
  changing the salt reshuffles cohorts. Baseline requests never fall through to
  candidate execution. Candidate requests may use eligible fallback targets.

`strategy="score"` selects by recorded weighted score with variant ID tie-breaks;
its fallback chain prefers other providers before same-provider alternatives.
`strategy="rule"` uses the exact ordered IDs in `rules[category_id]` after all
hard constraints. Unknown rule IDs cannot route, missing category rules escalate.
A different-provider fallback is possible only when eligible evidence exists.

Runtime `constraints` are **additional** to original category constraints; they
cannot loosen ModelFit restrictions. Missing evidence fails closed, including
incomplete costs under cost limits. Baselines and every fallback obey the same
checks. `minimum_confidence` applies the category recommendation's qualitative
confidence label; it is not a calibrated probability or per-target estimate.
No evidence freshness clock is enforced: hosts must regenerate/approve reports
when deployments or evidence change. Hashes identify supplied artifacts, not
independent verification of their claims.

Unknown categories, missing recommendations, low confidence and no eligible
model return `escalated` by default or `blocked` with `on_unroutable="block"`.
Neither invokes a callback. Escalation is a handoff to the host's human workflow;
Lens does not authenticate approvers or provide an approval service. After review,
the host must produce an eligible policy/evidence combination and route again.

## Failover and errors

Only an explicit `RetryableRouteError` triggers the next eligible target. Raise
it only when a failed call is safe to retry (for example an uncommitted provider
outage). Policy denials and potentially committed side effects must never be
wrapped in it. Other exceptions, invalid callback outcomes, unsuccessful quality
outcomes and absent callbacks stop the chain with a failed result. Exception text
is not retained. No implicit retry or policy bypass occurs.

## Audit and measurement

`RoutingAuditLog` appends/fsyncs decision, attempt-start, attempt-finish and result
records. Audit errors propagate before any further callback. A crash can leave
an attempt-start without a finish; reconcile provider state before retrying.
The optional sink is a single-process local journal, without tamper-proofing,
multi-writer locking, RBAC, retention or deletion services. Choose one writer per
path and manage permissions/retention in the host. Without a sink, keep the
returned decision/results yourself.

`summarize_routing` reports served results, shadow pairs, success rates, and mean
shadow-minus-primary latency/cost deltas. Cost deltas remain unavailable if any
pair lacks cost. Requests without a separately executed shadow are not pairs.
These are observed callback outcomes, not statistical causal or significance
claims. Schemas are published in `schemas/routing/` (Lens-local version 1.0).

## Ecosystem compatibility

| Package | Impact |
| --- | --- |
| AgenticLens 0.10.0 | Owns routing SDK, decisions, journal and measured summaries |
| Agentic Evals | Existing `>=0.7.1,<1` range covers current 0.8.0; scoring/gates stay native |
| Agentic Chaos 0.7.0 | Existing `agenticlens>=0.7.0` extra remains compatible; faults stay Chaos-owned |
| Agentic Sidecar 0.8.4 | Existing `agenticlens>=0.7.1,<1` extra remains compatible; Decision Gate/authority remain Sidecar-owned |
| MCP 0.3.12 | Hosted Lens pin 0.10.0 and read-only `lens.routing_decide`; never executes callbacks |
| Control Tower 0.7.0 | Inventory, host-applied settings, approval and native evidence semantics unchanged; no automatic routing adapter |
| AI Operations Specification | Routing artifacts are Lens-local; no normative shared schema or conformance claim added |

Only MCP requires a sibling patch release. The other packages need compatibility
documentation updates, without dependency or runtime changes.
