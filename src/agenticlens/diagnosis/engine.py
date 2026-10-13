"""Run every diagnosis rule over a trace and assemble a `DiagnosisReport`."""

from collections import Counter
from collections.abc import Sequence

from agenticlens.analysis.trace import analyze_trace
from agenticlens.diagnosis.anomaly import DEFAULT_MIN_BASELINE, DEFAULT_THRESHOLD, detect_anomalies
from agenticlens.diagnosis.attribution import attribute
from agenticlens.diagnosis.guardrails import AnalysisBudget, AnalysisGuard
from agenticlens.diagnosis.models import (
    Diagnosis,
    DiagnosisReport,
    DiagnosisSummary,
    RuleRef,
)
from agenticlens.diagnosis.rules import (
    DEFAULT_RULES,
    FALLBACK_RULE,
    DiagnosisConfig,
    DiagnosisRule,
)
from agenticlens.diagnosis.taxonomy import SEVERITY_ORDER, max_severity
from agenticlens.diagnosis.timeline import build_timeline
from agenticlens.diagnosis.view import TraceView
from agenticlens.models.trace import Run, SpanType

ENGINE_VERSION = "1.0"

LIMITATIONS = (
    "Diagnoses come from deterministic rules over recorded spans; behavior the trace "
    "did not record cannot be diagnosed.",
    "Attribution shares are rule-weighted blame, not calibrated probabilities. Check "
    "accuracy on controlled failures with evaluate_attribution().",
)


def _summary(view: TraceView, diagnoses: list[Diagnosis]) -> DiagnosisSummary:
    wasted = [span for span in view.spans if view.failed(span) or span.span_type is SpanType.RETRY]
    costs = [span.estimated_cost_usd for span in wasted]
    return DiagnosisSummary(
        total_diagnoses=len(diagnoses),
        unrecovered=sum(not d.recovered for d in diagnoses),
        highest_severity=max_severity([d.severity for d in diagnoses]) if diagnoses else None,
        categories=dict(Counter(d.category.value for d in diagnoses)),
        failed_spans=sum(view.failed(span) for span in view.spans),
        wasted_tokens=sum(span.total_tokens for span in wasted),
        wasted_latency_ms=round(sum(span.latency_ms for span in wasted), 3),
        wasted_cost_usd=(
            round(sum(c for c in costs if c is not None), 10)
            if all(c is not None for c in costs)
            else None
        ),
    )


def diagnose_run(
    run: Run,
    *,
    config: DiagnosisConfig | None = None,
    rules: Sequence[DiagnosisRule] | None = None,
    baseline: Sequence[Run] | None = None,
    budget: AnalysisBudget | None = None,
    anomaly_threshold: float = DEFAULT_THRESHOLD,
    min_baseline_samples: int = DEFAULT_MIN_BASELINE,
) -> DiagnosisReport:
    """Diagnose one run: failures, faulty step and agent, timeline, and anomalies.

    `rules` replaces the default rule set (the incomplete-task fallback
    still runs). Pass `baseline` runs of the same workflow to add anomaly
    detection. The `budget` caps spans, tree depth, diagnoses, and time; the
    report's `guardrails` says whether anything was cut short.
    """
    config = config or DiagnosisConfig()
    guard = AnalysisGuard(budget)
    view = TraceView(run, guard)
    active = tuple(rules) if rules is not None else DEFAULT_RULES

    found: list[Diagnosis] = []
    for rule in active:
        if guard.exhausted:
            break
        found.extend(rule.diagnose(view, config))
    if all(d.recovered for d in found):
        found.extend(FALLBACK_RULE.diagnose(view, config))

    # Most severe and least recovered first, then by where the failure began.
    found.sort(
        key=lambda d: (
            d.recovered,
            -SEVERITY_ORDER.index(d.severity),
            view.position.get(d.origin_span_id or "", len(view.spans)),
            d.rule_id,
        )
    )
    found = found[: guard.allow_diagnoses(len(found))]
    for index, diagnosis in enumerate(found, start=1):
        diagnosis.diagnosis_id = f"diag-{index:03d}"

    attribution = attribute(view, found)
    anomalies = (
        detect_anomalies(
            run,
            baseline,
            threshold=anomaly_threshold,
            min_baseline_samples=min_baseline_samples,
        )
        if baseline is not None
        else None
    )
    rule_refs = [RuleRef(rule_id=r.rule_id, version=r.version) for r in (*active, FALLBACK_RULE)]
    efficiency = analyze_trace(run)
    for index, finding in enumerate(efficiency, start=1):
        finding.finding_id = f"finding-{index:03d}"  # stable IDs keep reports reproducible
    limitations = list(LIMITATIONS)
    if config.max_cost_usd is not None and run.estimated_cost_usd is None:
        limitations.append("Cost budget not checked: at least one span has no cost.")
    return DiagnosisReport(
        engine_version=ENGINE_VERSION,
        run_id=run.run_id,
        trace_id=run.trace_id,
        application_name=run.application_name,
        run_status=run.status.value,
        task_success=run.task_success,
        rules=rule_refs,
        summary=_summary(view, found),
        diagnoses=found,
        attribution=attribution,
        timeline=build_timeline(view, attribution),
        anomalies=anomalies,
        efficiency_findings=efficiency,
        guardrails=guard.status(),
        limitations=limitations,
    )
