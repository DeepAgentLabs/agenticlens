"""ModelFit: recommend models per task category from experiment evidence.

Candidates are the variants of recorded experiment reports. For each task
category ModelFit measures every candidate on that category's cases, rejects
candidates that break a hard constraint (or whose evidence cannot show they
meet it), scores the rest, and recommends the best with a confidence level,
an explanation, alternatives, a fallback, savings against a reference
variant, and the quality risks of switching.
"""

from agenticlens.modelfit.evidence import (
    CandidateEvidence,
    CaseAttempt,
    CaseEvidence,
    ExperimentEvidence,
    collect_candidates,
    load_experiment_evidence,
)
from agenticlens.modelfit.io import (
    load_modelfit_config,
    load_modelfit_report,
    save_modelfit_report,
)
from agenticlens.modelfit.models import (
    MODELFIT_SCHEMA_VERSION,
    OVERALL_CATEGORY_ID,
    Alternative,
    CandidateMetrics,
    CategoryResult,
    EvidenceSource,
    MatrixRow,
    ModelCandidate,
    ModelConstraints,
    ModelFitConfig,
    ModelFitReport,
    ModelFitSummary,
    QualityRisk,
    Recommendation,
    SavingsEstimate,
    ScoringWeights,
    TaskCategory,
    Violation,
)
from agenticlens.modelfit.recommend import recommend_models
from agenticlens.modelfit.render import (
    render_markdown,
    render_matrix_csv,
    save_markdown,
    save_matrix_csv,
)
from agenticlens.modelfit.scoring import (
    check_constraints,
    cost_per_success_ranking,
    pareto_frontier,
)
from agenticlens.modelfit.taxonomy import derive_categories, resolve_taxonomy

__all__ = [
    "MODELFIT_SCHEMA_VERSION",
    "OVERALL_CATEGORY_ID",
    "Alternative",
    "CandidateEvidence",
    "CandidateMetrics",
    "CaseAttempt",
    "CaseEvidence",
    "CategoryResult",
    "EvidenceSource",
    "ExperimentEvidence",
    "MatrixRow",
    "ModelCandidate",
    "ModelConstraints",
    "ModelFitConfig",
    "ModelFitReport",
    "ModelFitSummary",
    "QualityRisk",
    "Recommendation",
    "SavingsEstimate",
    "ScoringWeights",
    "TaskCategory",
    "Violation",
    "check_constraints",
    "collect_candidates",
    "cost_per_success_ranking",
    "derive_categories",
    "load_experiment_evidence",
    "load_modelfit_config",
    "load_modelfit_report",
    "pareto_frontier",
    "recommend_models",
    "render_markdown",
    "render_matrix_csv",
    "resolve_taxonomy",
    "save_markdown",
    "save_matrix_csv",
    "save_modelfit_report",
]
