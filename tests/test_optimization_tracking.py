"""Decisions are tied to a report hash and follow the allowed transitions."""

from datetime import datetime, timezone

import pytest

from agenticlens.optimization import (
    RecommendationDecision,
    RecommendationLedger,
    analyze_optimizations,
    report_sha256,
)
from optimization_support import retrieval_run

AT = datetime(2026, 10, 20, tzinfo=timezone.utc)


@pytest.fixture()
def report():
    return analyze_optimizations([retrieval_run("a", [1]), retrieval_run("b", [2])])


def _decision(report, status, opportunity_id=None, digest=None):
    return RecommendationDecision(
        opportunity_id=opportunity_id or report.opportunities[0].opportunity_id,
        report_sha256=digest or report_sha256(report),
        status=status,
        decided_by="tester",
        decided_at=AT,
    )


def test_lifecycle_and_summary(tmp_path, report):
    ledger = RecommendationLedger(tmp_path / "ledger.jsonl")
    first = report.opportunities[0].opportunity_id
    for status in ("accepted", "adopted", "reverted"):
        ledger.record(report, _decision(report, status))
    assert ledger.status(first) == "reverted"
    summary = ledger.summary(report)
    assert summary[first] == "reverted"
    assert set(summary.values()) <= {"reverted", "proposed"}
    assert len(ledger.decisions()) == 3


@pytest.mark.parametrize(
    "history, status",
    [((), "adopted"), ((), "reverted"), (("accepted",), "accepted"), (("rejected",), "adopted")],
)
def test_invalid_transitions_are_refused(tmp_path, report, history, status):
    ledger = RecommendationLedger(tmp_path / "ledger.jsonl")
    for previous in history:
        ledger.record(report, _decision(report, previous))
    with pytest.raises(ValueError, match="cannot move"):
        ledger.record(report, _decision(report, status))


def test_rejection_can_be_reconsidered(tmp_path, report):
    ledger = RecommendationLedger(tmp_path / "ledger.jsonl")
    ledger.record(report, _decision(report, "rejected"))
    ledger.record(report, _decision(report, "accepted"))
    assert ledger.status(report.opportunities[0].opportunity_id) == "accepted"


def test_decision_must_match_report_and_opportunity(tmp_path, report):
    ledger = RecommendationLedger(tmp_path / "ledger.jsonl")
    with pytest.raises(ValueError, match="report_sha256"):
        ledger.record(report, _decision(report, "accepted", digest="0" * 64))
    with pytest.raises(KeyError):
        ledger.record(report, _decision(report, "accepted", opportunity_id="missing"))
    assert not ledger.path.exists()


def test_decisions_on_an_earlier_report_do_not_carry_over(tmp_path, report):
    ledger = RecommendationLedger(tmp_path / "ledger.jsonl")
    ledger.record(report, _decision(report, "accepted"))
    regenerated = analyze_optimizations(
        [retrieval_run("a", [1]), retrieval_run("b", [2]), retrieval_run("c", [1])]
    )
    target = report.opportunities[0].opportunity_id
    assert target in {o.opportunity_id for o in regenerated.opportunities}
    assert ledger.summary(regenerated)[target] == "proposed"
    with pytest.raises(ValueError, match="cannot move"):
        ledger.record(regenerated, _decision(regenerated, "adopted", opportunity_id=target))
    assert ledger.status(target) == "accepted"
