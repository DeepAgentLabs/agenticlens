"""Turn experiment reports into per-candidate, per-case attempt records.

Each variant of an experiment report is one ModelFit candidate. Every trial
contributes one attempt per suite case: a succeeded trial contributes the
case's evaluated outcome, latency, and cost; a failed trial (the target call
itself failed) contributes a failed attempt with no latency or cost, matching
how the experiment runner counts it.
"""

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

from agenticlens.experiments import ExperimentReport, ExperimentVariantResult
from agenticlens.modelfit.models import EvidenceSource, ModelCandidate, ModelFitConfig

DOMAIN_KEY = "domain"


@dataclass(frozen=True)
class ExperimentEvidence:
    """An experiment report plus where it was loaded from."""

    report: ExperimentReport
    file: str | None = None
    sha256: str | None = None


@dataclass(frozen=True)
class CaseAttempt:
    passed: bool
    completed: bool
    latency_ms: float | None = None
    cost_usd: float | None = None


@dataclass
class CaseEvidence:
    case_id: str
    tags: list[str] = field(default_factory=list)
    domain: str | None = None
    attempts: list[CaseAttempt] = field(default_factory=list)


@dataclass
class CandidateEvidence:
    variant: ExperimentVariantResult
    source_index: int
    model: str
    provider: str | None
    deployment: str | None
    capabilities: list[str]
    cases: dict[str, CaseEvidence]


def load_experiment_evidence(path: Path) -> ExperimentEvidence:
    """Load an experiment report and fingerprint the exact bytes it was read from."""
    data = path.read_bytes()
    report = ExperimentReport.model_validate_json(data)
    return ExperimentEvidence(
        report=report, file=path.name, sha256=hashlib.sha256(data).hexdigest()
    )


def as_evidence(item: ExperimentReport | ExperimentEvidence) -> ExperimentEvidence:
    return item if isinstance(item, ExperimentEvidence) else ExperimentEvidence(report=item)


def evidence_source(evidence: ExperimentEvidence) -> EvidenceSource:
    report = evidence.report
    return EvidenceSource(
        experiment_name=report.experiment_name,
        experiment_version=report.experiment_version,
        suite_name=report.suite_name,
        suite_version=report.suite_version,
        baseline_variant_id=report.baseline_variant_id,
        trial_count=report.trial_count,
        created_at=report.created_at,
        variant_ids=[variant.variant_id for variant in report.variants],
        file=evidence.file,
        sha256=evidence.sha256,
    )


def _case_universe(report: ExperimentReport) -> list[str]:
    if report.case_ids:
        return list(report.case_ids)
    seen: dict[str, None] = {}
    for variant in report.variants:
        for trial in variant.trials:
            if trial.report is not None:
                for case in trial.report.cases:
                    seen.setdefault(case.case_id, None)
    return list(seen)


def _identity(
    variant: ExperimentVariantResult,
    catalog: dict[str, ModelCandidate],
    model_factor: str,
    metadata: dict[str, str],
) -> tuple[str, str | None, str | None, list[str]]:
    entry = catalog.get(variant.variant_id)
    model = (
        (entry.model if entry else None)
        or variant.factors.get(model_factor)
        or metadata.get("model")
        or variant.variant_id
    )
    provider = (
        (entry.provider if entry else None)
        or metadata.get("provider")
        or variant.factors.get("provider")
    )
    deployment = (
        (entry.deployment if entry else None)
        or metadata.get("deployment")
        or variant.factors.get("deployment")
    )
    if entry is not None and "capabilities" in entry.model_fields_set:
        capabilities = list(entry.capabilities)
    else:
        raw = metadata.get("capabilities", "")
        capabilities = [item.strip() for item in raw.split(",") if item.strip()]
    return model, provider, deployment, capabilities


def collect_candidates(
    evidence: list[ExperimentEvidence],
    config: ModelFitConfig,
    variant_metadata: dict[str, dict[str, str]] | None = None,
) -> tuple[list[CandidateEvidence], list[str]]:
    """Build one `CandidateEvidence` per non-excluded variant across all reports.

    `variant_metadata` maps variant IDs to their manifest metadata when the
    caller has it; experiment reports do not carry variant metadata, so the
    config's `candidates` catalog is the usual source of provider and
    deployment facts.
    """
    catalog = {candidate.variant_id: candidate for candidate in config.candidates}
    excluded = set(config.exclude_variant_ids)
    metadata_by_variant = variant_metadata or {}
    candidates: list[CandidateEvidence] = []
    warnings: list[str] = []
    seen_variants: set[str] = set()

    for source_index, item in enumerate(evidence):
        report = item.report
        universe = _case_universe(report)
        for variant in report.variants:
            if variant.variant_id in excluded:
                continue
            if variant.variant_id in seen_variants:
                raise ValueError(
                    f"variant ID {variant.variant_id!r} appears in more than one experiment "
                    "report; exclude one of them or rename the variant"
                )
            seen_variants.add(variant.variant_id)
            cases = {case_id: CaseEvidence(case_id=case_id) for case_id in universe}
            for trial in variant.trials:
                outcomes = (
                    {case.case_id: case for case in trial.report.cases}
                    if trial.status == "succeeded" and trial.report is not None
                    else None
                )
                for case_id, case_evidence in cases.items():
                    case = outcomes.get(case_id) if outcomes is not None else None
                    if case is None:
                        case_evidence.attempts.append(CaseAttempt(passed=False, completed=False))
                        continue
                    if not case_evidence.tags and case.tags:
                        case_evidence.tags = list(case.tags)
                    if case_evidence.domain is None:
                        domain = case.metadata.get(DOMAIN_KEY)
                        if isinstance(domain, str) and domain:
                            case_evidence.domain = domain
                    case_evidence.attempts.append(
                        CaseAttempt(
                            passed=case.passed,
                            completed=True,
                            latency_ms=case.latency_ms,
                            cost_usd=case.cost_usd,
                        )
                    )
            model, provider, deployment, capabilities = _identity(
                variant,
                catalog,
                config.model_factor,
                metadata_by_variant.get(variant.variant_id, {}),
            )
            candidates.append(
                CandidateEvidence(
                    variant=variant,
                    source_index=source_index,
                    model=model,
                    provider=provider,
                    deployment=deployment,
                    capabilities=capabilities,
                    cases=cases,
                )
            )

    unknown = sorted(set(catalog) - seen_variants - excluded)
    if unknown:
        warnings.append(
            "Candidate catalog names variants that are not in any experiment report: "
            + ", ".join(unknown)
        )
    suites = {(item.report.suite_name, item.report.suite_version) for item in evidence}
    if len(suites) > 1:
        warnings.append(
            "Experiment reports use different suites; each candidate's category metrics "
            "cover only the cases its own experiment ran, so comparisons are not like-for-like."
        )
    by_model: dict[str, list[str]] = {}
    for candidate in candidates:
        by_model.setdefault(candidate.model, []).append(candidate.variant.variant_id)
    for model, variant_ids in sorted(by_model.items()):
        if len(variant_ids) > 1:
            warnings.append(
                f"Variants {', '.join(variant_ids)} share {config.model_factor} {model!r}; "
                "they are compared as separate configurations."
            )
    return candidates, warnings
