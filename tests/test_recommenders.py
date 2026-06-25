from datetime import datetime, timezone

from tokenlens.models import Metrics, Step, StepType, Workflow
from tokenlens.recommenders import RecommendationEngine


def test_engine_with_no_rules_returns_no_recommendations() -> None:
    workflow = Workflow(name="Test", start_time=datetime.now(timezone.utc))
    workflow.steps.append(
        Step(name="Planner", type=StepType.PLANNER, metrics=Metrics(total_tokens=100))
    )

    engine = RecommendationEngine()
    assert engine.run(workflow) == []


def test_estimated_savings_pct_formula() -> None:
    workflow = Workflow(name="Test", start_time=datetime.now(timezone.utc))
    workflow.steps.append(
        Step(name="Planner", type=StepType.PLANNER, metrics=Metrics(total_tokens=200))
    )
    from tokenlens.models.recommendation import Recommendation

    recs = [Recommendation(title="x", description="y", tokens_saved=50)]
    assert RecommendationEngine.estimated_savings_pct(workflow, recs) == 25.0


def test_estimated_savings_pct_caps_at_100() -> None:
    workflow = Workflow(name="Test", start_time=datetime.now(timezone.utc))
    workflow.steps.append(
        Step(name="Planner", type=StepType.PLANNER, metrics=Metrics(total_tokens=10))
    )
    from tokenlens.models.recommendation import Recommendation

    recs = [Recommendation(title="x", description="y", tokens_saved=999)]
    assert RecommendationEngine.estimated_savings_pct(workflow, recs) == 100.0
