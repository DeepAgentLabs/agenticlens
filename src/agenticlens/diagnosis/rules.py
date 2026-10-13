"""Deterministic diagnosis rules.

Each rule reads a `TraceView` and returns `Diagnosis` objects whose evidence
points at recorded spans. Rules never call models and never guess: when the
trace lacks the data a rule needs (for example no captured tool inputs), the
rule either lowers its confidence and says why, or stays silent.

Rules leave `diagnosis_id` empty; the engine numbers diagnoses in a fixed
order so reports are reproducible.
"""

from collections import defaultdict
from collections.abc import Sequence
from typing import Any, Protocol

from pydantic import BaseModel, Field

from agenticlens.analysis.handoffs import count_round_trips
from agenticlens.diagnosis.models import Diagnosis
from agenticlens.diagnosis.taxonomy import FailureCategory, Severity, describe
from agenticlens.diagnosis.view import TraceView
from agenticlens.models.trace import Evidence, RunStatus, Span, SpanType


class DiagnosisConfig(BaseModel):
    """Thresholds for the default rules. Budgets are off unless set."""

    loop_threshold: int = Field(
        default=3, ge=2, description="Identical consecutive tool calls that count as a loop."
    )
    handoff_round_trips: int = Field(
        default=2, ge=1, description="A->B->A round trips that count as a handoff loop."
    )
    stagnation_threshold: int = Field(
        default=3,
        ge=2,
        description="Identical consecutive model outputs that count as no progress.",
    )
    max_cost_usd: float | None = Field(default=None, ge=0)
    max_total_tokens: int | None = Field(default=None, gt=0)
    max_latency_ms: float | None = Field(default=None, gt=0)


class DiagnosisRule(Protocol):
    rule_id: str
    version: str

    def diagnose(self, view: TraceView, config: DiagnosisConfig) -> list[Diagnosis]: ...


def _diagnosis(
    rule: DiagnosisRule,
    category: FailureCategory,
    *,
    title: str,
    summary: str,
    confidence: float,
    spans: Sequence[Span],
    view: TraceView,
    evidence: list[Evidence],
    recovered: bool = False,
    severity: Severity | None = None,
) -> Diagnosis:
    origin = spans[0] if spans else None
    level: Severity = severity or ("low" if recovered else describe(category).default_severity)
    return Diagnosis(
        diagnosis_id="",
        category=category,
        title=title,
        summary=summary,
        severity=level,
        confidence=confidence,
        rule_id=rule.rule_id,
        rule_version=rule.version,
        origin_span_id=origin.span_id if origin else None,
        span_ids=list(dict.fromkeys(span.span_id for span in spans)),
        agent_name=view.agent_of(origin) if origin else None,
        recovered=recovered,
        evidence=evidence,
    )


_TYPE_CATEGORIES = {
    SpanType.TOOL_CALL: FailureCategory.TOOL_ERROR,
    SpanType.MODEL_CALL: FailureCategory.MODEL_ERROR,
    SpanType.PLANNING: FailureCategory.MODEL_ERROR,
    SpanType.FINAL_RESPONSE: FailureCategory.MODEL_ERROR,
    SpanType.RETRIEVAL: FailureCategory.RETRIEVAL_ERROR,
    SpanType.VALIDATION: FailureCategory.VALIDATION_FAILURE,
    SpanType.DELEGATION: FailureCategory.DELEGATION_FAILURE,
}


def failure_category(view: TraceView, span: Span) -> FailureCategory:
    """Classify one failed span."""
    if view.injected_fault(span):
        return FailureCategory.INJECTED_FAULT
    if view.timed_out(span):
        return FailureCategory.TIMEOUT
    if span.span_type in _TYPE_CATEGORIES:
        return _TYPE_CATEGORIES[span.span_type]
    if span.model_name and not span.tool_name:
        return FailureCategory.MODEL_ERROR
    return FailureCategory.TOOL_ERROR


def _failed_below(view: TraceView, span: Span) -> bool:
    """True when a descendant failed, ignoring retry subtrees (re-attempts, not causes)."""
    stack = list(view.children.get(span.span_id, []))
    while stack:
        child = stack.pop()
        if child.span_type is SpanType.RETRY:
            continue
        if view.failed(child):
            return True
        stack.extend(view.children.get(child.span_id, []))
    return False


class FailedSpanRule:
    """Failed spans, grouped so one repeated failure is one diagnosis.

    A failed span whose own children also failed only propagated the error,
    so diagnoses start at *origin* failures (failed spans with no failed
    descendant other than its own retries). Retry spans are left to
    `RetryExhaustionRule`. Identical
    origins (same span type, name, tool, and error type) merge into one
    diagnosis listing every occurrence.
    """

    rule_id = "failed_span"
    version = "1.0"

    def diagnose(self, view: TraceView, config: DiagnosisConfig) -> list[Diagnosis]:
        origins = [
            span
            for span in view.spans
            if view.failed(span)
            and span.span_type is not SpanType.RETRY
            and not _failed_below(view, span)
        ]
        groups: dict[tuple[str, str, str, str], list[Span]] = defaultdict(list)
        for span in origins:
            groups[(*view.operation_key(span), span.error_type or "")].append(span)

        diagnoses: list[Diagnosis] = []
        for spans in groups.values():
            first = spans[0]
            category = failure_category(view, first)
            recovery = view.recovered_by(spans[-1])
            propagated = [ancestor for ancestor in view.ancestors(first) if view.failed(ancestor)]
            fault = view.injected_fault(first)
            error = first.error_type or "an error"
            repeat = f" ({len(spans)} occurrences)" if len(spans) > 1 else ""
            summary = f"{first.span_type.value} span '{first.name}' failed with {error}{repeat}" + (
                f": {first.error_message.rstrip('.')}." if first.error_message else "."
            )
            if fault:
                summary += f" Injected fault: {fault.get('fault_type') or 'unspecified'}."
            if propagated:
                summary += (
                    " The failure propagated to "
                    + ", ".join(f"'{span.name}'" for span in propagated)
                    + "."
                )
            if recovery is not None:
                summary += f" Recovered by span '{recovery.name}'."
            evidence = [
                view.evidence(
                    span,
                    reasoning="Span status is failed and none of its children failed first.",
                    injected_fault=view.injected_fault(span),
                    latency_ms=span.latency_ms,
                )
                for span in spans
            ] + [
                view.evidence(
                    span,
                    source="trace.propagation",
                    reasoning="Ancestor failed after its child failed.",
                )
                for span in propagated
            ]
            if recovery is not None:
                evidence.append(
                    view.evidence(
                        recovery,
                        source="trace.recovery",
                        reasoning="A later attempt of the same operation succeeded.",
                    )
                )
            diagnoses.append(
                _diagnosis(
                    self,
                    category,
                    title=f"{describe(category).description.rstrip('.')}: {first.name}",
                    summary=summary,
                    confidence=1.0
                    if fault
                    else (0.9 if category is FailureCategory.TIMEOUT else 0.95),
                    spans=[*spans, *propagated],
                    view=view,
                    evidence=evidence,
                    recovered=recovery is not None,
                )
            )
        return diagnoses


class InjectedFaultRule:
    """Injected faults on spans that did not fail themselves.

    A fault such as added latency or a corrupted payload can let its own span
    succeed while breaking something downstream. These spans carry the
    agentic-chaos markers (`chaos.injected`, `chaos.fault_type`); failed
    injected spans are already covered by `FailedSpanRule`. The fault counts
    as recovered when the run neither failed nor reported task failure.
    """

    rule_id = "injected_fault"
    version = "1.0"

    def diagnose(self, view: TraceView, config: DiagnosisConfig) -> list[Diagnosis]:
        run = view.run
        absorbed = run.status is not RunStatus.FAILED and run.task_success is not False
        diagnoses: list[Diagnosis] = []
        for span in view.spans:
            fault = view.injected_fault(span)
            if fault is None or view.failed(span):
                continue
            kind = fault.get("fault_type") or "unspecified"
            outcome = (
                "the run still completed its task"
                if absorbed
                else "the run later failed, so the fault was not absorbed"
            )
            diagnoses.append(
                _diagnosis(
                    self,
                    FailureCategory.INJECTED_FAULT,
                    title=f"Injected fault {kind} on {span.name}",
                    summary=f"Fault '{kind}' was injected into '{span.name}'; {outcome}.",
                    confidence=1.0,
                    spans=[span],
                    view=view,
                    evidence=[
                        view.evidence(
                            span,
                            source="trace.chaos",
                            reasoning="Span carries agentic-chaos fault-injection markers.",
                            injected_fault=fault,
                        )
                    ],
                    recovered=absorbed,
                )
            )
        return diagnoses


class RetryExhaustionRule:
    """Retries that never succeeded, attributed to the failure they retried."""

    rule_id = "retry_exhaustion"
    version = "1.0"

    def diagnose(self, view: TraceView, config: DiagnosisConfig) -> list[Diagnosis]:
        groups: dict[str | None, list[Span]] = defaultdict(list)
        for retry_id, trigger_id in view.retry_triggers.items():
            groups[trigger_id].append(view.by_id[retry_id])

        diagnoses: list[Diagnosis] = []
        for trigger_id, retries in groups.items():
            succeeded = any(
                view.succeeded(span)
                or any(view.succeeded(d) for d in view.descendants(span.span_id))
                for span in retries
            )
            if succeeded:
                continue
            trigger = view.by_id.get(trigger_id or "")
            spans = ([trigger] if trigger else []) + retries
            target = f"'{trigger.name}'" if trigger else "an unidentified operation"
            evidence = [
                view.evidence(
                    span,
                    source="trace.retry",
                    reasoning="Retry span and its children did not succeed.",
                    retry_number=span.retry_number,
                    triggering_failure_span_id=trigger_id,
                )
                for span in retries
            ]
            if trigger:
                evidence.insert(
                    0,
                    view.evidence(trigger, reasoning="Original failure the retries targeted."),
                )
            diagnoses.append(
                _diagnosis(
                    self,
                    FailureCategory.RETRY_EXHAUSTED,
                    title=f"Retries exhausted for {target}",
                    summary=(
                        f"{len(retries)} retr{'y' if len(retries) == 1 else 'ies'} of "
                        f"{target} did not succeed."
                    ),
                    confidence=0.9 if trigger else 0.6,
                    spans=spans,
                    view=view,
                    evidence=evidence,
                )
            )
        return diagnoses


def _runs(items: list[tuple[Any, Span]], minimum: int) -> list[list[Span]]:
    """Maximal runs of consecutive items with the same key, at least `minimum` long."""
    found: list[list[Span]] = []
    current: list[Span] = []
    current_key: Any = object()
    for key, span in [*items, (object(), None)]:  # sentinel flushes the last run
        if key == current_key and span is not None:
            current.append(span)
            continue
        if len(current) >= minimum:
            found.append(current)
        current = [span] if span is not None else []
        current_key = key
    return found


class ToolLoopRule:
    """The same tool called with the same input several times in a row, per agent."""

    rule_id = "tool_loop"
    version = "1.0"

    def diagnose(self, view: TraceView, config: DiagnosisConfig) -> list[Diagnosis]:
        per_agent: dict[str | None, list[Span]] = defaultdict(list)
        for span in view.spans:
            if span.span_type is SpanType.TOOL_CALL:
                per_agent[view.agent_of(span)].append(span)
        diagnoses: list[Diagnosis] = []
        for calls in per_agent.values():
            keyed = [
                ((span.tool_name or span.name, view.input_fingerprint(span)), span)
                for span in calls
            ]
            for loop in _runs(keyed, config.loop_threshold):
                inputs_known = view.input_fingerprint(loop[0]) is not None
                tool = loop[0].tool_name or loop[0].name
                basis = (
                    "identical captured input" if inputs_known else "no captured input to compare"
                )
                diagnoses.append(
                    _diagnosis(
                        self,
                        FailureCategory.TOOL_LOOP,
                        title=f"Tool loop: {tool} called {len(loop)} times in a row",
                        summary=(
                            f"'{tool}' ran {len(loop)} consecutive times ({basis}); "
                            f"threshold {config.loop_threshold}."
                        ),
                        confidence=0.9 if inputs_known else 0.6,
                        spans=loop,
                        view=view,
                        evidence=[
                            view.evidence(
                                span,
                                source="trace.loop",
                                reasoning=f"Call {index + 1} of {len(loop)}.",
                                input_fingerprint=view.input_fingerprint(span),
                            )
                            for index, span in enumerate(loop)
                        ],
                    )
                )
        return diagnoses


_HANDOFF_TARGET_KEYS = ("to_agent", "target_agent", "handoff.to", "handoff_to")


class HandoffLoopRule:
    """Two agents handing control back and forth (A->B, B->A, ...)."""

    rule_id = "handoff_loop"
    version = "1.0"

    @staticmethod
    def _target(view: TraceView, span: Span, source: str | None) -> str | None:
        for key in _HANDOFF_TARGET_KEYS:
            value = span.attributes.get(key)
            if isinstance(value, str) and value:
                return value
        for child in view.children.get(span.span_id, []):
            if child.agent_name and child.agent_name != source:
                return child.agent_name
        return None

    def diagnose(self, view: TraceView, config: DiagnosisConfig) -> list[Diagnosis]:
        pairs: dict[frozenset[str], list[tuple[str, str, Span]]] = defaultdict(list)
        for span in view.spans:
            if span.span_type is not SpanType.DELEGATION:
                continue
            source = span.attributes.get("from_agent") or view.agent_of(span)
            target = self._target(view, span, source)
            if not isinstance(source, str) or not target or source == target:
                continue
            pairs[frozenset((source, target))].append((source, target, span))

        diagnoses: list[Diagnosis] = []
        for transitions in pairs.values():
            round_trips = count_round_trips([(s, t) for s, t, _ in transitions])
            if round_trips < config.handoff_round_trips:
                continue
            first_source, first_target, _ = transitions[0]
            spans = [span for _, _, span in transitions]
            diagnoses.append(
                _diagnosis(
                    self,
                    FailureCategory.HANDOFF_LOOP,
                    title=f"Handoff loop between {first_source} and {first_target}",
                    summary=(
                        f"{first_source} and {first_target} exchanged control "
                        f"{len(transitions)} times ({round_trips} round trips); "
                        f"threshold {config.handoff_round_trips}."
                    ),
                    confidence=0.85,
                    spans=spans,
                    view=view,
                    evidence=[
                        view.evidence(
                            span,
                            source="trace.handoff",
                            reasoning=f"Handoff {source} -> {target}.",
                            from_agent=source,
                            to_agent=target,
                        )
                        for source, target, span in transitions
                    ],
                )
            )
        return diagnoses


class StagnationRule:
    """Consecutive model calls by one agent that returned the same output."""

    rule_id = "stagnation"
    version = "1.0"

    def diagnose(self, view: TraceView, config: DiagnosisConfig) -> list[Diagnosis]:
        per_agent: dict[str | None, list[tuple[Any, Span]]] = defaultdict(list)
        for span in view.spans:
            if span.span_type not in (SpanType.MODEL_CALL, SpanType.PLANNING):
                continue
            output = view.output_fingerprint(span)
            # Spans without captured output get a unique key so they never match.
            per_agent[view.agent_of(span)].append((output or object(), span))
        diagnoses: list[Diagnosis] = []
        for calls in per_agent.values():
            for stalled in _runs(calls, config.stagnation_threshold):
                agent = view.agent_of(stalled[0]) or "the workflow"
                diagnoses.append(
                    _diagnosis(
                        self,
                        FailureCategory.STAGNATION,
                        title=f"No progress: {agent} repeated the same output",
                        summary=(
                            f"{len(stalled)} consecutive model calls by {agent} returned "
                            f"identical output; threshold {config.stagnation_threshold}."
                        ),
                        confidence=0.8,
                        spans=stalled,
                        view=view,
                        evidence=[
                            view.evidence(
                                span,
                                source="trace.output",
                                reasoning="Output matches the previous call's output.",
                                output_fingerprint=view.output_fingerprint(span),
                            )
                            for span in stalled
                        ],
                    )
                )
        return diagnoses


_RESULT_COUNT_KEYS = (
    "result_count",
    "results_count",
    "num_results",
    "retrieved_count",
    "documents_returned",
    "chunks_retrieved",
    "retrieval.result_count",
)
_DOCUMENT_KEYS = ("documents", "retrieval.documents", "chunks")


def retrieval_result_count(span: Span) -> int | None:
    """Documents a retrieval span returned, when the span records it."""
    for key in _RESULT_COUNT_KEYS:
        value = span.attributes.get(key)
        if isinstance(value, int) and not isinstance(value, bool):
            return value
    for key in _DOCUMENT_KEYS:
        value = span.attributes.get(key)
        if isinstance(value, list):
            return len(value)
    if isinstance(span.output_data, list):
        return len(span.output_data)
    return None


class EmptyRetrievalRule:
    """Retrieval spans that completed but returned nothing."""

    rule_id = "empty_retrieval"
    version = "1.0"

    def diagnose(self, view: TraceView, config: DiagnosisConfig) -> list[Diagnosis]:
        diagnoses: list[Diagnosis] = []
        for span in view.spans:
            if span.span_type is not SpanType.RETRIEVAL or view.failed(span):
                continue
            if retrieval_result_count(span) != 0:
                continue
            diagnoses.append(
                _diagnosis(
                    self,
                    FailureCategory.EMPTY_RETRIEVAL,
                    title=f"Retrieval returned no documents: {span.name}",
                    summary=(
                        f"Retrieval span '{span.name}' returned 0 results; later answers may "
                        "not be grounded in retrieved context."
                    ),
                    confidence=0.9,
                    spans=[span],
                    view=view,
                    evidence=[
                        view.evidence(
                            span,
                            source="trace.retrieval",
                            reasoning="Recorded result count is zero.",
                            result_count=0,
                        )
                    ],
                )
            )
        return diagnoses


class BudgetRule:
    """Run totals above the configured cost, token, or latency budget."""

    rule_id = "budget"
    version = "1.0"

    def diagnose(self, view: TraceView, config: DiagnosisConfig) -> list[Diagnosis]:
        run = view.run
        checks: list[tuple[str, float | None, float | None, Any]] = [
            ("cost_usd", run.estimated_cost_usd, config.max_cost_usd, _span_cost),
            (
                "total_tokens",
                float(run.total_tokens),
                _optional_float(config.max_total_tokens),
                _span_tokens,
            ),
            ("latency_ms", run.total_latency_ms, config.max_latency_ms, _span_latency),
        ]
        diagnoses: list[Diagnosis] = []
        for metric, observed, limit, measure in checks:
            if limit is None or observed is None or observed <= limit:
                continue
            top = sorted(view.spans, key=measure, reverse=True)[:3]
            diagnoses.append(
                _diagnosis(
                    self,
                    FailureCategory.BUDGET_EXCEEDED,
                    title=f"Run exceeded its {metric} budget",
                    summary=(
                        f"Run {metric} {observed:g} exceeded the budget of {limit:g}; the "
                        "largest contributors are listed as supporting spans."
                    ),
                    confidence=1.0,
                    spans=top,
                    view=view,
                    evidence=[
                        Evidence(
                            source="trace.metrics",
                            reasoning=f"Run {metric} compared with the configured budget.",
                            details={"metric": metric, "observed": observed, "budget": limit},
                        ),
                        *(
                            view.evidence(
                                span,
                                source="trace.contributor",
                                reasoning=f"Top {metric} contributor.",
                                value=measure(span),
                            )
                            for span in top
                        ),
                    ],
                )
            )
        return diagnoses


def _optional_float(value: int | None) -> float | None:
    return None if value is None else float(value)


def _span_cost(span: Span) -> float:
    return span.estimated_cost_usd or 0.0


def _span_tokens(span: Span) -> float:
    return float(span.total_tokens)


def _span_latency(span: Span) -> float:
    return span.latency_ms


class IncompleteTaskRule:
    """A failed run or task that no other rule explains.

    The engine runs this rule last and only when every other diagnosis is
    recovered (or there is none), so it never competes with a specific cause.
    """

    rule_id = "incomplete_task"
    version = "1.0"

    def diagnose(self, view: TraceView, config: DiagnosisConfig) -> list[Diagnosis]:
        run = view.run
        if run.task_success is not False and run.status is not RunStatus.FAILED:
            return []
        final = [s for s in view.spans if s.span_type is SpanType.FINAL_RESPONSE]
        anchor = final[-1] if final else (view.spans[-1] if view.spans else None)
        reason = "task_success is false" if run.task_success is False else "run status is failed"
        return [
            _diagnosis(
                self,
                FailureCategory.INCOMPLETE_TASK,
                title="Task not completed and no failing span explains it",
                summary=(
                    f"The run's {reason}, but no span failed in a way the rules can attribute. "
                    + (
                        f"The last answer came from '{anchor.name}'."
                        if anchor is not None
                        else "The run recorded no spans."
                    )
                ),
                confidence=0.4 if anchor is not None else 0.2,
                spans=[anchor] if anchor is not None else [],
                view=view,
                evidence=[
                    Evidence(
                        source="trace.run",
                        confidence=1.0,
                        reasoning=f"Run outcome: {reason}.",
                        details={"status": run.status.value, "task_success": run.task_success},
                    ),
                    *(
                        [
                            view.evidence(
                                anchor,
                                confidence=0.4,
                                reasoning="Last answer-producing span; a weak lead only.",
                            )
                        ]
                        if anchor is not None
                        else []
                    ),
                ],
            )
        ]


DEFAULT_RULES: tuple[DiagnosisRule, ...] = (
    FailedSpanRule(),
    InjectedFaultRule(),
    RetryExhaustionRule(),
    ToolLoopRule(),
    HandoffLoopRule(),
    StagnationRule(),
    EmptyRetrievalRule(),
    BudgetRule(),
)

#: Runs after `DEFAULT_RULES` only when nothing unrecovered was found.
FALLBACK_RULE: DiagnosisRule = IncompleteTaskRule()
