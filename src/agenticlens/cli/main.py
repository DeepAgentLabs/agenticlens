import runpy
from pathlib import Path

import typer
from rich.console import Console

from agenticlens.cli.render import render_recommendations, render_steps, render_summary
from agenticlens.exporters import CSVExporter, JSONExporter
from agenticlens.models.workflow import Workflow
from agenticlens.profiler.context import completed_workflows
from agenticlens.recommenders import RecommendationEngine

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
    render_recommendations(console, recommendations, savings_pct, workflow)


if __name__ == "__main__":
    app()
