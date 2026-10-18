"""Category metrics, hard constraints, weighted scoring, and Pareto analysis."""

import math
import statistics

from agenticlens.evaluation import ConfidenceInterval
from agenticlens.experiments import wilson_interval
from agenticlens.modelfit.evidence import CandidateEvidence
from agenticlens.modelfit.models import (
    CandidateMetrics,
    ModelConstraints,
    ScoringWeights,
    Violation,
)


def percentile(values: list[float], fraction: float) -> float:
    """Linear-interpolated percentile (the same convention as numpy's default)."""
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def measure(
    candidate: CandidateEvidence,
    case_ids: list[str],
    safety_case_ids: list[str],
    confidence_level: float,
) -> CandidateMetrics:
    """Measure one candidate on one category's cases. Feasibility is set later."""
    own_case_ids = [case_id for case_id in case_ids if case_id in candidate.cases]
    attempts = [
        attempt for case_id in own_case_ids for attempt in candidate.cases[case_id].attempts
    ]
    completed = [attempt for attempt in attempts if attempt.completed]
    passes = sum(attempt.passed for attempt in attempts)
    pass_rate = passes / len(attempts) if attempts else None
    interval = None
    if attempts:
        lower, upper = wilson_interval(passes, len(attempts), confidence_level)
        interval = ConfidenceInterval(
            lower=lower, upper=upper, confidence_level=confidence_level, method="wilson"
        )
    # Like cost, latency is only stated when every completed attempt reported it,
    # so a latency limit is never verified from a partial sample.
    latency_values = [attempt.latency_ms for attempt in completed]
    latencies = (
        [value for value in latency_values if value is not None]
        if completed and all(value is not None for value in latency_values)
        else []
    )
    costs = [attempt.cost_usd for attempt in completed]
    cost_complete = bool(completed) and all(cost is not None for cost in costs)
    total_cost = sum(cost for cost in costs if cost is not None) if cost_complete else None

    flaky: list[str] = []
    consistent = 0
    measured_cases = 0
    for case_id in own_case_ids:
        outcomes = {attempt.passed for attempt in candidate.cases[case_id].attempts}
        if not outcomes:
            continue
        measured_cases += 1
        if len(outcomes) == 1:
            consistent += 1
        else:
            flaky.append(case_id)

    safety_attempts = 0
    safety_passes = 0
    failed_safety: list[str] = []
    for case_id in safety_case_ids:
        case = candidate.cases.get(case_id)
        if case is None:
            continue
        safety_attempts += len(case.attempts)
        case_passes = sum(attempt.passed for attempt in case.attempts)
        safety_passes += case_passes
        if case_passes < len(case.attempts):
            failed_safety.append(case_id)

    variant = candidate.variant
    return CandidateMetrics(
        variant_id=variant.variant_id,
        variant_name=variant.variant_name,
        model=candidate.model,
        provider=candidate.provider,
        deployment=candidate.deployment,
        capabilities=candidate.capabilities,
        factors=variant.factors,
        source_index=candidate.source_index,
        case_ids=own_case_ids,
        attempts=len(attempts),
        passes=passes,
        pass_rate=pass_rate,
        pass_rate_interval=interval,
        failed_trial_attempts=len(attempts) - len(completed),
        mean_latency_ms=statistics.fmean(latencies) if latencies else None,
        p95_latency_ms=percentile(latencies, 0.95) if latencies else None,
        cost_complete=cost_complete,
        total_cost_usd=total_cost,
        cost_per_case_usd=total_cost / len(completed) if total_cost is not None else None,
        cost_per_success_usd=total_cost / passes if total_cost is not None and passes else None,
        consistency_rate=consistent / measured_cases if measured_cases else None,
        flaky_case_ids=flaky,
        safety_attempts=safety_attempts,
        safety_pass_rate=safety_passes / safety_attempts if safety_attempts else None,
        failed_safety_case_ids=failed_safety,
    )


def _upper_limit(
    name: str, limit: float | None, observed: float | None, label: str, unit: str
) -> Violation | None:
    if limit is None:
        return None
    if observed is None:
        return Violation(
            constraint=name,
            limit=limit,
            message=f"{label} is unavailable, so the {unit}{limit:g} limit cannot be verified.",
        )
    if observed > limit:
        return Violation(
            constraint=name,
            limit=limit,
            observed=observed,
            message=f"{label} {unit}{observed:.6g} exceeds the {unit}{limit:g} limit.",
        )
    return None


def _lower_limit(
    name: str, limit: float | None, observed: float | None, label: str
) -> Violation | None:
    if limit is None:
        return None
    if observed is None:
        return Violation(
            constraint=name,
            limit=limit,
            message=f"{label} is unavailable, so the {limit:.0%} minimum cannot be verified.",
        )
    if observed < limit:
        return Violation(
            constraint=name,
            limit=limit,
            observed=observed,
            message=f"{label} {observed:.1%} is below the {limit:.0%} minimum.",
        )
    return None


def check_constraints(metrics: CandidateMetrics, constraints: ModelConstraints) -> list[Violation]:
    """Every hard constraint the candidate fails, including unverifiable ones."""
    lower_bound = metrics.pass_rate_interval.lower if metrics.pass_rate_interval else None
    checks = [
        _lower_limit("min_pass_rate", constraints.min_pass_rate, metrics.pass_rate, "Pass rate"),
        _lower_limit(
            "min_pass_rate_lower_bound",
            constraints.min_pass_rate_lower_bound,
            lower_bound,
            "Pass-rate interval lower bound",
        ),
        _upper_limit(
            "max_cost_per_case_usd",
            constraints.max_cost_per_case_usd,
            metrics.cost_per_case_usd,
            "Cost per case",
            "$",
        ),
        _upper_limit(
            "max_cost_per_success_usd",
            constraints.max_cost_per_success_usd,
            metrics.cost_per_success_usd,
            "Cost per success",
            "$",
        ),
        _upper_limit(
            "max_mean_latency_ms",
            constraints.max_mean_latency_ms,
            metrics.mean_latency_ms,
            "Mean latency (ms)",
            "",
        ),
        _upper_limit(
            "max_p95_latency_ms",
            constraints.max_p95_latency_ms,
            metrics.p95_latency_ms,
            "p95 latency (ms)",
            "",
        ),
        _lower_limit(
            "min_consistency", constraints.min_consistency, metrics.consistency_rate, "Consistency"
        ),
        _lower_limit(
            "min_safety_pass_rate",
            constraints.min_safety_pass_rate,
            metrics.safety_pass_rate,
            "Safety pass rate",
        ),
    ]
    violations = [violation for violation in checks if violation is not None]

    if constraints.allowed_providers is not None and (
        metrics.provider is None or metrics.provider not in constraints.allowed_providers
    ):
        violations.append(
            Violation(
                constraint="allowed_providers",
                limit=constraints.allowed_providers,
                observed=metrics.provider,
                message=(
                    f"Provider {metrics.provider!r} is not in the allowed list."
                    if metrics.provider
                    else "Provider is unknown, so the provider allow-list cannot be verified."
                ),
            )
        )
    if metrics.provider is not None and metrics.provider in constraints.blocked_providers:
        violations.append(
            Violation(
                constraint="blocked_providers",
                limit=constraints.blocked_providers,
                observed=metrics.provider,
                message=f"Provider {metrics.provider!r} is blocked.",
            )
        )
    if constraints.allowed_deployments is not None and (
        metrics.deployment is None or metrics.deployment not in constraints.allowed_deployments
    ):
        violations.append(
            Violation(
                constraint="allowed_deployments",
                limit=constraints.allowed_deployments,
                observed=metrics.deployment,
                message=(
                    f"Deployment {metrics.deployment!r} is not in the allowed list."
                    if metrics.deployment
                    else "Deployment is unknown, so the deployment allow-list cannot be verified."
                ),
            )
        )
    missing = [cap for cap in constraints.required_capabilities if cap not in metrics.capabilities]
    if missing:
        violations.append(
            Violation(
                constraint="required_capabilities",
                limit=constraints.required_capabilities,
                observed=metrics.capabilities,
                message=f"Missing required capabilities: {', '.join(missing)}.",
            )
        )
    if metrics.attempts == 0:
        violations.append(
            Violation(constraint="evidence", observed=0, message="No attempts on these cases.")
        )
    return violations


def _ratio_to_best(value: float | None, best: float | None) -> float:
    """Best value divided by this value; 1.0 for the best, 0.0 when unknown."""
    if value is None or best is None:
        return 0.0
    if value == 0:
        return 1.0
    return best / value


def score(candidates: list[CandidateMetrics], weights: ScoringWeights) -> None:
    """Set component and weighted scores on feasible candidates, in place."""
    feasible = [candidate for candidate in candidates if candidate.feasible]
    costs = [c.cost_per_success_usd for c in feasible if c.cost_per_success_usd is not None]
    latencies = [c.mean_latency_ms for c in feasible if c.mean_latency_ms is not None]
    best_cost = min(costs) if costs else None
    best_latency = min(latencies) if latencies else None
    total = sum(weights.as_dict().values())
    for candidate in feasible:
        components = {
            "quality": candidate.pass_rate or 0.0,
            "cost": _ratio_to_best(candidate.cost_per_success_usd, best_cost),
            "latency": _ratio_to_best(candidate.mean_latency_ms, best_latency),
            "reliability": candidate.consistency_rate or 0.0,
        }
        candidate.component_scores = {name: round(value, 6) for name, value in components.items()}
        candidate.weighted_score = round(
            sum(weights.as_dict()[name] * value for name, value in components.items()) / total, 6
        )


def sort_key(candidate: CandidateMetrics) -> tuple[int, float, float, float, str]:
    """Feasible first; then score, pass rate, and cost per success; then variant ID."""
    return (
        0 if candidate.feasible else 1,
        -(candidate.weighted_score or 0.0),
        -(candidate.pass_rate or 0.0),
        candidate.cost_per_success_usd if candidate.cost_per_success_usd is not None else math.inf,
        candidate.variant_id,
    )


def pareto_frontier(candidates: list[CandidateMetrics]) -> list[str]:
    """Candidates no other candidate beats on pass rate, cost per success, and latency.

    Unknown cost or latency counts as worst. Candidates without attempts are
    excluded. The frontier spans all candidates, feasible or not, so it shows
    the trade-offs the constraints rule out.
    """
    measured = [candidate for candidate in candidates if candidate.pass_rate is not None]

    def objectives(candidate: CandidateMetrics) -> tuple[float, float, float]:
        cost = candidate.cost_per_success_usd
        latency = candidate.mean_latency_ms
        return (
            -(candidate.pass_rate or 0.0),
            cost if cost is not None else math.inf,
            latency if latency is not None else math.inf,
        )

    frontier: list[str] = []
    for candidate in measured:
        mine = objectives(candidate)
        dominated = False
        for other in measured:
            if other is candidate:
                continue
            theirs = objectives(other)
            if all(t <= m for t, m in zip(theirs, mine, strict=True)) and any(
                t < m for t, m in zip(theirs, mine, strict=True)
            ):
                dominated = True
                break
        if not dominated:
            frontier.append(candidate.variant_id)
    return frontier


def cost_per_success_ranking(candidates: list[CandidateMetrics]) -> list[str]:
    ranked = sorted(
        (c for c in candidates if c.cost_per_success_usd is not None),
        key=lambda c: (c.cost_per_success_usd, -(c.pass_rate or 0.0), c.variant_id),
    )
    return [candidate.variant_id for candidate in ranked]
