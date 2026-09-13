from pathlib import Path

from agentic_evals import (
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
    calibrate_judge,
)
from agenticlens.evaluation.datasets import (
    dataset_from_samples,
    dataset_to_samples,
    load_dataset,
    save_dataset,
    split_dataset,
    summarize_dataset,
)
from agenticlens.evaluation.html_report import render_html_report, save_html_report
from agenticlens.evaluation.models import (
    ConfidenceInterval,
    DatasetLabel,
    DatasetRecord,
    DatasetSummary,
    EvaluationDataset,
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
) -> EvaluationReport:
    """`agentic_evals.run_live_suite`, normalizing legacy `Run`-shaped traces.

    Live-target callables/HTTP endpoints (see `examples/live_evaluation_demo.py`)
    may still return AgenticLens's `Run`-shaped trace rather than
    `EvalTrace`'s shape -- see `to_eval_trace_dict()`.
    """
    return _agentic_evals_run_live_suite(
        suite, target, registry=registry, trace_adapter=to_eval_trace_dict
    )


__all__ = [
    "BusinessRuleEvaluator",
    "CalibrationCase",
    "CalibrationDataset",
    "CalibrationReport",
    "CallableEvaluator",
    "CaseEvaluation",
    "ConfidenceInterval",
    "DatasetLabel",
    "DatasetRecord",
    "DatasetSummary",
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
    "GateConfig",
    "GateDecision",
    "HTTPTarget",
    "LLMJudgeEvaluator",
    "LiveTarget",
    "PythonTarget",
    "ReferenceLabel",
    "Score",
    "TestCase",
    "TestSuite",
    "calibrate_judge",
    "dataset_from_samples",
    "dataset_to_samples",
    "evaluate_gate",
    "evaluate_suite",
    "load_dataset",
    "load_samples",
    "load_suite",
    "render_html_report",
    "run_live_suite",
    "save_dataset",
    "save_html_report",
    "split_dataset",
    "summarize_dataset",
    "to_eval_trace",
]
