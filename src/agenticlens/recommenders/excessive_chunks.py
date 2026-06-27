from tokenlens.config.settings import RecommenderConfig
from tokenlens.models.enums import Severity, StepType
from tokenlens.models.recommendation import Recommendation
from tokenlens.models.workflow import Workflow
from tokenlens.recommenders.base import BaseRecommender


class ExcessiveChunksRecommender(BaseRecommender):
    """Flags retriever steps that return more than `config.max_chunks` chunks.

    Reads `metadata["chunk_count"]` and `metadata["avg_tokens_per_chunk"]` on
    `RETRIEVER` steps.
    """

    def evaluate(self, workflow: Workflow, config: RecommenderConfig) -> list[Recommendation]:
        recommendations: list[Recommendation] = []

        for step in workflow.steps:
            if step.type != StepType.RETRIEVER:
                continue

            chunk_count = step.metadata.get("chunk_count")
            if chunk_count is None or chunk_count <= config.max_chunks:
                continue

            avg_tokens_per_chunk = step.metadata.get("avg_tokens_per_chunk", 0)
            excess = chunk_count - config.max_chunks
            tokens_saved = round(excess * avg_tokens_per_chunk)

            recommendations.append(
                Recommendation(
                    title="Excessive retrieved chunks",
                    description=(
                        f"Step '{step.name}' retrieved {chunk_count} chunks, "
                        f"{excess} more than the configured limit of "
                        f"{config.max_chunks}."
                    ),
                    severity=Severity.WARNING,
                    tokens_saved=tokens_saved,
                )
            )
        return recommendations
