"""Data models for diagnosis reports.

A `DiagnosisReport` is reproducible from the trace it was computed from: it
has no wall-clock timestamp of its own and its IDs are assigned in a fixed
order, so diagnosing the same saved trace twice yields the same JSON.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from agenticlens.diagnosis.taxonomy import TAXONOMY_VERSION, FailureCategory, Severity
from agenticlens.models.trace import Evidence, Finding

DIAGNOSIS_SCHEMA_VERSION = "1.1"


class Diagnosis(BaseModel):
    """One failure explained by a deterministic rule."""

    diagnosis_id: str
    category: FailureCategory
    title: str
    summary: str
    severity: Severity
    confidence: float = Field(ge=0, le=1)
    rule_id: str
    rule_version: str
    origin_span_id: str | None = Field(
        default=None,
        description="Span where the failure started; None when no single span is responsible.",
    )
    span_ids: list[str] = Field(
        default_factory=list, description="Every span that supports this diagnosis."
    )
    agent_name: str | None = None
    recovered: bool = Field(
        default=False,
        description="True when a later span of the same operation succeeded.",
    )
    evidence: list[Evidence] = Field(default_factory=list)


class AttributionCandidate(BaseModel):
    """A span that may be responsible for the run's failure, with its share of blame."""

    span_id: str
    span_name: str
    span_type: str
    agent_name: str | None = None
    score: float = Field(ge=0, le=1, description="Share of total blame; candidates sum to 1.")
    categories: list[FailureCategory] = Field(default_factory=list)
    diagnosis_ids: list[str] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)


AttributionStatus = Literal["attributed", "recovered", "unattributed", "no_failure"]


class Attribution(BaseModel):
    """Which step and agent most likely caused the run's failure.

    - ``attributed``: an unrecovered failure was traced to a span.
    - ``recovered``: failures happened but were all recovered and the run did
      not fail; candidates are still listed.
    - ``unattributed``: the run failed but no span explains it.
    - ``no_failure``: nothing failed.
    """

    status: AttributionStatus
    faulty_span_id: str | None = None
    faulty_step: str | None = None
    faulty_agent: str | None = None
    category: FailureCategory | None = None
    confidence: float = Field(default=0.0, ge=0, le=1)
    explanation: str
    candidates: list[AttributionCandidate] = Field(default_factory=list)
    agent_scores: dict[str, float] = Field(
        default_factory=dict, description="Blame share per agent (spans with no agent: '(none)')."
    )


TimelineEventKind = Literal[
    "supervision_decision",
    "run_started",
    "span_started",
    "span_completed",
    "span_failed",
    "retry",
    "handoff",
    "fault_injected",
    "recovered",
    "run_completed",
]


class TimelineEvent(BaseModel):
    offset_ms: float = Field(description="Milliseconds since the run started.")
    timestamp: datetime
    kind: TimelineEventKind
    description: str
    span_id: str | None = None
    span_name: str | None = None
    agent_name: str | None = None
    is_root_cause: bool = False


class IncidentTimeline(BaseModel):
    """Ordered events reconstructed from span timestamps and statuses."""

    run_id: str
    events: list[TimelineEvent] = Field(default_factory=list)
    first_failure_offset_ms: float | None = None
    root_cause_offset_ms: float | None = None
    recovered_span_ids: list[str] = Field(default_factory=list)
    truncated: bool = Field(default=False, description="True when max_events cut the timeline.")


class Anomaly(BaseModel):
    """A metric far outside the baseline runs' distribution."""

    scope: Literal["run", "span"]
    key: str = Field(description="'run' or '<span_type>:<span name>'.")
    metric: Literal["latency_ms", "total_tokens", "cost_usd"]
    observed: float
    baseline_median: float
    baseline_mad: float
    robust_z: float | None = Field(
        default=None,
        description=(
            "Modified z-score (MAD, or mean absolute deviation when MAD is 0); None when "
            "every baseline value is identical."
        ),
    )
    direction: Literal["high", "low"]
    baseline_samples: int
    span_ids: list[str] = Field(default_factory=list)


class AnomalyReport(BaseModel):
    method: str = "robust_z_mad"
    threshold: float
    min_baseline_samples: int
    baseline_runs: int
    anomalies: list[Anomaly] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class GuardrailStatus(BaseModel):
    """What the analysis budget allowed, and whether anything was cut short."""

    truncated: bool = False
    stop_reasons: list[str] = Field(default_factory=list)
    spans_analyzed: int = 0
    spans_total: int = 0
    max_depth_seen: int = 0
    iterations: int = 0
    stagnant_iterations: int = 0
    cost_usd: float = 0.0


class RuleRef(BaseModel):
    rule_id: str
    version: str


class DiagnosisSummary(BaseModel):
    total_diagnoses: int = 0
    unrecovered: int = 0
    highest_severity: Severity | None = None
    categories: dict[str, int] = Field(default_factory=dict)
    failed_spans: int = 0
    wasted_tokens: int = Field(default=0, description="Tokens spent in failed and retry spans.")
    wasted_latency_ms: float = 0.0
    wasted_cost_usd: float | None = Field(
        default=None, description="None when any failed or retry span has no cost."
    )


class DiagnosisReport(BaseModel):
    schema_version: str = DIAGNOSIS_SCHEMA_VERSION
    taxonomy_version: str = TAXONOMY_VERSION
    engine_version: str
    run_id: str
    trace_id: str
    application_name: str
    run_status: str
    task_success: bool | None = None
    rules: list[RuleRef] = Field(default_factory=list)
    summary: DiagnosisSummary
    diagnoses: list[Diagnosis] = Field(default_factory=list)
    attribution: Attribution
    timeline: IncidentTimeline
    anomalies: AnomalyReport | None = None
    efficiency_findings: list[Finding] = Field(
        default_factory=list,
        description="Memory, retry, and duplicated-context findings from analyze_trace().",
    )
    guardrails: GuardrailStatus = Field(default_factory=GuardrailStatus)
    limitations: list[str] = Field(default_factory=list)
