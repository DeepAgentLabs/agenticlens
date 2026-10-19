"""Routing acceptance: evidence, enforcement, safe failover and measured shadowing."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

from agenticlens.cli.main import app
from agenticlens.modelfit import ModelConstraints, load_modelfit_report
from agenticlens.routing import (
    RetryableRouteError,
    RouteOutcome,
    Router,
    RouteRequest,
    RoutingAuditLog,
    RoutingPolicy,
    RoutingResult,
    artifact_sha256,
    summarize_routing,
)

REPORT = Path(__file__).resolve().parents[1] / "examples/modelfit/artifacts/modelfit.json"


@pytest.fixture
def report():
    result = load_modelfit_report(REPORT)
    for category in result.categories:
        category.recommendation.confidence = "high"
    return result


def request(category="orders", request_id="request-1"):
    return RouteRequest(request_id=request_id, category_id=category)


def good(target, req):
    return RouteOutcome(success=True, cost_usd=0.002)


def unavailable(target, req):
    raise RetryableRouteError("secret provider details")


def callbacks(report):
    return {c.variant_id: good for cat in report.categories for c in cat.candidates}


def test_advisory_is_default_and_never_calls_models(report):
    def forbidden(*args):
        pytest.fail("advisory invoked a callback")

    router = Router(report)
    result = router.run(request(), {key: forbidden for key in callbacks(report)})
    assert result.status == "advisory" and not result.attempts
    assert result.decision.targets[0].variant_id == "small-a"
    assert result.decision.report_sha256 == artifact_sha256(report)
    assert result.decision.reasons


@pytest.mark.parametrize("disposition", ["block", "escalate"])
def test_unknown_category_fails_closed(report, disposition):
    result = Router(report, RoutingPolicy(mode="enforce", on_unroutable=disposition)).run(
        request("absent"), callbacks(report)
    )
    assert result.status == ("blocked" if disposition == "block" else "escalated")
    assert not result.attempts and not result.decision.targets


def test_constraints_apply_to_primary_and_all_fallbacks(report):
    policy = RoutingPolicy(
        mode="enforce", constraints=ModelConstraints(allowed_providers=["no-such-provider"])
    )
    result = Router(report, policy).run(request(), callbacks(report))
    assert result.status == "escalated"
    assert result.decision.rejected and not result.attempts
    # Original on-prem constraint cannot be loosened by an empty runtime policy.
    decision = Router(report).decide(request("account"))
    assert all(t.deployment == "on_prem" for t in decision.targets)


def test_low_confidence_escalates(report):
    category = next(c for c in report.categories if c.category.id == "orders")
    category.recommendation.confidence = "low"
    result = Router(report, RoutingPolicy(mode="enforce")).run(request(), callbacks(report))
    assert result.status == "escalated" and not result.attempts


def test_rule_order_is_respected_and_does_not_bypass_constraints(report):
    policy = RoutingPolicy(strategy="rule", rules={"orders": ["mid-b", "small-a"]})
    decision = Router(report, policy).decide(request())
    assert [t.variant_id for t in decision.targets] == ["mid-b", "small-a"]
    policy.rules = {"account": ["small-a"]}
    assert Router(report, policy).decide(request("account")).status == "escalated"
    assert Router(report, policy).decide(request("orders")).status == "escalated"


def test_retryable_provider_failover_and_bounded_attempts(report):
    router = Router(report, RoutingPolicy(mode="enforce"))
    selected = router.decide(request()).targets
    assert selected[0].provider != selected[1].provider
    calls = callbacks(report)
    calls[selected[0].variant_id] = unavailable
    result = router.run(request(), calls)
    assert result.status == "succeeded"
    assert result.served_variant_id == selected[1].variant_id
    assert [a.status for a in result.attempts] == ["retryable_error", "succeeded"]
    result = Router(report, RoutingPolicy(mode="enforce", max_attempts=1)).run(request(), calls)
    assert result.status == "failed" and len(result.attempts) == 1


@pytest.mark.parametrize("failure", ["exception", "unsuccessful", "invalid"])
def test_unknown_errors_and_unsuccessful_outputs_never_retry(report, failure):
    def fail(target, req):
        if failure == "exception":
            raise RuntimeError("sensitive response")
        if failure == "invalid":
            return None
        return RouteOutcome(success=False)

    router = Router(report, RoutingPolicy(mode="enforce"))
    calls = callbacks(report)
    calls[router.decide(request()).targets[0].variant_id] = fail
    result = router.run(request(), calls)
    assert result.status == "failed" and len(result.attempts) == 1
    assert "sensitive" not in result.model_dump_json()


def test_missing_callback_does_not_silently_failover(report):
    result = Router(report, RoutingPolicy(mode="enforce")).run(request(), {})
    assert result.status == "failed" and not result.attempts


def test_shadow_requires_separate_callback_and_measures_pairs(report):
    router = Router(report, RoutingPolicy(mode="shadow", baseline_variant_id="mid-b"))
    unmeasured = router.run(request(), callbacks(report))
    assert len(unmeasured.attempts) == 1
    assert unmeasured.served_variant_id == "mid-b"
    result = router.run(request(), callbacks(report), shadow_callbacks={"small-a": good})
    assert result.served_variant_id == "mid-b"
    assert [a.role for a in result.attempts] == ["primary", "shadow"]
    summary = summarize_routing([result, unmeasured])
    assert summary.served == 2 and summary.shadow_pairs == 1
    assert summary.shadow_success_rate == 1 and summary.primary_success_rate == 1
    assert summary.mean_shadow_cost_delta_usd == 0
    assert summary.mean_shadow_latency_delta_ms is not None
    result.attempts[-1].cost_usd = None
    assert summarize_routing([result]).mean_shadow_cost_delta_usd is None
    assert summarize_routing([]).shadow_success_rate is None


def test_shadow_failure_does_not_replace_baseline_result(report):
    result = Router(report, RoutingPolicy(mode="shadow", baseline_variant_id="mid-b")).run(
        request(), callbacks(report), shadow_callbacks={"small-a": unavailable}
    )
    assert result.status == "succeeded" and result.served_variant_id == "mid-b"
    assert result.attempts[-1].status == "retryable_error"


@pytest.mark.parametrize("mode", ["canary", "shadow"])
def test_baseline_cannot_bypass_constraints(report, mode):
    result = Router(report, RoutingPolicy(mode=mode, baseline_variant_id="small-a")).run(
        request("account"), callbacks(report), shadow_callbacks=callbacks(report)
    )
    assert result.status == "escalated" and not result.attempts


@pytest.mark.parametrize(
    "fraction, cohort, target", [(0, "baseline", "mid-b"), (1, "canary", "small-a")]
)
def test_canary_boundaries_and_repeatable_allocation(report, fraction, cohort, target):
    router = Router(
        report,
        RoutingPolicy(mode="canary", baseline_variant_id="mid-b", canary_fraction=fraction),
    )
    for _ in range(3):
        decision = router.decide(request())
        assert decision.cohort == cohort and decision.targets[0].variant_id == target
    router = Router(
        report, RoutingPolicy(mode="canary", baseline_variant_id="mid-b", canary_fraction=0.5)
    )
    allocations = [router.decide(request(request_id=str(i))).cohort for i in range(100)]
    assert "baseline" in allocations and "canary" in allocations
    assert router.decide(request()).cohort == router.decide(request()).cohort


def test_policy_report_and_callback_inputs_are_isolated(report):
    policy = RoutingPolicy(mode="enforce")
    router = Router(report, policy)
    before = router.decide(request())
    policy.mode = "advisory"
    report.categories.clear()

    def mutate(target, req):
        target.variant_id = "tampered"
        req.category_id = "tampered"
        return good(target, req)

    result = router.run(request(), {t.variant_id: mutate for t in before.targets})
    assert result.status == "succeeded"
    assert result.decision.targets == before.targets
    assert result.decision.request.category_id == "orders"


def test_audit_records_all_attempts_without_exception_text(report, tmp_path):
    path = tmp_path / "routing.jsonl"
    router = Router(report, RoutingPolicy(mode="enforce"), audit=RoutingAuditLog(path))
    calls = callbacks(report)
    calls[router.decide(request()).targets[0].variant_id] = unavailable
    result = router.run(request(), calls)
    records = [json.loads(line) for line in path.read_text().splitlines()]
    assert [r["event"] for r in records[1:]] == [
        "decision",
        "attempt_started",
        "attempt_finished",
        "attempt_started",
        "attempt_finished",
        "result",
    ]
    assert all(r["decision_id"] == result.decision.decision_id for r in records[1:])
    assert "secret provider" not in path.read_text()
    assert RoutingResult.model_validate(records[-1]["record"]) == result


def test_audit_failure_blocks_external_call(report, tmp_path):
    # Opening a directory for append fails on every supported platform.
    router = Router(report, RoutingPolicy(mode="enforce"), audit=RoutingAuditLog(tmp_path))
    calls = []
    with pytest.raises(OSError):
        router.run(request(), {"small-a": lambda *args: calls.append(args)})
    assert not calls


def test_audit_failure_between_attempts_never_triggers_failover(report, tmp_path):
    class FailingAudit(RoutingAuditLog):
        def append(self, event, decision_id, record):
            if event == "attempt_finished":
                raise OSError("disk full")
            super().append(event, decision_id, record)

    calls = []

    def retry(target, req):
        calls.append(target.variant_id)
        raise RetryableRouteError()

    router = Router(report, RoutingPolicy(mode="enforce"), audit=FailingAudit(tmp_path / "log"))
    with pytest.raises(OSError):
        router.run(request(), {key: retry for key in callbacks(report)})
    assert calls == ["small-a"]


def test_missing_cost_and_source_evidence_fail_closed(report):
    category = next(c for c in report.categories if c.category.id == "orders")
    for c in category.candidates:
        c.cost_complete = False
        c.cost_per_case_usd = 0  # Contradictory imported evidence cannot bypass coverage.
    decision = Router(
        report, RoutingPolicy(constraints=ModelConstraints(max_cost_per_case_usd=1))
    ).decide(request())
    assert decision.status == "escalated"
    for c in category.candidates:
        c.source_index = 100
    assert Router(report).decide(request()).status == "escalated"


def test_duplicate_evidence_rejected(report):
    report.categories.append(report.categories[0])
    with pytest.raises(ValueError, match="duplicate category"):
        Router(report)


@pytest.mark.parametrize(
    "config",
    [
        {"mode": "shadow"},
        {"mode": "canary"},
        {"canary_fraction": float("nan")},
        {"rules": {"x": ["a", "a"]}},
        {"max_attempts": 0},
    ],
)
def test_invalid_policies(config):
    with pytest.raises(ValidationError):
        RoutingPolicy.model_validate(config)


def test_cli_decide_exit_codes_and_summary(report, tmp_path):
    runner = CliRunner()
    saved = tmp_path / "decision.json"
    policy = tmp_path / "policy.json"
    policy.write_text(RoutingPolicy(minimum_confidence="low").model_dump_json())
    base = ["routing", "decide", str(REPORT), "--request-id", "cli-1", "--policy", str(policy)]
    response = runner.invoke(app, [*base, "--category", "orders", "--save", str(saved)])
    assert response.exit_code == 0, response.output
    assert json.loads(saved.read_text())["targets"][0]["variant_id"] == "small-a"
    assert runner.invoke(app, [*base, "--category", "missing"]).exit_code == 5
    assert (
        runner.invoke(app, [*base, "--category", "orders", "--policy", "missing.json"]).exit_code
        == 1
    )
    result = Router(report, RoutingPolicy(mode="shadow", baseline_variant_id="mid-b")).run(
        request(), callbacks(report), shadow_callbacks=callbacks(report)
    )
    path = tmp_path / "result.json"
    path.write_text(result.model_dump_json())
    response = runner.invoke(app, ["routing", "summary", str(path)])
    assert response.exit_code == 0, response.output
    assert json.loads(response.output)["shadow_pairs"] == 1


def test_nonfinite_constraints_and_unknown_schema_are_rejected(report):
    policy = RoutingPolicy(constraints=ModelConstraints(max_cost_per_case_usd=float("inf")))
    with pytest.raises(ValueError):
        Router(report, policy)
    report.schema_version = "2.0"
    with pytest.raises(ValueError, match="unsupported"):
        Router(report)
