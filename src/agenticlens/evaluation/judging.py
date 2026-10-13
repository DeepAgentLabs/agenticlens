"""Structured LLM-judge verdicts.

`LLMJudgeEvaluator` accepts any function that returns a `Score`. This module
adds a structured contract on top: the judge returns a `JudgeVerdict`
(verdict, confidence, and a factual-grounding breakdown), and
`structured_judge()` turns it into a `Score` whose metadata keeps every
field, so reports and calibration can read the judge's reasoning rather
than one number.

AgenticLens still never calls a model itself — the application supplies the
judge function and states which model it uses. The judge may also report
what its call cost (`JudgeVerdict.usage`); the score then records judge cost,
tokens, and latency so reports can show judge spend separately from the
cost of the agent under evaluation (see `analyze_scores()`).
"""

import hashlib
import time
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


class JudgeUsage(BaseModel):
    """What one judge call consumed, as reported by the application."""

    cost_usd: float | None = Field(default=None, ge=0)
    cost_source: Literal["measured", "estimated"] | None = None
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)


class JudgeVerdict(BaseModel):
    """What a judge concluded about one output, and why."""

    verdict: Verdict
    confidence: float = Field(ge=0, le=1)
    rationale: str = ""
    unsupported_claims: list[str] = Field(default_factory=list)
    evidence_missed: list[str] = Field(default_factory=list)
    usage: JudgeUsage | None = None
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


def prompt_fingerprint(prompt_template: str) -> str:
    """SHA-256 of a judge prompt template, recorded so prompt edits are visible."""
    return hashlib.sha256(prompt_template.encode("utf-8")).hexdigest()


def _usage_metadata(usage: JudgeUsage | None, latency_ms: float) -> dict[str, Any]:
    recorded: dict[str, Any] = {"judge_latency_ms": round(latency_ms, 3)}
    if usage is None:
        return recorded
    recorded["judge_input_tokens"] = usage.input_tokens
    recorded["judge_output_tokens"] = usage.output_tokens
    if usage.cost_usd is not None:
        recorded["judge_cost_usd"] = usage.cost_usd
        recorded["judge_cost_source"] = usage.cost_source or "estimated"
    return recorded


def structured_judge(
    name: str,
    judge: JudgeFunction,
    *,
    judge_model: str,
    version: str,
    verdict_values: Mapping[Verdict, float] | None = None,
    allow_self_judging: bool = False,
    judge_provider: str | None = None,
    prompt_version: str | None = None,
    prompt_template: str | None = None,
) -> LLMJudgeEvaluator:
    """Wrap a verdict-returning judge as an `LLMJudgeEvaluator`.

    The score value is the verdict's value (see `DEFAULT_VERDICT_VALUES`);
    confidence is recorded alongside, not multiplied in, so a confident
    "partially agree" stays distinguishable from an unsure "agree".

    When the judge model is the same as the model being evaluated, the judge
    is grading its own work. By default that case is scored as skipped with an
    explanation; pass `allow_self_judging=True` to score it anyway, in which
    case the score carries `self_confirmation_risk: True` in its metadata.

    Every score records the judge's model and, when given, its provider,
    `prompt_version`, and the SHA-256 of `prompt_template`, so a changed
    judge prompt is visible in saved reports. The judge call's wall-clock
    latency is measured; tokens and cost come from `JudgeVerdict.usage`.
    Without a reported cost, `analyze_scores()` estimates one from tokens
    and pricing when `judge_provider` is set.
    """
    if not judge_model.strip():
        raise ValueError("judge_model must not be empty")
    values = dict(DEFAULT_VERDICT_VALUES if verdict_values is None else verdict_values)
    missing = set(DEFAULT_VERDICT_VALUES) - set(values)
    if missing:
        raise ValueError(f"verdict_values is missing {sorted(missing)}")
    if any(not 0 <= value <= 1 for value in values.values()):
        raise ValueError("verdict_values must be between 0 and 1")
    judge_identity: dict[str, Any] = {"judge_model": judge_model}
    if judge_provider:
        judge_identity["judge_provider"] = judge_provider
    if prompt_version:
        judge_identity["judge_prompt_version"] = prompt_version
    if prompt_template is not None:
        judge_identity["judge_prompt_sha256"] = prompt_fingerprint(prompt_template)

    def _score(context: EvaluationContext) -> Score:
        target_model = evaluated_model(context)
        self_judging = _same_model(judge_model, target_model)
        if self_judging and not allow_self_judging:
            return Score.skip(
                name,
                f"Judge model {judge_model!r} is the model under evaluation; "
                "use a different judge model to avoid self-confirmation bias.",
                metadata={**judge_identity, "evaluated_model": target_model},
            )
        started = time.perf_counter()
        result = judge(context)
        latency_ms = (time.perf_counter() - started) * 1000
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
                **judge_identity,
                "evaluated_model": target_model,
                "self_confirmation_risk": self_judging,
                **_usage_metadata(result.usage, latency_ms),
            },
        )

    return LLMJudgeEvaluator(name, _score, version=version)


def judge_verdict(score: Score) -> JudgeVerdict | None:
    """Read the structured verdict back out of a score, if it has one."""
    payload = score.metadata.get("judge_verdict")
    return JudgeVerdict.model_validate(payload) if isinstance(payload, dict) else None
