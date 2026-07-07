from datetime import datetime, timezone

from agenticlens.models import Metrics, Severity, Step, StepType, Workflow
from agenticlens.models.recommendation import Recommendation


def test_workflow_aggregates_step_metrics() -> None:
    workflow = Workflow(name="Test Workflow", start_time=datetime.now(timezone.utc))
    workflow.steps.append(
        Step(
            name="Planner",
            type=StepType.PLANNER,
            metrics=Metrics(prompt_tokens=100, completion_tokens=50, total_tokens=150, cost=0.01),
        )
    )
    workflow.steps.append(
        Step(
            name="Retriever",
            type=StepType.RETRIEVER,
            metrics=Metrics(prompt_tokens=20, completion_tokens=0, total_tokens=20, cost=0.001),
        )
    )

    assert workflow.total_tokens == 170
    assert workflow.total_cost == 0.011


def test_workflow_total_cost_none_when_unpriced() -> None:
    workflow = Workflow(name="Test Workflow", start_time=datetime.now(timezone.utc))
    workflow.steps.append(Step(name="Planner", type=StepType.PLANNER))

    assert workflow.total_cost is None


def test_metrics_tps() -> None:
    metrics = Metrics(completion_tokens=100, latency=2.0)
    assert metrics.tps == 50.0


def test_metrics_tps_none_when_no_latency() -> None:
    metrics = Metrics(completion_tokens=100, latency=0.0)
    assert metrics.tps is None


def test_recommendation_defaults() -> None:
    rec = Recommendation(title="Repeated system prompt", description="...")
    assert rec.severity == Severity.INFO
    assert rec.tokens_saved == 0
