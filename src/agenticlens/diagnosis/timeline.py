"""Incident timeline reconstruction from span timestamps and statuses."""

from datetime import datetime

from agenticlens.diagnosis.models import Attribution, IncidentTimeline, TimelineEvent
from agenticlens.diagnosis.view import TraceView
from agenticlens.models.trace import Span, SpanType

DEFAULT_MAX_EVENTS = 500


def _offset(view: TraceView, moment: datetime) -> float:
    return round(max(0.0, (moment - view.run.started_at).total_seconds() * 1000), 3)


def _label(span: Span) -> str:
    return f"{span.span_type.value} '{span.name}'"


def build_timeline(
    view: TraceView,
    attribution: Attribution,
    *,
    max_events: int = DEFAULT_MAX_EVENTS,
) -> IncidentTimeline:
    """Order run, span, failure, retry, handoff, and recovery events in time.

    Successful spans contribute only a start event unless they are notable
    (retries, handoffs, recoveries), which keeps long traces readable while
    every failure stays on the timeline.
    """
    run = view.run
    root = attribution.faulty_span_id if attribution.status == "attributed" else None
    events: list[tuple[datetime, int, TimelineEvent]] = []

    def add(moment: datetime, order: int, event: TimelineEvent) -> None:
        events.append((moment, order, event))

    add(
        run.started_at,
        0,
        TimelineEvent(
            offset_ms=0.0,
            timestamp=run.started_at,
            kind="run_started",
            description=f"Run of {run.application_name} started.",
        ),
    )
    recovered: list[str] = []
    for span in view.spans:
        agent = view.agent_of(span)
        common = {"span_id": span.span_id, "span_name": span.name, "agent_name": agent}
        for record in span.attributes.get("sidecar.decisions", []):
            moment = datetime.fromisoformat(record["timestamp"].replace("Z", "+00:00"))
            decision = record["decision"]
            add(
                moment,
                2,
                TimelineEvent(
                    offset_ms=_offset(view, moment),
                    timestamp=moment,
                    kind="supervision_decision",
                    is_root_cause=False,
                    description=(
                        f"Sidecar {decision['status']} ({decision['decision_id']}): "
                        f"{decision['reason']}"
                    ),
                    **common,
                ),
            )
        is_root = span.span_id == root
        fault = view.injected_fault(span)
        if span.span_type is SpanType.RETRY:
            kind = "retry"
            text = f"Retry #{span.retry_number or 1}: {_label(span)} started."
        elif span.span_type is SpanType.DELEGATION:
            kind = "handoff"
            text = f"Handoff by {agent or 'unknown agent'}: {_label(span)}."
        elif fault:
            kind = "fault_injected"
            text = (
                f"Fault injected into {_label(span)}: {fault.get('fault_type') or 'unspecified'}."
            )
        else:
            kind = "span_started"
            text = f"{_label(span)} started."
        add(
            span.started_at,
            1,
            TimelineEvent(
                offset_ms=_offset(view, span.started_at),
                timestamp=span.started_at,
                kind=kind,  # type: ignore[arg-type]
                description=text,
                is_root_cause=is_root and kind != "span_started",
                **common,
            ),
        )
        end = span.completed_at or span.started_at
        if view.failed(span):
            error = f"{span.error_type or 'error'}" + (
                f": {span.error_message}" if span.error_message else ""
            )
            add(
                end,
                2,
                TimelineEvent(
                    offset_ms=_offset(view, end),
                    timestamp=end,
                    kind="span_failed",
                    description=f"{_label(span)} failed ({error}).",
                    is_root_cause=is_root,
                    **common,
                ),
            )
            recovery = view.recovered_by(span)
            if recovery is not None and recovery.span_id not in recovered:
                recovered.append(recovery.span_id)
                moment = recovery.completed_at or recovery.started_at
                add(
                    moment,
                    3,
                    TimelineEvent(
                        offset_ms=_offset(view, moment),
                        timestamp=moment,
                        kind="recovered",
                        description=f"{_label(recovery)} succeeded, recovering '{span.name}'.",
                        span_id=recovery.span_id,
                        span_name=recovery.name,
                        agent_name=view.agent_of(recovery),
                    ),
                )
        elif is_root:
            add(
                end,
                2,
                TimelineEvent(
                    offset_ms=_offset(view, end),
                    timestamp=end,
                    kind="span_completed",
                    description=f"{_label(span)} completed; identified as the root cause.",
                    is_root_cause=True,
                    **common,
                ),
            )
    if run.completed_at is not None:
        outcome = run.status.value + (
            "" if run.task_success is None else f", task_success={run.task_success}"
        )
        add(
            run.completed_at,
            9,
            TimelineEvent(
                offset_ms=_offset(view, run.completed_at),
                timestamp=run.completed_at,
                kind="run_completed",
                description=f"Run completed ({outcome}).",
            ),
        )

    ordered = [event for _, _, event in sorted(events, key=lambda item: (item[0], item[1]))]
    truncated = len(ordered) > max_events
    if truncated:
        keep = [e for e in ordered if e.kind != "span_started"]
        ordered = keep if len(keep) <= max_events else keep[:max_events]
    failures = [e.offset_ms for e in ordered if e.kind == "span_failed"]
    roots = [e.offset_ms for e in ordered if e.is_root_cause]
    return IncidentTimeline(
        run_id=run.run_id,
        events=ordered,
        first_failure_offset_ms=min(failures) if failures else None,
        root_cause_offset_ms=min(roots) if roots else None,
        recovered_span_ids=recovered,
        truncated=truncated,
    )
