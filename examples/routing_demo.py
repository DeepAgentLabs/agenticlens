"""Offline routing acceptance demo using recorded ModelFit support evidence.

Run: uv run python examples/routing_demo.py
No providers or network calls. Synthetic callbacks report fixed costs; latency
is measured locally. Low-confidence evidence is explicitly opted into for this
demo only. The default routing policy requires medium confidence.
"""

from pathlib import Path

from agenticlens.modelfit import load_modelfit_report
from agenticlens.routing import (
    RetryableRouteError,
    RouteOutcome,
    Router,
    RouteRequest,
    RouteTarget,
    RoutingAuditLog,
    RoutingPolicy,
    summarize_routing,
)

HERE = Path(__file__).resolve().parent


def success(target: RouteTarget, request: RouteRequest) -> RouteOutcome:
    return RouteOutcome(success=True, cost_usd=0.001 if target.variant_id == "small-a" else 0.004)


def unavailable(target: RouteTarget, request: RouteRequest) -> RouteOutcome:
    raise RetryableRouteError("Synthetic provider outage; no request was committed")


def main(output: Path | None = None) -> dict[str, object]:
    output = output or HERE / "routing/artifacts"
    output.mkdir(parents=True, exist_ok=True)
    report = load_modelfit_report(HERE / "modelfit/artifacts/modelfit.json")
    request = RouteRequest(request_id="offline-demo-1", category_id="orders")
    policy = RoutingPolicy(name="offline-demo", mode="enforce", minimum_confidence="low")
    policy_path = output / "policy.json"
    policy_path.write_text(policy.model_dump_json(indent=2) + "\n", encoding="utf-8")
    audit_path = output / "routing.jsonl"
    # Each run writes a fresh demo journal. Production callers choose their own retention.
    if audit_path.exists():
        audit_path.unlink()
    router = Router(report, policy, audit=RoutingAuditLog(audit_path))
    failover = router.run(request, {"small-a": unavailable, "mid-b": success})
    (output / "failover.json").write_text(
        failover.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )
    shadow = Router(
        report,
        RoutingPolicy(
            name="offline-shadow",
            mode="shadow",
            baseline_variant_id="mid-b",
            minimum_confidence="low",
        ),
    ).run(request, {"mid-b": success}, shadow_callbacks={"small-a": success})
    (output / "shadow.json").write_text(shadow.model_dump_json(indent=2) + "\n", encoding="utf-8")
    summary = summarize_routing([shadow])
    (output / "summary.json").write_text(summary.model_dump_json(indent=2) + "\n", encoding="utf-8")
    blocked = Router(report, policy).run(
        RouteRequest(request_id="unknown-task", category_id="unknown"), {}
    )
    result: dict[str, object] = {
        "failover_served": failover.served_variant_id,
        "failover_statuses": [a.status for a in failover.attempts],
        "shadow_served": shadow.served_variant_id,
        "shadow_pairs": summary.shadow_pairs,
        "shadow_cost_delta_usd": summary.mean_shadow_cost_delta_usd,
        "unknown_task": blocked.status,
    }
    print(result)
    return result


if __name__ == "__main__":
    main()
