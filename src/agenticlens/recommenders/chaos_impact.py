from collections import defaultdict
from datetime import datetime
from typing import Any

from agenticlens.config.settings import RecommenderConfig
from agenticlens.models.enums import Severity
from agenticlens.models.recommendation import Recommendation
from agenticlens.models.step import Step
from agenticlens.models.trace import Evidence
from agenticlens.models.workflow import Workflow
from agenticlens.recommenders.base import BaseRecommender

_OUTCOME_SEVERITY: dict[str, Severity] = {
    "errored": Severity.CRITICAL,
    "degraded": Severity.CRITICAL,
    "delayed": Severity.WARNING,
}


def _parse_timestamp(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None


class ChaosImpactRecommender(BaseRecommender):
    """Reads `workflow.chaos_events` (see docs/workflow-schema-spec.md) and reports
    on how the workflow behaved under injected faults.

    A no-op when `chaos_events` is empty, so it is safe to run against every
    workflow regardless of whether a fault-injection tool such as agentic-chaos
    produced it. Groups events by (step, fault_type, outcome) rather than emitting
    one recommendation per event, since a single fault commonly fires on every
    retry of the same step.
    """

    def evaluate(self, workflow: Workflow, config: RecommenderConfig) -> list[Recommendation]:
        if not workflow.chaos_events:
            return []

        steps_by_id = {step.id: step for step in workflow.steps}
        steps_by_name = {step.name: step for step in workflow.steps}
        groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
        for event in workflow.chaos_events:
            fault_type = str(event.get("fault_type", "unknown_fault"))
            outcome = str(event.get("outcome", "unknown"))
            step_id = event.get("step_id")
            known_step = steps_by_id.get(str(step_id)) if step_id is not None else None
            step_name = event.get("step_name") or (
                known_step.name if known_step else "unknown step"
            )
            groups[(step_name, fault_type, outcome)].append(event)

        recommendations = []
        for (step_name, fault_type, outcome), events in groups.items():
            recommendation = self._recommendation_for(step_name, fault_type, outcome, events)
            step = self._resolve_step(events, step_name, steps_by_id, steps_by_name)
            if step is not None:
                recommendation.step_id = step.id
                recommendation.step_type = step.type.value
            else:
                # Keep the producer's correlation even when the step isn't in this workflow.
                recommendation.step_id = next(
                    (str(e["step_id"]) for e in events if e.get("step_id") is not None), None
                )
            recommendation.evidence = [
                self._evidence_for(event, recommendation.step_id) for event in events
            ]
            recommendations.append(recommendation)
        return recommendations

    @staticmethod
    def _resolve_step(
        events: list[dict[str, Any]],
        step_name: str,
        steps_by_id: dict[str, Step],
        steps_by_name: dict[str, Step],
    ) -> Step | None:
        for event in events:
            step_id = event.get("step_id")
            if step_id is not None and str(step_id) in steps_by_id:
                return steps_by_id[str(step_id)]
        return steps_by_name.get(step_name)

    @staticmethod
    def _evidence_for(event: dict[str, Any], step_id: str | None) -> Evidence:
        return Evidence(
            source="workflow.chaos_event",
            span_id=step_id,
            timestamp=_parse_timestamp(event.get("timestamp")),
            reasoning=str(event.get("message")) if event.get("message") else None,
            details={
                "chaos_event_id": event.get("id"),
                "fault_type": event.get("fault_type"),
                "outcome": event.get("outcome"),
            },
        )

    def _recommendation_for(
        self,
        step_name: str,
        fault_type: str,
        outcome: str,
        events: list[dict[str, Any]],
    ) -> Recommendation:
        count = len(events)
        occurrences = "1 time" if count == 1 else f"{count} times"
        sample_message = events[0].get("message")

        if outcome == "errored":
            description = (
                f"Injected fault '{fault_type}' hit step '{step_name}' {occurrences} and "
                f"the call raised an error each time ({sample_message}). chaos_events only "
                "records failed attempts, so whether the app ultimately recovered (e.g. via "
                "a later retry) isn't visible here -- check whether this step's final metrics "
                "reflect a successful call, or whether the workflow failed outright."
            )
        elif outcome == "degraded":
            description = (
                f"Injected fault '{fault_type}' hit step '{step_name}' {occurrences} and "
                "the call returned successfully with corrupted/degraded output — latency "
                "and token counts looked normal. Add an output-quality check downstream "
                "(schema validation, confidence scoring, or a citation check) since this "
                "class of failure is invisible to cost/latency monitoring alone."
            )
        else:
            description = (
                f"Injected fault '{fault_type}' hit step '{step_name}' {occurrences} "
                f"({sample_message})."
            )

        return Recommendation(
            title=f"Chaos impact: {fault_type} on '{step_name}'",
            description=description,
            optimization_type="resilience",
            step_name=step_name,
            severity=_OUTCOME_SEVERITY.get(outcome, Severity.INFO),
            tokens_saved=0,
            metadata={
                "fault_type": fault_type,
                "outcome": outcome,
                "occurrences": count,
            },
        )
