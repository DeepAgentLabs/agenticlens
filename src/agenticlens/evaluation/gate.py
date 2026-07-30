from pydantic import BaseModel, Field

from agenticlens.evaluation.models import EvaluationReport


class GateConfig(BaseModel):
    min_pass_rate: float = Field(default=1.0, ge=0, le=1)
    min_average_score: float = Field(default=1.0, ge=0, le=1)
    max_failed_cases: int = Field(default=0, ge=0)
    max_average_latency_ms: float | None = Field(default=None, gt=0)
    max_total_cost_usd: float | None = Field(default=None, ge=0)


class GateDecision(BaseModel):
    passed: bool
    reasons: list[str]
    observed: dict[str, float | int | None]


def evaluate_gate(report: EvaluationReport, config: GateConfig) -> GateDecision:
    summary = report.summary
    reasons: list[str] = []
    if summary.pass_rate < config.min_pass_rate:
        reasons.append(f"Pass rate {summary.pass_rate:.1%} is below {config.min_pass_rate:.1%}.")
    if summary.average_score < config.min_average_score:
        reasons.append(
            f"Average score {summary.average_score:.3f} is below {config.min_average_score:.3f}."
        )
    if summary.failed_cases > config.max_failed_cases:
        reasons.append(f"Failed cases {summary.failed_cases} exceed {config.max_failed_cases}.")
    if (
        config.max_average_latency_ms is not None
        and summary.average_latency_ms > config.max_average_latency_ms
    ):
        reasons.append(
            f"Average latency {summary.average_latency_ms:.1f} ms exceeds "
            f"{config.max_average_latency_ms:.1f} ms."
        )
    if config.max_total_cost_usd is not None:
        if summary.total_cost_usd is None:
            reasons.append("Total cost is unavailable.")
        elif summary.total_cost_usd > config.max_total_cost_usd:
            reasons.append(
                f"Total cost ${summary.total_cost_usd:.6f} exceeds "
                f"${config.max_total_cost_usd:.6f}."
            )
    return GateDecision(
        passed=not reasons,
        reasons=reasons,
        observed={
            "pass_rate": summary.pass_rate,
            "average_score": summary.average_score,
            "failed_cases": summary.failed_cases,
            "average_latency_ms": summary.average_latency_ms,
            "total_cost_usd": summary.total_cost_usd,
        },
    )
