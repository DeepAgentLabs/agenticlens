from agenticlens.config.settings import RecommenderConfig
from agenticlens.models.enums import Severity
from agenticlens.models.recommendation import Recommendation
from agenticlens.models.workflow import Workflow
from agenticlens.recommenders.base import BaseRecommender
from agenticlens.recommenders.utils import prefix_hash


class RepeatedSystemPromptRecommender(BaseRecommender):
    """Flags steps whose prompt shares a repeated prefix with an earlier step.

    Detection: hash the first `config.system_prompt_prefix_tokens` words of each
    step's `metadata["prompt"]`. A hash seen in >=2 steps means every occurrence
    after the first is flagged.
    """

    def evaluate(self, workflow: Workflow, config: RecommenderConfig) -> list[Recommendation]:
        recommendations: list[Recommendation] = []
        seen_hashes: dict[str, str] = {}  # prefix hash -> name of first step seen

        for step in workflow.steps:
            prompt = step.metadata.get("prompt")
            if not prompt:
                continue

            words = prompt.split()
            prefix_words = words[: config.system_prompt_prefix_tokens]
            if not prefix_words:
                continue

            hash_ = prefix_hash(prompt, config.system_prompt_prefix_tokens)
            first_seen_name = seen_hashes.get(hash_)
            if first_seen_name is None:
                seen_hashes[hash_] = step.name
                continue

            ratio = len(prefix_words) / len(words)
            tokens_saved = round(ratio * step.metrics.prompt_tokens)
            recommendations.append(
                Recommendation(
                    title="Repeated system prompt",
                    description=(
                        f"Step '{step.name}' repeats the same prompt prefix as "
                        f"'{first_seen_name}'. Consider caching or deduplicating it."
                    ),
                    optimization_type="prompt_caching",
                    step_id=step.id,
                    step_name=step.name,
                    step_type=step.type.value,
                    severity=Severity.WARNING,
                    tokens_saved=tokens_saved,
                    metadata={
                        "first_seen_step": first_seen_name,
                        "repeated_prefix_tokens": len(prefix_words),
                    },
                )
            )
        return recommendations
