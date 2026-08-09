import csv
from pathlib import Path

from agenticlens.comparison.markdown import render_comparison_markdown
from agenticlens.comparison.models import ComparisonReport


def export_comparison_json(report: ComparisonReport, path: Path) -> None:
    path.write_text(report.model_dump_json(indent=2), encoding="utf-8")


def export_comparison_csv(report: ComparisonReport, path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["metric", "baseline", "candidate", "absolute_delta", "relative_delta"])
        rows = [
            (
                "success_rate",
                report.baseline.success_rate,
                report.candidate.success_rate,
                report.success_rate_delta,
            ),
            (
                "mean_tokens",
                report.baseline.tokens.mean,
                report.candidate.tokens.mean,
                report.mean_tokens_delta,
            ),
            (
                "mean_latency_ms",
                report.baseline.latency_ms.mean,
                report.candidate.latency_ms.mean,
                report.mean_latency_ms_delta,
            ),
        ]
        if report.baseline.cost_usd and report.candidate.cost_usd and report.mean_cost_usd_delta:
            rows.append(
                (
                    "mean_cost_usd",
                    report.baseline.cost_usd.mean,
                    report.candidate.cost_usd.mean,
                    report.mean_cost_usd_delta,
                )
            )
        for name, baseline, candidate, delta in rows:
            writer.writerow([name, baseline, candidate, delta.absolute, delta.relative])


def export_comparison_markdown(report: ComparisonReport, path: Path) -> None:
    path.write_text(render_comparison_markdown(report), encoding="utf-8")
