from rich.console import Console
from rich.table import Table
from rich.tree import Tree

from agenticlens.analysis import analyze_trace, next_best_analyses
from agenticlens.metrics.trace import (
    latency_by_span_type,
    retry_count,
    tokens_by_span_type,
    tool_call_count,
)
from agenticlens.models.trace import Run, Span


def _escape_markdown_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\r", "").replace("\n", "<br>")


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
                "; ".join(
                    f"{item.source}: {item.reasoning or item.details}" for item in finding.evidence
                ),
            )
        console.print(finding_table)
        suggestions = next_best_analyses(findings)
        if suggestions:
            console.print("[bold]Next Best Analysis[/bold]")
            for suggestion in suggestions:
                console.print(f"  • {suggestion}")


def render_trace_markdown(run: Run) -> str:
    findings = analyze_trace(run)
    lines = [
        f"# Trace Report: {run.application_name}",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Run ID | `{run.run_id}` |",
        f"| Status | {run.status.value} |",
        f"| Total tokens | {run.total_tokens} |",
        f"| Latency (ms) | {run.total_latency_ms:.1f} |",
        f"| Retries | {retry_count(run)} |",
        f"| Tool calls | {tool_call_count(run)} |",
        "",
        "## Spans",
        "",
        "| Name | Type | Parent | Tokens | Latency (ms) | Status |",
        "| --- | --- | --- | ---: | ---: | --- |",
    ]
    for span in run.spans:
        lines.append(
            f"| {_escape_markdown_cell(span.name)} | {span.span_type.value} "
            f"| {_escape_markdown_cell(span.parent_span_id or '-')} "
            f"| {span.total_tokens} | {span.latency_ms:.1f} | {span.status.value} |"
        )
    if findings:
        lines.extend(["", "## Findings", ""])
        for finding in findings:
            lines.append(f"### {finding.title}")
            lines.append("")
            lines.append(f"- Severity: {finding.severity}")
            lines.append(f"- Category: {finding.category}")
            lines.append(f"- Confidence: {finding.confidence:.2f}")
            if finding.span_ids:
                lines.append(f"- Spans: {', '.join(finding.span_ids)}")
            for item in finding.evidence:
                lines.append(f"- Evidence ({item.source}): {item.reasoning or item.details}")
            lines.append("")
        suggestions = next_best_analyses(findings)
        if suggestions:
            lines.extend(["## Next Best Analysis", ""])
            lines.extend([f"- {suggestion}" for suggestion in suggestions])
            lines.append("")
    return "\n".join(lines) + "\n"
