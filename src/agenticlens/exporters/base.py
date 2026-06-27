from abc import ABC, abstractmethod
from pathlib import Path

from agenticlens.models.workflow import Workflow


class BaseExporter(ABC):
    """Interface for exporting a profiled Workflow to a file format."""

    @abstractmethod
    def export(self, workflow: Workflow, path: str | Path) -> None:
        raise NotImplementedError
