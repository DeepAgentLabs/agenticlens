from pathlib import Path

from agenticlens.exporters.base import BaseExporter
from agenticlens.models.workflow import Workflow


class JSONExporter(BaseExporter):
    def export(self, workflow: Workflow, path: str | Path) -> None:
        Path(path).write_text(workflow.model_dump_json(indent=2))
