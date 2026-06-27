from abc import ABC, abstractmethod

from tokenlens.config.settings import RecommenderConfig
from tokenlens.models.recommendation import Recommendation
from tokenlens.models.workflow import Workflow


class BaseRecommender(ABC):
    """Interface for a single heuristic recommendation rule."""

    @abstractmethod
    def evaluate(self, workflow: Workflow, config: RecommenderConfig) -> list[Recommendation]:
        raise NotImplementedError
