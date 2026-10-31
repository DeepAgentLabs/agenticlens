"""Accepted and rejected recommendation tracking in an append-only local ledger."""

import json
import os
from pathlib import Path

from agenticlens.optimization.models import (
    DecisionStatus,
    OptimizationReport,
    RecommendationDecision,
)
from agenticlens.routing.audit import artifact_sha256

# Statuses each status may follow. `proposed` is implicit for every opportunity.
_ALLOWED: dict[DecisionStatus, set[DecisionStatus]] = {
    "proposed": set(),
    "accepted": {"proposed", "rejected"},
    "rejected": {"proposed", "accepted"},
    "adopted": {"accepted"},
    "reverted": {"adopted"},
}


def report_sha256(report: OptimizationReport) -> str:
    return artifact_sha256(report)


class RecommendationLedger:
    """JSONL decision history. Single-writer; each record is fsynced.

    Decisions are tied to the SHA-256 of the report that proposed them, so a
    decision can never silently attach to a regenerated report.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def decisions(self) -> list[RecommendationDecision]:
        if not self.path.exists():
            return []
        lines = self.path.read_text(encoding="utf-8").splitlines()
        return [RecommendationDecision.model_validate_json(line) for line in lines if line]

    def status(self, opportunity_id: str) -> DecisionStatus:
        latest: DecisionStatus = "proposed"
        for decision in self.decisions():
            if decision.opportunity_id == opportunity_id:
                latest = decision.status
        return latest

    def record(
        self, report: OptimizationReport, decision: RecommendationDecision
    ) -> RecommendationDecision:
        report.opportunity(decision.opportunity_id)
        if decision.report_sha256 != report_sha256(report):
            raise ValueError("decision report_sha256 does not match the report")
        current = self.status(decision.opportunity_id)
        if current not in _ALLOWED[decision.status]:
            raise ValueError(f"cannot move from {current!r} to {decision.status!r}")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(decision.model_dump(mode="json"), allow_nan=False) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        return decision

    def summary(self, report: OptimizationReport) -> dict[str, DecisionStatus]:
        """Latest status of every opportunity in the report, in report order."""
        latest: dict[str, DecisionStatus] = {}
        for decision in self.decisions():
            latest[decision.opportunity_id] = decision.status
        return {
            item.opportunity_id: latest.get(item.opportunity_id, "proposed")
            for item in report.opportunities
        }
