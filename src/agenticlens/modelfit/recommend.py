"""Recommend a model per task category from experiment evidence."""

from collections.abc import Sequence

from agenticlens.experiments import ExperimentReport, two_proportion_p_value
from agenticlens.modelfit.evidence import (
    CandidateEvidence,
    ExperimentEvidence,
    as_evidence,
    collect_candidates,
    evidence_source,
)
from agenticlens.modelfit.models import (
    Alternative,
    CandidateMetrics,
    CategoryResult,
    Confidence,
    MatrixRow,
    ModelConstraints,
    ModelFitConfig,
    ModelFitReport,
    ModelFitSummary,
    QualityRisk,
    Recommendation,
    SavingsEstimate,
    ScoringWeights,
    TaskCategory,
)
from agenticlens.modelfit.scoring import (
    check_constraints,
    cost_per_success_ranking,
    measure,
    pareto_frontier,
    score,
    sort_key,
)
from agenticlens.modelfit.taxonomy import case_index, resolve_taxonomy

#: Score margin under which the top two candidates are treated as close.
CLOSE_SCORE_MARGIN = 0.05


def _money(value: float | None) -> str:
    return "unavailable" if value is None else f"${value:.4f}"


def _rate(value: float | None) -> str:
    return "unavailable" if value is None else f"{value:.1%}"


def _describe(metrics: CandidateMetrics) -> str:
    interval = metrics.pass_rate_interval
    bounds = f" (CI {interval.lower:.0%}-{interval.upper:.0%})" if interval else ""
    latency = (
        "unavailable" if metrics.mean_latency_ms is None else f"{metrics.mean_latency_ms:.0f} ms"
    )
    return (
        f"pass rate {_rate(metrics.pass_rate)}{bounds} over {metrics.attempts} attempts, "
        f"cost per success {_money(metrics.cost_per_success_usd)}, mean latency {latency}"
    )


def _confidence(
    top: CandidateMetrics,
    runner_up: CandidateMetrics | None,
    config: ModelFitConfig,
    constraints: ModelConstraints,
    weights: ScoringWeights,
) -> tuple[Confidence, list[str]]:
    reasons: list[str] = []
    level: Confidence = "high"

    def lower(to: Confidence, reason: str) -> None:
        nonlocal level
        order = {"high": 0, "medium": 1, "low": 2}
        if order[to] > order[level]:
            level = to
        reasons.append(reason)

    if top.attempts < config.minimum_attempts:
        lower(
            "low",
            f"Only {top.attempts} attempts on this category; at least "
            f"{config.minimum_attempts} are needed for a confident recommendation.",
        )
    if runner_up is not None and top.weighted_score is not None:
        margin = top.weighted_score - (runner_up.weighted_score or 0.0)
        p_value = two_proportion_p_value(
            top.passes, top.attempts, runner_up.passes, runner_up.attempts
        )
        if margin < CLOSE_SCORE_MARGIN:
            significant = p_value is not None and p_value < config.significance_level
            if not significant:
                p_text = "n/a" if p_value is None else f"{p_value:.3f}"
                lower(
                    "medium",
                    f"Runner-up {runner_up.variant_id} scores within {margin:.3f} and the "
                    f"pass-rate difference is not statistically significant (p={p_text}).",
                )
    if (
        constraints.min_pass_rate is not None
        and top.pass_rate_interval is not None
        and top.pass_rate_interval.lower < constraints.min_pass_rate
    ):
        lower(
            "medium",
            f"The pass-rate interval's lower bound {top.pass_rate_interval.lower:.1%} is below "
            f"the {constraints.min_pass_rate:.0%} minimum, so more trials could reverse it.",
        )
    if weights.cost > 0 and not top.cost_complete:
        lower("medium", "Cost evidence is incomplete, so the cost component scored zero.")
    if not reasons:
        reasons.append(
            f"{top.attempts} attempts and a clear lead over the alternatives."
            if runner_up is not None
            else f"{top.attempts} attempts; it is the only feasible candidate."
        )
    return level, reasons


def _alternatives(
    top: CandidateMetrics, feasible: list[CandidateMetrics], limit: int
) -> tuple[list[Alternative], Alternative | None]:
    others = [candidate for candidate in feasible if candidate.variant_id != top.variant_id]
    alternatives = [
        Alternative(
            variant_id=candidate.variant_id,
            model=candidate.model,
            provider=candidate.provider,
            role="alternative",
            weighted_score=candidate.weighted_score,
            pass_rate=candidate.pass_rate,
            cost_per_success_usd=candidate.cost_per_success_usd,
            reason=f"Ranked {candidate.rank} of {len(feasible)} feasible candidates.",
        )
        for candidate in others[:limit]
    ]
    fallback_candidate = None
    reason = ""
    if top.provider is not None:
        for candidate in others:
            if candidate.provider is not None and candidate.provider != top.provider:
                fallback_candidate = candidate
                reason = (
                    f"Best feasible candidate on a different provider ({candidate.provider}), "
                    f"for failover if {top.provider} is unavailable."
                )
                break
    if fallback_candidate is None and others:
        fallback_candidate = others[0]
        reason = (
            "Next-best feasible candidate; it shares the recommended provider, so it does "
            "not protect against a provider outage."
            if top.provider is not None and fallback_candidate.provider == top.provider
            else "Next-best feasible candidate; provider diversity cannot be checked."
        )
    fallback = None
    if fallback_candidate is not None:
        fallback = Alternative(
            variant_id=fallback_candidate.variant_id,
            model=fallback_candidate.model,
            provider=fallback_candidate.provider,
            role="fallback",
            weighted_score=fallback_candidate.weighted_score,
            pass_rate=fallback_candidate.pass_rate,
            cost_per_success_usd=fallback_candidate.cost_per_success_usd,
            reason=reason,
        )
    return alternatives, fallback


def _savings(
    top: CandidateMetrics,
    reference: CandidateMetrics | None,
    reference_variant_id: str,
    category: TaskCategory,
) -> SavingsEstimate:
    if reference is None:
        return SavingsEstimate(
            reference_variant_id=reference_variant_id,
            recommended_variant_id=top.variant_id,
            available=False,
            reason="The reference variant has no evidence on this category.",
            recommended_cost_per_case_usd=top.cost_per_case_usd,
            recommended_cost_per_success_usd=top.cost_per_success_usd,
            recommended_pass_rate=top.pass_rate,
            recommended_attempts=top.attempts,
            case_ids=top.case_ids,
            source_indexes=[top.source_index],
        )
    p_value = two_proportion_p_value(top.passes, top.attempts, reference.passes, reference.attempts)
    pass_delta = (
        top.pass_rate - reference.pass_rate
        if top.pass_rate is not None and reference.pass_rate is not None
        else None
    )
    base = SavingsEstimate(
        available=False,
        reference_variant_id=reference.variant_id,
        recommended_variant_id=top.variant_id,
        reference_cost_per_case_usd=reference.cost_per_case_usd,
        recommended_cost_per_case_usd=top.cost_per_case_usd,
        reference_cost_per_success_usd=reference.cost_per_success_usd,
        recommended_cost_per_success_usd=top.cost_per_success_usd,
        monthly_volume=category.monthly_volume,
        reference_pass_rate=reference.pass_rate,
        recommended_pass_rate=top.pass_rate,
        pass_rate_delta=pass_delta,
        pass_rate_p_value=p_value,
        reference_attempts=reference.attempts,
        recommended_attempts=top.attempts,
        case_ids=sorted(set(top.case_ids) | set(reference.case_ids)),
        source_indexes=sorted({top.source_index, reference.source_index}),
    )
    if set(top.case_ids) != set(reference.case_ids):
        only_top = sorted(set(top.case_ids) - set(reference.case_ids))
        only_reference = sorted(set(reference.case_ids) - set(top.case_ids))
        return base.model_copy(
            update={
                "reason": (
                    f"{top.variant_id} and {reference.variant_id} were measured on different "
                    f"cases ({len(only_top)} only in {top.variant_id}, {len(only_reference)} "
                    f"only in {reference.variant_id}), so their costs are not comparable."
                )
            }
        )
    if top.cost_per_case_usd is None or reference.cost_per_case_usd is None:
        missing = [
            candidate.variant_id
            for candidate in (reference, top)
            if candidate.cost_per_case_usd is None
        ]
        return base.model_copy(
            update={
                "reason": f"Cost evidence is incomplete for {', '.join(dict.fromkeys(missing))}."
            }
        )
    per_case = reference.cost_per_case_usd - top.cost_per_case_usd
    per_success = (
        reference.cost_per_success_usd - top.cost_per_success_usd
        if reference.cost_per_success_usd is not None and top.cost_per_success_usd is not None
        else None
    )
    return base.model_copy(
        update={
            "available": True,
            "reason": (
                "The recommendation is the reference."
                if top.variant_id == reference.variant_id
                else "Measured on the same cases in recorded experiment trials."
            ),
            "cost_per_case_savings_usd": per_case,
            "cost_per_case_savings_ratio": (
                per_case / reference.cost_per_case_usd if reference.cost_per_case_usd else None
            ),
            "cost_per_success_savings_usd": per_success,
            "projected_monthly_savings_usd": (
                per_case * category.monthly_volume if category.monthly_volume is not None else None
            ),
        }
    )


def _case_pass_rates(candidate: CandidateEvidence, case_ids: list[str]) -> dict[str, float]:
    rates: dict[str, float] = {}
    for case_id in case_ids:
        case = candidate.cases.get(case_id)
        if case and case.attempts:
            rates[case_id] = sum(attempt.passed for attempt in case.attempts) / len(case.attempts)
    return rates


def _risks(
    top: CandidateMetrics,
    reference: CandidateMetrics | None,
    top_evidence: CandidateEvidence,
    reference_evidence: CandidateEvidence | None,
    fallback: Alternative | None,
    config: ModelFitConfig,
) -> list[QualityRisk]:
    risks: list[QualityRisk] = []
    if (
        reference is not None
        and reference_evidence is not None
        and reference.variant_id != top.variant_id
    ):
        if (
            top.pass_rate is not None
            and reference.pass_rate is not None
            and top.pass_rate < reference.pass_rate
        ):
            p_value = two_proportion_p_value(
                top.passes, top.attempts, reference.passes, reference.attempts
            )
            significant = p_value is not None and p_value < config.significance_level
            p_text = "n/a" if p_value is None else f"{p_value:.3f}"
            risks.append(
                QualityRisk(
                    kind="quality_regression",
                    severity="high" if significant else "medium",
                    message=(
                        f"Pass rate {top.pass_rate:.1%} is "
                        f"{reference.pass_rate - top.pass_rate:.1%} below the reference "
                        f"{reference.variant_id} ({reference.pass_rate:.1%}, p={p_text}"
                        + (", statistically significant)." if significant else ").")
                    ),
                )
            )
        mine = _case_pass_rates(top_evidence, top.case_ids)
        theirs = _case_pass_rates(reference_evidence, reference.case_ids)
        regressed = sorted(
            case_id
            for case_id, rate in mine.items()
            if case_id in theirs and rate < theirs[case_id]
        )
        if regressed:
            risks.append(
                QualityRisk(
                    kind="regressed_cases",
                    severity="medium",
                    message=(
                        f"{len(regressed)} case(s) pass less often than with the reference "
                        f"{reference.variant_id}."
                    ),
                    case_ids=regressed,
                )
            )
    if top.failed_safety_case_ids:
        risks.append(
            QualityRisk(
                kind="safety_failures",
                severity="high",
                message=(
                    f"Failed safety-tagged case(s) at least once; safety pass rate "
                    f"{_rate(top.safety_pass_rate)} over {top.safety_attempts} attempts."
                ),
                case_ids=top.failed_safety_case_ids,
            )
        )
    if top.flaky_case_ids:
        risks.append(
            QualityRisk(
                kind="flaky_cases",
                severity="low",
                message=f"{len(top.flaky_case_ids)} case(s) passed on some attempts only.",
                case_ids=top.flaky_case_ids,
            )
        )
    if top.attempts < config.minimum_attempts:
        risks.append(
            QualityRisk(
                kind="low_evidence",
                severity="medium",
                message=(
                    f"Only {top.attempts} attempts; at least {config.minimum_attempts} are "
                    "recommended before acting on this."
                ),
            )
        )
    if not top.cost_complete:
        risks.append(
            QualityRisk(
                kind="cost_unavailable",
                severity="medium",
                message="Some completed attempts reported no cost, so costs are unavailable.",
            )
        )
    if top.failed_trial_attempts:
        risks.append(
            QualityRisk(
                kind="failed_trials",
                severity="medium",
                message=(
                    f"{top.failed_trial_attempts} attempt(s) were lost to failed trials and "
                    "count as failures."
                ),
            )
        )
    if fallback is None:
        risks.append(
            QualityRisk(
                kind="no_fallback",
                severity="low",
                message="No other candidate satisfies the constraints, so there is no fallback.",
            )
        )
    return risks


def _explain(
    top: CandidateMetrics,
    feasible: list[CandidateMetrics],
    infeasible: list[CandidateMetrics],
    savings: SavingsEstimate,
    weights: ScoringWeights,
) -> list[str]:
    lines = [
        f"Recommended {top.variant_id} ({top.model}): {_describe(top)}; "
        f"weighted score {top.weighted_score:.3f} "
        f"(quality {weights.quality:g}, cost {weights.cost:g}, latency {weights.latency:g}, "
        f"reliability {weights.reliability:g}).",
        f"It satisfies every hard constraint; {len(feasible)} of "
        f"{len(feasible) + len(infeasible)} candidates do.",
    ]
    if top.pareto_optimal:
        lines.append("It is on the Pareto frontier of pass rate, cost per success, and latency.")
    if savings.available and savings.recommended_variant_id != savings.reference_variant_id:
        saving = savings.cost_per_case_savings_usd or 0.0
        ratio = savings.cost_per_case_savings_ratio
        direction = "cheaper" if saving >= 0 else "more expensive"
        ratio_text = f" ({abs(ratio):.0%})" if ratio is not None else ""
        lines.append(
            f"Per case it is {_money(abs(saving))}{ratio_text} {direction} than the reference "
            f"{savings.reference_variant_id}"
            + (
                f", a projected monthly {'saving' if saving >= 0 else 'increase'} of "
                f"${abs(savings.projected_monthly_savings_usd):,.2f} at "
                f"{savings.monthly_volume:,} requests."
                if savings.projected_monthly_savings_usd is not None
                else "."
            )
        )
    for candidate in feasible:
        if candidate.variant_id != top.variant_id:
            lines.append(
                f"Ranked {candidate.rank}: {candidate.variant_id}, score "
                f"{candidate.weighted_score:.3f}: {_describe(candidate)}."
            )
    for candidate in infeasible:
        reasons = " ".join(violation.message for violation in candidate.violations)
        lines.append(f"Rejected {candidate.variant_id}: {reasons}")
    return lines


def _role(candidate: CandidateMetrics, recommendation: Recommendation) -> str:
    if candidate.variant_id == recommendation.variant_id:
        return "recommended"
    if recommendation.fallback and candidate.variant_id == recommendation.fallback.variant_id:
        return "fallback"
    if any(alt.variant_id == candidate.variant_id for alt in recommendation.alternatives):
        return "alternative"
    return "feasible" if candidate.feasible else "infeasible"


def _category_result(
    category: TaskCategory,
    case_ids: list[str],
    candidates: list[CandidateEvidence],
    safety_case_ids: list[str],
    reference_variant_id: str,
    config: ModelFitConfig,
) -> CategoryResult:
    constraints = config.defaults.merged(category.constraints)
    weights = category.weights or config.weights
    metrics = [
        measure(candidate, case_ids, safety_case_ids, config.confidence_level)
        for candidate in candidates
    ]
    for item in metrics:
        item.violations = check_constraints(item, constraints)
        item.feasible = not item.violations
    score(metrics, weights)
    metrics.sort(key=sort_key)
    feasible = [item for item in metrics if item.feasible]
    infeasible = [item for item in metrics if not item.feasible]
    for rank, item in enumerate(feasible, start=1):
        item.rank = rank
    frontier = pareto_frontier(metrics)
    ranking = cost_per_success_ranking(metrics)
    for item in metrics:
        item.pareto_optimal = item.variant_id in frontier
        item.cost_per_success_rank = (
            ranking.index(item.variant_id) + 1 if item.variant_id in ranking else None
        )

    evidence_by_id = {candidate.variant.variant_id: candidate for candidate in candidates}
    reference = next((item for item in metrics if item.variant_id == reference_variant_id), None)
    if reference is not None and reference.attempts == 0:
        reference = None
    rejected = [item.variant_id for item in infeasible]

    if not case_ids or all(item.attempts == 0 for item in metrics):
        recommendation = Recommendation(
            category_id=category.id,
            status="no_evidence",
            explanation=["No candidate has attempts on this category's cases."],
            rejected_variant_ids=rejected,
        )
    elif not feasible:
        recommendation = Recommendation(
            category_id=category.id,
            status="no_feasible_model",
            explanation=[
                "No candidate satisfies every hard constraint.",
                *(
                    f"Rejected {item.variant_id}: "
                    + " ".join(violation.message for violation in item.violations)
                    for item in infeasible
                ),
            ],
            rejected_variant_ids=rejected,
        )
    else:
        top = feasible[0]
        runner_up = feasible[1] if len(feasible) > 1 else None
        confidence, confidence_reasons = _confidence(top, runner_up, config, constraints, weights)
        alternatives, fallback = _alternatives(top, feasible, config.max_alternatives)
        savings = _savings(top, reference, reference_variant_id, category)
        risks = _risks(
            top,
            reference,
            evidence_by_id[top.variant_id],
            evidence_by_id.get(reference.variant_id) if reference else None,
            fallback,
            config,
        )
        if confidence == "high" and any(
            risk.severity == "high" and risk.kind in {"quality_regression", "safety_failures"}
            for risk in risks
        ):
            confidence = "medium"
            confidence_reasons = [
                "The ranking is clear, but it trades away quality or safety the reference "
                "delivers; see the high-severity quality risks."
            ]
        recommendation = Recommendation(
            category_id=category.id,
            status="recommended",
            variant_id=top.variant_id,
            model=top.model,
            provider=top.provider,
            weighted_score=top.weighted_score,
            confidence=confidence,
            confidence_reasons=confidence_reasons,
            explanation=_explain(top, feasible, infeasible, savings, weights),
            alternatives=alternatives,
            fallback=fallback,
            savings=savings,
            quality_risks=risks,
            rejected_variant_ids=rejected,
        )
    return CategoryResult(
        category=category,
        case_ids=case_ids,
        constraints=constraints,
        weights=weights,
        candidates=metrics,
        pareto_frontier_variant_ids=frontier,
        cost_per_success_ranking=ranking,
        recommendation=recommendation,
    )


def recommend_models(
    reports: Sequence[ExperimentReport | ExperimentEvidence],
    config: ModelFitConfig | None = None,
    *,
    variant_metadata: dict[str, dict[str, str]] | None = None,
) -> ModelFitReport:
    """Recommend a model for every task category from recorded experiment reports.

    Pass `ExperimentEvidence` from `load_experiment_evidence` to record each
    report's file name and SHA-256 in the result's `sources`.
    """
    if not reports:
        raise ValueError("ModelFit needs at least one experiment report")
    config = config or ModelFitConfig()
    evidence = [as_evidence(item) for item in reports]
    candidates, warnings = collect_candidates(evidence, config, variant_metadata)
    if not candidates:
        raise ValueError("every experiment variant is excluded; nothing to recommend")

    candidate_ids = [candidate.variant.variant_id for candidate in candidates]
    reference_variant_id = config.reference_variant_id or evidence[0].report.baseline_variant_id
    if config.reference_variant_id is None:
        baselines = {item.report.baseline_variant_id for item in evidence}
        if len(baselines) > 1:
            warnings.append(
                f"Reports have different baselines; savings are measured against "
                f"{reference_variant_id}, the first report's baseline."
            )
    if reference_variant_id not in candidate_ids:
        if config.reference_variant_id is not None:
            raise ValueError(
                f"reference_variant_id {reference_variant_id!r} is not a candidate variant"
            )
        warnings.append(
            f"Reference variant {reference_variant_id!r} is excluded, so savings are unavailable."
        )

    cases = case_index(candidates)
    safety_tags = set(config.safety_tags)
    safety_case_ids = [
        case_id for case_id, case in cases.items() if safety_tags.intersection(case.tags)
    ]
    taxonomy, uncategorized, taxonomy_warnings = resolve_taxonomy(config, cases)
    warnings.extend(taxonomy_warnings)

    results = [
        _category_result(
            category, case_ids, candidates, safety_case_ids, reference_variant_id, config
        )
        for category, case_ids in taxonomy
    ]
    matrix = [
        MatrixRow(
            category_id=result.category.id,
            variant_id=item.variant_id,
            model=item.model,
            provider=item.provider,
            role=_role(item, result.recommendation),  # type: ignore[arg-type]
            feasible=item.feasible,
            attempts=item.attempts,
            pass_rate=item.pass_rate,
            cost_per_success_usd=item.cost_per_success_usd,
            mean_latency_ms=item.mean_latency_ms,
            weighted_score=item.weighted_score,
            violations=[violation.constraint for violation in item.violations],
        )
        for result in results
        for item in result.candidates
    ]
    recommended = [r for r in results if r.recommendation.status == "recommended"]
    return ModelFitReport(
        name=config.name,
        model_factor=config.model_factor,
        reference_variant_id=reference_variant_id,
        safety_tags=config.safety_tags,
        minimum_attempts=config.minimum_attempts,
        confidence_level=config.confidence_level,
        sources=[evidence_source(item) for item in evidence],
        summary=ModelFitSummary(
            categories=len(results),
            recommended=len(recommended),
            unfit_category_ids=[
                r.category.id for r in results if r.recommendation.status != "recommended"
            ],
            low_confidence_category_ids=[
                r.category.id for r in recommended if r.recommendation.confidence == "low"
            ],
            candidates=len(candidates),
        ),
        categories=results,
        matrix=matrix,
        uncategorized_case_ids=uncategorized,
        warnings=warnings,
    )
