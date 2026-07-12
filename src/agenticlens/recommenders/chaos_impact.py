from collections import defaultdict
from typing import Any

from agenticlens.config.settings import RecommenderConfig
from agenticlens.models.enums import Severity
from agenticlens.models.recommendation import Recommendation
from agenticlens.models.workflow import Workflow
from agenticlens.recommenders.base import BaseRecommender

_OUTCOME_SEVERITY: dict[str, Severity] = {
    "errored": Severity.CRITICAL,
    "degraded": Severity.CRITICAL,
    "delayed": Severity.WARNING,
}


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

        step_names = {step.id: step.name for step in workflow.steps}
        groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
        for event in workflow.chaos_events:
            fault_type = str(event.get("fault_type", "unknown_fault"))
            outcome = str(event.get("outcome", "unknown"))
            step_id = event.get("step_id")
            step_name = event.get("step_name") or step_names.get(str(step_id), "unknown step")
            groups[(step_name, fault_type, outcome)].append(event)

        recommendations = []
        for (step_name, fault_type, outcome), events in groups.items():
            recommendations.append(self._recommendation_for(step_name, fault_type, outcome, events))
        return recommendations

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
            severity=_OUTCOME_SEVERITY.get(outcome, Severity.INFO),
            tokens_saved=0,
        )
