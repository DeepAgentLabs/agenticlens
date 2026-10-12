"""Check that an evaluation report carries the evidence its conclusions need.

The audit answers three questions about a saved `EvaluationReport`:

- Does every score name the evaluator and evaluator version that produced it?
- Can every failed case be traced back to a recorded trace?
- How complete is the cost data, and was it measured or estimated?

It reads the report only; it never re-runs evaluators or targets.
"""

from typing import Literal

from agentic_evals import EvaluationReport
from pydantic import BaseModel, Field

IssueKind = Literal[
    "unattributed_score",
    "unversioned_evaluator",
    "missing_sample",
    "missing_trace_id",
    "incomplete_cost",
    "unspecified_cost_source",
]


class EvidenceIssue(BaseModel):
    kind: IssueKind
    message: str
    case_id: str | None = None
    score_name: str | None = None
    evaluator: str | None = None
    blocking: bool = True


class CostCoverage(BaseModel):
    total_cases: int
    priced_cases: int
    sources: dict[str, int] = Field(default_factory=dict)
    complete: bool


class EvidenceAudit(BaseModel):
    schema_version: Literal["1.0"] = "1.0"
    suite_name: str
    suite_version: str
    passed: bool
    evaluators: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Evaluator name -> sorted declared versions ('unversioned' when none).",
    )
    failed_cases: int
    failed_cases_with_trace: int
    cost: CostCoverage
    issues: list[EvidenceIssue] = Field(default_factory=list)


def audit_report(
    report: EvaluationReport,
    *,
    require_evaluator_versions: bool = True,
    require_complete_cost: bool = False,
    require_cost_source: bool = False,
) -> EvidenceAudit:
    """Audit a report's evidence. `passed` is False when any blocking issue exists.

    Missing trace evidence on a failed case is always blocking: a failure that
    cannot be traced cannot be diagnosed. The `require_*` flags decide whether
    unversioned evaluators, incomplete cost data, and cost without a stated
    provenance block too; when they don't, those are still listed as
    non-blocking issues.
    """
    issues: list[EvidenceIssue] = []
    evaluators: dict[str, set[str]] = {}
    for case in report.cases:
        for score in case.scores:
            if not score.evaluator:
                issues.append(
                    EvidenceIssue(
                        kind="unattributed_score",
                        message=(
                            f"Score {score.name!r} on case {case.case_id!r} does not name "
                            "its evaluator (report predates agentic-evals 0.7.1?)."
                        ),
                        case_id=case.case_id,
                        score_name=score.name,
                        blocking=require_evaluator_versions,
                    )
                )
                continue
            evaluators.setdefault(score.evaluator, set()).add(
                score.evaluator_version or "unversioned"
            )
    for name in sorted(evaluators):
        if "unversioned" in evaluators[name]:
            issues.append(
                EvidenceIssue(
                    kind="unversioned_evaluator",
                    message=f"Evaluator {name!r} produced scores without a declared version.",
                    evaluator=name,
                    blocking=require_evaluator_versions,
                )
            )

    failed = [case for case in report.cases if not case.passed]
    traced = 0
    for case in failed:
        if not case.sample_available:
            issues.append(
                EvidenceIssue(
                    kind="missing_sample",
                    message=f"Failed case {case.case_id!r} has no sample, so no trace exists.",
                    case_id=case.case_id,
                )
            )
        elif not case.trace_id:
            issues.append(
                EvidenceIssue(
                    kind="missing_trace_id",
                    message=f"Failed case {case.case_id!r} has a sample but no trace ID.",
                    case_id=case.case_id,
                )
            )
        else:
            traced += 1

    summary = report.summary
    priced = sum(case.cost_usd is not None for case in report.cases)
    sources: dict[str, int] = {}
    for case in report.cases:
        if case.cost_usd is not None:
            key = case.cost_source or "unspecified"
            sources[key] = sources.get(key, 0) + 1
    complete = priced == len(report.cases) and summary.total_cost_usd is not None
    if not complete:
        issues.append(
            EvidenceIssue(
                kind="incomplete_cost",
                message=(
                    f"{priced} of {len(report.cases)} cases have a cost; total cost is unavailable."
                ),
                blocking=require_complete_cost,
            )
        )
    if sources.get("unspecified"):
        issues.append(
            EvidenceIssue(
                kind="unspecified_cost_source",
                message=(
                    f"{sources['unspecified']} priced case(s) do not say whether their cost "
                    "was measured or estimated."
                ),
                blocking=require_cost_source,
            )
        )

    return EvidenceAudit(
        suite_name=report.suite_name,
        suite_version=report.suite_version,
        passed=not any(issue.blocking for issue in issues),
        evaluators={name: sorted(versions) for name, versions in sorted(evaluators.items())},
        failed_cases=len(failed),
        failed_cases_with_trace=traced,
        cost=CostCoverage(
            total_cases=len(report.cases),
            priced_cases=priced,
            sources=dict(sorted(sources.items())),
            complete=complete,
        ),
        issues=issues,
    )
