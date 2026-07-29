from rich.console import Console
from rich.table import Table
from rich.tree import Tree

from agenticlens.analysis import analyze_trace
from agenticlens.metrics.trace import (
    latency_by_span_type,
    retry_count,
    tokens_by_span_type,
    tool_call_count,
)
from agenticlens.models.trace import Run, Span


def _span_label(span: Span) -> str:
    status = "green" if span.status.value == "succeeded" else "red"
    return (
        f"[{status}]{span.name}[/{status}] ({span.span_type.value}) "
        f"{span.total_tokens} tokens, {span.latency_ms:.1f} ms"
    )


def _tree(run: Run) -> Tree:
    root = Tree(f"[bold]{run.application_name}[/bold] [{run.status.value}]")
    nodes: dict[str, Tree] = {}
    for span in run.spans:
        parent = nodes.get(span.parent_span_id) if span.parent_span_id else None
        nodes[span.span_id] = (parent or root).add(_span_label(span))
    return root


def render_trace(console: Console, run: Run) -> None:
    summary = Table(title="Run Summary", show_header=False)
    summary.add_column("Metric")
    summary.add_column("Value", justify="right")
    summary.add_row("Run ID", run.run_id)
    summary.add_row("Status", run.status.value)
    summary.add_row("Total tokens", str(run.total_tokens))
    summary.add_row("Latency", f"{run.total_latency_ms:.1f} ms")
    summary.add_row("Retries", str(retry_count(run)))
    summary.add_row("Tool calls", str(tool_call_count(run)))
    if run.error_type:
        summary.add_row("Error", run.error_type)
    console.print(summary)
    console.print(_tree(run))

    distribution = Table(title="Distribution")
    distribution.add_column("Span type")
    distribution.add_column("Tokens", justify="right")
    distribution.add_column("Latency", justify="right")
    token_totals = tokens_by_span_type(run)
    latency_totals = latency_by_span_type(run)
    for span_type in sorted(set(token_totals) | set(latency_totals), key=lambda item: item.value):
        distribution.add_row(
            span_type.value,
            str(token_totals.get(span_type, 0)),
            f"{latency_totals.get(span_type, 0.0):.1f} ms",
        )
    console.print(distribution)
    findings = analyze_trace(run)
    if findings:
        finding_table = Table(title="Findings")
        finding_table.add_column("Severity")
        finding_table.add_column("Finding")
        finding_table.add_column("Evidence")
        for finding in findings:
            finding_table.add_row(
                finding.severity,
                finding.title,
                ", ".join(f"{key}={value}" for key, value in finding.evidence.items()),
            )
        console.print(finding_table)
