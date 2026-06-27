import csv
from pathlib import Path

from agenticlens.exporters.base import BaseExporter
from agenticlens.models.workflow import Workflow

FIELDNAMES = [
    "step_id",
    "step_name",
    "step_type",
    "provider",
    "model",
    "prompt_tokens",
    "completion_tokens",
    "total_tokens",
    "latency",
    "ttft",
    "cost",
]


class CSVExporter(BaseExporter):
    """Exports a per-step breakdown of a workflow to CSV."""

    def export(self, workflow: Workflow, path: str | Path) -> None:
        with Path(path).open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            for s in workflow.steps:
                writer.writerow(
                    {
                        "step_id": s.id,
                        "step_name": s.name,
                        "step_type": s.type.value,
                        "provider": s.provider,
                        "model": s.model,
                        "prompt_tokens": s.metrics.prompt_tokens,
                        "completion_tokens": s.metrics.completion_tokens,
                        "total_tokens": s.metrics.total_tokens,
                        "latency": s.metrics.latency,
                        "ttft": s.metrics.ttft,
                        "cost": s.metrics.cost,
                    }
                )
