from tokenlens.config.settings import RecommenderConfig
from tokenlens.models.enums import Severity
from tokenlens.models.recommendation import Recommendation
from tokenlens.models.workflow import Workflow
from tokenlens.recommenders.base import BaseRecommender


class LongHistoryRecommender(BaseRecommender):
    """Flags steps whose conversation history exceeds `config.history_token_limit`.

    Reads `metadata["history_tokens"]` -- the portion of `prompt_tokens`
    attributable to conversation history/memory content.
    """

    def evaluate(self, workflow: Workflow, config: RecommenderConfig) -> list[Recommendation]:
        recommendations: list[Recommendation] = []

        for step in workflow.steps:
            history_tokens = step.metadata.get("history_tokens")
            if history_tokens is None or history_tokens <= config.history_token_limit:
                continue

            tokens_saved = history_tokens - config.history_token_limit
            recommendations.append(
                Recommendation(
                    title="Long conversation history",
                    description=(
                        f"Step '{step.name}' carries {history_tokens} history tokens, "
                        f"{tokens_saved} over the configured limit of "
                        f"{config.history_token_limit}. Consider summarizing or "
                        f"truncating older turns."
                    ),
                    severity=Severity.WARNING,
                    tokens_saved=tokens_saved,
                )
            )
        return recommendations
