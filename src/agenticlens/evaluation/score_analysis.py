"""Score analysis: deterministic vs model-based results, judge cost, and disagreement.

An `EvaluationReport` mixes deterministic checks with model-based judges.
`analyze_scores()` reports them separately, totals what the judges cost (kept
apart from the cost of the agent under evaluation), and shows where
evaluators disagree on the same case.

Judge cost is read from score metadata. `structured_judge()` records it from
the verdict's `usage`; any other judge can set the same keys itself:

- ``judge_cost_usd``: cost of the judge call, if known
- ``judge_cost_source``: ``measured`` (provider-reported) or ``estimated``
- ``judge_input_tokens`` / ``judge_output_tokens``
- ``judge_latency_ms``
- ``judge_model`` / ``judge_provider``

When a judge reports tokens and its model but no cost, the cost is
estimated from AgenticLens pricing and labeled ``estimated``.
"""

import warnings
from collections import defaultdict
from itertools import combinations
from typing import Any, Literal

from agentic_evals import EvaluationReport, Score
from pydantic import BaseModel, Field

from agenticlens.config.pricing import UnknownModelPricingWarning, calculate_cost

ScoreKind = Literal["deterministic", "model_based"]

#: `Score.evaluator_type` values produced by model-graded evaluators.
MODEL_BASED_TYPES = frozenset({"llm_judge", "llm_rubric"})
DETERMINISTIC_UNIT = "deterministic"


def score_kind(score: Score) -> ScoreKind:
    """``model_based`` for LLM judges and rubrics, otherwise ``deterministic``."""
    if score.evaluator_type in MODEL_BASED_TYPES or "judge_model" in score.metadata:
        return "model_based"
    return "deterministic"


class KindSummary(BaseModel):
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    pass_rate: float | None = None
    average_score: float | None = None
    evaluators: list[str] = Field(default_factory=list)


class JudgeCost(BaseModel):
    evaluator: str
    judge_models: list[str] = Field(default_factory=list)
    scores: int = 0
    priced_scores: int = 0
    total_cost_usd: float | None = Field(
        default=None, description="Sum over priced scores; None when no score is priced."
    )
    cost_sources: dict[str, int] = Field(default_factory=dict)
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: float = 0.0


class JudgeCostSummary(BaseModel):
    judge_scores: int = Field(default=0, description="Judge scores from an actual judge call.")
    skipped_scores: int = Field(
        default=0,
        description="Judge scores skipped before any call (e.g. self-judging); not costed.",
    )
    priced_scores: int = 0
    complete: bool = Field(
        default=True, description="True when every judge score has a known cost."
    )
    total_cost_usd: float | None = None
    cost_per_case_usd: float | None = None
    evaluators: list[JudgeCost] = Field(default_factory=list)


class Disagreement(BaseModel):
    case_id: str
    passing: list[str]
    failing: list[str]
    deterministic_vs_model: bool = Field(
        description="True when the deterministic checks and a model judge disagree."
    )
    details: dict[str, str] = Field(default_factory=dict)


class PairwiseAgreement(BaseModel):
    evaluator_a: str
    evaluator_b: str
    shared_cases: int
    agreements: int
    agreement_rate: float | None


class ScoreAnalysis(BaseModel):
    deterministic: KindSummary
    model_based: KindSummary
    judge_cost: JudgeCostSummary
    agent_cost_usd: float | None = Field(
        default=None, description="Cost of the evaluated runs, from the report summary."
    )
    comparable_cases: int = Field(
        default=0, description="Cases where at least two evaluator units gave a verdict."
    )
    disagreement_cases: int = 0
    disagreement_rate: float | None = None
    disagreements: list[Disagreement] = Field(default_factory=list)
    pairwise_agreement: list[PairwiseAgreement] = Field(default_factory=list)


def _unit(score: Score) -> str:
    """The evaluator unit a score votes for.

    All deterministic checks vote together as one unit; each model-based
    evaluator votes on its own, so two judges can disagree with each other.
    """
    if score_kind(score) == "deterministic":
        return DETERMINISTIC_UNIT
    return score.evaluator or score.name


def _summarize(scores: list[Score]) -> KindSummary:
    active = [s for s in scores if not s.skipped]
    passed = sum(s.passed for s in active)
    return KindSummary(
        total=len(scores),
        passed=passed,
        failed=len(active) - passed,
        skipped=len(scores) - len(active),
        pass_rate=passed / len(active) if active else None,
        average_score=sum(s.value for s in active) / len(active) if active else None,
        evaluators=sorted({s.evaluator or s.name for s in scores}),
    )


def _number(value: Any) -> float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    return None


def judge_usage(score: Score) -> tuple[float | None, str | None, int, int, float]:
    """(cost, cost source, input tokens, output tokens, latency) recorded on a score."""
    meta = score.metadata
    cost = _number(meta.get("judge_cost_usd"))
    source = meta.get("judge_cost_source")
    input_tokens = int(_number(meta.get("judge_input_tokens")) or 0)
    output_tokens = int(_number(meta.get("judge_output_tokens")) or 0)
    latency = _number(meta.get("judge_latency_ms")) or 0.0
    model = meta.get("judge_model")
    provider = meta.get("judge_provider")
    if (
        cost is None
        and (input_tokens or output_tokens)
        and isinstance(model, str)
        and isinstance(provider, str)
    ):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UnknownModelPricingWarning)
            cost = calculate_cost(provider, model, input_tokens, output_tokens)
        source = "estimated" if cost is not None else None
    if cost is not None and source not in ("measured", "estimated"):
        source = "estimated"
    return cost, (source if cost is not None else None), input_tokens, output_tokens, latency


def _judge_costs(all_scores: list[Score], total_cases: int) -> JudgeCostSummary:
    per: dict[str, JudgeCost] = {}
    scores = [s for s in all_scores if not s.skipped]
    for score in scores:
        name = score.evaluator or score.name
        entry = per.setdefault(name, JudgeCost(evaluator=name))
        cost, source, input_tokens, output_tokens, latency = judge_usage(score)
        entry.scores += 1
        entry.input_tokens += input_tokens
        entry.output_tokens += output_tokens
        entry.latency_ms += latency
        model = score.metadata.get("judge_model")
        if isinstance(model, str) and model not in entry.judge_models:
            entry.judge_models.append(model)
        if cost is not None and source is not None:
            entry.priced_scores += 1
            entry.total_cost_usd = (entry.total_cost_usd or 0.0) + cost
            entry.cost_sources[source] = entry.cost_sources.get(source, 0) + 1
    priced = sum(e.priced_scores for e in per.values())
    costs = [e.total_cost_usd for e in per.values() if e.total_cost_usd is not None]
    total = sum(costs) if costs else None
    return JudgeCostSummary(
        judge_scores=len(scores),
        skipped_scores=len(all_scores) - len(scores),
        priced_scores=priced,
        complete=priced == len(scores),
        total_cost_usd=total,
        cost_per_case_usd=(
            total / total_cases
            if total is not None and total_cases and priced == len(scores)
            else None
        ),
        evaluators=sorted(per.values(), key=lambda e: e.evaluator),
    )


def analyze_scores(report: EvaluationReport) -> ScoreAnalysis:
    """Split scores by kind, total judge cost, and find evaluator disagreement."""
    all_scores = [score for case in report.cases for score in case.scores]
    deterministic = [s for s in all_scores if score_kind(s) == "deterministic"]
    model_based = [s for s in all_scores if score_kind(s) == "model_based"]

    verdicts: dict[str, dict[str, bool]] = {}
    disagreements: list[Disagreement] = []
    for case in report.cases:
        units: dict[str, list[Score]] = defaultdict(list)
        for score in case.scores:
            if not score.skipped:
                units[_unit(score)].append(score)
        case_votes = {unit: all(s.passed for s in scores) for unit, scores in units.items()}
        verdicts[case.case_id] = case_votes
        if len(case_votes) < 2 or len(set(case_votes.values())) < 2:
            continue
        passing = sorted(u for u, ok in case_votes.items() if ok)
        failing = sorted(u for u, ok in case_votes.items() if not ok)
        disagreements.append(
            Disagreement(
                case_id=case.case_id,
                passing=passing,
                failing=failing,
                deterministic_vs_model=DETERMINISTIC_UNIT in case_votes
                and any(case_votes[u] != case_votes[DETERMINISTIC_UNIT] for u in case_votes),
                details={
                    unit: "; ".join(s.explanation for s in units[unit] if not s.passed) or "passed"
                    for unit in sorted(case_votes)
                },
            )
        )

    unit_names = sorted({unit for votes in verdicts.values() for unit in votes})
    pairwise: list[PairwiseAgreement] = []
    for first, second in combinations(unit_names, 2):
        shared = [v for v in verdicts.values() if first in v and second in v]
        agreements = sum(v[first] == v[second] for v in shared)
        pairwise.append(
            PairwiseAgreement(
                evaluator_a=first,
                evaluator_b=second,
                shared_cases=len(shared),
                agreements=agreements,
                agreement_rate=agreements / len(shared) if shared else None,
            )
        )
    comparable = sum(len(v) >= 2 for v in verdicts.values())
    return ScoreAnalysis(
        deterministic=_summarize(deterministic),
        model_based=_summarize(model_based),
        judge_cost=_judge_costs(model_based, report.summary.total_cases),
        agent_cost_usd=report.summary.total_cost_usd,
        comparable_cases=comparable,
        disagreement_cases=len(disagreements),
        disagreement_rate=len(disagreements) / comparable if comparable else None,
        disagreements=disagreements,
        pairwise_agreement=pairwise,
    )
