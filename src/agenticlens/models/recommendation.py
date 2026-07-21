from pydantic import BaseModel, Field

from agenticlens.models.enums import Severity


class Recommendation(BaseModel):
    """An actionable optimization suggestion produced by a recommender rule."""

    title: str
    description: str
    severity: Severity = Severity.INFO
    tokens_saved: int = 0
    estimated_savings: float | None = None
    cost_savings: float | None = Field(
        default=None,
        description=(
            "Projected dollar savings for cost-aware recommenders (e.g. model swaps). "
            "Distinct from `estimated_savings`, which is a token-reduction percentage."
        ),
    )
