from abc import ABC, abstractmethod

from agenticlens.config.settings import RecommenderConfig
from agenticlens.models.recommendation import Recommendation
from agenticlens.models.workflow import Workflow


class BaseRecommender(ABC):
    """Interface for a single heuristic recommendation rule."""

    @abstractmethod
    def evaluate(self, workflow: Workflow, config: RecommenderConfig) -> list[Recommendation]:
        raise NotImplementedError
