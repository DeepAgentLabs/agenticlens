from pydantic import BaseModel, Field


class Metrics(BaseModel):
    """Token, cost, and performance metrics for a single step."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency: float = 0.0
    ttft: float | None = Field(
        default=None,
        description="Time To First Token in seconds. Only set for streaming calls.",
    )
    cost: float | None = Field(
        default=None,
        description="Total cost for the step. None when pricing is unknown for the model.",
    )

    @property
    def tps(self) -> float | None:
        """Tokens per second, or None if latency is zero."""
        if self.latency <= 0:
            return None
        return self.completion_tokens / self.latency
