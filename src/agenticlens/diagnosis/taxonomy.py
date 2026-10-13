"""Failure taxonomy shared by diagnosis rules, attribution, and reports.

Each category names *what kind* of failure a diagnosis describes, which
layer of an agent system it belongs to, how severe it is by default, and
what to inspect next. The taxonomy is versioned so saved diagnosis reports
say which category set they were produced with.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Literal

#: Bump when a category is added, removed, or changes meaning.
TAXONOMY_VERSION = "1.0"

Severity = Literal["low", "medium", "high", "critical"]
Layer = Literal[
    "tool",
    "model",
    "retrieval",
    "orchestration",
    "quality",
    "resource",
    "environment",
    "outcome",
]

#: Severity order, lowest first.
SEVERITY_ORDER: tuple[Severity, ...] = ("low", "medium", "high", "critical")


class FailureCategory(str, Enum):
    TOOL_ERROR = "tool_error"
    MODEL_ERROR = "model_error"
    RETRIEVAL_ERROR = "retrieval_error"
    TIMEOUT = "timeout"
    RETRY_EXHAUSTED = "retry_exhausted"
    TOOL_LOOP = "tool_loop"
    HANDOFF_LOOP = "handoff_loop"
    STAGNATION = "stagnation"
    EMPTY_RETRIEVAL = "empty_retrieval"
    VALIDATION_FAILURE = "validation_failure"
    DELEGATION_FAILURE = "delegation_failure"
    BUDGET_EXCEEDED = "budget_exceeded"
    INJECTED_FAULT = "injected_fault"
    INCOMPLETE_TASK = "incomplete_task"


@dataclass(frozen=True)
class CategoryInfo:
    """What a failure category means and how to follow it up."""

    category: FailureCategory
    layer: Layer
    description: str
    default_severity: Severity
    #: How strongly a diagnosis of this category points at its own span as
    #: the root cause (0-1). Explicit errors point at the failing span;
    #: budget or outcome diagnoses only point at where symptoms appeared.
    attribution_weight: float
    next_step: str


FAILURE_TAXONOMY: Mapping[FailureCategory, CategoryInfo] = {
    info.category: info
    for info in (
        CategoryInfo(
            FailureCategory.TOOL_ERROR,
            "tool",
            "A tool call returned an error or raised.",
            "high",
            0.9,
            "Inspect the tool's input arguments and error message; check whether the "
            "error is transient (retryable) or caused by the arguments the agent chose.",
        ),
        CategoryInfo(
            FailureCategory.MODEL_ERROR,
            "model",
            "A model call failed (provider error, refusal, or malformed response).",
            "high",
            0.9,
            "Check the provider error type, rate limits, and the prompt size sent to the model.",
        ),
        CategoryInfo(
            FailureCategory.RETRIEVAL_ERROR,
            "retrieval",
            "A retrieval step failed before returning results.",
            "high",
            0.9,
            "Check the retriever's backing store and the query it was given.",
        ),
        CategoryInfo(
            FailureCategory.TIMEOUT,
            "environment",
            "A span exceeded its time limit or failed with a timeout error.",
            "high",
            0.85,
            "Compare the span's latency with its timeout and with earlier runs; look for "
            "slow dependencies or oversized inputs.",
        ),
        CategoryInfo(
            FailureCategory.RETRY_EXHAUSTED,
            "orchestration",
            "Every retry of a failed operation also failed.",
            "high",
            0.8,
            "Look at the original failure the retries targeted; repeating an identical "
            "request rarely fixes a non-transient error.",
        ),
        CategoryInfo(
            FailureCategory.TOOL_LOOP,
            "orchestration",
            "The same tool was called repeatedly with the same input.",
            "medium",
            0.7,
            "Check whether the agent reads the tool's result; add a loop limit or cache.",
        ),
        CategoryInfo(
            FailureCategory.HANDOFF_LOOP,
            "orchestration",
            "Agents handed control back and forth without converging.",
            "medium",
            0.7,
            "Review the handoff conditions between the two agents; one of them is "
            "returning work it should finish or escalate.",
        ),
        CategoryInfo(
            FailureCategory.STAGNATION,
            "quality",
            "Consecutive model calls produced the same output (no progress).",
            "medium",
            0.65,
            "Check whether new information reaches the model between calls; a planner "
            "repeating itself usually lacks tool results or feedback.",
        ),
        CategoryInfo(
            FailureCategory.EMPTY_RETRIEVAL,
            "retrieval",
            "A retrieval step returned no documents.",
            "medium",
            0.6,
            "Check the query and index; downstream answers may be ungrounded.",
        ),
        CategoryInfo(
            FailureCategory.VALIDATION_FAILURE,
            "quality",
            "An output or intermediate result failed validation.",
            "high",
            0.85,
            "Compare the rejected value with the validator's rule; check the step that "
            "produced the value, not only the validator.",
        ),
        CategoryInfo(
            FailureCategory.DELEGATION_FAILURE,
            "orchestration",
            "Delegating work to another agent failed.",
            "high",
            0.85,
            "Check the receiving agent's availability and the payload it was handed.",
        ),
        CategoryInfo(
            FailureCategory.BUDGET_EXCEEDED,
            "resource",
            "The run exceeded a configured cost, token, or latency budget.",
            "medium",
            0.4,
            "Start with the spans that consumed the most of the exceeded budget.",
        ),
        CategoryInfo(
            FailureCategory.INJECTED_FAULT,
            "environment",
            "A deliberately injected fault (for example from agentic-chaos) hit this span.",
            "medium",
            1.0,
            "Check whether the workflow detected and recovered from the injected fault.",
        ),
        CategoryInfo(
            FailureCategory.INCOMPLETE_TASK,
            "outcome",
            "The run did not complete its task and no specific failure explains why.",
            "medium",
            0.3,
            "Evaluate the final response against the task; consider adding spans or "
            "validation steps so the failure becomes attributable.",
        ),
    )
}


def describe(category: FailureCategory) -> CategoryInfo:
    """The taxonomy entry for `category`."""
    return FAILURE_TAXONOMY[category]


def max_severity(values: list[Severity]) -> Severity:
    """The most severe of `values` (``low`` when empty)."""
    return max(values, key=SEVERITY_ORDER.index, default="low")
