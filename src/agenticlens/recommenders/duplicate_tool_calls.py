import json

from tokenlens.config.settings import RecommenderConfig
from tokenlens.models.enums import Severity, StepType
from tokenlens.models.recommendation import Recommendation
from tokenlens.models.workflow import Workflow
from tokenlens.recommenders.base import BaseRecommender


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
                    severity=Severity.WARNING,
                    tokens_saved=tokens_saved,
                )
            )
        return recommendations
