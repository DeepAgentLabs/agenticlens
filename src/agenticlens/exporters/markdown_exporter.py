from pathlib import Path

from agenticlens.exporters.base import BaseExporter
from agenticlens.models.recommendation import Recommendation
from agenticlens.models.workflow import Workflow


class MarkdownExporter(BaseExporter):
    """Exports a workflow profiling report as a human-readable Markdown file."""

    def export(
        self,
        workflow: Workflow,
        path: str | Path | None = None,
        recommendations: list[Recommendation] | None = None,
    ) -> None:
        lines: list[str] = []
        safe_name = workflow.name.replace("|", "\\|").replace("\r", "").replace("\n", " ")
        lines.append(f"# Workflow Report: {safe_name}\n")

        # Summary section
        lines.append("## Summary\n")
        lines.append("| Metric | Value |")
        lines.append("| --- | --- |")
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

        def _md_cell(value: str) -> str:
            return value.replace("|", "\\|").replace("\r", "").replace("\n", "<br>")

        for i, s in enumerate(workflow.steps, 1):
            provider = _md_cell(s.provider) if s.provider else "-"
            model = _md_cell(s.model) if s.model else "-"
            lines.append(
                f"| {i} | {_md_cell(s.name)} | {s.type.value} | {provider} "
                f"| {model} | {s.metrics.prompt_tokens:,} "
                f"| {s.metrics.completion_tokens:,} | {s.metrics.total_tokens:,} "
                f"| {s.metrics.latency:.2f}s | {self._fmt_cost(s.metrics.cost)} |"
            )
        lines.append("")

        # Recommendations section
        if recommendations:
            lines.append("## Optimization Recommendations\n")
            for rec in recommendations:
                lines.append(f"### {rec.title}\n")
                lines.append(f"- **Severity:** {rec.severity.value}")
                lines.append(f"- **Tokens Saved:** {rec.tokens_saved:,}")
                if rec.confidence is not None:
                    lines.append(f"- **Confidence:** {rec.confidence:.0%}")
                if rec.quality_risk:
                    lines.append(f"- **Quality Risk:** {rec.quality_risk}")
                lines.append(f"\n{rec.description}\n")

        if path is None:
            raise ValueError("MarkdownExporter requires a path")
        Path(path).write_text("\n".join(lines), encoding="utf-8")

    @staticmethod
    def _fmt_cost(cost: float | None) -> str:
        if cost is None:
            return "-"
        return f"${cost:.6f}"
