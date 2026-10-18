"""`agenticlens modelfit ...`: recommend models per task category from experiments.

Exit codes: 1 for unusable input, 8 when `--fail-on-unfit` is set and some
category has no feasible candidate (or no evidence), or when
`--fail-on-low-confidence` is set and some recommendation is low confidence.
"""

import json
from collections.abc import Callable
from functools import partial
from pathlib import Path
from typing import TypeVar

import typer
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table

from agenticlens.experiments import load_manifest
from agenticlens.modelfit import (
    ModelFitConfig,
    ModelFitReport,
    load_experiment_evidence,
    load_modelfit_config,
    load_modelfit_report,
    recommend_models,
    resolve_taxonomy,
    save_markdown,
    save_matrix_csv,
    save_modelfit_report,
)
from agenticlens.modelfit.evidence import collect_candidates
from agenticlens.modelfit.taxonomy import case_index

modelfit_app = typer.Typer(
    help="Recommend models per task category from recorded experiment evidence.",
    no_args_is_help=True,
)
console = Console()

UNFIT_EXIT = 8

T = TypeVar("T")

_USER_ERRORS = (OSError, ValueError, KeyError, ValidationError)


def _run(action: str, operation: Callable[[], T]) -> T:
    try:
        return operation()
    except _USER_ERRORS as exc:
        message = exc.args[0] if isinstance(exc, KeyError) and exc.args else exc
        console.print(f"[red]Unable to {action}:[/red] {message}")
        raise typer.Exit(code=1) from exc


def _config(path: Path | None) -> ModelFitConfig:
    if path is None:
        return ModelFitConfig()
    return _run("load ModelFit config", lambda: load_modelfit_config(path))


def _variant_metadata(manifests: list[Path]) -> dict[str, dict[str, str]]:
    metadata: dict[str, dict[str, str]] = {}
    for path in manifests:
        manifest = _run("load experiment manifest", partial(load_manifest, path))
        for variant in manifest.variants:
            metadata[variant.id] = dict(variant.metadata)
    return metadata


def _money(value: float | None) -> str:
    return "—" if value is None else f"${value:.4f}"


def _rate(value: float | None) -> str:
    return "—" if value is None else f"{value:.1%}"


def _render(report: ModelFitReport) -> None:
    table = Table(title=f"ModelFit: {report.name} (reference {report.reference_variant_id})")
    for column in (
        "Category",
        "Recommended",
        "Confidence",
        "Pass rate",
        "Cost/success",
        "Saving/case",
        "Fallback",
    ):
        table.add_column(column)
    for result in report.categories:
        rec = result.recommendation
        top = next((c for c in result.candidates if c.variant_id == rec.variant_id), None)
        if rec.status != "recommended" or top is None:
            table.add_row(
                result.category.display_name,
                f"[red]{rec.status.replace('_', ' ')}[/red]",
                "—",
                "—",
                "—",
                "—",
                "—",
            )
            continue
        saving = "—"
        if (
            rec.savings
            and rec.savings.available
            and rec.savings.cost_per_case_savings_usd is not None
        ):
            saving = f"{rec.savings.cost_per_case_savings_usd:+.4f}"
        color = {"high": "green", "medium": "yellow", "low": "red"}.get(rec.confidence or "", "")
        table.add_row(
            result.category.display_name,
            f"{rec.variant_id} ({rec.model})",
            f"[{color}]{rec.confidence}[/{color}]" if color else str(rec.confidence),
            _rate(top.pass_rate),
            _money(top.cost_per_success_usd),
            saving,
            rec.fallback.variant_id if rec.fallback else "—",
        )
    console.print(table)
    for result in report.categories:
        risks = [risk for risk in result.recommendation.quality_risks if risk.severity == "high"]
        for risk in risks:
            console.print(
                f"  [red]{result.category.id}: {risk.kind}[/red] {risk.message}"
                + (f" ({', '.join(risk.case_ids)})" if risk.case_ids else "")
            )
    for warning in report.warnings:
        console.print(f"[yellow]Warning:[/yellow] {warning}")


def _render_matrix(report: ModelFitReport) -> None:
    variant_ids = list(dict.fromkeys(row.variant_id for row in report.matrix))
    table = Table(title="Task-level model matrix (pass rate / cost per success)")
    table.add_column("Category")
    for variant_id in variant_ids:
        table.add_column(variant_id)
    styles = {"recommended": "bold green", "fallback": "cyan", "infeasible": "dim red"}
    for result in report.categories:
        cells = {
            row.variant_id: row for row in report.matrix if row.category_id == result.category.id
        }
        values = []
        for variant_id in variant_ids:
            row = cells.get(variant_id)
            if row is None:
                values.append("—")
                continue
            text = f"{_rate(row.pass_rate)} / {_money(row.cost_per_success_usd)}"
            style = styles.get(row.role)
            values.append(f"[{style}]{text}[/{style}]" if style else text)
        table.add_row(result.category.display_name, *values)
    console.print(table)
    console.print(
        "[bold green]recommended[/bold green], [cyan]fallback[/cyan], [dim red]infeasible[/dim red]"
    )


@modelfit_app.command("recommend")
def modelfit_recommend(
    reports: list[Path] = typer.Argument(
        ..., help="Experiment report JSON files (experiment run --save)."
    ),
    config_path: Path | None = typer.Option(
        None, "--config", help="ModelFit config (YAML or JSON)."
    ),
    manifests: list[Path] = typer.Option(
        [],
        "--manifest",
        help="Experiment manifests whose variant metadata names provider/deployment.",
    ),
    save: Path | None = typer.Option(None, "--save", help="Write the ModelFit report JSON."),
    markdown: Path | None = typer.Option(None, "--markdown", help="Write a Markdown report."),
    matrix_csv: Path | None = typer.Option(
        None, "--csv", help="Write the task-level model matrix as CSV."
    ),
    json_output: bool = typer.Option(False, "--json", help="Print the report as JSON."),
    fail_on_unfit: bool = typer.Option(
        False, "--fail-on-unfit", help="Exit 8 when a category has no feasible candidate."
    ),
    fail_on_low_confidence: bool = typer.Option(
        False, "--fail-on-low-confidence", help="Exit 8 when a recommendation is low confidence."
    ),
) -> None:
    """Recommend a model for every task category under hard constraints."""
    config = _config(config_path)
    metadata = _variant_metadata(manifests)
    evidence = [
        _run("load experiment report", partial(load_experiment_evidence, path)) for path in reports
    ]
    report = _run(
        "recommend models",
        lambda: recommend_models(evidence, config, variant_metadata=metadata or None),
    )
    if save:
        save_modelfit_report(report, save)
    if markdown:
        save_markdown(report, markdown)
    if matrix_csv:
        save_matrix_csv(report, matrix_csv)
    if json_output:
        console.print_json(report.model_dump_json())
    else:
        _render(report)
        for path, label in ((save, "report"), (markdown, "Markdown"), (matrix_csv, "matrix CSV")):
            if path:
                console.print(f"Saved {label} to {path}")
    if fail_on_unfit and report.summary.unfit_category_ids:
        if not json_output:
            console.print(
                "[red]No feasible model for:[/red] " + ", ".join(report.summary.unfit_category_ids)
            )
        raise typer.Exit(code=UNFIT_EXIT)
    if fail_on_low_confidence and report.summary.low_confidence_category_ids:
        if not json_output:
            console.print(
                "[red]Low-confidence recommendations for:[/red] "
                + ", ".join(report.summary.low_confidence_category_ids)
            )
        raise typer.Exit(code=UNFIT_EXIT)


@modelfit_app.command("matrix")
def modelfit_matrix(
    report_path: Path = typer.Argument(
        ..., help="ModelFit report JSON (modelfit recommend --save)."
    ),
    matrix_csv: Path | None = typer.Option(None, "--csv", help="Write the matrix as CSV."),
    markdown: Path | None = typer.Option(None, "--markdown", help="Write the Markdown report."),
) -> None:
    """Show the task-level model matrix of a saved ModelFit report."""
    report = _run("load ModelFit report", lambda: load_modelfit_report(report_path))
    _render_matrix(report)
    if matrix_csv:
        save_matrix_csv(report, matrix_csv)
        console.print(f"Saved matrix CSV to {matrix_csv}")
    if markdown:
        save_markdown(report, markdown)
        console.print(f"Saved Markdown to {markdown}")


@modelfit_app.command("taxonomy")
def modelfit_taxonomy(
    reports: list[Path] = typer.Argument(..., help="Experiment report JSON files."),
    config_path: Path | None = typer.Option(
        None, "--config", help="ModelFit config (YAML or JSON)."
    ),
    json_output: bool = typer.Option(False, "--json", help="Print categories as JSON."),
) -> None:
    """Show which cases each task category covers, before recommending."""
    config = _config(config_path)
    evidence = [
        _run("load experiment report", partial(load_experiment_evidence, path)) for path in reports
    ]
    candidates, _ = _run("read candidates", lambda: collect_candidates(evidence, config))
    taxonomy, uncategorized, warnings = resolve_taxonomy(config, case_index(candidates))
    if json_output:
        console.print_json(
            json.dumps(
                {
                    "categories": [
                        {"id": category.id, "name": category.display_name, "case_ids": case_ids}
                        for category, case_ids in taxonomy
                    ],
                    "uncategorized_case_ids": uncategorized,
                    "warnings": warnings,
                }
            )
        )
        return
    table = Table(title="Task taxonomy")
    table.add_column("Category")
    table.add_column("Cases", justify="right")
    table.add_column("Case IDs")
    for category, case_ids in taxonomy:
        table.add_row(
            f"{category.display_name} ({category.id})", str(len(case_ids)), ", ".join(case_ids)
        )
    console.print(table)
    if uncategorized:
        console.print("Uncategorized: " + ", ".join(uncategorized))
    for warning in warnings:
        console.print(f"[yellow]Warning:[/yellow] {warning}")
