"""Faulty-step and faulty-agent attribution.

Blame is assigned from diagnoses, not guessed from span names. Each
diagnosis contributes to its origin span:

    weight = taxonomy attribution_weight x diagnosis confidence
             x 0.3 if the failure was recovered
             x 1.15 for the earliest unrecovered origin (causal precedence)
             x 0.5 for unrecovered origins that start after it (likely consequences)

Contributions are summed per span and normalized into shares that sum to 1.
The top candidate is the faulty step; the attribution confidence is its share
scaled by the confidence of its strongest diagnosis, so a lone weak lead
(for example an `incomplete_task` fallback) stays low-confidence.
"""

from collections import defaultdict

from agenticlens.diagnosis.models import (
    Attribution,
    AttributionCandidate,
    AttributionStatus,
    Diagnosis,
)
from agenticlens.diagnosis.taxonomy import describe
from agenticlens.diagnosis.view import TraceView
from agenticlens.models.trace import RunStatus

RECOVERED_FACTOR = 0.3
PRECEDENCE_FACTOR = 1.15
CONSEQUENCE_FACTOR = 0.5
NO_AGENT = "(none)"


def _run_failed(view: TraceView) -> bool:
    return view.run.status is RunStatus.FAILED or view.run.task_success is False


def attribute(view: TraceView, diagnoses: list[Diagnosis]) -> Attribution:
    """Rank spans by their share of blame for the run's failure."""
    run_failed = _run_failed(view)
    anchored = [d for d in diagnoses if d.origin_span_id in view.by_id]
    if not anchored:
        if run_failed:
            return Attribution(
                status="unattributed",
                explanation=(
                    "The run failed but no diagnosis points at a recorded span; the trace "
                    "does not contain enough evidence to attribute the failure."
                ),
            )
        return Attribution(status="no_failure", explanation="No failures were diagnosed.")

    unrecovered = [d for d in anchored if not d.recovered]
    earliest = min(
        unrecovered,
        key=lambda d: view.position[d.origin_span_id or ""],
        default=None,
    )

    raw: dict[str, float] = defaultdict(float)
    best: dict[str, Diagnosis] = {}
    contributors: dict[str, list[Diagnosis]] = defaultdict(list)
    for diagnosis in anchored:
        span_id = diagnosis.origin_span_id or ""
        weight = describe(diagnosis.category).attribution_weight * diagnosis.confidence
        if diagnosis.recovered:
            weight *= RECOVERED_FACTOR
        if diagnosis is earliest:
            weight *= PRECEDENCE_FACTOR
        elif earliest is not None and not diagnosis.recovered and _after(view, diagnosis, earliest):
            weight *= CONSEQUENCE_FACTOR
        raw[span_id] += weight
        contributors[span_id].append(diagnosis)
        current = best.get(span_id)
        if current is None or _strength(diagnosis) > _strength(current):
            best[span_id] = diagnosis

    total = sum(raw.values()) or 1.0
    ranked = sorted(raw, key=lambda span_id: (-raw[span_id], view.position[span_id]))
    candidates: list[AttributionCandidate] = []
    agent_scores: dict[str, float] = defaultdict(float)
    for span_id in ranked:
        span = view.by_id[span_id]
        share = raw[span_id] / total
        agent = view.agent_of(span)
        agent_scores[agent or NO_AGENT] += share
        found = contributors[span_id]
        candidates.append(
            AttributionCandidate(
                span_id=span_id,
                span_name=span.name,
                span_type=span.span_type.value,
                agent_name=agent,
                score=round(share, 6),
                categories=list(dict.fromkeys(d.category for d in found)),
                diagnosis_ids=[d.diagnosis_id for d in found],
                reasons=[
                    f"{d.category.value} ({d.confidence:.2f} confidence"
                    + (", recovered" if d.recovered else "")
                    + ")"
                    for d in found
                ],
            )
        )

    top = candidates[0]
    lead = best[top.span_id]
    confidence = round(top.score * lead.confidence, 6)
    status: AttributionStatus = "attributed" if unrecovered or run_failed else "recovered"
    if status == "recovered":
        explanation = (
            f"All diagnosed failures were recovered; '{top.span_name}' was the most "
            f"significant ({lead.category.value})."
        )
    else:
        runner_up = (
            f" Next candidate: '{candidates[1].span_name}' ({candidates[1].score:.0%})."
            if len(candidates) > 1
            else ""
        )
        agent = f" in agent '{top.agent_name}'" if top.agent_name else ""
        explanation = (
            f"Most likely faulty step: '{top.span_name}'{agent} — {lead.category.value}, "
            f"{top.score:.0%} of attributed blame.{runner_up}"
        )
    return Attribution(
        status=status,
        faulty_span_id=top.span_id,
        faulty_step=top.span_name,
        faulty_agent=top.agent_name,
        category=lead.category,
        confidence=min(1.0, confidence),
        explanation=explanation,
        candidates=candidates,
        agent_scores={name: round(score, 6) for name, score in agent_scores.items()},
    )


def _after(view: TraceView, diagnosis: Diagnosis, earliest: Diagnosis) -> bool:
    return (
        view.position[diagnosis.origin_span_id or ""] > view.position[earliest.origin_span_id or ""]
    )


def _strength(diagnosis: Diagnosis) -> float:
    weight = describe(diagnosis.category).attribution_weight * diagnosis.confidence
    return weight * (RECOVERED_FACTOR if diagnosis.recovered else 1.0)
