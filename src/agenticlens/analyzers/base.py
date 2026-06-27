from abc import ABC, abstractmethod
from typing import Any

from tokenlens.models.workflow import Workflow


class BaseAnalyzer(ABC):
    """Interface for workflow analysis / pattern detection.

    Concrete analyzers (duplicate-prompt detection, chunk-utility scoring, ...)
    are implemented after the project scaffold lands -- see the MVP Heuristic
    Rules table in TokenLens_Spec.md.
    """

    @abstractmethod
    def analyze(self, workflow: Workflow) -> dict[str, Any]:
        raise NotImplementedError
