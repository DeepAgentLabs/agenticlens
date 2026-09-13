import json
import runpy
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from agenticlens.adapters import load_otlp_export
from agenticlens.api.store import PersistentTraceStore
from agenticlens.cli.render import (
    render_agent_summary,
    render_recommendations,
    render_steps,
    render_summary,
    render_token_optimization,
)
from agenticlens.comparison import (
    ComparisonReport,
    compare_runs,
    export_comparison_csv,
    export_comparison_json,
    export_comparison_markdown,
    load_runs,
)
from agenticlens.evaluation import (
    CalibrationDataset,
    EvaluationReport,
    GateConfig,
    HTTPTarget,
    PythonTarget,
    calibrate_judge,
    dataset_to_samples,
    evaluate_gate,
    evaluate_suite,
    load_dataset,
    load_samples,
    load_suite,
    run_live_suite,
    save_dataset,
    save_html_report,
    split_dataset,
    summarize_dataset,
)
from agenticlens.experiments import load_experiment_suite, load_manifest, run_experiment
from agenticlens.exporters import CSVExporter, JSONExporter
from agenticlens.models.trace import Run
from agenticlens.models.workflow import Workflow
from agenticlens.profiler.context import completed_workflows
from agenticlens.recommenders import RecommendationEngine
from agenticlens.reports import (
    render_history_html,
    render_trace,
    render_trace_markdown,
    save_dashboard_html,
)
from agenticlens.validation import ConformanceReport, validate_aios_artifact

app = typer.Typer(
    name="agenticlens",
    help="Profile, analyze, and optimize token consumption in LLM-powered applications.",
    no_args_is_help=True,
)
dataset_app = typer.Typer(help="Manage versioned evaluation datasets.")
experiment_app = typer.Typer(help="Run repeated multi-variant evaluation experiments.")
app.add_typer(dataset_app, name="dataset")
app.add_typer(experiment_app, name="experiment")
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
    html: Path | None = typer.Option(
        None, "--html", help="Also render a standalone HTML dashboard (cost + findings)."
    ),
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
    if html is not None:
        save_dashboard_html(html, workflow=workflow, recommendations=recommendations)
        console.print(f"\nSaved HTML dashboard to {html}")


@app.command("inspect")
def inspect_run(
    run_file: Path = typer.Argument(..., help="Path to a saved AgenticLens trace (JSON)."),
    save: Path | None = typer.Option(None, "--save", help="Save a Markdown trace report."),
    html: Path | None = typer.Option(
        None, "--html", help="Also render a standalone HTML dashboard (agent timeline)."
    ),
) -> None:
    """Inspect a validated run trace, span tree, and raw metric distributions."""
    run = _load_run(run_file)
    render_trace(console, run)
    if save is not None:
        save.write_text(render_trace_markdown(run), encoding="utf-8")
        console.print(f"Saved trace report to {save}")
    if html is not None:
        save_dashboard_html(html, run=run)
        console.print(f"Saved HTML dashboard to {html}")


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
    html: Path | None = typer.Option(
        None, "--html", help="Also render a standalone HTML dashboard (comparison strip)."
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
    if html is not None:
        save_dashboard_html(html, comparison=report)
        console.print(f"Saved HTML dashboard to {html}")
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


@app.command("import-otlp")
def import_otlp(
    source: Path = typer.Argument(..., help="OTLP/HTTP JSON export file, or a directory of them."),
    save_dir: Path | None = typer.Option(
        None, "--save-dir", help="Write one <trace_id>.json AgenticLens run file per trace here."
    ),
) -> None:
    """Convert OTLP/HTTP JSON trace exports into AgenticLens run files."""
    try:
        runs = load_otlp_export(source)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        console.print(f"[red]Unable to import OTLP export:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    if not runs:
        console.print("[yellow]No traces found in the OTLP export.[/yellow]")
        return

    table = Table(title="Imported OTLP Traces")
    table.add_column("Trace ID")
    table.add_column("Application")
    table.add_column("Spans", justify="right")
    table.add_column("Tokens", justify="right")
    table.add_column("Cost", justify="right")
    for run in runs:
        cost = "unavailable" if run.estimated_cost_usd is None else f"${run.estimated_cost_usd:.4f}"
        table.add_row(
            run.trace_id, run.application_name, str(len(run.spans)), str(run.total_tokens), cost
        )
    console.print(table)

    if save_dir is not None:
        save_dir.mkdir(parents=True, exist_ok=True)
        for run in runs:
            out = save_dir / f"{run.trace_id}.json"
            out.write_text(run.model_dump_json(indent=2), encoding="utf-8")
        console.print(f"Saved {len(runs)} run(s) to {save_dir}")


@app.command("serve-otlp")
def serve_otlp(
    host: str = typer.Option(
        "127.0.0.1",
        "--host",
        help="Bind address. Stays localhost by default: this endpoint has no built-in auth.",
    ),
    port: int = typer.Option(4318, "--port", help="OTLP/HTTP's conventional port."),
    save_dir: Path | None = typer.Option(
        None, "--save-dir", help="Also persist every received trace as <trace_id>.json here."
    ),
    max_traces: int = typer.Option(
        200, "--max-traces", min=1, help="Most recent in-memory traces kept before evicting."
    ),
    db: Path | None = typer.Option(
        None,
        "--db",
        help="Persist traces to a SQLite file here instead of memory-only. "
        "Traces survive a restart; view them anytime with `agenticlens history`.",
    ),
    max_persisted: int | None = typer.Option(
        None,
        "--max-persisted",
        min=1,
        help="Cap on traces kept in --db before evicting the oldest. Unbounded by default.",
    ),
) -> None:
    """Run a live OTLP/HTTP receiver with a real-time dashboard. Requires `agenticlens[api]`."""
    try:
        import uvicorn

        from agenticlens.api.http import create_app
        from agenticlens.api.store import LiveTraceStore
    except ImportError as exc:
        console.print(
            "[red]The live receiver needs the optional `api` extra.[/red] "
            "Install it with: pip install 'agenticlens[api]'"
        )
        raise typer.Exit(code=1) from exc

    store = (
        PersistentTraceStore(db, max_traces=max_persisted)
        if db is not None
        else LiveTraceStore(max_traces=max_traces)
    )
    app_instance = create_app(store, save_dir=save_dir)
    console.print(f"OTLP endpoint: http://{host}:{port}/v1/traces")
    console.print(f"Live dashboard: http://{host}:{port}/")
    console.print(f"Trace history: http://{host}:{port}/history")
    if save_dir is not None:
        console.print(f"Persisting received traces as JSON to {save_dir}")
    if db is not None:
        console.print(f"Persisting traces to {db} (survives a restart)")
    uvicorn.run(app_instance, host=host, port=port, log_level="warning")


@app.command("history")
def history(
    source: Path = typer.Argument(
        ..., help="A `--db` SQLite file, or a directory/file of AgenticLens run JSON."
    ),
    save: Path | None = typer.Option(
        None, "--save", help="Write the rendered HTML history page here."
    ),
) -> None:
    """Render a cross-trace history view from a --db file or a run-JSON directory."""
    if source.suffix == ".db":
        runs = PersistentTraceStore(source).list_recent()
    else:
        try:
            runs = load_runs(source)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            console.print(f"[red]Unable to load runs:[/red] {exc}")
            raise typer.Exit(code=1) from exc

    if not runs:
        console.print("[yellow]No traces found.[/yellow]")
        return

    table = Table(title="Trace History")
    table.add_column("Trace ID")
    table.add_column("Application")
    table.add_column("Status")
    table.add_column("Spans", justify="right")
    table.add_column("Tokens", justify="right")
    table.add_column("Cost", justify="right")
    for run in runs:
        cost = "unavailable" if run.estimated_cost_usd is None else f"${run.estimated_cost_usd:.4f}"
        table.add_row(
            run.trace_id,
            run.application_name,
            run.status.value,
            str(len(run.spans)),
            str(run.total_tokens),
            cost,
        )
    console.print(table)

    if save is not None:
        save.parent.mkdir(parents=True, exist_ok=True)
        save.write_text(render_history_html(runs), encoding="utf-8")
        console.print(f"Saved HTML history to {save}")


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


@dataset_app.command("summary")
def dataset_summary(
    dataset_file: Path = typer.Argument(..., help="Evaluation dataset JSON or YAML."),
) -> None:
    """Summarize dataset size, split assignment, and available human labels."""
    try:
        dataset = load_dataset(dataset_file)
        summary = summarize_dataset(dataset)
    except (OSError, ValueError) as exc:
        console.print(f"[red]Unable to summarize dataset:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    table = Table(title=f"Dataset · {dataset.name}")
    table.add_column("Metric")
    table.add_column("Value", justify="right")
    table.add_row("Version", dataset.version)
    table.add_row("Records", str(summary.total_records))
    table.add_row("Labeled records", str(summary.labeled_records))
    table.add_row("Total labels", str(summary.total_labels))
    table.add_row(
        "Splits",
        ", ".join(f"{name}={count}" for name, count in sorted(summary.split_counts.items()))
        or "none",
    )
    table.add_row(
        "Label keys",
        ", ".join(f"{name}={count}" for name, count in sorted(summary.label_counts.items()))
        or "none",
    )
    table.add_row("Tags", ", ".join(summary.tags) or "none")
    console.print(table)


@dataset_app.command("split")
def dataset_split(
    dataset_file: Path = typer.Argument(..., help="Evaluation dataset JSON or YAML."),
    save: Path = typer.Option(..., "--save", help="Save the updated dataset JSON file."),
    train_ratio: float = typer.Option(0.7, min=0.0, max=1.0),
    validation_ratio: float = typer.Option(0.15, min=0.0, max=1.0),
    test_ratio: float = typer.Option(0.15, min=0.0, max=1.0),
    seed: int = typer.Option(0, help="Random seed used for deterministic split assignment."),
) -> None:
    """Assign deterministic train, validation, and test splits to a dataset."""
    try:
        dataset = load_dataset(dataset_file)
        updated = split_dataset(
            dataset,
            train_ratio=train_ratio,
            validation_ratio=validation_ratio,
            test_ratio=test_ratio,
            seed=seed,
        )
        save_dataset(updated, save)
    except (OSError, ValueError) as exc:
        console.print(f"[red]Unable to split dataset:[/red] {exc}")
        raise typer.Exit(code=1) from exc
    console.print(f"Saved dataset split to {save}")


@dataset_app.command("export-samples")
def dataset_export_samples(
    dataset_file: Path = typer.Argument(..., help="Evaluation dataset JSON or YAML."),
    save: Path = typer.Option(..., "--save", help="Save a samples JSON file."),
    split: str | None = typer.Option(
        None,
        "--split",
        help="Optional split filter: train, validation, or test.",
    ),
) -> None:
    """Export evaluation samples from a versioned dataset artifact."""
    try:
        dataset = load_dataset(dataset_file)
        samples = dataset_to_samples(dataset, split=split)
    except (OSError, ValueError) as exc:
        console.print(f"[red]Unable to export dataset samples:[/red] {exc}")
        raise typer.Exit(code=1) from exc
    save.parent.mkdir(parents=True, exist_ok=True)
    payload = {"samples": [sample.model_dump(mode="json") for sample in samples]}
    save.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    console.print(f"Saved {len(samples)} sample(s) to {save}")


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


@app.command("judge-calibrate")
def judge_calibrate(
    report_file: Path = typer.Argument(..., help="AgenticLens evaluation report JSON."),
    dataset_file: Path = typer.Argument(..., help="Labeled evaluation dataset JSON or YAML."),
    score_name: str = typer.Option(..., "--score-name", help="Judge score name to calibrate."),
    confidence_level: float = typer.Option(0.95, "--confidence-level", min=0.5, max=0.999),
    save: Path | None = typer.Option(
        None,
        "--save",
        help="Optionally save the machine-readable calibration report.",
    ),
) -> None:
    """Compare judge scores against labeled reference judgments and summarize agreement."""
    try:
        report = EvaluationReport.model_validate_json(report_file.read_text(encoding="utf-8"))
        dataset = load_dataset(dataset_file)
        calibration = calibrate_judge(
            report,
            dataset,
            score_name=score_name,
            confidence_level=confidence_level,
        )
    except (OSError, ValueError) as exc:
        console.print(f"[red]Unable to calibrate judge:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    table = Table(title=f"Judge Calibration · {calibration.score_name}")
    table.add_column("Metric")
    table.add_column("Value", justify="right")
    table.add_column("Samples", justify="right")
    for metric in calibration.summary:
        value = f"{metric.value:.3f}"
        if metric.confidence_interval is not None:
            ci = metric.confidence_interval
            value = f"{value} ({ci.confidence_level:.0%} CI {ci.lower:.3f} to {ci.upper:.3f})"
        table.add_row(metric.name, value, str(metric.sample_size))
    console.print(table)
    console.print(
        f"Calibrated against {len(calibration.cases)} labeled case(s) "
        f"from {calibration.dataset_name} {calibration.dataset_version}."
    )
    if save is not None:
        save.parent.mkdir(parents=True, exist_ok=True)
        save.write_text(calibration.model_dump_json(indent=2), encoding="utf-8")
        console.print(f"Saved calibration report to {save}")


@experiment_app.command("run")
def experiment_run(
    manifest_file: Path = typer.Argument(..., help="Experiment manifest JSON or YAML."),
    suite_file: Path = typer.Argument(..., help="YAML or JSON evaluation suite."),
    save: Path = typer.Option(
        Path("agenticlens-experiment.json"),
        "--save",
        help="Save the machine-readable experiment report.",
    ),
    confidence_level: float = typer.Option(0.95, "--confidence-level", min=0.5, max=0.999),
    regression_threshold: float = typer.Option(
        0.05,
        "--regression-threshold",
        min=0.0,
        help="Relative degradation threshold for baseline deltas.",
    ),
) -> None:
    """Run repeated trials for three or more live variants against one suite."""
    try:
        manifest = load_manifest(manifest_file)
        suite = load_experiment_suite(suite_file)
        report = run_experiment(
            manifest,
            suite,
            confidence_level=confidence_level,
            regression_threshold=regression_threshold,
        )
    except (OSError, ValueError) as exc:
        console.print(f"[red]Unable to run experiment:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    summary_table = Table(title=f"Experiment · {report.experiment_name}")
    summary_table.add_column("Variant")
    summary_table.add_column("Trial success", justify="right")
    summary_table.add_column("Completed", justify="right")
    summary_table.add_column("Failed", justify="right")
    summary_table.add_column("Mean pass rate", justify="right")
    summary_table.add_column("Mean score", justify="right")
    summary_table.add_column("Mean latency", justify="right")
    summary_table.add_column("Mean cost", justify="right")
    summary_table.add_column("Pareto", justify="center")
    for variant in report.variants:
        pass_rate = (
            f"{variant.summary.pass_rate.mean:.1%}"
            if variant.summary.pass_rate is not None
            else "n/a"
        )
        average_score = (
            f"{variant.summary.average_score.mean:.3f}"
            if variant.summary.average_score is not None
            else "n/a"
        )
        average_latency = (
            f"{variant.summary.average_latency_ms.mean:.1f} ms"
            if variant.summary.average_latency_ms is not None
            else "n/a"
        )
        cost = (
            f"${variant.summary.total_cost_usd.mean:.4f}"
            if variant.summary.total_cost_usd is not None
            else "n/a"
        )
        summary_table.add_row(
            variant.variant_name,
            f"{variant.summary.trial_success_rate:.1%}",
            str(variant.summary.completed_trials),
            str(variant.summary.failed_trials),
            pass_rate,
            average_score,
            average_latency,
            cost,
            "yes" if variant.pareto_optimal else "no",
        )
    console.print(summary_table)

    delta_table = Table(title=f"Baseline Deltas · {report.baseline_variant_id}")
    delta_table.add_column("Variant")
    delta_table.add_column("Pass rate", justify="right")
    delta_table.add_column("Score", justify="right")
    delta_table.add_column("Latency", justify="right")
    delta_table.add_column("Cost", justify="right")
    for comparison in report.comparisons:
        cost_delta = (
            f"{comparison.total_cost_usd_delta.absolute:+.4f}"
            if comparison.total_cost_usd_delta is not None
            else "n/a"
        )
        delta_table.add_row(
            comparison.candidate_variant_id,
            f"{comparison.pass_rate_delta.absolute:+.1%}",
            f"{comparison.average_score_delta.absolute:+.3f}",
            f"{comparison.average_latency_ms_delta.absolute:+.1f} ms",
            cost_delta,
        )
    console.print(delta_table)
    pareto_frontier = ", ".join(report.pareto_frontier_variant_ids) or "none"
    console.print(f"Pareto frontier: {pareto_frontier} | Trials per variant: {report.trial_count}")

    save.parent.mkdir(parents=True, exist_ok=True)
    save.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    console.print(f"Saved experiment report to {save}")


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


@app.command()
def dashboard(
    workflow_file: Path | None = typer.Option(
        None, "--workflow", help="Saved workflow JSON (from `profile --save`)."
    ),
    run_file: Path | None = typer.Option(
        None, "--run", help="Saved run trace JSON (from the trace API)."
    ),
    evaluation_file: Path | None = typer.Option(
        None, "--evaluation", help="Saved evaluation report JSON (from `evaluate --save`)."
    ),
    comparison_file: Path | None = typer.Option(
        None,
        "--comparison",
        help="Saved comparison report JSON (from `compare --save --format json`).",
    ),
    min_pass_rate: float = typer.Option(1.0, min=0.0, max=1.0),
    min_average_score: float = typer.Option(1.0, min=0.0, max=1.0),
    max_failed_cases: int = typer.Option(0, min=0),
    max_average_latency_ms: float | None = typer.Option(None, min=0.0),
    max_total_cost_usd: float | None = typer.Option(None, min=0.0),
    save: Path = typer.Option(Path("agenticlens-dashboard.html"), "--save"),
) -> None:
    """Combine a workflow, run, evaluation report, and/or comparison into one HTML dashboard."""
    no_inputs = (
        workflow_file is None
        and run_file is None
        and evaluation_file is None
        and comparison_file is None
    )
    if no_inputs:
        console.print(
            "[red]Provide at least one of --workflow, --run, --evaluation, --comparison.[/red]"
        )
        raise typer.Exit(code=1)

    try:
        workflow = _load_workflow(workflow_file) if workflow_file is not None else None
        run = _load_run(run_file) if run_file is not None else None
        evaluation = (
            EvaluationReport.model_validate_json(evaluation_file.read_text(encoding="utf-8"))
            if evaluation_file is not None
            else None
        )
        comparison = (
            ComparisonReport.model_validate_json(comparison_file.read_text(encoding="utf-8"))
            if comparison_file is not None
            else None
        )
    except (OSError, ValueError) as exc:
        console.print(f"[red]Unable to build dashboard:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    recommendations = RecommendationEngine().run(workflow) if workflow is not None else None
    gate_decision = (
        evaluate_gate(
            evaluation,
            GateConfig(
                min_pass_rate=min_pass_rate,
                min_average_score=min_average_score,
                max_failed_cases=max_failed_cases,
                max_average_latency_ms=max_average_latency_ms,
                max_total_cost_usd=max_total_cost_usd,
            ),
        )
        if evaluation is not None
        else None
    )

    save_dashboard_html(
        save,
        workflow=workflow,
        recommendations=recommendations,
        run=run,
        evaluation=evaluation,
        gate=gate_decision,
        comparison=comparison,
    )
    console.print(f"Saved HTML dashboard to {save}")


def _render_aios_report(report: ConformanceReport, save: Path | None) -> None:
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


@app.command("calibrate")
def calibrate(
    report_file: Path = typer.Argument(..., help="Saved evaluation report JSON."),
    labels_file: Path = typer.Argument(..., help="Versioned reference labels JSON."),
    evaluator: str = typer.Option(..., "--evaluator", help="Exact llm_judge score name."),
    save: Path = typer.Option(Path("agenticlens-calibration.json"), "--save"),
) -> None:
    """Compare saved judge verdicts with human reference labels."""
    try:
        report = EvaluationReport.model_validate_json(report_file.read_text(encoding="utf-8"))
        labels = CalibrationDataset.model_validate_json(labels_file.read_text(encoding="utf-8"))
        result = calibrate_judge(report, labels, evaluator=evaluator)
        save.parent.mkdir(parents=True, exist_ok=True)
        save.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    except (OSError, ValueError) as exc:
        console.print(f"[red]Unable to calibrate judge:[/red] {exc}")
        raise typer.Exit(code=1) from exc
    low, high = result.agreement_interval
    console.print(
        f"Agreement: {result.agreement_rate:.1%} "
        f"(95% Wilson interval: {low:.1%}-{high:.1%}; n={result.sample_count})"
    )
    console.print(f"False accepts: {result.false_accepts}; false rejects: {result.false_rejects}")
    for warning in result.warnings:
        console.print(warning)
    console.print(f"Saved calibration to {save}")
