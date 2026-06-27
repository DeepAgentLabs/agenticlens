from pathlib import Path

from tokenlens.exporters.base import BaseExporter
from tokenlens.models.workflow import Workflow


class JSONExporter(BaseExporter):
    def export(self, workflow: Workflow, path: str | Path) -> None:
        Path(path).write_text(workflow.model_dump_json(indent=2))
