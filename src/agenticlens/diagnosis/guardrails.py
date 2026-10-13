"""Guardrails for automated analysis.

`AnalysisBudget` declares limits; `AnalysisGuard` enforces them while an
analyzer runs and reports what was cut short. The diagnosis engine uses a
guard for span, depth, diagnosis, and time limits. Iterative analyzers (for
example one that asks a model follow-up questions about a trace) can use the
same guard for iteration, cost, and stagnation limits:

```python
guard = AnalysisGuard(AnalysisBudget(max_iterations=10, max_cost_usd=0.50))
while not guard.exhausted:
    finding = ask_model(...)
    guard.charge(cost_usd=finding.cost)
    guard.record([finding.fingerprint])  # stagnation: no new fingerprints
```

A guard never raises; callers check `exhausted` and the final
`GuardrailStatus` records every limit that was reached.
"""

import time
from collections.abc import Iterable

from pydantic import BaseModel, Field

from agenticlens.diagnosis.models import GuardrailStatus


class AnalysisBudget(BaseModel):
    """Limits for one analysis. ``None`` disables a limit."""

    max_spans: int | None = Field(default=10_000, gt=0)
    max_depth: int | None = Field(default=64, gt=0, description="Span-tree recursion cap.")
    max_diagnoses: int | None = Field(default=500, gt=0)
    max_iterations: int | None = Field(default=None, gt=0)
    max_cost_usd: float | None = Field(default=None, ge=0)
    max_seconds: float | None = Field(default=None, gt=0)
    stagnation_limit: int | None = Field(
        default=3,
        gt=0,
        description="Stop after this many consecutive iterations that add nothing new.",
    )


class AnalysisGuard:
    """Tracks an analysis against an `AnalysisBudget`."""

    def __init__(self, budget: AnalysisBudget | None = None) -> None:
        self.budget = budget or AnalysisBudget()
        self._started = time.perf_counter()
        self._reasons: list[str] = []
        self._seen: set[str] = set()
        self.iterations = 0
        self.stagnant_iterations = 0
        self.cost_usd = 0.0
        self.max_depth_seen = 0
        self.spans_analyzed = 0
        self.spans_total = 0

    def _stop(self, reason: str) -> None:
        if reason not in self._reasons:
            self._reasons.append(reason)

    @property
    def exhausted(self) -> bool:
        """True once any limit has been reached (including the time limit)."""
        self._check_time()
        return bool(self._reasons)

    @property
    def stop_reasons(self) -> list[str]:
        return list(self._reasons)

    @property
    def out_of_time(self) -> bool:
        """True once the time limit has passed (other limits trim work instead)."""
        self._check_time()
        return any(reason.startswith("time limit") for reason in self._reasons)

    def _check_time(self) -> None:
        limit = self.budget.max_seconds
        if limit is not None and time.perf_counter() - self._started > limit:
            self._stop(f"time limit of {limit:g}s reached")

    def limit_spans(self, total: int) -> int:
        """How many of `total` spans may be analyzed."""
        self.spans_total = total
        limit = self.budget.max_spans
        allowed = total if limit is None else min(total, limit)
        if allowed < total:
            self._stop(f"span limit reached: analyzed {allowed} of {total} spans")
        self.spans_analyzed = allowed
        return allowed

    def allow_depth(self, depth: int) -> bool:
        """False (and records why) when `depth` exceeds the recursion cap."""
        self.max_depth_seen = max(self.max_depth_seen, depth)
        limit = self.budget.max_depth
        if limit is not None and depth > limit:
            self._stop(f"span tree deeper than max_depth={limit}; deeper spans were cut off")
            return False
        return True

    def allow_diagnoses(self, count: int) -> int:
        """How many of `count` diagnoses may be kept."""
        limit = self.budget.max_diagnoses
        if limit is None or count <= limit:
            return count
        self._stop(f"diagnosis limit reached: kept {limit} of {count}")
        return limit

    def charge(self, *, cost_usd: float = 0.0) -> None:
        """Record spend by an analyzer that calls paid services."""
        self.cost_usd += cost_usd
        limit = self.budget.max_cost_usd
        if limit is not None and self.cost_usd >= limit:
            self._stop(f"cost budget of ${limit:g} reached")

    def record(self, fingerprints: Iterable[str]) -> bool:
        """Count one iteration; returns True when it produced something new.

        An iteration that adds no unseen fingerprint is stagnant; after
        ``stagnation_limit`` stagnant iterations in a row the guard stops.
        """
        self.iterations += 1
        new = {item for item in fingerprints if item not in self._seen}
        self._seen.update(new)
        self.stagnant_iterations = 0 if new else self.stagnant_iterations + 1
        if self.budget.max_iterations is not None and self.iterations >= (
            self.budget.max_iterations
        ):
            self._stop(f"iteration limit of {self.budget.max_iterations} reached")
        limit = self.budget.stagnation_limit
        if limit is not None and self.stagnant_iterations >= limit:
            self._stop(f"stagnation: {limit} consecutive iterations found nothing new")
        self._check_time()
        return bool(new)

    def status(self) -> GuardrailStatus:
        self._check_time()
        return GuardrailStatus(
            truncated=bool(self._reasons),
            stop_reasons=list(self._reasons),
            spans_analyzed=self.spans_analyzed,
            spans_total=self.spans_total,
            max_depth_seen=self.max_depth_seen,
            iterations=self.iterations,
            stagnant_iterations=self.stagnant_iterations,
            cost_usd=self.cost_usd,
        )
