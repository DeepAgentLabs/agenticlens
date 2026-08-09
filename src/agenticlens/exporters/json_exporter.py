import json
from pathlib import Path

from agenticlens.exporters.base import BaseExporter
from agenticlens.models.recommendation import Recommendation
from agenticlens.models.workflow import Workflow


class JSONExporter(BaseExporter):
    def export(
        self,
        workflow: Workflow,
        path: str | Path | None = None,
        recommendations: list[Recommendation] | None = None,
    ) -> None:
        data = workflow.model_dump(mode="json")
        if recommendations:
            data["recommendations"] = [
                rec.model_dump(mode="json", exclude_none=True) for rec in recommendations
            ]
        if path is None:
            raise ValueError("JSONExporter requires a path")
        Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")
