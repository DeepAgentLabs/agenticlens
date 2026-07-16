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
    table.add_column("Agent")
    table.add_column("Type")
    table.add_column("Prompt", justify="right")
    table.add_column("Completion", justify="right")
    table.add_column("Cost", justify="right")
    table.add_column("Latency", justify="right")

    for step in workflow.steps:
        cost_display = f"${step.metrics.cost:.4f}" if step.metrics.cost is not None else "n/a"
        table.add_row(
            step.name,
            step.agent_name or "-",
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
    workflow: Workflow | None = None,
) -> None:
    """Render optimization suggestions and the aggregate estimated savings."""
    if not recommendations:
        console.print("[green]No optimization suggestions -- workflow looks efficient.[/green]")
        return

    total_usd_savings = sum(rec.estimated_usd_savings or 0.0 for rec in recommendations)
    total_monthly_savings = sum(rec.estimated_monthly_savings or 0.0 for rec in recommendations)
    if workflow is not None and workflow.total_cost is not None:
        console.print(
            "[bold]Budget Optimization[/bold] "
            f"Run cost: ${workflow.total_cost:.4f}; "
            f"reducible: ~${total_usd_savings:.4f}/run "
            f"({estimated_savings_pct:.0f}%), "
            f"~${total_monthly_savings:.2f}/month."
        )
        console.print()

    console.print("[bold]Optimization Suggestions[/bold]")
    for rec in recommendations:
        style = _SEVERITY_STYLES.get(rec.severity, "white")
        console.print(f"  [{style}]*[/{style}] {rec.title}")
        details = [f"~{rec.tokens_saved} tokens"]
        if rec.estimated_usd_savings is not None:
            details.append(f"~${rec.estimated_usd_savings:.4f}/run")
        if rec.estimated_monthly_savings is not None:
            details.append(f"~${rec.estimated_monthly_savings:.2f}/month")
        if rec.confidence is not None:
            details.append(f"{rec.confidence:.0%} confidence")
        if rec.quality_risk:
            details.append(f"{rec.quality_risk} quality risk")
        console.print(f"    -- {rec.description} ({', '.join(details)})")

    console.print(f"\n[bold]Estimated Savings:[/bold] {estimated_savings_pct:.0f}%")


def render_token_optimization(
    console: Console,
    workflow: Workflow,
    recommendations: list[Recommendation],
) -> None:
    """Render token savings grouped by workflow step."""
    token_recommendations = [rec for rec in recommendations if rec.tokens_saved > 0]
    if not token_recommendations:
        console.print("[green]No step-level token waste detected.[/green]")
        return

    by_step: dict[str, list[Recommendation]] = {}
    for rec in token_recommendations:
        key = rec.step_id or rec.step_name or "workflow"
        by_step.setdefault(key, []).append(rec)

    table = Table(title="Step Token Optimization", box=box.SIMPLE_HEAVY)
    table.add_column("Step")
    table.add_column("Type")
    table.add_column("Step Tokens", justify="right")
    table.add_column("Reducible", justify="right")
    table.add_column("Savings", justify="right")
    table.add_column("Primary Fix")

    rendered_steps: set[str] = set()
    for step in workflow.steps:
        recs = by_step.get(step.id) or by_step.get(step.name) or []
        if not recs:
            continue
        rendered_steps.add(step.id)
        tokens_saved = sum(rec.tokens_saved for rec in recs)
        token_basis = _step_token_basis(step.metrics.total_tokens, recs)
        savings_pct = min(100.0, (tokens_saved / token_basis) * 100) if token_basis else 0.0
        primary = max(recs, key=lambda rec: rec.tokens_saved)
        table.add_row(
            step.name,
            step.type.value,
            f"{token_basis:,}",
            f"~{tokens_saved:,}",
            f"{savings_pct:.0f}%",
            _fix_label(primary),
        )

    for key, recs in by_step.items():
        if key in rendered_steps:
            continue
        tokens_saved = sum(rec.tokens_saved for rec in recs)
        primary = max(recs, key=lambda rec: rec.tokens_saved)
        table.add_row(
            primary.step_name or "Workflow",
            primary.step_type or "-",
            "-",
            f"~{tokens_saved:,}",
            "-",
            _fix_label(primary),
        )

    console.print(table)


def render_agent_summary(console: Console, workflow: Workflow) -> None:
    """Render token/cost totals grouped by agent for multi-agent workflows."""
    agent_steps = [step for step in workflow.steps if step.agent_name]
    if not agent_steps:
        return

    grouped: dict[str, dict[str, float | int]] = {}
    for step in agent_steps:
        assert step.agent_name is not None
        data = grouped.setdefault(
            step.agent_name,
            {"steps": 0, "tokens": 0, "cost": 0.0, "has_cost": 0},
        )
        data["steps"] = int(data["steps"]) + 1
        data["tokens"] = int(data["tokens"]) + step.metrics.total_tokens
        if step.metrics.cost is not None:
            data["cost"] = float(data["cost"]) + step.metrics.cost
            data["has_cost"] = int(data["has_cost"]) + 1

    table = Table(title="Agent Token Summary", box=box.SIMPLE_HEAVY)
    table.add_column("Agent")
    table.add_column("Steps", justify="right")
    table.add_column("Tokens", justify="right")
    table.add_column("Share", justify="right")
    table.add_column("Cost", justify="right")

    total_tokens = sum(int(data["tokens"]) for data in grouped.values())
    for agent_name, data in sorted(
        grouped.items(),
        key=lambda item: int(item[1]["tokens"]),
        reverse=True,
    ):
        tokens = int(data["tokens"])
        share = (tokens / total_tokens) * 100 if total_tokens else 0.0
        cost_display = f"${float(data['cost']):.4f}" if int(data["has_cost"]) else "n/a"
        table.add_row(
            agent_name,
            f"{int(data['steps'])}",
            f"{tokens:,}",
            f"{share:.0f}%",
            cost_display,
        )

    console.print(table)


def _fix_label(rec: Recommendation) -> str:
    labels = {
        "prompt_caching": "Cache or dedupe repeated prompt prefix",
        "rag_top_k_reduction": "Lower RAG top-k",
        "rag_chunk_pruning": "Prune or rerank low-utility chunks",
        "memory_summarization": "Summarize or truncate history",
        "tool_result_caching": "Cache duplicate tool result",
        "agent_handoff_summarization": "Summarize agent handoff context",
    }
    return labels.get(rec.optimization_type, rec.title)


def _step_token_basis(step_tokens: int, recommendations: list[Recommendation]) -> int:
    """Use retrieved context tokens for RAG steps whose LLM metrics are recorded later."""
    context_tokens = [
        value
        for rec in recommendations
        if isinstance((value := rec.metadata.get("retrieved_context_tokens")), int)
    ]
    if context_tokens:
        return max(step_tokens, max(context_tokens))
    return step_tokens
