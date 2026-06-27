from pydantic import BaseModel

from agenticlens.models.enums import Severity


class Recommendation(BaseModel):
    """An actionable optimization suggestion produced by a recommender rule."""

    title: str
    description: str
    severity: Severity = Severity.INFO
    tokens_saved: int = 0
    estimated_savings: float | None = None
