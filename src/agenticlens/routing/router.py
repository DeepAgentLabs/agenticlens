"""Evidence-driven routing with explicitly bounded caller-owned execution."""

import hashlib
import math
from collections.abc import Callable, Mapping
from time import perf_counter
from typing import Literal

from agenticlens.modelfit import ModelFitReport, check_constraints
from agenticlens.modelfit.models import CandidateMetrics
from agenticlens.routing.audit import RoutingAuditLog, artifact_sha256
from agenticlens.routing.models import (
    RouteAttempt,
    RouteDecision,
    RouteOutcome,
    RouteRequest,
    RouteTarget,
    RoutingPolicy,
    RoutingResult,
)

CONFIDENCE = {"low": 0, "medium": 1, "high": 2}
RouteCallback = Callable[[RouteTarget, RouteRequest], RouteOutcome]


class RetryableRouteError(Exception):
    """Caller certifies a failed call is safe to retry on the next target.

    Never wrap policy denials or potentially committed side effects in this.
    Other exceptions stop the serving chain. Exception text is not recorded.
    """


def _target(candidate: CandidateMetrics) -> RouteTarget:
    return RouteTarget(
        variant_id=candidate.variant_id,
        model=candidate.model,
        provider=candidate.provider,
        deployment=candidate.deployment,
        source_index=candidate.source_index,
        weighted_score=candidate.weighted_score,
    )


class Router:
    """Snapshot evidence and policy. Callbacks own invocation and timeouts.

    No provider SDK, credentials, network or approval service is embedded.
    Escalation returns a terminal result for the host to handle.
    """

    def __init__(
        self,
        report: ModelFitReport,
        policy: RoutingPolicy | None = None,
        *,
        audit: RoutingAuditLog | None = None,
    ):
        # Reject NaN/Infinity before JSON could normalize them to null and erase a limit.
        artifact_sha256(report)
        artifact_sha256(policy or RoutingPolicy())
        if report.schema_version != "1.0":
            raise ValueError("unsupported ModelFit schema version")
        self._report = ModelFitReport.model_validate_json(report.model_dump_json())
        self._policy = RoutingPolicy.model_validate_json(
            (policy or RoutingPolicy()).model_dump_json()
        )
        ids = [result.category.id for result in self._report.categories]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate category IDs in ModelFit report")
        for result in self._report.categories:
            variants = [candidate.variant_id for candidate in result.candidates]
            if len(variants) != len(set(variants)):
                raise ValueError("duplicate candidate IDs in category")
        self._report_hash = artifact_sha256(self._report)
        self._policy_hash = artifact_sha256(self._policy)
        self._audit = audit

    def _record(
        self,
        event: str,
        decision: RouteDecision,
        record: RouteAttempt | RoutingResult | RouteDecision,
    ) -> None:
        if self._audit is not None:
            self._audit.append(event, decision.decision_id, record)

    def decide(self, request: RouteRequest) -> RouteDecision:
        """Select without invoking a model. Unknown categories fail closed."""
        policy = self._policy
        request = RouteRequest.model_validate_json(request.model_dump_json())
        decision = RouteDecision(
            request=request,
            policy_name=policy.name,
            policy_version=policy.version,
            policy_sha256=self._policy_hash,
            report_sha256=self._report_hash,
            mode=policy.mode,
            status="escalated" if policy.on_unroutable == "escalate" else "blocked",
        )
        category = next(
            (c for c in self._report.categories if c.category.id == request.category_id), None
        )
        if category is None:
            decision.reasons.append("Unknown task category; no implicit overall-category fallback.")
            return self._finish(decision)
        rec = category.recommendation
        decision.confidence = rec.confidence
        if rec.status != "recommended" or rec.confidence is None:
            decision.reasons.append(
                "ModelFit has no recommendation with confidence for this category."
            )
            return self._finish(decision)
        recommended = next((c for c in category.candidates if c.variant_id == rec.variant_id), None)
        if (
            rec.category_id != category.category.id
            or recommended is None
            or not recommended.feasible
            or recommended.violations
            or check_constraints(recommended, category.constraints)
            or rec.model != recommended.model
            or rec.provider != recommended.provider
        ):
            decision.reasons.append(
                "Inconsistent ModelFit recommendation; evidence is not routable."
            )
            return self._finish(decision)
        if CONFIDENCE[rec.confidence] < CONFIDENCE[policy.minimum_confidence]:
            decision.reasons.append("ModelFit confidence is below the routing threshold.")
            return self._finish(decision)
        eligible: list[CandidateMetrics] = []
        for candidate in category.candidates:
            reasons = [v.message for v in candidate.violations]
            reasons.extend(v.message for v in check_constraints(candidate, category.constraints))
            reasons.extend(v.message for v in check_constraints(candidate, policy.constraints))
            if not candidate.feasible:
                reasons.append("ModelFit marked this candidate infeasible.")
            if not 0 <= candidate.source_index < len(self._report.sources):
                reasons.append("Missing source experiment evidence.")
            elif (
                candidate.variant_id not in self._report.sources[candidate.source_index].variant_ids
            ):
                reasons.append("Variant is absent from source experiment evidence.")
            numeric = [
                candidate.weighted_score,
                candidate.pass_rate,
                candidate.mean_latency_ms,
                candidate.p95_latency_ms,
                candidate.cost_per_case_usd,
                candidate.cost_per_success_usd,
                candidate.consistency_rate,
                candidate.safety_pass_rate,
            ]
            if any(v is not None and (not math.isfinite(v) or v < 0) for v in numeric):
                reasons.append("Invalid nonfinite or negative evidence metrics.")
            if candidate.weighted_score is None:
                reasons.append("No evidence-backed score.")
            if not candidate.cost_complete and any(
                value is not None
                for value in (
                    policy.constraints.max_cost_per_case_usd,
                    policy.constraints.max_cost_per_success_usd,
                    category.constraints.max_cost_per_case_usd,
                    category.constraints.max_cost_per_success_usd,
                )
            ):
                reasons.append("Cost evidence is incomplete under a cost constraint.")
            if reasons:
                decision.rejected[candidate.variant_id] = list(dict.fromkeys(reasons))
            else:
                eligible.append(candidate)
        if policy.strategy == "rule":
            order = policy.rules.get(request.category_id, [])
            eligible = sorted(
                (c for c in eligible if c.variant_id in order),
                key=lambda c: order.index(c.variant_id),
            )
            decision.reasons.append("Applied explicit category rule order after hard constraints.")
        else:
            eligible.sort(key=lambda c: (-(c.weighted_score or 0), c.variant_id))
            decision.reasons.append(
                "Ranked feasible candidates by recorded ModelFit weighted score."
            )
        if not eligible:
            decision.reasons.append("No candidate meets routing rules and evidence constraints.")
            return self._finish(decision)
        selected = eligible[0]
        targets = [selected]
        if policy.strategy == "score":
            diverse = [
                c
                for c in eligible[1:]
                if c.provider and selected.provider and c.provider != selected.provider
            ]
            targets.extend(diverse)
            targets.extend(c for c in eligible[1:] if c not in diverse)
        else:
            targets.extend(eligible[1:])
        if policy.mode in {"shadow", "canary"}:
            baseline = next(
                (c for c in eligible if c.variant_id == policy.baseline_variant_id), None
            )
            if baseline is None:
                decision.reasons.append("Baseline is not eligible; refusing baseline traffic.")
                return self._finish(decision)
            if policy.mode == "shadow":
                targets = [baseline]
                if selected.variant_id != baseline.variant_id:
                    decision.shadow_target = _target(selected)
                if decision.shadow_target is not None:
                    decision.reasons.append(
                        "Baseline serves; a separate shadow callback can measure the candidate."
                    )
                else:
                    decision.reasons.append(
                        "Baseline is the proposed candidate; no shadow call planned."
                    )
            else:
                key = f"{policy.allocation_salt}\0{request.category_id}\0{request.request_id}"
                bucket = int.from_bytes(hashlib.sha256(key.encode()).digest()[:8], "big") / 2**64
                decision.cohort = "canary" if bucket < policy.canary_fraction else "baseline"
                if decision.cohort == "baseline":
                    targets = [baseline]
                decision.reasons.append(f"Stable canary allocation: {decision.cohort}.")
        decision.targets = [_target(c) for c in targets[: policy.max_attempts]]
        decision.status = "selected"
        decision.reasons.append(
            f"Serving target: {targets[0].variant_id}; ModelFit recommendation: {rec.variant_id}. "
            "Confidence describes the original category recommendation evidence."
        )
        decision.reasons.extend(f"ModelFit context: {text}" for text in rec.explanation)
        return self._finish(decision)

    def _finish(self, decision: RouteDecision) -> RouteDecision:
        self._record("decision", decision, decision)
        return decision

    def run(
        self,
        request: RouteRequest,
        callbacks: Mapping[str, RouteCallback],
        *,
        shadow_callbacks: Mapping[str, RouteCallback] | None = None,
    ) -> RoutingResult:
        """Execute in explicit execution modes; unknown errors stop serving.

        Callbacks enforce timeouts and side-effect safety. Shadow callbacks are
        separately supplied to prevent accidental serving-callback replay.
        """
        decision = self.decide(request)
        if decision.status != "selected":
            result = RoutingResult(decision=decision, status=decision.status)
        elif self._policy.mode == "advisory":
            result = RoutingResult(decision=decision, status="advisory")
        else:
            result = RoutingResult(decision=decision, status="failed")
            for index, target in enumerate(decision.targets):
                callback = callbacks.get(target.variant_id)
                if callback is None:
                    break  # Configuration errors must not silently cause provider failover.
                attempt = self._invoke(
                    decision, target, callback, "primary" if index == 0 else "fallback"
                )
                result.attempts.append(attempt)
                if attempt.status == "succeeded":
                    result.served_variant_id = target.variant_id
                    result.status = "succeeded"
                    break
                if attempt.status != "retryable_error":
                    break
            if result.status == "succeeded" and decision.shadow_target is not None:
                callback = (shadow_callbacks or {}).get(decision.shadow_target.variant_id)
                if callback is not None:
                    result.attempts.append(
                        self._invoke(decision, decision.shadow_target, callback, "shadow")
                    )
        self._record("result", decision, result)
        return result

    def _invoke(
        self,
        decision: RouteDecision,
        target: RouteTarget,
        callback: RouteCallback,
        role: Literal["primary", "fallback", "shadow"],
    ) -> RouteAttempt:
        # Persist exact attempted target before every external call, including fallback.
        self._record(
            "attempt_started",
            decision,
            decision.model_copy(update={"targets": [target]}, deep=True),
        )
        start = perf_counter()
        cost = None
        status: Literal["succeeded", "unsuccessful", "retryable_error", "error"] = "error"
        try:
            outcome = callback(target.model_copy(deep=True), decision.request.model_copy(deep=True))
            outcome = RouteOutcome.model_validate(outcome.model_dump())
            cost = outcome.cost_usd
            status = "succeeded" if outcome.success else "unsuccessful"
        except RetryableRouteError:
            status = "retryable_error"
        except Exception:
            status = "error"
        attempt = RouteAttempt(
            target=target,
            role=role,
            status=status,
            latency_ms=(perf_counter() - start) * 1000,
            cost_usd=cost,
        )
        self._record("attempt_finished", decision, attempt)
        return attempt
