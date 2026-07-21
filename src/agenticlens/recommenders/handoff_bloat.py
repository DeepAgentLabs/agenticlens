from agenticlens.config.settings import RecommenderConfig
from agenticlens.models.enums import Severity
from agenticlens.models.recommendation import Recommendation
from agenticlens.models.workflow import Workflow
from agenticlens.recommenders.base import BaseRecommender


class HandoffBloatRecommender(BaseRecommender):
    """Flags oversized context handoffs between agents or workflow steps.

    Reads `handoff_tokens` or `input_context_tokens` from step metadata. This keeps
    the rule deterministic and local while letting frameworks provide richer
    token attribution when available.
    """

    def evaluate(self, workflow: Workflow, config: RecommenderConfig) -> list[Recommendation]:
        recommendations: list[Recommendation] = []

        for step in workflow.steps:
            handoff_tokens = self._handoff_tokens(step.metadata)
            if handoff_tokens is None or handoff_tokens <= config.handoff_token_limit:
                continue

            tokens_saved = handoff_tokens - config.handoff_token_limit
            source = step.handoff_from or step.metadata.get("handoff_from") or "upstream context"
            target = step.agent_name or step.handoff_to or step.name
            recommendations.append(
                Recommendation(
                    title="Large agent handoff context",
                    description=(
                        f"Step '{step.name}' receives {handoff_tokens} handoff/context tokens "
                        f"from {source}, {tokens_saved} over the configured limit of "
                        f"{config.handoff_token_limit}. Consider passing a structured summary, "
                        "key facts, citations, or tool outputs instead of the full transcript."
                    ),
                    optimization_type="agent_handoff_summarization",
                    step_id=step.id,
                    step_name=step.name,
                    step_type=step.type.value,
                    severity=Severity.WARNING,
                    tokens_saved=tokens_saved,
                    metadata={
                        "agent_name": step.agent_name,
                        "handoff_from": source,
                        "handoff_to": target,
                        "handoff_tokens": handoff_tokens,
                        "recommended_handoff_token_limit": config.handoff_token_limit,
                    },
                )
            )

        return recommendations

    @staticmethod
    def _handoff_tokens(metadata: dict[str, object]) -> int | None:
        for key in ("handoff_tokens", "input_context_tokens", "handoff_context_tokens"):
            value = metadata.get(key)
            if isinstance(value, int) and not isinstance(value, bool):
                return value
        return None
