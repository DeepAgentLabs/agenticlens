from agenticlens.config.settings import RecommenderConfig
from agenticlens.models.enums import Severity, StepType
from agenticlens.models.recommendation import Recommendation
from agenticlens.models.workflow import Workflow
from agenticlens.recommenders.base import BaseRecommender


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
            retrieved_context_tokens = round(chunk_count * avg_tokens_per_chunk)

            recommendations.append(
                Recommendation(
                    title="Excessive retrieved chunks",
                    description=(
                        f"Step '{step.name}' retrieved {chunk_count} chunks, "
                        f"{excess} more than the configured limit of "
                        f"{config.max_chunks}."
                    ),
                    optimization_type="rag_top_k_reduction",
                    step_id=step.id,
                    step_name=step.name,
                    step_type=step.type.value,
                    severity=Severity.WARNING,
                    tokens_saved=tokens_saved,
                    metadata={
                        "chunk_count": chunk_count,
                        "recommended_max_chunks": config.max_chunks,
                        "excess_chunks": excess,
                        "avg_tokens_per_chunk": avg_tokens_per_chunk,
                        "retrieved_context_tokens": retrieved_context_tokens,
                    },
                )
            )
        return recommendations
