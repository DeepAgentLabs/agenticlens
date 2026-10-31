"""Deterministic optimization rules over recorded traces.

Every rule reads only what the trace records. A saving is projected from the
spans it would remove or shrink; a missing measurement skips the span instead
of being guessed.
"""

import hashlib
import json
from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol

from agenticlens.modelfit.models import Confidence
from agenticlens.models.trace import Run, Span, SpanType
from agenticlens.optimization.models import (
    Opportunity,
    OpportunityEvidence,
    OptimizationArea,
    OptimizationConfig,
    ProjectedBenefit,
    QualityRisk,
)

_LEVELS: tuple[Confidence, ...] = ("low", "medium", "high")
_WORK_SPANS = {SpanType.MODEL_CALL, SpanType.TOOL_CALL, SpanType.RETRIEVAL, SpanType.PLANNING}
_HANDOFF_TARGET_KEYS = ("to_agent", "target_agent", "handoff.to", "handoff_to")


class OptimizationRule(Protocol):
    rule_id: str
    version: str

    def analyze(self, runs: Sequence[Run], config: OptimizationConfig) -> list[Opportunity]: ...


def fingerprint(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, ensure_ascii=True, default=str)
    return hashlib.sha256(encoded.encode()).hexdigest()


def opportunity_id(rule_id: str, subject: dict[str, Any]) -> str:
    return f"{rule_id}-{fingerprint(subject)[:12]}"


def input_fingerprint(span: Span) -> str | None:
    if span.input_reference:
        return "ref:" + span.input_reference
    if span.input_data is not None:
        return "data:" + fingerprint(span.input_data)
    return None


def output_fingerprint(span: Span) -> str | None:
    if span.output_reference:
        return "ref:" + span.output_reference
    if span.output_data is not None:
        return "data:" + fingerprint(span.output_data)
    return None


def _first(attributes: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in attributes:
            return attributes[key]
    return None


def _int(value: Any) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else None


def subtree(run: Run, root: Span) -> list[Span]:
    children: dict[str, list[Span]] = defaultdict(list)
    for span in run.spans:
        if span.parent_span_id:
            children[span.parent_span_id].append(span)
    found: list[Span] = []
    pending = [root]
    while pending:
        span = pending.pop()
        found.append(span)
        pending.extend(children.get(span.span_id, []))
    return found


def run_cost_per_token(run: Run) -> float | None:
    cost = run.estimated_cost_usd
    return cost / run.total_tokens if cost is not None and run.total_tokens else None


@dataclass
class Savings:
    """Accumulated savings; one unknown cost makes the whole cost unknown."""

    tokens: float = 0.0
    cost: float | None = 0.0
    latency_ms: float = 0.0
    evidence: list[OpportunityEvidence] = field(default_factory=list)

    def add(self, tokens: float, cost: float | None, latency_ms: float = 0.0) -> None:
        self.tokens += tokens
        self.latency_ms += latency_ms
        self.cost = None if cost is None or self.cost is None else self.cost + cost

    def add_spans(self, spans: Iterable[Span]) -> None:
        for span in spans:
            self.add(span.total_tokens, span.estimated_cost_usd, span.latency_ms)


def grade_confidence(
    runs_affected: int,
    runs_observed: int,
    cost_available: bool,
    config: OptimizationConfig,
    *,
    cap: Confidence | None = None,
    reasons: Sequence[str] = (),
) -> tuple[Confidence, list[str]]:
    share = runs_affected / runs_observed if runs_observed else 0.0
    notes = [f"Observed in {runs_affected} of {runs_observed} runs ({share:.0%})."]
    if (
        runs_affected >= config.high_confidence_min_runs
        and share >= config.high_confidence_min_share
    ):
        level: Confidence = "high"
    elif runs_affected >= 2:
        level = "medium"
    else:
        level = "low"
        notes.append("Seen in a single run; repeat on more traffic before adopting.")
    if not cost_available and level == "high":
        level = "medium"
        notes.append("Cost evidence is incomplete, so the saving cannot be priced.")
    if cap is not None and _LEVELS.index(level) > _LEVELS.index(cap):
        level = cap
    notes.extend(reasons)
    return level, notes


def build_opportunity(
    rule: OptimizationRule,
    *,
    area: OptimizationArea,
    kind: str,
    title: str,
    summary: str,
    action: str,
    subject: dict[str, Any],
    thresholds: dict[str, Any],
    runs: Sequence[Run],
    savings: Savings,
    basis: str,
    config: OptimizationConfig,
    risks: list[QualityRisk],
    confidence_cap: Confidence | None = None,
    confidence_reasons: Sequence[str] = (),
) -> Opportunity:
    observed = len(runs)
    affected = len({item.run_id for item in savings.evidence})
    cost_per_run = savings.cost / observed if savings.cost is not None and observed else None
    monthly = (
        cost_per_run * config.monthly_runs
        if cost_per_run is not None and config.monthly_runs is not None
        else None
    )
    level, reasons = grade_confidence(
        affected,
        observed,
        cost_per_run is not None,
        config,
        cap=confidence_cap,
        reasons=confidence_reasons,
    )
    return Opportunity(
        opportunity_id=opportunity_id(kind, subject),
        rule_id=rule.rule_id,
        rule_version=rule.version,
        area=area,
        kind=kind,
        title=title,
        summary=summary,
        action=action,
        subject=subject,
        thresholds=thresholds,
        runs_observed=observed,
        runs_affected=affected,
        evidence=savings.evidence,
        benefit=ProjectedBenefit(
            tokens_per_run=savings.tokens / observed if observed else 0.0,
            cost_usd_per_run=cost_per_run,
            latency_ms_per_run=savings.latency_ms / observed if observed else 0.0,
            monthly_cost_usd=monthly,
            cost_available=cost_per_run is not None,
            basis=basis + " Averaged over every observed run, including unaffected ones.",
        ),
        confidence=level,
        confidence_reasons=reasons,
        risks=risks,
    )


class PromptCachingRule:
    """A long prompt prefix that repeats across model calls without a cache hit.

    Reads `prompt.prefix_sha256` and `prompt.prefix_tokens` on model-call spans.
    Spans whose `prompt.cached_tokens` already covers the prefix are skipped.
    """

    rule_id = "prompt_caching"
    version = "1"

    def analyze(self, runs: Sequence[Run], config: OptimizationConfig) -> list[Opportunity]:
        groups: dict[str, list[tuple[Run, Span, int]]] = defaultdict(list)
        for run in runs:
            for span in run.spans:
                if span.span_type is not SpanType.MODEL_CALL:
                    continue
                attrs = span.attributes
                digest = _first(attrs, "prompt.prefix_sha256", "prompt_prefix_sha256")
                tokens = _int(_first(attrs, "prompt.prefix_tokens", "prompt_prefix_tokens"))
                cached = _int(_first(attrs, "prompt.cached_tokens", "cached_tokens")) or 0
                if not isinstance(digest, str) or tokens is None:
                    continue
                if tokens < config.prompt_cache_min_prefix_tokens or cached >= tokens:
                    continue
                groups[digest].append((run, span, min(tokens, span.input_tokens)))

        ratio = 1 - config.prompt_cache_read_price_ratio
        found: list[Opportunity] = []
        for digest, calls in sorted(groups.items()):
            if len(calls) < config.prompt_cache_min_repeats:
                continue
            savings = Savings()
            for run, span, tokens in calls[1:]:
                share = tokens / span.total_tokens if span.total_tokens else 0.0
                cost = (
                    span.estimated_cost_usd * share * ratio
                    if span.estimated_cost_usd is not None
                    else None
                )
                savings.add(tokens * ratio, cost)
                savings.evidence.append(
                    OpportunityEvidence(
                        run_id=run.run_id,
                        span_ids=[span.span_id],
                        measurements={
                            "prefix_tokens": tokens,
                            "input_tokens": span.input_tokens,
                            "model": span.model_name,
                        },
                        reasoning="Uncached repeat of a prefix already sent in an earlier call.",
                    )
                )
            prefix_tokens = calls[0][2]
            found.append(
                build_opportunity(
                    self,
                    area="prompt",
                    kind="prompt_caching",
                    title="Cache a repeated prompt prefix",
                    summary=(
                        f"A {prefix_tokens}-token prompt prefix was sent {len(calls)} times "
                        "without a provider cache hit."
                    ),
                    action=(
                        "Move the shared prefix to the start of the prompt and enable provider "
                        "prompt caching (or a local prefix cache)."
                    ),
                    subject={"prefix_sha256": digest},
                    thresholds={
                        "prompt_cache_min_prefix_tokens": config.prompt_cache_min_prefix_tokens,
                        "prompt_cache_min_repeats": config.prompt_cache_min_repeats,
                        "prompt_cache_read_price_ratio": config.prompt_cache_read_price_ratio,
                    },
                    runs=runs,
                    savings=savings,
                    basis=(
                        "Billable-equivalent prefix tokens on every repeat after the first, "
                        "discounted by the configured cached-read price ratio. Cost is the "
                        "span cost pro-rated by token share, an upper bound when output "
                        "tokens are priced above input tokens."
                    ),
                    config=config,
                    risks=[
                        QualityRisk(
                            kind="cache_invalidation",
                            severity="low",
                            description=(
                                "Dynamic content inside the prefix, or calls outside the "
                                "provider cache lifetime, will miss the cache."
                            ),
                        )
                    ],
                )
            )
        return found


class PromptCompressionRule:
    """Model calls whose input dwarfs their output, grouped by span name."""

    rule_id = "prompt_compression"
    version = "1"

    def analyze(self, runs: Sequence[Run], config: OptimizationConfig) -> list[Opportunity]:
        groups: dict[tuple[str, str | None], list[tuple[Run, Span]]] = defaultdict(list)
        for run in runs:
            for span in run.spans:
                if (
                    span.span_type is SpanType.MODEL_CALL
                    and span.input_tokens >= config.prompt_compression_min_input_tokens
                    and span.output_tokens > 0
                    and span.input_tokens / span.output_tokens
                    >= config.prompt_compression_min_ratio
                ):
                    groups[(span.name, span.agent_name)].append((run, span))

        target = config.prompt_compression_target_reduction
        found: list[Opportunity] = []
        for (name, agent), calls in sorted(groups.items(), key=lambda item: str(item[0])):
            savings = Savings()
            for run, span in calls:
                share = span.input_tokens / span.total_tokens
                cost = (
                    span.estimated_cost_usd * share * target
                    if span.estimated_cost_usd is not None
                    else None
                )
                savings.add(span.input_tokens * target, cost)
                savings.evidence.append(
                    OpportunityEvidence(
                        run_id=run.run_id,
                        span_ids=[span.span_id],
                        measurements={
                            "input_tokens": span.input_tokens,
                            "output_tokens": span.output_tokens,
                            "input_output_ratio": round(span.input_tokens / span.output_tokens, 2),
                        },
                        reasoning="Input-to-output ratio exceeds the configured threshold.",
                    )
                )
            found.append(
                build_opportunity(
                    self,
                    area="prompt",
                    kind="prompt_compression",
                    title=f"Compress the prompt of '{name}'",
                    summary=(
                        f"'{name}' sent at least {config.prompt_compression_min_input_tokens} "
                        f"input tokens per call for {len(calls)} calls with output "
                        f"{config.prompt_compression_min_ratio:g}x smaller."
                    ),
                    action=(
                        "Trim boilerplate, deduplicate context, or summarize long inputs; "
                        "evaluate the compressed prompt on the suite before adopting."
                    ),
                    subject={"span_name": name, "agent_name": agent},
                    thresholds={
                        "prompt_compression_min_input_tokens": (
                            config.prompt_compression_min_input_tokens
                        ),
                        "prompt_compression_min_ratio": config.prompt_compression_min_ratio,
                        "prompt_compression_target_reduction": target,
                    },
                    runs=runs,
                    savings=savings,
                    basis=(
                        f"The configured {target:.0%} target reduction of measured input "
                        "tokens; the reduction itself is an assumption until measured."
                    ),
                    config=config,
                    risks=[
                        QualityRisk(
                            kind="instruction_loss",
                            severity="medium",
                            description=(
                                "Compression can drop instructions or facts the model needs; "
                                "require a passing evaluation before rollout."
                            ),
                        )
                    ],
                    confidence_cap="medium",
                    confidence_reasons=["The reduction is a configured target, not measured."],
                )
            )
        return found


DEFAULT_RULES: tuple[OptimizationRule, ...] = (
    PromptCachingRule(),
    PromptCompressionRule(),
)
