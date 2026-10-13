"""Advanced diagnosis: failure taxonomy, deterministic rules, faulty-step and
faulty-agent attribution, incident timelines, anomaly detection, analysis
guardrails, investigation narratives, and attribution accuracy on
controlled failures."""

from agenticlens.diagnosis.accuracy import (
    AccuracyMetric,
    AttributionAccuracyReport,
    AttributionOutcome,
    ControlledFailure,
    controlled_failure_from_run,
    evaluate_attribution,
    load_controlled_failures,
)
from agenticlens.diagnosis.anomaly import detect_anomalies
from agenticlens.diagnosis.engine import ENGINE_VERSION, diagnose_run
from agenticlens.diagnosis.guardrails import AnalysisBudget, AnalysisGuard
from agenticlens.diagnosis.models import (
    DIAGNOSIS_SCHEMA_VERSION,
    Anomaly,
    AnomalyReport,
    Attribution,
    AttributionCandidate,
    Diagnosis,
    DiagnosisReport,
    DiagnosisSummary,
    GuardrailStatus,
    IncidentTimeline,
    TimelineEvent,
)
from agenticlens.diagnosis.narrative import explain_recommendations, explain_run
from agenticlens.diagnosis.rules import (
    DEFAULT_RULES,
    DiagnosisConfig,
    DiagnosisRule,
    failure_category,
)
from agenticlens.diagnosis.taxonomy import (
    FAILURE_TAXONOMY,
    TAXONOMY_VERSION,
    CategoryInfo,
    FailureCategory,
    describe,
)
from agenticlens.diagnosis.view import (
    CHAOS_EVENT_ID_KEY,
    CHAOS_FAULT_TYPE_KEY,
    CHAOS_INJECTED_KEY,
    TraceView,
)

__all__ = [
    "CHAOS_EVENT_ID_KEY",
    "CHAOS_FAULT_TYPE_KEY",
    "CHAOS_INJECTED_KEY",
    "DEFAULT_RULES",
    "DIAGNOSIS_SCHEMA_VERSION",
    "ENGINE_VERSION",
    "FAILURE_TAXONOMY",
    "TAXONOMY_VERSION",
    "AccuracyMetric",
    "AnalysisBudget",
    "AnalysisGuard",
    "Anomaly",
    "AnomalyReport",
    "Attribution",
    "AttributionAccuracyReport",
    "AttributionCandidate",
    "AttributionOutcome",
    "CategoryInfo",
    "ControlledFailure",
    "Diagnosis",
    "DiagnosisConfig",
    "DiagnosisReport",
    "DiagnosisRule",
    "DiagnosisSummary",
    "FailureCategory",
    "GuardrailStatus",
    "IncidentTimeline",
    "TimelineEvent",
    "TraceView",
    "controlled_failure_from_run",
    "describe",
    "detect_anomalies",
    "diagnose_run",
    "evaluate_attribution",
    "explain_recommendations",
    "explain_run",
    "failure_category",
    "load_controlled_failures",
]
