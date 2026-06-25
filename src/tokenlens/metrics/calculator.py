from tokenlens.config.pricing import calculate_cost
from tokenlens.config.settings import TokenLensConfig
from tokenlens.models.step import Step


def apply_cost(step: Step, config: TokenLensConfig | None = None) -> None:
    """Compute and attach `step.metrics.cost` based on resolved pricing.

    No-op if the step has no provider/model set (cost stays None).
    """
    if step.provider is None or step.model is None:
        return
    overrides = config.pricing_overrides if config else None
    step.metrics.cost = calculate_cost(
        provider=step.provider,
        model=step.model,
        prompt_tokens=step.metrics.prompt_tokens,
        completion_tokens=step.metrics.completion_tokens,
        overrides=overrides,
    )
