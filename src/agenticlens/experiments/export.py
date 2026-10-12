"""CSV exports for experiment reports.

- variant summary: one row per variant with quality, cost, latency,
  reliability, consistency, and pass@k / pass^k columns, plus baseline deltas.
- case matrix: one row per (variant, case) — the data behind the heatmap.
"""

import csv
import io
from pathlib import Path

from agenticlens.experiments.models import ExperimentReport


def _fmt(value: float | int | None) -> str:
    return "" if value is None else str(value)


def render_variant_csv(report: ExperimentReport) -> str:
    comparisons = {c.candidate_variant_id: c for c in report.comparisons}
    k_columns = [f"{name}{k}" for k in report.pass_k for name in ("pass_at_", "pass_hat_")]
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(
        [
            "variant_id",
            "variant_name",
            "target_kind",
            "factors",
            "is_baseline",
            "pareto_optimal",
            "attempted_trials",
            "completed_trials",
            "trial_success_rate",
            "case_pass_rate",
            "case_pass_rate_lower",
            "case_pass_rate_upper",
            "mean_score",
            "mean_latency_ms",
            "mean_cost_usd",
            "priced_trials",
            "consistency_rate",
            "flaky_case_ids",
            *k_columns,
            "case_pass_rate_delta",
            "case_pass_rate_p_value",
            "statistically_significant",
            "changed_factors",
        ]
    )
    for variant in report.variants:
        summary = variant.summary
        interval = summary.case_pass_rate_interval
        comparison = comparisons.get(variant.variant_id)
        writer.writerow(
            [
                variant.variant_id,
                variant.variant_name,
                variant.target_kind,
                ";".join(f"{k}={v}" for k, v in variant.factors.items()),
                variant.variant_id == report.baseline_variant_id,
                variant.pareto_optimal,
                summary.attempted_trials,
                summary.completed_trials,
                summary.trial_success_rate,
                _fmt(summary.case_pass_rate),
                _fmt(interval.lower if interval else None),
                _fmt(interval.upper if interval else None),
                _fmt(summary.average_score.mean if summary.average_score else None),
                _fmt(summary.average_latency_ms.mean if summary.average_latency_ms else None),
                _fmt(summary.total_cost_usd.mean if summary.total_cost_usd else None),
                summary.priced_trials,
                _fmt(summary.consistency_rate),
                ";".join(summary.flaky_case_ids),
                *[
                    _fmt(getattr(summary, field).get(str(k)))
                    for k in report.pass_k
                    for field in ("pass_at_k", "pass_hat_k")
                ],
                _fmt(comparison.case_pass_rate_delta if comparison else None),
                _fmt(comparison.case_pass_rate_p_value if comparison else None),
                _fmt(comparison.statistically_significant if comparison else None),
                ";".join(
                    f"{name}={values[0]}->{values[1]}"
                    for name, values in (comparison.changed_factors.items() if comparison else [])
                ),
            ]
        )
    return buffer.getvalue()


def render_case_matrix_csv(report: ExperimentReport) -> str:
    k_columns = [f"{name}{k}" for k in report.pass_k for name in ("pass_at_", "pass_hat_")]
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(
        [
            "variant_id",
            "case_id",
            "case_name",
            "attempts",
            "passes",
            "pass_rate",
            "mean_score",
            "score_standard_deviation",
            "consistent",
            *k_columns,
        ]
    )
    for variant in report.variants:
        for case in variant.cases:
            writer.writerow(
                [
                    variant.variant_id,
                    case.case_id,
                    case.case_name,
                    case.attempts,
                    case.passes,
                    case.pass_rate,
                    _fmt(case.mean_score),
                    _fmt(case.score_standard_deviation),
                    case.consistent,
                    *[
                        _fmt(getattr(case, field).get(str(k)))
                        for k in report.pass_k
                        for field in ("pass_at_k", "pass_hat_k")
                    ],
                ]
            )
    return buffer.getvalue()


def save_variant_csv(report: ExperimentReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_variant_csv(report), encoding="utf-8")


def save_case_matrix_csv(report: ExperimentReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_case_matrix_csv(report), encoding="utf-8")
