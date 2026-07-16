import csv
from pathlib import Path

from agenticlens.exporters.base import BaseExporter
from agenticlens.models.recommendation import Recommendation
from agenticlens.models.workflow import Workflow

STEP_FIELDNAMES = [
    "step_id",
    "step_name",
    "step_type",
    "agent_name",
    "agent_role",
    "parent_step_id",
    "handoff_from",
    "handoff_to",
    "provider",
    "model",
    "prompt_tokens",
    "completion_tokens",
    "total_tokens",
    "latency",
    "ttft",
    "cost",
]

RECOMMENDATION_FIELDNAMES = [
    "title",
    "optimization_type",
    "step_id",
    "step_name",
    "step_type",
    "severity",
    "tokens_saved",
    "estimated_savings",
    "estimated_usd_savings",
    "estimated_monthly_savings",
    "confidence",
    "quality_risk",
    "description",
]


class CSVExporter(BaseExporter):
    """Exports a per-step breakdown of a workflow to CSV.

    If recommendations are provided, a second file is written alongside
    with a '_recommendations' suffix containing the optimization suggestions.
    """

    def export(
        self,
        workflow: Workflow,
        path: str | Path | None = None,
        recommendations: list[Recommendation] | None = None,
    ) -> None:
        if path is None:
            raise ValueError("CSVExporter requires a path")
        path = Path(path)
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=STEP_FIELDNAMES)
            writer.writeheader()
            for s in workflow.steps:
                writer.writerow(
                    {
                        "step_id": s.id,
                        "step_name": s.name,
                        "step_type": s.type.value,
                        "agent_name": s.agent_name,
                        "agent_role": s.agent_role,
                        "parent_step_id": s.parent_step_id,
                        "handoff_from": s.handoff_from,
                        "handoff_to": s.handoff_to,
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

        if recommendations:
            rec_path = path.with_name(f"{path.stem}_recommendations{path.suffix}")
            with rec_path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=RECOMMENDATION_FIELDNAMES)
                writer.writeheader()
                for rec in recommendations:
                    writer.writerow(
                        {
                            "title": rec.title,
                            "optimization_type": rec.optimization_type,
                            "step_id": rec.step_id,
                            "step_name": rec.step_name,
                            "step_type": rec.step_type,
                            "severity": rec.severity.value,
                            "tokens_saved": rec.tokens_saved,
                            "estimated_savings": rec.estimated_savings,
                            "estimated_usd_savings": rec.estimated_usd_savings,
                            "estimated_monthly_savings": rec.estimated_monthly_savings,
                            "confidence": rec.confidence,
                            "quality_risk": rec.quality_risk,
                            "description": rec.description,
                        }
                    )
