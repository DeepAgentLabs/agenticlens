"""Structured LLM-judge verdicts.

`LLMJudgeEvaluator` accepts any function that returns a `Score`. This module
adds a structured contract on top: the judge returns a `JudgeVerdict`
(verdict, confidence, and a factual-grounding breakdown), and
`structured_judge()` turns it into a `Score` whose metadata keeps every
field, so reports and calibration can read the judge's reasoning rather
than one number.

AgenticLens still never calls a model itself — the application supplies the
judge function and states which model it uses.
"""

from collections.abc import Callable, Mapping
from typing import Any, Literal

from agentic_evals import EvaluationContext, LLMJudgeEvaluator, Score
from pydantic import BaseModel, Field

Verdict = Literal["agree", "partially_agree", "disagree"]

#: Default score for each verdict before confidence is applied.
DEFAULT_VERDICT_VALUES: Mapping[Verdict, float] = {
    "agree": 1.0,
    "partially_agree": 0.5,
    "disagree": 0.0,
}

#: Keys checked, in order, in case metadata and then trace metadata for the
#: model that produced the output under evaluation.
EVALUATED_MODEL_KEYS = ("evaluated_model", "model", "model_name")


class JudgeVerdict(BaseModel):
    """What a judge concluded about one output, and why."""

    verdict: Verdict
    confidence: float = Field(ge=0, le=1)
    rationale: str = ""
    unsupported_claims: list[str] = Field(default_factory=list)
    evidence_missed: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


JudgeFunction = Callable[[EvaluationContext], JudgeVerdict]


def evaluated_model(context: EvaluationContext) -> str | None:
    """The model that produced the judged output, if the case or trace says."""
    for source in (context.case.metadata, context.sample.trace.metadata):
        for key in EVALUATED_MODEL_KEYS:
            value = source.get(key)
            if isinstance(value, str) and value:
                return value
    return None


def _same_model(judge_model: str, other: str | None) -> bool:
    return other is not None and judge_model.strip().casefold() == other.strip().casefold()


def structured_judge(
    name: str,
    judge: JudgeFunction,
    *,
    judge_model: str,
    version: str,
    verdict_values: Mapping[Verdict, float] | None = None,
    allow_self_judging: bool = False,
) -> LLMJudgeEvaluator:
    """Wrap a verdict-returning judge as an `LLMJudgeEvaluator`.

    The score value is the verdict's value (see `DEFAULT_VERDICT_VALUES`);
    confidence is recorded alongside, not multiplied in, so a confident
    "partially agree" stays distinguishable from an unsure "agree".

    When the judge model is the same as the model being evaluated, the judge
    is grading its own work. By default that case is scored as skipped with an
    explanation; pass `allow_self_judging=True` to score it anyway, in which
    case the score carries `self_confirmation_risk: True` in its metadata.
    """
    if not judge_model.strip():
        raise ValueError("judge_model must not be empty")
    values = dict(DEFAULT_VERDICT_VALUES if verdict_values is None else verdict_values)
    missing = set(DEFAULT_VERDICT_VALUES) - set(values)
    if missing:
        raise ValueError(f"verdict_values is missing {sorted(missing)}")
    if any(not 0 <= value <= 1 for value in values.values()):
        raise ValueError("verdict_values must be between 0 and 1")

    def _score(context: EvaluationContext) -> Score:
        target_model = evaluated_model(context)
        self_judging = _same_model(judge_model, target_model)
        if self_judging and not allow_self_judging:
            return Score.skip(
                name,
                f"Judge model {judge_model!r} is the model under evaluation; "
                "use a different judge model to avoid self-confirmation bias.",
                metadata={"judge_model": judge_model, "evaluated_model": target_model},
            )
        result = judge(context)
        value = values[result.verdict]
        grounding = (
            f" {len(result.unsupported_claims)} unsupported claim(s),"
            f" {len(result.evidence_missed)} missed evidence item(s)."
            if result.unsupported_claims or result.evidence_missed
            else ""
        )
        return Score(
            name=name,
            value=value,
            passed=value >= context.config.threshold,
            explanation=(
                f"Judge verdict {result.verdict!r} at confidence {result.confidence:.2f}."
                f"{grounding} {result.rationale}".strip()
            ),
            metadata={
                "judge_verdict": result.model_dump(mode="json"),
                "judge_model": judge_model,
                "evaluated_model": target_model,
                "self_confirmation_risk": self_judging,
            },
        )

    return LLMJudgeEvaluator(name, _score, version=version)


def judge_verdict(score: Score) -> JudgeVerdict | None:
    """Read the structured verdict back out of a score, if it has one."""
    payload = score.metadata.get("judge_verdict")
    return JudgeVerdict.model_validate(payload) if isinstance(payload, dict) else None
