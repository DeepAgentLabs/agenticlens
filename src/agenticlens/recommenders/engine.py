from agenticlens.config.settings import RecommenderConfig
from agenticlens.models.enums import Severity
from agenticlens.models.recommendation import Recommendation
from agenticlens.models.workflow import Workflow
from agenticlens.recommenders.base import BaseRecommender
from agenticlens.recommenders.chaos_impact import ChaosImpactRecommender
from agenticlens.recommenders.duplicate_tool_calls import DuplicateToolCallsRecommender
from agenticlens.recommenders.excessive_chunks import ExcessiveChunksRecommender
from agenticlens.recommenders.handoff_bloat import HandoffBloatRecommender
from agenticlens.recommenders.long_history import LongHistoryRecommender
from agenticlens.recommenders.rag_chunk_utility import RAGChunkUtilityRecommender
from agenticlens.recommenders.model_swap import ModelSwapRecommender
from agenticlens.recommenders.repeated_prompt import RepeatedSystemPromptRecommender

DEFAULT_RECOMMENDERS: list[BaseRecommender] = [
    RepeatedSystemPromptRecommender(),
    ExcessiveChunksRecommender(),
    RAGChunkUtilityRecommender(),
    LongHistoryRecommender(),
    DuplicateToolCallsRecommender(),
    HandoffBloatRecommender(),
    ChaosImpactRecommender(),
    ModelSwapRecommender(),
]


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
        return self._with_budget_impact(workflow, recommendations)

    @staticmethod
    def estimated_savings_pct(workflow: Workflow, recommendations: list[Recommendation]) -> float:
        """Aggregate savings estimate. See 'Estimated Savings Formula' in AgenticLens_Spec.md."""
        if workflow.total_tokens == 0:
            return 0.0
        total_saved = sum(r.tokens_saved for r in recommendations)
        return min(100.0, (total_saved / workflow.total_tokens) * 100)

    def _with_budget_impact(
        self,
        workflow: Workflow,
        recommendations: list[Recommendation],
    ) -> list[Recommendation]:
        if not recommendations:
            return []

        total_tokens = workflow.total_tokens
        total_cost = workflow.total_cost
        blended_cost_per_token = (
            total_cost / total_tokens if total_cost is not None and total_tokens > 0 else None
        )

        enriched: list[Recommendation] = []
        for rec in recommendations:
            savings_pct = (
                min(100.0, (rec.tokens_saved / total_tokens) * 100) if total_tokens else 0.0
            )
            usd_savings = (
                rec.tokens_saved * blended_cost_per_token
                if blended_cost_per_token is not None
                else None
            )

            rec.estimated_savings = savings_pct
            rec.estimated_usd_savings = usd_savings
            rec.estimated_monthly_savings = (
                usd_savings * self.config.monthly_runs if usd_savings is not None else None
            )
            # Recommenders with no token savings (e.g. ChaosImpactRecommender) aren't
            # graded by budget impact -- keep the severity they assigned themselves.
            if rec.tokens_saved > 0:
                rec.severity = self._severity_for(savings_pct, usd_savings)
            enriched.append(rec)

        return sorted(
            enriched,
            key=lambda rec: (
                rec.estimated_usd_savings or 0.0,
                rec.estimated_savings or 0.0,
                rec.tokens_saved,
            ),
            reverse=True,
        )

    def _severity_for(self, savings_pct: float, usd_savings: float | None) -> Severity:
        if savings_pct >= self.config.critical_savings_pct or (
            usd_savings is not None and usd_savings >= self.config.critical_savings_usd
        ):
            return Severity.CRITICAL
        if savings_pct >= self.config.warning_savings_pct or (
            usd_savings is not None and usd_savings >= self.config.warning_savings_usd
        ):
            return Severity.WARNING
        return Severity.INFO

    @staticmethod
    def estimated_cost_savings(recommendations: list[Recommendation]) -> float | None:
        """Aggregate dollar savings from cost-aware recommendations (e.g. model swaps)."""
        savings = [r.cost_savings for r in recommendations if r.cost_savings is not None]
        return sum(savings) if savings else None
