from pathlib import Path

from agentic_evals import (
    BUILTIN_EVALUATOR,
    BusinessRuleEvaluator,
    CallableEvaluator,
    CaseEvaluation,
    EvalSpan,
    EvalTrace,
    EvaluationContext,
    EvaluationReport,
    EvaluationSample,
    EvaluationSummary,
    Evaluator,
    EvaluatorConfig,
    EvaluatorRegistry,
    GateConfig,
    GateDecision,
    HTTPTarget,
    LiveTarget,
    LLMJudgeEvaluator,
    PythonTarget,
    Score,
    TestCase,
    TestSuite,
    evaluate_gate,
    evaluate_suite,
    load_suite,
)
from agentic_evals import load_samples as _agentic_evals_load_samples
from agentic_evals import run_live_suite as _agentic_evals_run_live_suite

from agenticlens.evaluation._trace_adapter import to_eval_trace, to_eval_trace_dict
from agenticlens.evaluation.calibration import (
    CalibrationCase,
    CalibrationDataset,
    CalibrationReport,
    ReferenceLabel,
    ThresholdPoint,
    ThresholdTuningReport,
    calibrate_judge,
    tune_judge_threshold,
)
from agenticlens.evaluation.datasets import (
    dataset_from_samples,
    dataset_to_samples,
    load_dataset,
    save_dataset,
    split_dataset,
    summarize_dataset,
)
from agenticlens.evaluation.evidence import (
    CostCoverage,
    EvidenceAudit,
    EvidenceIssue,
    audit_report,
)
from agenticlens.evaluation.html_report import render_html_report, save_html_report
from agenticlens.evaluation.judging import (
    DEFAULT_VERDICT_VALUES,
    JudgeUsage,
    JudgeVerdict,
    evaluated_model,
    judge_verdict,
    prompt_fingerprint,
    structured_judge,
)
from agenticlens.evaluation.models import (
    ConfidenceInterval,
    DatasetLabel,
    DatasetRecord,
    DatasetSummary,
    EvaluationDataset,
)
from agenticlens.evaluation.notifications import (
    Breach,
    NotificationResult,
    breached_thresholds,
    build_payload,
    notify_gate_breach,
)
from agenticlens.evaluation.score_analysis import (
    Disagreement,
    JudgeCost,
    JudgeCostSummary,
    KindSummary,
    PairwiseAgreement,
    ScoreAnalysis,
    analyze_scores,
    score_kind,
)
from agenticlens.evaluation.trace_evaluators import (
    TRACE_EVALUATOR_VERSION,
    TRACE_EVALUATORS,
    default_registry,
    register_trace_evaluators,
    trace_evaluators,
)


def load_samples(path: Path) -> list[EvaluationSample]:
    """`agentic_evals.load_samples`, normalizing legacy `Run`-shaped traces.

    Older saved sample files may still carry AgenticLens's `Run`-shaped
    trace (`started_at`/`completed_at`, per-span cost) rather than
    `EvalTrace`'s shape -- see `to_eval_trace_dict()`.
    """
    return _agentic_evals_load_samples(path, trace_adapter=to_eval_trace_dict)


def run_live_suite(
    suite: TestSuite,
    target: LiveTarget,
    *,
    registry: EvaluatorRegistry | None = None,
    max_workers: int = 1,
) -> EvaluationReport:
    """`agentic_evals.run_live_suite`, normalizing legacy `Run`-shaped traces.

    Live-target callables/HTTP endpoints (see `examples/live_evaluation_demo.py`)
    may still return AgenticLens's `Run`-shaped trace rather than
    `EvalTrace`'s shape -- see `to_eval_trace_dict()`. `max_workers` above 1
    calls the target for several cases concurrently; case order is preserved.
    """
    return _agentic_evals_run_live_suite(
        suite,
        target,
        registry=registry,
        trace_adapter=to_eval_trace_dict,
        max_workers=max_workers,
    )


__all__ = [
    "BUILTIN_EVALUATOR",
    "DEFAULT_VERDICT_VALUES",
    "TRACE_EVALUATORS",
    "TRACE_EVALUATOR_VERSION",
    "Breach",
    "BusinessRuleEvaluator",
    "CalibrationCase",
    "CalibrationDataset",
    "CalibrationReport",
    "CallableEvaluator",
    "CaseEvaluation",
    "ConfidenceInterval",
    "CostCoverage",
    "DatasetLabel",
    "DatasetRecord",
    "DatasetSummary",
    "Disagreement",
    "EvalSpan",
    "EvalTrace",
    "EvaluationContext",
    "EvaluationDataset",
    "EvaluationReport",
    "EvaluationSample",
    "EvaluationSummary",
    "Evaluator",
    "EvaluatorConfig",
    "EvaluatorRegistry",
    "EvidenceAudit",
    "EvidenceIssue",
    "GateConfig",
    "GateDecision",
    "HTTPTarget",
    "JudgeCost",
    "JudgeCostSummary",
    "JudgeUsage",
    "JudgeVerdict",
    "KindSummary",
    "LLMJudgeEvaluator",
    "LiveTarget",
    "NotificationResult",
    "PairwiseAgreement",
    "PythonTarget",
    "ReferenceLabel",
    "Score",
    "ScoreAnalysis",
    "TestCase",
    "TestSuite",
    "ThresholdPoint",
    "ThresholdTuningReport",
    "analyze_scores",
    "audit_report",
    "breached_thresholds",
    "build_payload",
    "calibrate_judge",
    "dataset_from_samples",
    "dataset_to_samples",
    "default_registry",
    "evaluate_gate",
    "evaluate_suite",
    "evaluated_model",
    "judge_verdict",
    "load_dataset",
    "load_samples",
    "load_suite",
    "notify_gate_breach",
    "prompt_fingerprint",
    "register_trace_evaluators",
    "render_html_report",
    "run_live_suite",
    "save_dataset",
    "save_html_report",
    "score_kind",
    "split_dataset",
    "structured_judge",
    "summarize_dataset",
    "to_eval_trace",
    "trace_evaluators",
    "tune_judge_threshold",
]
