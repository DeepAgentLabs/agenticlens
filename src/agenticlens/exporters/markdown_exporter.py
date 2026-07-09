from pathlib import Path

from agenticlens.exporters.base import BaseExporter
from agenticlens.models.workflow import Workflow


class MarkdownExporter(BaseExporter):
    """Exports a workflow profiling report as a human-readable Markdown file."""

    def export(self, workflow: Workflow, path: str | Path) -> None:
        lines: list[str] = []
        lines.append(f"# Workflow Report: {workflow.name}\n")

        # Summary section
        lines.append("## Summary\n")
        lines.append(f"| Metric | Value |")
        lines.append(f"| --- | --- |")
        lines.append(f"| Total Tokens | {workflow.total_tokens:,} |")
        lines.append(f"| Total Cost | {self._fmt_cost(workflow.total_cost)} |")
        lines.append(f"| Latency | {workflow.latency:.2f}s |")
        lines.append(f"| Steps | {len(workflow.steps)} |")
        lines.append("")

        # Per-step breakdown
        lines.append("## Steps\n")
        lines.append(
            "| # | Name | Type | Provider | Model "
            "| Prompt Tokens | Completion Tokens | Total Tokens | Latency | Cost |"
        )
        lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        for i, s in enumerate(workflow.steps, 1):
            lines.append(
                f"| {i} | {s.name} | {s.type.value} | {s.provider or '-'} "
                f"| {s.model or '-'} | {s.metrics.prompt_tokens:,} "
                f"| {s.metrics.completion_tokens:,} | {s.metrics.total_tokens:,} "
                f"| {s.metrics.latency:.2f}s | {self._fmt_cost(s.metrics.cost)} |"
            )
        lines.append("")

        Path(path).write_text("\n".join(lines), encoding="utf-8")

    @staticmethod
    def _fmt_cost(cost: float | None) -> str:
        if cost is None:
            return "-"
        return f"${cost:.6f}"
