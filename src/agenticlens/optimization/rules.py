"""Deterministic optimization rules over recorded traces.

Every rule reads only what the trace records. A saving is projected from the
spans it would remove or shrink; a missing measurement skips the span instead
of being guessed.
"""

import hashlib
import json
import math
from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol

from agenticlens.modelfit.models import Confidence
from agenticlens.models.trace import Run, RunStatus, Span, SpanType
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


def run_cost(run: Run) -> float | None:
    """Exactly rounded, so reports match across Python versions; None if any span is unpriced."""
    costs = [span.estimated_cost_usd for span in run.spans]
    if not costs or any(cost is None for cost in costs):
        return None
    return math.fsum(cost for cost in costs if cost is not None)


def run_cost_per_token(run: Run) -> float | None:
    cost = run_cost(run)
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


@dataclass
class _Chunk:
    rank: int
    tokens: int
    used: bool


def _chunks(span: Span) -> list[_Chunk] | None:
    raw = _first(span.attributes, "retrieval.chunks", "chunks")
    if not isinstance(raw, list) or not raw:
        return None
    chunks: list[_Chunk] = []
    for index, item in enumerate(raw, start=1):
        if not isinstance(item, dict):
            return None
        used = _first(item, "used", "cited")
        tokens = _int(item.get("tokens"))
        rank = _int(item.get("rank")) or index
        if not isinstance(used, bool) or tokens is None:
            return None
        chunks.append(_Chunk(rank=rank, tokens=tokens, used=used))
    return sorted(chunks, key=lambda chunk: chunk.rank)


def _downstream_cost_per_token(run: Run, span: Span) -> float | None:
    """Price retrieved context at the next model call that consumed it."""
    index = run.spans.index(span)
    for later in run.spans[index + 1 :]:
        if later.span_type is SpanType.MODEL_CALL:
            if later.estimated_cost_usd is None or not later.total_tokens:
                return None
            return later.estimated_cost_usd / later.total_tokens
    return None


class RetrievalRule:
    """Retrieved chunks the answer never used, and used chunks ranked too deep.

    Reads `retrieval.chunks` (or `chunks`): a list of objects with `tokens`,
    `used` (or `cited`), and optional `rank`. Spans without complete chunk
    usage are skipped.
    """

    rule_id = "retrieval"
    version = "1"

    def analyze(self, runs: Sequence[Run], config: OptimizationConfig) -> list[Opportunity]:
        groups: dict[str, list[tuple[Run, Span, list[_Chunk]]]] = defaultdict(list)
        for run in runs:
            for span in run.spans:
                if span.span_type is not SpanType.RETRIEVAL:
                    continue
                chunks = _chunks(span)
                if chunks is not None and len(chunks) >= config.retrieval_min_chunks:
                    groups[span.name].append((run, span, chunks))

        found: list[Opportunity] = []
        for name, spans in sorted(groups.items()):
            found.extend(self._pruning(name, spans, runs, config))
            found.extend(self._reranking(name, spans, runs, config))
        return found

    def _pruning(
        self,
        name: str,
        spans: list[tuple[Run, Span, list[_Chunk]]],
        runs: Sequence[Run],
        config: OptimizationConfig,
    ) -> list[Opportunity]:
        low_utility = [
            item
            for item in spans
            if sum(c.used for c in item[2]) / len(item[2]) <= config.retrieval_max_utility
        ]
        if not low_utility:
            return []
        # Never cut a chunk any observed answer used.
        top_k = max((c.rank for _, _, chunks in spans for c in chunks if c.used), default=1)
        savings = Savings()
        for run, span, chunks in low_utility:
            cut = [c for c in chunks if c.rank > top_k]
            if not cut:
                continue
            tokens = sum(c.tokens for c in cut)
            price = _downstream_cost_per_token(run, span)
            savings.add(tokens, tokens * price if price is not None else None)
            savings.evidence.append(
                OpportunityEvidence(
                    run_id=run.run_id,
                    span_ids=[span.span_id],
                    measurements={
                        "retrieved_chunks": len(chunks),
                        "used_chunks": sum(c.used for c in chunks),
                        "chunks_cut": len(cut),
                        "tokens_cut": tokens,
                    },
                    reasoning=f"No used chunk was ranked below {top_k}.",
                )
            )
        if not savings.evidence:
            return []
        retrieved = max(len(chunks) for _, _, chunks in spans)
        return [
            build_opportunity(
                self,
                area="retrieval",
                kind="retrieval_pruning",
                title=f"Lower top-k for '{name}'",
                summary=(
                    f"'{name}' retrieved up to {retrieved} chunks, but no answer across "
                    f"{len(spans)} retrievals used a chunk ranked below {top_k}."
                ),
                action=f"Reduce top-k from {retrieved} to {top_k}.",
                subject={"span_name": name, "recommended_top_k": top_k},
                thresholds={
                    "retrieval_min_chunks": config.retrieval_min_chunks,
                    "retrieval_max_utility": config.retrieval_max_utility,
                },
                runs=runs,
                savings=savings,
                basis=(
                    "Tokens of chunks ranked below the deepest used chunk, priced at the "
                    "next model call's cost per token."
                ),
                config=config,
                risks=[
                    QualityRisk(
                        kind="recall_loss",
                        severity="medium" if len(spans) < 5 else "low",
                        description=(
                            f"{len(spans)} retrievals were observed; unseen queries may "
                            "need deeper chunks."
                        ),
                    )
                ],
            )
        ]

    def _reranking(
        self,
        name: str,
        spans: list[tuple[Run, Span, list[_Chunk]]],
        runs: Sequence[Run],
        config: OptimizationConfig,
    ) -> list[Opportunity]:
        savings = Savings()
        for run, span, chunks in spans:
            deepest = max((c.rank for c in chunks if c.used), default=0)
            if deepest < config.retrieval_rerank_min_rank:
                continue
            skipped = [c for c in chunks if not c.used and c.rank < deepest]
            if not skipped:
                continue
            tokens = sum(c.tokens for c in skipped)
            price = _downstream_cost_per_token(run, span)
            savings.add(tokens, tokens * price if price is not None else None)
            savings.evidence.append(
                OpportunityEvidence(
                    run_id=run.run_id,
                    span_ids=[span.span_id],
                    measurements={
                        "deepest_used_rank": deepest,
                        "unused_chunks_ranked_above": len(skipped),
                        "tokens_ranked_above": tokens,
                    },
                    reasoning="A used chunk was ranked below unused ones.",
                )
            )
        if not savings.evidence:
            return []
        return [
            build_opportunity(
                self,
                area="retrieval",
                kind="retrieval_reranking",
                title=f"Rerank results of '{name}'",
                summary=(
                    f"In {len(savings.evidence)} retrievals the answer used a chunk ranked "
                    f"{config.retrieval_rerank_min_rank} or lower while higher-ranked chunks "
                    "went unused."
                ),
                action="Add a reranker, then lower top-k to the reranked depth that answers use.",
                subject={"span_name": name},
                thresholds={"retrieval_rerank_min_rank": config.retrieval_rerank_min_rank},
                runs=runs,
                savings=savings,
                basis=(
                    "Upper bound: tokens of unused chunks ranked above the deepest used chunk, "
                    "which a perfect reranker would drop. Reranker cost and latency excluded."
                ),
                config=config,
                risks=[
                    QualityRisk(
                        kind="reranker_overhead",
                        severity="low",
                        description="A reranker adds its own latency and cost per query.",
                    ),
                    QualityRisk(
                        kind="reranker_quality",
                        severity="medium",
                        description="A reranker can demote chunks answers need; evaluate it.",
                    ),
                ],
                confidence_cap="medium",
                confidence_reasons=["Benefit assumes a perfect reranker."],
            )
        ]


class MemoryRule:
    """Memory reads that dominate a run's input tokens."""

    rule_id = "memory"
    version = "1"

    def analyze(self, runs: Sequence[Run], config: OptimizationConfig) -> list[Opportunity]:
        savings = Savings()
        growing_runs = 0
        for run in runs:
            reads = [s for s in run.spans if s.span_type is SpanType.MEMORY_READ]
            memory = sum(s.total_tokens for s in reads)
            share = memory / run.total_tokens if run.total_tokens else 0.0
            if share <= config.memory_max_share or memory <= config.memory_token_budget:
                continue
            sizes = [s.total_tokens for s in reads]
            growing = len(sizes) >= 3 and all(a < b for a, b in zip(sizes, sizes[1:], strict=False))
            growing_runs += growing
            excess = memory - config.memory_token_budget
            price = run_cost_per_token(run)
            savings.add(excess, excess * price if price is not None else None)
            savings.evidence.append(
                OpportunityEvidence(
                    run_id=run.run_id,
                    span_ids=[s.span_id for s in reads],
                    measurements={
                        "memory_tokens": memory,
                        "run_tokens": run.total_tokens,
                        "memory_share": round(share, 4),
                        "grows_every_read": growing,
                    },
                    reasoning="Memory reads exceed the configured share and token budget.",
                )
            )
        if not savings.evidence:
            return []
        budget = config.memory_token_budget
        action = f"Summarize older memory into a digest of about {budget} tokens"
        if growing_runs:
            action += " and add a retention window, since memory grew on every read"
        return [
            build_opportunity(
                self,
                area="memory",
                kind="memory_summarization",
                title="Bound memory with summarization and retention",
                summary=(
                    f"Memory reads took over {config.memory_max_share:.0%} of tokens in "
                    f"{len(savings.evidence)} runs; {growing_runs} grew on every read."
                ),
                action=action + ".",
                subject={"span_type": SpanType.MEMORY_READ.value},
                thresholds={
                    "memory_max_share": config.memory_max_share,
                    "memory_token_budget": config.memory_token_budget,
                },
                runs=runs,
                savings=savings,
                basis=(
                    "Memory tokens above the configured budget, priced at each run's "
                    "blended cost per token."
                ),
                config=config,
                risks=[
                    QualityRisk(
                        kind="fact_loss",
                        severity="medium",
                        description="Summaries can drop facts that later turns rely on.",
                    )
                ],
            )
        ]


class ToolCachingRule:
    """Successful tool calls repeated with identical arguments in one run.

    Tools that declare `idempotent: false` or `side_effects: true` are skipped.
    """

    rule_id = "tool_caching"
    version = "1"

    def analyze(self, runs: Sequence[Run], config: OptimizationConfig) -> list[Opportunity]:
        per_tool: dict[str, Savings] = defaultdict(Savings)
        declared: dict[str, bool] = {}
        # The action memoizes the whole tool, so one unsafe call anywhere excludes it.
        unsafe = {
            span.tool_name or span.name
            for run in runs
            for span in run.spans
            if span.span_type is SpanType.TOOL_CALL
            and (
                span.attributes.get("idempotent") is False
                or span.attributes.get("side_effects") is True
            )
        }
        for run in runs:
            calls: dict[tuple[str, str], list[Span]] = defaultdict(list)
            for span in run.spans:
                if span.span_type is not SpanType.TOOL_CALL or span.status is not (
                    RunStatus.SUCCEEDED
                ):
                    continue
                attrs = span.attributes
                tool = span.tool_name or span.name
                if tool in unsafe:
                    continue
                args = attrs.get("tool_args")
                key = "args:" + fingerprint(args) if args is not None else input_fingerprint(span)
                if key is None:
                    continue
                calls[(tool, key)].append(span)
                declared[tool] = declared.get(tool, True) and attrs.get("idempotent") is True
            for (tool, _), spans in sorted(calls.items()):
                if len(spans) < config.tool_cache_min_repeats:
                    continue
                repeats = spans[1:]
                per_tool[tool].add_spans(repeats)
                per_tool[tool].evidence.append(
                    OpportunityEvidence(
                        run_id=run.run_id,
                        span_ids=[s.span_id for s in spans],
                        measurements={
                            "calls": len(spans),
                            "repeat_tokens": sum(s.total_tokens for s in repeats),
                            "repeat_latency_ms": sum(s.latency_ms for s in repeats),
                        },
                        reasoning="Identical arguments returned successfully more than once.",
                    )
                )

        found: list[Opportunity] = []
        for tool, savings in sorted(per_tool.items()):
            idempotent = declared.get(tool, False)
            found.append(
                build_opportunity(
                    self,
                    area="tool",
                    kind="tool_result_caching",
                    title=f"Cache results of tool '{tool}'",
                    summary=(
                        f"'{tool}' was called repeatedly with identical arguments in "
                        f"{len(savings.evidence)} runs."
                    ),
                    action=f"Memoize '{tool}' by arguments for the duration of a run.",
                    subject={"tool_name": tool},
                    thresholds={"tool_cache_min_repeats": config.tool_cache_min_repeats},
                    runs=runs,
                    savings=savings,
                    basis="Measured tokens, cost and latency of every repeat after the first.",
                    config=config,
                    risks=[
                        QualityRisk(
                            kind="stale_result",
                            severity="low" if idempotent else "medium",
                            description=(
                                "The tool is declared idempotent; cached results can still "
                                "go stale if they outlive the data."
                                if idempotent
                                else "The tool does not declare idempotent: true; caching "
                                "may hide state changes between calls."
                            ),
                        )
                    ],
                )
            )
        return found


def _retry_recovered(run: Run, span: Span) -> bool:
    return span.status is RunStatus.SUCCEEDED or any(
        child.status is RunStatus.SUCCEEDED for child in subtree(run, span)[1:]
    )


def _retry_trigger(run: Run, span: Span) -> str:
    by_id = {s.span_id: s for s in run.spans}
    parent = by_id.get(span.parent_span_id or "")
    if parent is not None and parent.status is RunStatus.FAILED:
        return parent.error_type or "unknown"
    index = run.spans.index(span)
    for earlier in reversed(run.spans[:index]):
        if earlier.status is RunStatus.FAILED and earlier.span_type is not SpanType.RETRY:
            return earlier.error_type or "unknown"
    return span.error_type or "unknown"


class RetryPolicyRule:
    """Retries of an error type that no observed retry ever recovered."""

    rule_id = "retry_policy"
    version = "1"

    def analyze(self, runs: Sequence[Run], config: OptimizationConfig) -> list[Opportunity]:
        failed: dict[str, Savings] = defaultdict(Savings)
        recovered: dict[str, int] = defaultdict(int)
        for run in runs:
            by_error: dict[str, list[Span]] = defaultdict(list)
            for span in run.spans:
                if span.span_type is not SpanType.RETRY:
                    continue
                error = _retry_trigger(run, span)
                if _retry_recovered(run, span):
                    recovered[error] += 1
                else:
                    by_error[error].append(span)
            for error, spans in sorted(by_error.items()):
                failed[error].add_spans(spans)
                failed[error].evidence.append(
                    OpportunityEvidence(
                        run_id=run.run_id,
                        span_ids=[s.span_id for s in spans],
                        measurements={"unrecovered_retries": len(spans), "error_type": error},
                        reasoning="Retries after this error type did not recover.",
                    )
                )

        found: list[Opportunity] = []
        for error, savings in sorted(failed.items()):
            attempts = sum(len(item.span_ids) for item in savings.evidence)
            if recovered[error] or attempts < config.retry_min_unrecovered:
                continue
            found.append(
                build_opportunity(
                    self,
                    area="tool",
                    kind="retry_policy",
                    title=f"Stop retrying '{error}'",
                    summary=(
                        f"{attempts} retries after '{error}' were observed and none recovered."
                    ),
                    action=(f"Treat '{error}' as non-retryable: fail fast or route to a fallback."),
                    subject={"error_type": error},
                    thresholds={"retry_min_unrecovered": config.retry_min_unrecovered},
                    runs=runs,
                    savings=savings,
                    basis="Measured tokens, cost and latency of the unrecovered retry spans.",
                    config=config,
                    risks=[
                        QualityRisk(
                            kind="transient_error",
                            severity="medium" if attempts < 5 else "low",
                            description=(
                                f"{attempts} retries were observed; the error may be "
                                "transient on traffic not in these traces."
                            ),
                        )
                    ],
                )
            )
        return found


class RedundantStepRule:
    """Steps re-executed with identical input and output in one run."""

    rule_id = "redundant_step"
    version = "1"
    span_types = frozenset(
        {
            SpanType.MODEL_CALL,
            SpanType.RETRIEVAL,
            SpanType.PLANNING,
            SpanType.VALIDATION,
            SpanType.MEMORY_READ,
        }
    )

    def analyze(self, runs: Sequence[Run], config: OptimizationConfig) -> list[Opportunity]:
        per_step: dict[tuple[str, str], Savings] = defaultdict(Savings)
        for run in runs:
            seen: dict[tuple[str, str, str, str], list[Span]] = defaultdict(list)
            for span in run.spans:
                if span.span_type not in self.span_types:
                    continue
                source, result = input_fingerprint(span), output_fingerprint(span)
                if source is None or result is None:
                    continue
                seen[(span.span_type.value, span.name, source, result)].append(span)
            for (kind, name, _, _), spans in sorted(seen.items()):
                if len(spans) < config.redundant_step_min_repeats:
                    continue
                per_step[(kind, name)].add_spans(spans[1:])
                per_step[(kind, name)].evidence.append(
                    OpportunityEvidence(
                        run_id=run.run_id,
                        span_ids=[s.span_id for s in spans],
                        measurements={"executions": len(spans)},
                        reasoning="Same input produced the same output again.",
                    )
                )

        return [
            build_opportunity(
                self,
                area="workflow",
                kind="redundant_step",
                title=f"Remove the repeated '{name}' step",
                summary=(
                    f"'{name}' ({kind}) re-ran with identical input and output in "
                    f"{len(savings.evidence)} runs."
                ),
                action=f"Reuse the first '{name}' result instead of re-executing it.",
                subject={"span_type": kind, "span_name": name},
                thresholds={"redundant_step_min_repeats": config.redundant_step_min_repeats},
                runs=runs,
                savings=savings,
                basis="Measured tokens, cost and latency of every identical re-execution.",
                config=config,
                risks=[
                    QualityRisk(
                        kind="intentional_repeat",
                        severity="low",
                        description=(
                            "Repeats can be deliberate (self-consistency sampling, polling); "
                            "confirm before removing."
                        ),
                    )
                ],
            )
            for (kind, name), savings in sorted(per_step.items())
        ]


class UnnecessaryHandoffRule:
    """Delegations where the receiving agent did no work or echoed its input."""

    rule_id = "unnecessary_handoff"
    version = "1"

    def analyze(self, runs: Sequence[Run], config: OptimizationConfig) -> list[Opportunity]:
        per_pair: dict[tuple[str, str], Savings] = defaultdict(Savings)
        for run in runs:
            for span in run.spans:
                if span.span_type is not SpanType.DELEGATION:
                    continue
                tree = subtree(run, span)
                source = span.attributes.get("from_agent") or span.agent_name or "unknown"
                target = next(
                    (
                        value
                        for key in _HANDOFF_TARGET_KEYS
                        if isinstance(value := span.attributes.get(key), str) and value
                    ),
                    next((c.agent_name for c in tree[1:] if c.agent_name), "unknown"),
                )
                did_work = any(child.span_type in _WORK_SPANS for child in tree[1:])
                echoed = input_fingerprint(span) is not None and input_fingerprint(
                    span
                ) == output_fingerprint(span)
                if did_work and not echoed:
                    continue
                pair = (str(source), str(target))
                per_pair[pair].add_spans(tree)
                per_pair[pair].evidence.append(
                    OpportunityEvidence(
                        run_id=run.run_id,
                        span_ids=[s.span_id for s in tree],
                        measurements={
                            "subtree_spans": len(tree),
                            "receiver_did_work": did_work,
                            "output_equals_input": echoed,
                        },
                        reasoning=(
                            "The receiving agent returned its input unchanged."
                            if echoed
                            else "The receiving agent made no model, tool or retrieval call."
                        ),
                    )
                )

        return [
            build_opportunity(
                self,
                area="workflow",
                kind="unnecessary_handoff",
                title=f"Skip the handoff {source} -> {target}",
                summary=(
                    f"{len(savings.evidence)} handoffs from {source} to {target} added no work."
                ),
                action=f"Let {source} continue directly, or merge {target} into it.",
                subject={"from_agent": source, "to_agent": target},
                thresholds={"handoff_min_occurrences": config.handoff_min_occurrences},
                runs=runs,
                savings=savings,
                basis="Measured tokens, cost and latency of each handoff and its subtree.",
                config=config,
                risks=[
                    QualityRisk(
                        kind="handoff_semantics",
                        severity="medium",
                        description=(
                            "A handoff can carry authorization, audit, or ownership "
                            "semantics that tokens do not show."
                        ),
                    )
                ],
            )
            for (source, target), savings in sorted(per_pair.items())
            if len(savings.evidence) >= config.handoff_min_occurrences
        ]


DEFAULT_RULES: tuple[OptimizationRule, ...] = (
    PromptCachingRule(),
    PromptCompressionRule(),
    RetrievalRule(),
    MemoryRule(),
    ToolCachingRule(),
    RetryPolicyRule(),
    RedundantStepRule(),
    UnnecessaryHandoffRule(),
)
