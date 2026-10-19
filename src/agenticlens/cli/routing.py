"""Offline routing decisions and measured result summaries."""

import json
from pathlib import Path

import typer
from rich.console import Console

from agenticlens.modelfit import load_modelfit_report
from agenticlens.routing import (
    Router,
    RouteRequest,
    RoutingAuditLog,
    RoutingPolicy,
    RoutingResult,
    summarize_routing,
)

routing_app = typer.Typer(help="Explain runtime routing from saved ModelFit evidence.")
console = Console()


@routing_app.command("decide")
def decide(
    report: Path = typer.Argument(..., help="Saved ModelFit report JSON."),
    category: str = typer.Option(..., "--category"),
    request_id: str = typer.Option(..., "--request-id", help="Opaque allocation/correlation ID."),
    policy: Path | None = typer.Option(None, "--policy", help="RoutingPolicy JSON."),
    save: Path | None = typer.Option(None, "--save"),
    audit: Path | None = typer.Option(None, "--audit", help="Append local JSONL audit records."),
) -> None:
    """Select and explain without invoking models, in every policy mode.

    Exit 5 means blocked or escalated; exit 1 means invalid inputs.
    """
    try:
        config = RoutingPolicy.model_validate_json(policy.read_text("utf-8")) if policy else None
        router = Router(
            load_modelfit_report(report), config, audit=RoutingAuditLog(audit) if audit else None
        )
        decision = router.decide(RouteRequest(request_id=request_id, category_id=category))
        if save:
            save.parent.mkdir(parents=True, exist_ok=True)
            save.write_text(decision.model_dump_json(indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError) as exc:
        console.print(f"Unable to route: {exc}")
        raise typer.Exit(1) from exc
    console.print_json(decision.model_dump_json())
    if decision.status != "selected":
        raise typer.Exit(5)


@routing_app.command("summary")
def summary(
    results: list[Path] = typer.Argument(..., help="RoutingResult JSON files from Router.run."),
    save: Path | None = typer.Option(None, "--save"),
) -> None:
    """Summarize measured serving/shadow outcomes; unknown costs stay unknown."""
    try:
        report = summarize_routing(
            [RoutingResult.model_validate_json(path.read_text("utf-8")) for path in results]
        )
        payload = report.model_dump_json(indent=2)
        if save:
            save.parent.mkdir(parents=True, exist_ok=True)
            save.write_text(payload + "\n", encoding="utf-8")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        console.print(f"Unable to summarize routing: {exc}")
        raise typer.Exit(1) from exc
    console.print_json(payload)
