"""Measure attribution accuracy on controlled failures.

A controlled failure is a trace whose faulty step is known in advance:
either a fault was injected on purpose (span attribute ``chaos.injected``,
written by agentic-chaos) or the producer recorded the expected answer in
``run.metadata["expected_faulty_span_id"]`` (and optionally
``expected_faulty_agent`` / ``expected_category``).

`evaluate_attribution()` diagnoses every case and reports how often the
top-ranked span, agent, and category match, with Wilson intervals, plus a
calibration gap between mean confidence and observed accuracy.
"""

import json
from collections.abc import Sequence
from pathlib import Path

from pydantic import BaseModel, Field, model_validator

from agenticlens.diagnosis.engine import diagnose_run
from agenticlens.diagnosis.rules import DiagnosisConfig
from agenticlens.diagnosis.taxonomy import FailureCategory
from agenticlens.diagnosis.view import CHAOS_INJECTED_KEY
from agenticlens.experiments.stats import wilson_interval
from agenticlens.models.trace import Run

ACCURACY_SCHEMA_VERSION = "1.0"
MIN_RELIABLE_CASES = 30


class ControlledFailure(BaseModel):
    """A run with a known faulty step."""

    case_id: str
    run: Run
    expected_span_id: str | None = None
    expected_span_name: str | None = None
    expected_agent: str | None = None
    expected_category: FailureCategory | None = None
    notes: str = ""

    @model_validator(mode="after")
    def require_expected_step(self) -> "ControlledFailure":
        if self.expected_span_id is None and self.expected_span_name is None:
            raise ValueError("a controlled failure needs expected_span_id or expected_span_name")
        return self


def controlled_failure_from_run(run: Run, *, case_id: str | None = None) -> ControlledFailure:
    """Build a `ControlledFailure` from ground truth the run itself records.

    Uses ``metadata["expected_faulty_span_id"]`` when present, otherwise the
    single span marked ``chaos.injected``. Raises `ValueError` when neither
    identifies exactly one span.
    """
    metadata = run.metadata
    expected = metadata.get("expected_faulty_span_id")
    if not isinstance(expected, str):
        injected = [s for s in run.spans if s.attributes.get(CHAOS_INJECTED_KEY)]
        if len(injected) != 1:
            raise ValueError(
                f"run {run.run_id}: expected exactly one span with {CHAOS_INJECTED_KEY}, "
                f"found {len(injected)}; or set metadata['expected_faulty_span_id']"
            )
        expected = injected[0].span_id
    span = next((s for s in run.spans if s.span_id == expected), None)
    if span is None:
        raise ValueError(f"run {run.run_id}: expected span {expected} is not in the trace")
    category = metadata.get("expected_category")
    agent = metadata.get("expected_faulty_agent", span.agent_name)
    return ControlledFailure(
        case_id=case_id or run.run_id,
        run=run,
        expected_span_id=expected,
        expected_span_name=span.name,
        expected_agent=agent if isinstance(agent, str) else None,
        expected_category=FailureCategory(category) if isinstance(category, str) else None,
    )


def load_controlled_failures(path: Path) -> list[ControlledFailure]:
    """Load cases from a directory of trace JSON files or one JSON file.

    Files may contain a saved `Run` (ground truth read from the run, see
    `controlled_failure_from_run`) or a `ControlledFailure` object, or a list
    of either. Directory files load in name order.
    """
    files = sorted(path.glob("*.json")) if path.is_dir() else [path]
    if not files:
        raise ValueError(f"no JSON files found in {path}")
    cases: list[ControlledFailure] = []
    for file in files:
        payload = json.loads(file.read_text(encoding="utf-8"))
        items = payload if isinstance(payload, list) else [payload]
        for index, item in enumerate(items):
            if isinstance(item, dict) and "run" in item and "case_id" in item:
                cases.append(ControlledFailure.model_validate(item))
            else:
                suffix = f"#{index}" if len(items) > 1 else ""
                cases.append(
                    controlled_failure_from_run(
                        Run.model_validate(item), case_id=f"{file.stem}{suffix}"
                    )
                )
    ids = [case.case_id for case in cases]
    if len(ids) != len(set(ids)):
        raise ValueError("controlled failure case IDs must be unique")
    return cases


class AttributionOutcome(BaseModel):
    case_id: str
    expected_span: str
    predicted_span_id: str | None
    predicted_span_name: str | None
    predicted_agent: str | None
    predicted_category: FailureCategory | None
    confidence: float
    step_correct: bool
    top3_correct: bool
    agent_correct: bool | None = Field(
        default=None, description="None when the case names no expected agent."
    )
    category_correct: bool | None = Field(
        default=None, description="None when the case names no expected category."
    )


class AccuracyMetric(BaseModel):
    correct: int
    total: int
    accuracy: float | None
    interval: tuple[float, float] | None = Field(
        default=None, description="Wilson interval at the report's confidence level."
    )


class AttributionAccuracyReport(BaseModel):
    schema_version: str = ACCURACY_SCHEMA_VERSION
    total_cases: int
    confidence_level: float
    step: AccuracyMetric
    top3_step: AccuracyMetric
    agent: AccuracyMetric
    category: AccuracyMetric
    mean_confidence: float
    calibration_gap: float = Field(
        description=(
            "Mean attribution confidence minus top-1 step accuracy (positive = overconfident)."
        )
    )
    outcomes: list[AttributionOutcome]
    warnings: list[str] = Field(default_factory=list)


def _metric(values: Sequence[bool | None], confidence_level: float) -> AccuracyMetric:
    scored = [v for v in values if v is not None]
    correct = sum(scored)
    if not scored:
        return AccuracyMetric(correct=0, total=0, accuracy=None)
    return AccuracyMetric(
        correct=correct,
        total=len(scored),
        accuracy=correct / len(scored),
        interval=wilson_interval(correct, len(scored), confidence_level),
    )


def _matches(case: ControlledFailure, span_id: str | None, span_name: str | None) -> bool:
    if case.expected_span_id is not None:
        return span_id == case.expected_span_id
    return span_name == case.expected_span_name


def evaluate_attribution(
    cases: Sequence[ControlledFailure],
    *,
    config: DiagnosisConfig | None = None,
    confidence_level: float = 0.95,
) -> AttributionAccuracyReport:
    """Diagnose each controlled failure and score the attribution against ground truth."""
    if not cases:
        raise ValueError("at least one controlled failure is required")
    outcomes: list[AttributionOutcome] = []
    for case in cases:
        attribution = diagnose_run(case.run, config=config).attribution
        top3 = attribution.candidates[:3]
        outcomes.append(
            AttributionOutcome(
                case_id=case.case_id,
                expected_span=case.expected_span_id or case.expected_span_name or "",
                predicted_span_id=attribution.faulty_span_id,
                predicted_span_name=attribution.faulty_step,
                predicted_agent=attribution.faulty_agent,
                predicted_category=attribution.category,
                confidence=attribution.confidence,
                step_correct=_matches(case, attribution.faulty_span_id, attribution.faulty_step),
                top3_correct=any(_matches(case, c.span_id, c.span_name) for c in top3),
                agent_correct=(
                    None
                    if case.expected_agent is None
                    else attribution.faulty_agent == case.expected_agent
                ),
                category_correct=(
                    None
                    if case.expected_category is None
                    else attribution.category is case.expected_category
                ),
            )
        )
    step = _metric([o.step_correct for o in outcomes], confidence_level)
    mean_confidence = sum(o.confidence for o in outcomes) / len(outcomes)
    warnings: list[str] = []
    if len(cases) < MIN_RELIABLE_CASES:
        warnings.append(
            f"Only {len(cases)} controlled failure(s); accuracy intervals are wide below "
            f"{MIN_RELIABLE_CASES} cases."
        )
    return AttributionAccuracyReport(
        total_cases=len(cases),
        confidence_level=confidence_level,
        step=step,
        top3_step=_metric([o.top3_correct for o in outcomes], confidence_level),
        agent=_metric([o.agent_correct for o in outcomes], confidence_level),
        category=_metric([o.category_correct for o in outcomes], confidence_level),
        mean_confidence=round(mean_confidence, 6),
        calibration_gap=round(mean_confidence - (step.accuracy or 0.0), 6),
        outcomes=outcomes,
        warnings=warnings,
    )
