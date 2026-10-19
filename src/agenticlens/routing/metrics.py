"""Measured shadow comparisons; unknown cost stays unavailable."""

from agenticlens.routing.models import RoutingResult, RoutingSummary


def summarize_routing(results: list[RoutingResult]) -> RoutingSummary:
    latency: list[float] = []
    costs: list[float] = []
    shadow_successes: list[bool] = []
    primary_successes: list[bool] = []
    shadows = 0
    for result in results:
        shadow = next((a for a in result.attempts if a.role == "shadow"), None)
        primary = next((a for a in result.attempts if a.role == "primary"), None)
        if shadow is None:
            continue
        shadows += 1
        if primary is None:
            continue
        latency.append(shadow.latency_ms - primary.latency_ms)
        shadow_successes.append(shadow.status == "succeeded")
        primary_successes.append(primary.status == "succeeded")
        if primary.cost_usd is not None and shadow.cost_usd is not None:
            costs.append(shadow.cost_usd - primary.cost_usd)
    pairs = len(latency)
    return RoutingSummary(
        results=len(results),
        served=sum(r.status == "succeeded" for r in results),
        shadow_attempts=shadows,
        shadow_pairs=pairs,
        mean_shadow_latency_delta_ms=sum(latency) / pairs if pairs else None,
        mean_shadow_cost_delta_usd=sum(costs) / pairs if pairs and len(costs) == pairs else None,
        shadow_success_rate=sum(shadow_successes) / pairs if pairs else None,
        primary_success_rate=sum(primary_successes) / pairs if pairs else None,
    )
