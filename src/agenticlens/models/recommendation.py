from typing import Any

from pydantic import BaseModel, Field

from agenticlens.models.enums import Severity


class Recommendation(BaseModel):
    """An actionable optimization suggestion produced by a recommender rule."""

    title: str
    description: str
    optimization_type: str = Field(
        default="token_optimization",
        description="Machine-readable optimization category, e.g. rag_chunk_pruning.",
    )
    step_id: str | None = None
    step_name: str | None = None
    step_type: str | None = None
    severity: Severity = Severity.INFO
    tokens_saved: int = 0
    estimated_savings: float | None = None
    estimated_usd_savings: float | None = None
    estimated_monthly_savings: float | None = None
    confidence: float | None = None
    quality_risk: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    cost_savings: float | None = Field(
        default=None,
        description=(
            "Projected dollar savings for cost-aware recommenders (e.g. model swaps). "
            "Distinct from `estimated_savings`, which is a token-reduction percentage."
        ),
    )
