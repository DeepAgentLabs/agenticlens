from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from agenticlens.evaluation.models import (
    EvaluationSample,
    EvaluatorConfig,
    Score,
    TestCase,
)


@dataclass(frozen=True)
class EvaluationContext:
    case: TestCase
    sample: EvaluationSample
    config: EvaluatorConfig


class Evaluator(Protocol):
    @property
    def name(self) -> str: ...

    def evaluate(self, context: EvaluationContext) -> list[Score]: ...


EvaluationFunction = Callable[[EvaluationContext], Score | list[Score]]


class CallableEvaluator:
    """Adapt a trusted Python function to the unified evaluator contract."""

    def __init__(
        self,
        name: str,
        function: EvaluationFunction,
        *,
        evaluator_type: str = "custom",
    ) -> None:
        if not name:
            raise ValueError("evaluator name must not be empty")
        self._name = name
        self._function = function
        self._evaluator_type = evaluator_type

    @property
    def name(self) -> str:
        return self._name

    def evaluate(self, context: EvaluationContext) -> list[Score]:
        result = self._function(context)
        scores = result if isinstance(result, list) else [result]
        return [
            score.model_copy(
                update={
                    "evaluator_type": self._evaluator_type,
                    "passed": score.value >= context.config.threshold,
                    "required": context.config.required,
                }
            )
            for score in scores
        ]


class LLMJudgeEvaluator(CallableEvaluator):
    """Provider-neutral adapter for an application-supplied LLM judge function."""

    def __init__(self, name: str, judge: EvaluationFunction) -> None:
        super().__init__(name, judge, evaluator_type="llm_judge")


class EvaluatorRegistry:
    def __init__(self) -> None:
        self._evaluators: dict[str, Evaluator] = {}

    def register(self, evaluator: Evaluator, *, replace: bool = False) -> None:
        if evaluator.name in self._evaluators and not replace:
            raise ValueError(f"evaluator {evaluator.name!r} is already registered")
        self._evaluators[evaluator.name] = evaluator

    def get(self, name: str) -> Evaluator:
        try:
            return self._evaluators[name]
        except KeyError as exc:
            raise ValueError(f"evaluator {name!r} is not registered") from exc

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._evaluators))
