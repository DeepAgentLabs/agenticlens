from pydantic import BaseModel

from agenticlens.models.enums import Severity


class Recommendation(BaseModel):
    """An actionable optimization suggestion produced by a recommender rule."""

    title: str
    description: str
    severity: Severity = Severity.INFO
    tokens_saved: int = 0
    estimated_savings: float | None = None
    estimated_usd_savings: float | None = None
    estimated_monthly_savings: float | None = None
    confidence: float | None = None
    quality_risk: str | None = None
