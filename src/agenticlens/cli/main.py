import runpy
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from agenticlens.cli.render import (
    render_agent_summary,
    render_recommendations,
    render_steps,
    render_summary,
    render_token_optimization,
)
from agenticlens.comparison import (
    compare_runs,
    export_comparison_csv,
    export_comparison_json,
    load_runs,
)
from agenticlens.exporters import CSVExporter, JSONExporter
from agenticlens.models.trace import Run
from agenticlens.models.workflow import Workflow
from agenticlens.profiler.context import completed_workflows
from agenticlens.recommenders import RecommendationEngine
from agenticlens.reports import render_trace

app = typer.Typer(
    name="agenticlens",
    help="Profile, analyze, and optimize token consumption in LLM-powered applications.",
    no_args_is_help=True,
)
console = Console()


def _load_workflow(path: Path) -> Workflow:
    if not path.exists():
        console.print(f"[red]File not found:[/red] {path}")
        raise typer.Exit(code=1)
    return Workflow.model_validate_json(path.read_text())


def _load_run(path: Path) -> Run:
    if not path.exists():
        console.print(f"[red]File not found:[/red] {path}")
        raise typer.Exit(code=1)
    try:
        return Run.model_validate_json(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        console.print(f"[red]Invalid trace:[/red] {exc}")
        raise typer.Exit(code=1) from exc


@app.command()
def profile(
    script: Path = typer.Argument(..., help="Path to a Python script to profile."),
    save: Path | None = typer.Option(
        None, "--save", help="Export the profiled workflow to this file after running."
    ),
    export_format: str = typer.Option(
        "json", "--format", help="Export format for --save: 'json' or 'csv'."
    ),
) -> None:
    """Run a script that uses `agenticlens.profile()` / `agenticlens.step()` and report it."""
    if not script.exists():
        console.print(f"[red]Script not found:[/red] {script}")
        raise typer.Exit(code=1)

    before = len(completed_workflows)
    runpy.run_path(str(script), run_name="__main__")
    new_workflows = completed_workflows[before:]

    if not new_workflows:
        console.print(
            "[yellow]No workflow was profiled.[/yellow] "
            "Did the script call `agenticlens.profile()`?"
        )
        raise typer.Exit(code=1)

    workflow = new_workflows[-1]
    render_summary(console, workflow)
    render_agent_summary(console, workflow)
    render_steps(console, workflow)

    if save is not None:
        if export_format == "csv":
            CSVExporter().export(workflow, save)
        elif export_format == "json":
            JSONExporter().export(workflow, save)
        else:
            console.print(f"[red]Unknown export format:[/red] {export_format}")
            raise typer.Exit(code=1)
        console.print(f"\nSaved workflow to {save}")


@app.command()
def report(
    report_file: Path = typer.Argument(..., help="Path to a saved workflow report (JSON)."),
) -> None:
    """Display a saved workflow report."""
    workflow = _load_workflow(report_file)
    render_summary(console, workflow)
    render_agent_summary(console, workflow)
    render_steps(console, workflow)


@app.command()
def analyze(
    workflow_file: Path = typer.Argument(..., help="Path to a saved workflow (JSON)."),
) -> None:
    """Run the recommendation engine against a saved workflow."""
    workflow = _load_workflow(workflow_file)
    engine = RecommendationEngine()
    recommendations = engine.run(workflow)
    savings_pct = RecommendationEngine.estimated_savings_pct(workflow, recommendations)
    render_agent_summary(console, workflow)
    if any(step.agent_name for step in workflow.steps):
        console.print()
    render_token_optimization(console, workflow, recommendations)
    console.print()
    cost_savings = RecommendationEngine.estimated_cost_savings(recommendations)
    render_recommendations(console, recommendations, savings_pct, workflow, cost_savings)


@app.command("inspect")
def inspect_run(
    run_file: Path = typer.Argument(..., help="Path to a saved AgenticLens trace (JSON)."),
) -> None:
    """Inspect a validated run trace, span tree, and raw metric distributions."""
    render_trace(console, _load_run(run_file))


@app.command()
def compare(
    baseline: Path = typer.Argument(..., help="Baseline trace JSON file or directory."),
    candidate: Path = typer.Argument(..., help="Candidate trace JSON file or directory."),
    threshold: float = typer.Option(
        0.05,
        "--regression-threshold",
        min=0.0,
        help="Relative degradation that counts as a regression.",
    ),
    save: Path | None = typer.Option(None, "--save", help="Save the comparison report."),
    export_format: str = typer.Option("json", "--format", help="'json' or 'csv'."),
    fail_on_regression: bool = typer.Option(
        False,
        "--fail-on-regression",
        help="Return a non-zero exit status when regressions are detected.",
    ),
) -> None:
    """Compare repeated baseline and candidate traces."""
    try:
        report = compare_runs(
            load_runs(baseline),
            load_runs(candidate),
            regression_threshold=threshold,
        )
    except (OSError, ValueError) as exc:
        console.print(f"[red]Unable to compare traces:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    table = Table(title="Run Comparison")
    table.add_column("Metric")
    table.add_column("Baseline", justify="right")
    table.add_column("Candidate", justify="right")
    table.add_column("Delta", justify="right")
    table.add_row(
        "Success rate",
        f"{report.baseline.success_rate:.1%}",
        f"{report.candidate.success_rate:.1%}",
        f"{report.success_rate_delta.absolute:+.1%}",
    )
    table.add_row(
        "Mean tokens",
        f"{report.baseline.tokens.mean:.1f}",
        f"{report.candidate.tokens.mean:.1f}",
        f"{report.mean_tokens_delta.absolute:+.1f}",
    )
    table.add_row(
        "Mean latency",
        f"{report.baseline.latency_ms.mean:.1f} ms",
        f"{report.candidate.latency_ms.mean:.1f} ms",
        f"{report.mean_latency_ms_delta.absolute:+.1f} ms",
    )
    console.print(table)
    if report.regressions:
        console.print(f"[red]Regressions:[/red] {', '.join(report.regressions)}")
    else:
        console.print("[green]No regressions detected.[/green]")

    if save is not None:
        if export_format == "json":
            export_comparison_json(report, save)
        elif export_format == "csv":
            export_comparison_csv(report, save)
        else:
            console.print(f"[red]Unknown export format:[/red] {export_format}")
            raise typer.Exit(code=1)
        console.print(f"Saved comparison to {save}")
    if fail_on_regression and report.regressions:
        raise typer.Exit(code=2)


if __name__ == "__main__":
    app()
