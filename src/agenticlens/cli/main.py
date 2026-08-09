import json
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
    export_comparison_markdown,
    load_runs,
)
from agenticlens.evaluation import (
    EvaluationReport,
    GateConfig,
    HTTPTarget,
    PythonTarget,
    evaluate_gate,
    evaluate_suite,
    load_samples,
    load_suite,
    run_live_suite,
    save_html_report,
)
from agenticlens.exporters import CSVExporter, JSONExporter
from agenticlens.models.trace import Run
from agenticlens.models.workflow import Workflow
from agenticlens.profiler.context import completed_workflows
from agenticlens.recommenders import RecommendationEngine
from agenticlens.reports import render_trace, render_trace_markdown
from agenticlens.validation import validate_aios_artifact

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
    save: Path | None = typer.Option(None, "--save", help="Save a Markdown trace report."),
) -> None:
    """Inspect a validated run trace, span tree, and raw metric distributions."""
    run = _load_run(run_file)
    render_trace(console, run)
    if save is not None:
        save.write_text(render_trace_markdown(run), encoding="utf-8")
        console.print(f"Saved trace report to {save}")


@app.command()
def validate(
    artifact_file: Path = typer.Argument(..., help="AIOS workflow or run artifact JSON."),
    version: str = typer.Option(
        "0.4",
        "--version",
        help="AI Operations Specification version to validate against.",
    ),
    spec_root: Path | None = typer.Option(
        None,
        "--spec-root",
        help="Path to the ai-operations-spec repository root.",
    ),
    save: Path | None = typer.Option(
        None,
        "--save",
        help="Save the machine-readable validation report.",
    ),
) -> None:
    """Validate an AIOS artifact against the draft JSON Schema."""
    try:
        report = validate_aios_artifact(
            artifact_file,
            spec_version=version,
            mode="validate",
            spec_root=spec_root,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        console.print(f"[red]Unable to validate artifact:[/red] {exc}")
        raise typer.Exit(code=1) from exc
    _render_aios_report(report, save)
    if not report.schema_valid:
        raise typer.Exit(code=2)


@app.command()
def conformance(
    artifact_file: Path = typer.Argument(..., help="AIOS workflow or run artifact JSON."),
    version: str = typer.Option(
        "0.4",
        "--version",
        help="AI Operations Specification version to validate against.",
    ),
    spec_root: Path | None = typer.Option(
        None,
        "--spec-root",
        help="Path to the ai-operations-spec repository root.",
    ),
    save: Path | None = typer.Option(
        None,
        "--save",
        help="Save the machine-readable conformance report.",
    ),
) -> None:
    """Run schema and semantic AIOS draft checks and report draft alignment."""
    try:
        report = validate_aios_artifact(
            artifact_file,
            spec_version=version,
            mode="conformance",
            spec_root=spec_root,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        console.print(f"[red]Unable to check conformance:[/red] {exc}")
        raise typer.Exit(code=1) from exc
    _render_aios_report(report, save)
    if not report.aligned:
        raise typer.Exit(code=2)


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
    export_format: str = typer.Option("json", "--format", help="'json', 'csv', or 'md'."),
    fail_on_regression: bool = typer.Option(
        False,
        "--fail-on-regression",
        help="Return a non-zero exit status when regressions are detected.",
    ),
    min_samples: int | None = typer.Option(
        None,
        "--min-samples",
        min=1,
        help=(
            "Require at least this many runs in both baseline and candidate cohorts. "
            "Returns a non-zero exit status when the comparison is under-sampled."
        ),
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
        elif export_format == "md":
            export_comparison_markdown(report, save)
        else:
            console.print(f"[red]Unknown export format:[/red] {export_format}")
            raise typer.Exit(code=1)
        console.print(f"Saved comparison to {save}")
    if report.sample_size_guidance:
        console.print(f"[yellow]{report.sample_size_guidance}[/yellow]")
    if min_samples is not None:
        observed_min = min(report.baseline.run_count, report.candidate.run_count)
        if observed_min < min_samples:
            console.print(
                "[red]Comparison sample size requirement not met.[/red] "
                f"Observed {observed_min} run(s); required at least {min_samples} per cohort."
            )
            raise typer.Exit(code=3)
    if fail_on_regression and report.regressions:
        raise typer.Exit(code=2)


@app.command()
def evaluate(
    suite_file: Path = typer.Argument(..., help="YAML or JSON evaluation suite."),
    samples_file: Path = typer.Argument(..., help="YAML or JSON outputs and traces."),
    save: Path = typer.Option(
        Path("agenticlens-evaluation.json"),
        "--save",
        help="Save the machine-readable evaluation report.",
    ),
    html: Path | None = typer.Option(
        None,
        "--html",
        help="Also create a standalone HTML report.",
    ),
) -> None:
    """Score agent outputs, tool use, latency, and cost against a test suite."""
    try:
        result = evaluate_suite(load_suite(suite_file), load_samples(samples_file))
    except (OSError, ValueError) as exc:
        console.print(f"[red]Unable to evaluate suite:[/red] {exc}")
        raise typer.Exit(code=1) from exc
    save.parent.mkdir(parents=True, exist_ok=True)
    save.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    if html is not None:
        save_html_report(result, html)

    table = Table(title=f"Evaluation · {result.suite_name}")
    table.add_column("Cases", justify="right")
    table.add_column("Passed", justify="right")
    table.add_column("Pass rate", justify="right")
    table.add_column("Average score", justify="right")
    table.add_column("Average latency", justify="right")
    table.add_row(
        str(result.summary.total_cases),
        str(result.summary.passed_cases),
        f"{result.summary.pass_rate:.1%}",
        f"{result.summary.average_score:.3f}",
        f"{result.summary.average_latency_ms:.1f} ms",
    )
    console.print(table)
    console.print(f"Saved evaluation to {save}")
    if html is not None:
        console.print(f"Saved HTML report to {html}")


@app.command("evaluate-live")
def evaluate_live(
    suite_file: Path = typer.Argument(..., help="YAML or JSON evaluation suite."),
    target_kind: str = typer.Option(..., "--target-kind", help="'python' or 'http'."),
    target: str = typer.Option(
        ...,
        "--target",
        help="Python target as module:function or HTTP target as a URL.",
    ),
    save: Path = typer.Option(
        Path("agenticlens-evaluation-live.json"),
        "--save",
        help="Save the machine-readable evaluation report.",
    ),
) -> None:
    """Run one trusted live Python or HTTP target against an evaluation suite."""
    try:
        suite = load_suite(suite_file)
        live_target = (
            PythonTarget(callable_path=target)
            if target_kind == "python"
            else HTTPTarget(url=target)
            if target_kind == "http"
            else None
        )
        if live_target is None:
            raise ValueError("target kind must be 'python' or 'http'")
        result = run_live_suite(suite, live_target)
    except (OSError, ValueError) as exc:
        console.print(f"[red]Unable to run live evaluation:[/red] {exc}")
        raise typer.Exit(code=1) from exc
    save.parent.mkdir(parents=True, exist_ok=True)
    save.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    console.print(
        "Live evaluation complete: "
        f"{result.summary.passed_cases}/{result.summary.total_cases} cases passed."
    )
    console.print(f"Saved evaluation to {save}")


@app.command()
def gate(
    report_file: Path = typer.Argument(..., help="AgenticLens evaluation report JSON."),
    min_pass_rate: float = typer.Option(1.0, min=0.0, max=1.0),
    min_average_score: float = typer.Option(1.0, min=0.0, max=1.0),
    max_failed_cases: int = typer.Option(0, min=0),
    max_average_latency_ms: float | None = typer.Option(None, min=0.0),
    max_total_cost_usd: float | None = typer.Option(None, min=0.0),
) -> None:
    """Apply release thresholds and return exit code 2 when the gate fails."""
    try:
        report = EvaluationReport.model_validate_json(report_file.read_text(encoding="utf-8"))
        decision = evaluate_gate(
            report,
            GateConfig(
                min_pass_rate=min_pass_rate,
                min_average_score=min_average_score,
                max_failed_cases=max_failed_cases,
                max_average_latency_ms=max_average_latency_ms,
                max_total_cost_usd=max_total_cost_usd,
            ),
        )
    except (OSError, ValueError) as exc:
        console.print(f"[red]Unable to apply release gate:[/red] {exc}")
        raise typer.Exit(code=1) from exc
    if decision.passed:
        console.print("[green]Release gate passed.[/green]")
        return
    console.print("[red]Release gate failed.[/red]")
    for reason in decision.reasons:
        console.print(f"  • {reason}")
    raise typer.Exit(code=2)


def _render_aios_report(report, save: Path | None) -> None:
    table = Table(title=f"AIOS {report.mode.title()} · {report.artifact_type}")
    table.add_column("Check")
    table.add_column("Result")
    table.add_row("Spec version", f"v{report.spec_version}-draft")
    table.add_row("Schema", "pass" if report.schema_valid else "fail")
    table.add_row(
        "Semantics",
        "pass" if report.semantic_valid else ("n/a" if report.mode == "validate" else "fail"),
    )
    table.add_row("Draft alignment", "pass" if report.aligned else "fail")
    console.print(table)
    console.print(report.draft_alignment_claim)
    if report.issues:
        console.print("[yellow]AIOS-defined issues:[/yellow]")
        for issue in report.issues:
            location = f" ({issue.location})" if issue.location else ""
            console.print(f"  • {issue.code}: {issue.message}{location}")
    else:
        console.print("[green]No AIOS issues detected.[/green]")
    if save is not None:
        save.parent.mkdir(parents=True, exist_ok=True)
        save.write_text(report.model_dump_json(indent=2), encoding="utf-8")
        console.print(f"Saved report to {save}")


if __name__ == "__main__":
    app()
