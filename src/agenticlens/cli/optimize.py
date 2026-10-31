"""Optimization opportunities, decisions, and post-adoption outcomes."""

from datetime import datetime, timezone
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from agenticlens.optimization import (
    RecommendationDecision,
    RecommendationLedger,
    analyze_optimizations,
    evaluate_outcome,
    load_optimization_config,
    load_optimization_report,
    load_traces,
    render_optimization_markdown,
    render_outcome_markdown,
    report_sha256,
    save_optimization_report,
)
from agenticlens.optimization.models import DecisionStatus

optimize_app = typer.Typer(help="Find, track, and verify evidence-backed optimizations.")
console = Console()

#: `optimize outcome --fail-on-regression` exits with this when quality regressed.
REGRESSION_EXIT = 9


def _usd(value: float | None) -> str:
    return "unavailable" if value is None else f"${value:.6f}"


@optimize_app.command("analyze")
def analyze(
    traces: list[Path] = typer.Argument(..., help="Trace JSON files or directories of them."),
    config: Path | None = typer.Option(None, "--config", help="Thresholds (YAML or JSON)."),
    baseline_variant: str | None = typer.Option(
        None, "--baseline-variant", help="Variant to compare trade-offs against."
    ),
    ledger: Path | None = typer.Option(None, "--ledger", help="Show decision statuses."),
    save: Path | None = typer.Option(None, "--save", help="Write the report JSON."),
    markdown: Path | None = typer.Option(None, "--markdown", help="Write a Markdown report."),
) -> None:
    """Rank opportunities by projected cost saving, with evidence, confidence, and risks."""
    try:
        report = analyze_optimizations(
            load_traces(traces),
            load_optimization_config(config) if config else None,
            baseline_variant_id=baseline_variant,
        )
        statuses = RecommendationLedger(ledger).summary(report) if ledger else {}
        if save:
            save_optimization_report(report, save)
        if markdown:
            markdown.parent.mkdir(parents=True, exist_ok=True)
            markdown.write_text(render_optimization_markdown(report, statuses), encoding="utf-8")
    except (OSError, ValueError) as exc:
        console.print(f"Unable to analyze: {exc}")
        raise typer.Exit(1) from exc

    table = Table(title=f"Optimization opportunities ({len(report.runs)} runs)")
    table.add_column("ID", overflow="fold")
    for column in ("Opportunity", "Tokens/run", "Cost/run", "Confidence", "Risks", "Status"):
        table.add_column(column)
    for item in report.opportunities:
        table.add_row(
            item.opportunity_id,
            item.title,
            f"{item.benefit.tokens_per_run:,.0f}",
            _usd(item.benefit.cost_usd_per_run),
            item.confidence,
            ", ".join(f"{r.kind} ({r.severity})" for r in item.risks),
            statuses.get(item.opportunity_id, "proposed"),
        )
    console.print(table)
    if not report.opportunities:
        console.print("No opportunities met the configured thresholds.")


@optimize_app.command("decide")
def decide(
    report_file: Path = typer.Argument(..., help="Saved optimization report JSON."),
    opportunity_id: str = typer.Argument(...),
    status: str = typer.Option(..., "--status", help="accepted, rejected, adopted, or reverted."),
    decided_by: str = typer.Option(..., "--by", help="Person or process deciding."),
    ledger: Path = typer.Option(..., "--ledger", help="Append-only JSONL decision ledger."),
    reason: str = typer.Option("", "--reason"),
    change: str | None = typer.Option(None, "--change", help="PR, commit, or config version."),
) -> None:
    """Record a decision. Adopting requires a prior accept; reverting requires adoption."""
    if status not in {"accepted", "rejected", "adopted", "reverted"}:
        console.print(f"Unknown status {status!r}.")
        raise typer.Exit(1)
    try:
        report = load_optimization_report(report_file)
        decision = RecommendationLedger(ledger).record(
            report,
            RecommendationDecision(
                opportunity_id=opportunity_id,
                report_sha256=report_sha256(report),
                status=status,  # type: ignore[arg-type]
                decided_by=decided_by,
                decided_at=datetime.now(timezone.utc),
                reason=reason,
                change_reference=change,
            ),
        )
    except (OSError, ValueError, KeyError) as exc:
        console.print(f"Unable to record decision: {exc}")
        raise typer.Exit(1) from exc
    console.print_json(decision.model_dump_json())


@optimize_app.command("status")
def status_command(
    report_file: Path = typer.Argument(..., help="Saved optimization report JSON."),
    ledger: Path = typer.Option(..., "--ledger"),
) -> None:
    """Show the latest decision status of every opportunity in a report."""
    try:
        report = load_optimization_report(report_file)
        statuses = RecommendationLedger(ledger).summary(report)
    except (OSError, ValueError) as exc:
        console.print(f"Unable to read decisions: {exc}")
        raise typer.Exit(1) from exc
    counts: dict[DecisionStatus, int] = {}
    for value in statuses.values():
        counts[value] = counts.get(value, 0) + 1
    console.print_json(data={"statuses": statuses, "counts": counts})


@optimize_app.command("outcome")
def outcome(
    report_file: Path = typer.Argument(..., help="Saved optimization report JSON."),
    opportunity_id: str = typer.Argument(...),
    before: list[Path] = typer.Option(..., "--before", help="Traces before adoption."),
    after: list[Path] = typer.Option(..., "--after", help="Traces after adoption."),
    ledger: Path | None = typer.Option(None, "--ledger"),
    min_runs: int = typer.Option(3, "--min-runs", min=1),
    save: Path | None = typer.Option(None, "--save"),
    markdown: Path | None = typer.Option(None, "--markdown"),
    fail_on_regression: bool = typer.Option(
        False, "--fail-on-regression", help=f"Exit {REGRESSION_EXIT} if quality regressed."
    ),
) -> None:
    """Compare projected and observed savings; the projection is never adjusted."""
    try:
        evaluation = evaluate_outcome(
            load_optimization_report(report_file),
            opportunity_id,
            load_traces(before),
            load_traces(after),
            ledger=RecommendationLedger(ledger) if ledger else None,
            min_runs=min_runs,
        )
        payload = evaluation.model_dump_json(indent=2)
        if save:
            save.parent.mkdir(parents=True, exist_ok=True)
            save.write_text(payload + "\n", encoding="utf-8")
        if markdown:
            markdown.parent.mkdir(parents=True, exist_ok=True)
            markdown.write_text(render_outcome_markdown(evaluation), encoding="utf-8")
    except (OSError, ValueError, KeyError) as exc:
        console.print(f"Unable to evaluate outcome: {exc}")
        raise typer.Exit(1) from exc
    console.print_json(payload)
    if fail_on_regression and evaluation.status == "quality_regressed":
        raise typer.Exit(REGRESSION_EXIT)
