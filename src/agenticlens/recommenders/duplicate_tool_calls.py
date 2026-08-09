import json

from agenticlens.config.settings import RecommenderConfig
from agenticlens.models.enums import Severity, StepType
from agenticlens.models.recommendation import Recommendation
from agenticlens.models.workflow import Workflow
from agenticlens.recommenders.base import BaseRecommender


class DuplicateToolCallsRecommender(BaseRecommender):
    """Flags tool-call steps that repeat an earlier call's (tool_name, arguments).

    Reads `metadata["tool_name"]` and `metadata["tool_args"]` on `TOOL_CALL` steps.
    """

    def evaluate(self, workflow: Workflow, config: RecommenderConfig) -> list[Recommendation]:
        recommendations: list[Recommendation] = []
        seen_signatures: dict[tuple[str, str], str] = {}  # signature -> first step name

        for step in workflow.steps:
            if step.type != StepType.TOOL_CALL:
                continue

            tool_name = step.metadata.get("tool_name")
            if tool_name is None:
                continue

            tool_args = step.metadata.get("tool_args", {})
            signature = (tool_name, json.dumps(tool_args, sort_keys=True, default=str))

            first_seen_name = seen_signatures.get(signature)
            if first_seen_name is None:
                seen_signatures[signature] = step.name
                continue

            tokens_saved = step.metrics.prompt_tokens + step.metrics.completion_tokens
            recommendations.append(
                Recommendation(
                    title="Duplicate tool call",
                    description=(
                        f"Step '{step.name}' calls tool '{tool_name}' with the same "
                        f"arguments as '{first_seen_name}'. Consider caching the result."
                    ),
                    optimization_type="tool_result_caching",
                    step_id=step.id,
                    step_name=step.name,
                    step_type=step.type.value,
                    severity=Severity.WARNING,
                    tokens_saved=tokens_saved,
                    metadata={
                        "tool_name": tool_name,
                        "first_seen_step": first_seen_name,
                    },
                )
            )
        return recommendations
