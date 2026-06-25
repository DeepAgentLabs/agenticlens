from pathlib import Path

import typer
from rich.console import Console

app = typer.Typer(
    name="tokenlens",
    help="Profile, analyze, and optimize token consumption in LLM-powered applications.",
    no_args_is_help=True,
)
console = Console()


@app.command()
def profile(
    script: Path = typer.Argument(..., help="Path to a Python script to profile."),
) -> None:
    """Profile a script that uses `tokenlens.profile()` / `tokenlens.step()`."""
    console.print(f"[yellow]Not yet implemented:[/yellow] profile {script}")
    raise typer.Exit(code=1)


@app.command()
def report(
    report_file: Path = typer.Argument(..., help="Path to a saved workflow report (JSON)."),
) -> None:
    """Display a saved workflow report."""
    console.print(f"[yellow]Not yet implemented:[/yellow] report {report_file}")
    raise typer.Exit(code=1)


@app.command()
def analyze(
    workflow_file: Path = typer.Argument(..., help="Path to a saved workflow (JSON)."),
) -> None:
    """Run the recommendation engine against a saved workflow."""
    console.print(f"[yellow]Not yet implemented:[/yellow] analyze {workflow_file}")
    raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
