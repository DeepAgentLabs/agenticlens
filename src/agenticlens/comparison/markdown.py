from agenticlens.comparison.models import ComparisonReport


def render_comparison_markdown(report: ComparisonReport) -> str:
    lines = [
        "# Run Comparison",
        "",
        "## Summary",
        "",
        "| Metric | Baseline | Candidate | Delta |",
        "| --- | ---: | ---: | ---: |",
        (
            f"| Success rate | {report.baseline.success_rate:.1%} "
            f"| {report.candidate.success_rate:.1%} "
            f"| {report.success_rate_delta.absolute:+.1%} |"
        ),
        (
            f"| Mean tokens | {report.baseline.tokens.mean:.1f} "
            f"| {report.candidate.tokens.mean:.1f} "
            f"| {report.mean_tokens_delta.absolute:+.1f} |"
        ),
        (
            f"| Mean latency (ms) | {report.baseline.latency_ms.mean:.1f} "
            f"| {report.candidate.latency_ms.mean:.1f} "
            f"| {report.mean_latency_ms_delta.absolute:+.1f} |"
        ),
    ]
    if report.mean_cost_usd_delta and report.baseline.cost_usd and report.candidate.cost_usd:
        lines.append(
            f"| Mean cost (USD) | {report.baseline.cost_usd.mean:.6f} "
            f"| {report.candidate.cost_usd.mean:.6f} "
            f"| {report.mean_cost_usd_delta.absolute:+.6f} |"
        )
    lines.extend(["", "## Regressions", ""])
    if report.regressions:
        lines.extend([f"- `{metric}`" for metric in report.regressions])
    else:
        lines.append("- None detected")
    if report.sample_size_guidance:
        lines.extend(["", "## Sample Size Guidance", "", report.sample_size_guidance])
    return "\n".join(lines) + "\n"
