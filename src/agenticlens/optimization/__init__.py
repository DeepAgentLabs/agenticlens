"""Evidence-backed optimization recommendations from recorded traces."""

from agenticlens.optimization.engine import analyze_optimizations
from agenticlens.optimization.io import (
    load_optimization_config,
    load_optimization_report,
    load_traces,
    save_optimization_report,
)
from agenticlens.optimization.models import (
    MetricChange,
    ObservedOutcome,
    Opportunity,
    OpportunityEvidence,
    OptimizationConfig,
    OptimizationReport,
    OutcomeEvaluation,
    ProjectedBenefit,
    QualityRisk,
    RecommendationDecision,
    TradeoffAnalysis,
    VariantTradeoff,
)
from agenticlens.optimization.outcomes import evaluate_outcome
from agenticlens.optimization.render import render_optimization_markdown, render_outcome_markdown
from agenticlens.optimization.rules import (
    DEFAULT_RULES,
    MemoryRule,
    OptimizationRule,
    PromptCachingRule,
    PromptCompressionRule,
    RedundantStepRule,
    RetrievalRule,
    RetryPolicyRule,
    ToolCachingRule,
    UnnecessaryHandoffRule,
)
from agenticlens.optimization.tracking import RecommendationLedger, report_sha256
from agenticlens.optimization.tradeoffs import QualityCostTradeoffRule, analyze_tradeoffs

__all__ = [
    "DEFAULT_RULES",
    "MemoryRule",
    "MetricChange",
    "ObservedOutcome",
    "Opportunity",
    "OpportunityEvidence",
    "OptimizationConfig",
    "OptimizationReport",
    "OptimizationRule",
    "OutcomeEvaluation",
    "ProjectedBenefit",
    "PromptCachingRule",
    "PromptCompressionRule",
    "QualityCostTradeoffRule",
    "QualityRisk",
    "RecommendationDecision",
    "RecommendationLedger",
    "RedundantStepRule",
    "RetrievalRule",
    "RetryPolicyRule",
    "ToolCachingRule",
    "TradeoffAnalysis",
    "UnnecessaryHandoffRule",
    "VariantTradeoff",
    "analyze_optimizations",
    "analyze_tradeoffs",
    "evaluate_outcome",
    "load_optimization_config",
    "load_optimization_report",
    "load_traces",
    "render_optimization_markdown",
    "render_outcome_markdown",
    "report_sha256",
    "save_optimization_report",
]
