"""The v0.9 optimization example reproduces its recorded traces and artifacts, and
the committed artifacts meet the milestone's completion criteria."""

import json
import runpy
from pathlib import Path

from agenticlens.optimization import OptimizationReport, OutcomeEvaluation

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "optimization"
DEMO = EXAMPLE.parent / "optimization_demo.py"


def test_recorded_traces_are_reproducible(tmp_path: Path, monkeypatch) -> None:
    module = runpy.run_path(str(EXAMPLE / "record_traces.py"))
    monkeypatch.setitem(module["main"].__globals__, "HERE", tmp_path)
    module["main"]()
    recorded = sorted((EXAMPLE / "traces").rglob("*.json"))
    assert len(recorded) == 16
    for path in recorded:
        produced = tmp_path / path.relative_to(EXAMPLE)
        assert produced.read_text("utf-8") == path.read_text("utf-8"), path.name


def test_demo_reproduces_committed_artifacts(tmp_path: Path) -> None:
    result = runpy.run_path(str(DEMO))["main"](tmp_path)
    assert result["outcome"] == "realized"
    assert result["statuses"]["tool_result_caching"] == "adopted"
    assert result["statuses"]["unnecessary_handoff"] == "rejected"
    for name in ("report.json", "report.md", "ledger.jsonl", "outcome.json", "outcome.md"):
        committed = (EXAMPLE / "artifacts" / name).read_text("utf-8")
        assert (tmp_path / name).read_text("utf-8") == committed, name


def test_committed_artifacts_meet_the_completion_criteria() -> None:
    artifacts = EXAMPLE / "artifacts"
    report = OptimizationReport.model_validate_json((artifacts / "report.json").read_text())
    kinds = {o.kind for o in report.opportunities}
    # Every planned deliverable area produced a recommendation.
    assert {
        "prompt_caching",
        "prompt_compression",
        "retrieval_pruning",
        "retrieval_reranking",
        "memory_summarization",
        "tool_result_caching",
        "retry_policy",
        "redundant_step",
        "unnecessary_handoff",
        "quality_cost_tradeoff",
    } <= kinds
    run_ids = {run.run_id for run in report.runs}
    for opportunity in report.opportunities:
        # Recommendations cite measured evidence from the analysed traces.
        assert opportunity.evidence
        assert {e.run_id for e in opportunity.evidence} <= run_ids
        assert opportunity.benefit.basis and opportunity.thresholds
        # Expected benefit and quality risk are separate fields, never netted.
        assert opportunity.risks
    outcome = OutcomeEvaluation.model_validate_json((artifacts / "outcome.json").read_text())
    # Projected and observed outcomes are reported independently.
    adopted = report.opportunity(outcome.opportunity_id)
    assert outcome.projected == adopted.benefit
    assert outcome.observed.tokens_per_run.delta is not None
    assert outcome.decision_status == "adopted"
    ledger = [json.loads(line) for line in (artifacts / "ledger.jsonl").read_text().splitlines()]
    assert [d["status"] for d in ledger] == ["accepted", "adopted", "accepted", "rejected"]
