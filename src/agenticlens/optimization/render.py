"""Markdown views of optimization reports and outcome evaluations."""

from agenticlens.optimization.models import (
    DecisionStatus,
    MetricChange,
    OptimizationReport,
    OutcomeEvaluation,
    ProjectedBenefit,
)


def _usd(value: float | None) -> str:
    return "unavailable" if value is None else f"${value:.6f}"


def _benefit(benefit: ProjectedBenefit) -> str:
    text = (
        f"{benefit.tokens_per_run:,.0f} tokens, {_usd(benefit.cost_usd_per_run)}, "
        f"{benefit.latency_ms_per_run:,.0f} ms per run"
    )
    if benefit.monthly_cost_usd is not None:
        text += f"; {_usd(benefit.monthly_cost_usd)} per month"
    return text


def render_optimization_markdown(
    report: OptimizationReport, statuses: dict[str, DecisionStatus] | None = None
) -> str:
    statuses = statuses or {}
    lines = [
        "# Optimization opportunities",
        "",
        f"{len(report.runs)} runs, {report.total_tokens:,} tokens, "
        f"total cost {_usd(report.total_cost_usd)}. Benefits are projections; "
        "risks are listed separately and never netted against them.",
        "",
        "| # | Opportunity | Area | Projected benefit per run | Confidence | Risks | Status |",
        "|---|---|---|---|---|---|---|",
    ]
    for index, item in enumerate(report.opportunities, start=1):
        risks = ", ".join(f"{r.kind} ({r.severity})" for r in item.risks) or "none"
        lines.append(
            f"| {index} | {item.title} | {item.area} | {_benefit(item.benefit)} | "
            f"{item.confidence} | {risks} | {statuses.get(item.opportunity_id, 'proposed')} |"
        )
    for item in report.opportunities:
        lines += [
            "",
            f"## {item.title}",
            "",
            f"- ID: `{item.opportunity_id}` (rule `{item.rule_id}` v{item.rule_version})",
            f"- Finding: {item.summary}",
            f"- Action: {item.action}",
            f"- Projected benefit: {_benefit(item.benefit)}",
            f"- Basis: {item.benefit.basis}",
            f"- Confidence: {item.confidence} — {' '.join(item.confidence_reasons)}",
            f"- Evidence: {item.runs_affected} of {item.runs_observed} runs, "
            f"{sum(len(e.span_ids) for e in item.evidence)} spans",
        ]
        lines += [f"- Risk ({r.severity}, {r.kind}): {r.description}" for r in item.risks]
    if report.tradeoffs.variants:
        lines += [
            "",
            "## Quality-cost trade-offs",
            "",
            f"Baseline: `{report.tradeoffs.baseline_variant_id}`",
            "",
            "| Variant | Runs | Success | Interval | Mean cost | Cost/success | Δ success "
            "| Δ cost | Pareto |",
            "|---|---|---|---|---|---|---|---|---|",
        ]
        for v in report.tradeoffs.variants:
            low, high = v.success_interval
            delta = "—" if v.success_rate_delta is None else f"{v.success_rate_delta:+.0%}"
            lines.append(
                f"| {v.variant_id} | {v.runs} | {v.success_rate:.0%} | {low:.0%}–{high:.0%} | "
                f"{_usd(v.mean_cost_usd)} | {_usd(v.cost_per_success_usd)} | {delta} | "
                f"{'—' if v.cost_delta_usd is None else _usd(v.cost_delta_usd)} | "
                f"{'yes' if v.pareto_optimal else 'no'} |"
            )
    return "\n".join(lines) + "\n"


def _row(name: str, change: MetricChange, fmt: str) -> str:
    def value(number: float | None) -> str:
        return "unavailable" if number is None else format(number, fmt)

    return f"| {name} | {value(change.before)} | {value(change.after)} | {value(change.delta)} |"


def render_outcome_markdown(outcome: OutcomeEvaluation) -> str:
    observed = outcome.observed
    ratio = (
        "unavailable"
        if outcome.realized_ratio is None
        else f"{outcome.realized_ratio:.0%} of projected {outcome.realized_basis}"
    )
    lines = [
        f"# Outcome of `{outcome.opportunity_id}`: {outcome.status}",
        "",
        f"Projected (from the report): {_benefit(outcome.projected)}.",
        f"Observed: {observed.before_runs} runs before, {observed.after_runs} after; "
        f"realized {ratio}.",
        "",
        "| Metric per run | Before | After | Change |",
        "|---|---|---|---|",
        _row("Tokens", observed.tokens_per_run, ",.0f"),
        _row("Cost (USD)", observed.cost_usd_per_run, ".6f"),
        _row("Latency (ms)", observed.latency_ms_per_run, ",.0f"),
        _row("Success rate", observed.success_rate, ".2%"),
        "",
        f"Still detected after adoption: {'yes' if observed.still_detected else 'no'}.",
    ]
    lines += [f"- {reason}" for reason in outcome.reasons]
    return "\n".join(lines) + "\n"
