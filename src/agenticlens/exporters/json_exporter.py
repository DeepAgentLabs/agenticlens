import json
from pathlib import Path

from agenticlens.exporters.base import BaseExporter
from agenticlens.models.recommendation import Recommendation
from agenticlens.models.workflow import Workflow


class JSONExporter(BaseExporter):
    def export(
        self,
        workflow: Workflow,
        path: str | Path,
        recommendations: list[Recommendation] | None = None,
    ) -> None:
        data = json.loads(workflow.model_dump_json())
        if recommendations:
            data["recommendations"] = [
                rec.model_dump(exclude_none=True) for rec in recommendations
            ]
        Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")
