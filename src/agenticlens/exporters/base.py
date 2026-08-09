from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agenticlens.models.recommendation import Recommendation

from agenticlens.models.workflow import Workflow


class BaseExporter(ABC):
    """Interface for exporting a profiled Workflow to a file format."""

    @abstractmethod
    def export(
        self,
        workflow: Workflow,
        path: str | Path | None = None,
        recommendations: list[Recommendation] | None = None,
    ) -> None:
        raise NotImplementedError
