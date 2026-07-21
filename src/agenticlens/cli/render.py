from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from agenticlens.models.enums import Severity
from agenticlens.models.recommendation import Recommendation
from agenticlens.models.workflow import Workflow

_SEVERITY_STYLES = {
    Severity.INFO: "blue",
    Severity.WARNING: "yellow",
    Severity.CRITICAL: "red",
}


def render_summary(console: Console, workflow: Workflow) -> None:
    """Render the workflow-level totals as a boxed panel."""
    cost = workflow.total_cost
    cost_display = f"${cost:.2f}" if cost is not None else "n/a"

    body = Table.grid(padding=(0, 2))
    body.add_column(justify="left", style="bold")
    body.add_column(justify="right")
    body.add_row("Total Tokens", f"{workflow.total_tokens:,}")
    body.add_row("Total Cost", cost_display)
    body.add_row("Latency", f"{workflow.latency:.2f} sec")

    console.print(Panel(body, title=workflow.name, box=box.DOUBLE, expand=False))


def render_steps(console: Console, workflow: Workflow) -> None:
    """Render a per-step token/cost/latency breakdown table."""
    table = Table(title="Step Breakdown", box=box.SIMPLE_HEAVY)
    table.add_column("Step")
    table.add_column("Type")
    table.add_column("Prompt", justify="right")
    table.add_column("Completion", justify="right")
    table.add_column("Cost", justify="right")
    table.add_column("Latency", justify="right")

    for step in workflow.steps:
        cost_display = f"${step.metrics.cost:.4f}" if step.metrics.cost is not None else "n/a"
        table.add_row(
            step.name,
            step.type.value,
            f"{step.metrics.prompt_tokens:,}",
            f"{step.metrics.completion_tokens:,}",
            cost_display,
            f"{step.metrics.latency:.2f}s",
        )

    console.print(table)


def render_recommendations(
    console: Console,
    recommendations: list[Recommendation],
    estimated_savings_pct: float,
    cost_savings: float | None = None,
) -> None:
    """Render optimization suggestions and the aggregate estimated savings."""
    if not recommendations:
        console.print("[green]No optimization suggestions -- workflow looks efficient.[/green]")
        return

    console.print("[bold]Optimization Suggestions[/bold]")
    for rec in recommendations:
        style = _SEVERITY_STYLES.get(rec.severity, "white")
        console.print(f"  [{style}]*[/{style}] {rec.title}")
        extras = []
        if rec.tokens_saved:
            extras.append(f"~{rec.tokens_saved} tokens")
        if rec.cost_savings is not None:
            extras.append(f"~${rec.cost_savings:.4f} saved")
        suffix = f" ({', '.join(extras)})" if extras else ""
        console.print(f"    -- {rec.description}{suffix}")

    console.print(f"\n[bold]Estimated Savings:[/bold] {estimated_savings_pct:.0f}%")
    if cost_savings is not None:
        console.print(f"[bold]Estimated Cost Savings:[/bold] ${cost_savings:.4f}")
