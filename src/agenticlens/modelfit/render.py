"""Markdown and CSV renderings of a ModelFit report."""

import csv
import io
from pathlib import Path

from agenticlens.modelfit.models import ModelFitReport

MATRIX_COLUMNS = [
    "category_id",
    "variant_id",
    "model",
    "provider",
    "role",
    "feasible",
    "attempts",
    "pass_rate",
    "cost_per_success_usd",
    "mean_latency_ms",
    "weighted_score",
    "violations",
]


def _number(value: float | None, digits: int = 6) -> str:
    return "" if value is None else f"{value:.{digits}g}"


def render_matrix_csv(report: ModelFitReport) -> str:
    """The task-level model matrix: one row per category x candidate."""
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(MATRIX_COLUMNS)
    for row in report.matrix:
        writer.writerow(
            [
                row.category_id,
                row.variant_id,
                row.model,
                row.provider or "",
                row.role,
                "true" if row.feasible else "false",
                row.attempts,
                _number(row.pass_rate),
                _number(row.cost_per_success_usd),
                _number(row.mean_latency_ms),
                _number(row.weighted_score),
                ";".join(row.violations),
            ]
        )
    return buffer.getvalue()


def save_matrix_csv(report: ModelFitReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_matrix_csv(report), encoding="utf-8")


def _cell(value: float | None, kind: str) -> str:
    if value is None:
        return "—"
    if kind == "rate":
        return f"{value:.0%}"
    if kind == "money":
        return f"${value:.4f}"
    if kind == "ms":
        return f"{value:.0f} ms"
    return f"{value:.3f}"


def render_markdown(report: ModelFitReport) -> str:
    lines = [f"# ModelFit: {report.name}", ""]
    lines.append(
        f"{report.summary.recommended} of {report.summary.categories} task categories have a "
        f"recommendation from {report.summary.candidates} candidates. Savings and quality "
        f"risks are measured against `{report.reference_variant_id}`."
    )
    lines.append("")
    lines.append("## Evidence")
    lines.append("")
    for source in report.sources:
        digest = f", sha256 `{source.sha256[:12]}`" if source.sha256 else ""
        file = f" (`{source.file}`{digest})" if source.file else ""
        lines.append(
            f"- Experiment `{source.experiment_name}` {source.experiment_version} on suite "
            f"`{source.suite_name}` {source.suite_version}, {source.trial_count} trials per "
            f"variant{file}"
        )
    lines.append("")

    lines.append("## Recommendations")
    lines.append("")
    lines.append(
        "| Category | Model | Confidence | Pass rate | Cost/success | Saving/case | Fallback |"
    )
    lines.append("|---|---|---|---|---|---|---|")
    for result in report.categories:
        rec = result.recommendation
        top = next((c for c in result.candidates if c.variant_id == rec.variant_id), None)
        if rec.status != "recommended" or top is None:
            status = rec.status.replace("_", " ")
            lines.append(f"| {result.category.display_name} | **{status}** | — | — | — | — | — |")
            continue
        saving = "—"
        if (
            rec.savings
            and rec.savings.available
            and rec.savings.cost_per_case_savings_usd is not None
        ):
            saving = f"{rec.savings.cost_per_case_savings_usd:+.4f}"
        fallback = rec.fallback.variant_id if rec.fallback else "—"
        lines.append(
            f"| {result.category.display_name} | `{rec.variant_id}` ({rec.model}) | "
            f"{rec.confidence} | {_cell(top.pass_rate, 'rate')} | "
            f"{_cell(top.cost_per_success_usd, 'money')} | {saving} | {fallback} |"
        )
    lines.append("")

    variant_ids = list(dict.fromkeys(row.variant_id for row in report.matrix))
    lines.append("## Task-level model matrix")
    lines.append("")
    lines.append("Pass rate / cost per success; ✅ recommended, ↪ fallback, ✖ infeasible.")
    lines.append("")
    lines.append("| Category | " + " | ".join(f"`{v}`" for v in variant_ids) + " |")
    lines.append("|---|" + "---|" * len(variant_ids))
    for result in report.categories:
        cells = {
            row.variant_id: row for row in report.matrix if row.category_id == result.category.id
        }
        rendered = []
        for variant_id in variant_ids:
            row = cells.get(variant_id)
            if row is None:
                rendered.append("—")
                continue
            marker = {"recommended": "✅ ", "fallback": "↪ ", "infeasible": "✖ "}.get(row.role, "")
            rate = _cell(row.pass_rate, "rate")
            rendered.append(f"{marker}{rate} / {_cell(row.cost_per_success_usd, 'money')}")
        lines.append(f"| {result.category.display_name} | " + " | ".join(rendered) + " |")
    lines.append("")

    for result in report.categories:
        rec = result.recommendation
        lines.append(f"## {result.category.display_name} (`{result.category.id}`)")
        lines.append("")
        lines.append(
            f"{len(result.case_ids)} cases: {', '.join(f'`{c}`' for c in result.case_ids)}"
        )
        lines.append("")
        for line in rec.explanation:
            lines.append(f"- {line}")
        if rec.confidence:
            lines.append("")
            lines.append(f"Confidence **{rec.confidence}**: " + " ".join(rec.confidence_reasons))
        if rec.quality_risks:
            lines.append("")
            lines.append("Quality risks:")
            lines.append("")
            for risk in rec.quality_risks:
                cases = f" ({', '.join(risk.case_ids)})" if risk.case_ids else ""
                lines.append(f"- **{risk.severity}** {risk.kind}: {risk.message}{cases}")
        if rec.fallback:
            lines.append("")
            lines.append(f"Fallback `{rec.fallback.variant_id}`: {rec.fallback.reason}")
        lines.append("")
        lines.append(
            "Pareto frontier: "
            + (", ".join(f"`{v}`" for v in result.pareto_frontier_variant_ids) or "none")
            + ". Cost per success, cheapest first: "
            + (", ".join(f"`{v}`" for v in result.cost_per_success_ranking) or "none")
            + "."
        )
        lines.append("")

    if report.uncategorized_case_ids:
        lines.append(
            "Uncategorized cases: " + ", ".join(f"`{c}`" for c in report.uncategorized_case_ids)
        )
        lines.append("")
    if report.warnings:
        lines.append("## Warnings")
        lines.append("")
        lines.extend(f"- {warning}" for warning in report.warnings)
        lines.append("")
    return "\n".join(lines)


def save_markdown(report: ModelFitReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown(report), encoding="utf-8")
