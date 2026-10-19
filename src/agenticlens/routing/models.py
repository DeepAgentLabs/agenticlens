"""Lens-local routing artifacts; these are not a shared AIOS contract."""

from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

from agenticlens.modelfit.models import Confidence, ModelConstraints


class RoutingModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class RoutingPolicy(RoutingModel):
    name: str = Field(default="routing", min_length=1)
    version: str = Field(default="1", min_length=1)
    mode: Literal["advisory", "enforce", "shadow", "canary"] = "advisory"
    strategy: Literal["score", "rule"] = "score"
    rules: dict[str, list[str]] = Field(default_factory=dict)
    constraints: ModelConstraints = Field(default_factory=ModelConstraints)
    minimum_confidence: Confidence = "medium"
    on_unroutable: Literal["block", "escalate"] = "escalate"
    baseline_variant_id: str | None = None
    canary_fraction: float = Field(default=0.1, ge=0, le=1)
    allocation_salt: str = "lens-routing-v1"
    max_attempts: int = Field(default=3, ge=1, le=20)

    @model_validator(mode="after")
    def check_modes(self) -> "RoutingPolicy":
        if self.mode in {"shadow", "canary"} and not self.baseline_variant_id:
            raise ValueError("shadow/canary requires baseline_variant_id")
        if any(not ids or len(ids) != len(set(ids)) for ids in self.rules.values()):
            raise ValueError("rules must contain nonempty, unique variant IDs")
        return self


class RouteRequest(RoutingModel):
    request_id: str = Field(min_length=1)
    category_id: str = Field(min_length=1)


class RouteTarget(RoutingModel):
    variant_id: str
    model: str
    provider: str | None = None
    deployment: str | None = None
    source_index: int
    weighted_score: float | None = None


class RouteDecision(RoutingModel):
    schema_version: Literal["1.0"] = "1.0"
    decision_id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    request: RouteRequest
    policy_name: str
    policy_version: str
    policy_sha256: str
    report_sha256: str
    mode: Literal["advisory", "enforce", "shadow", "canary"]
    status: Literal["selected", "blocked", "escalated"]
    confidence: Confidence | None = None
    reasons: list[str] = Field(default_factory=list)
    rejected: dict[str, list[str]] = Field(default_factory=dict)
    targets: list[RouteTarget] = Field(default_factory=list)
    shadow_target: RouteTarget | None = None
    cohort: Literal["baseline", "canary"] | None = None


class RouteOutcome(RoutingModel):
    """Caller-measured outcome. Output/prompt content never enters routing records."""

    success: bool
    cost_usd: float | None = Field(default=None, ge=0)


class RouteAttempt(RoutingModel):
    target: RouteTarget
    role: Literal["primary", "fallback", "shadow"]
    status: Literal["succeeded", "unsuccessful", "retryable_error", "error"]
    latency_ms: float = Field(ge=0)
    cost_usd: float | None = Field(default=None, ge=0)


class RoutingResult(RoutingModel):
    decision: RouteDecision
    attempts: list[RouteAttempt] = Field(default_factory=list)
    served_variant_id: str | None = None
    status: Literal["advisory", "blocked", "escalated", "succeeded", "failed"]


class RoutingSummary(RoutingModel):
    results: int
    served: int
    shadow_attempts: int
    shadow_pairs: int
    mean_shadow_latency_delta_ms: float | None = None
    mean_shadow_cost_delta_usd: float | None = None
    shadow_success_rate: float | None = None
    primary_success_rate: float | None = None
