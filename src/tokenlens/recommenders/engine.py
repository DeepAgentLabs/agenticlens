from tokenlens.config.settings import RecommenderConfig
from tokenlens.models.recommendation import Recommendation
from tokenlens.models.workflow import Workflow
from tokenlens.recommenders.base import BaseRecommender

# MVP heuristic rules (repeated system prompt, excessive chunks, long history,
# duplicate tool calls) are specified in TokenLens_Spec.md but intentionally
# not implemented yet -- the scaffold-first plan defers optimization
# algorithms until project structure is complete.
DEFAULT_RECOMMENDERS: list[BaseRecommender] = []


class RecommendationEngine:
    """Runs registered recommenders against a workflow and aggregates savings."""

    def __init__(
        self,
        recommenders: list[BaseRecommender] | None = None,
        config: RecommenderConfig | None = None,
    ) -> None:
        self.recommenders = recommenders if recommenders is not None else DEFAULT_RECOMMENDERS
        self.config = config or RecommenderConfig()

    def run(self, workflow: Workflow) -> list[Recommendation]:
        recommendations: list[Recommendation] = []
        for recommender in self.recommenders:
            recommendations.extend(recommender.evaluate(workflow, self.config))
        return recommendations

    @staticmethod
    def estimated_savings_pct(workflow: Workflow, recommendations: list[Recommendation]) -> float:
        """Aggregate savings estimate. See 'Estimated Savings Formula' in TokenLens_Spec.md."""
        if workflow.total_tokens == 0:
            return 0.0
        total_saved = sum(r.tokens_saved for r in recommendations)
        return min(100.0, (total_saved / workflow.total_tokens) * 100)
