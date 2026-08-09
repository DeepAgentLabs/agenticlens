from datetime import datetime, timezone

from agenticlens.models import Metrics, Severity, Step, StepType, Workflow
from agenticlens.recommenders import RecommendationEngine


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
    from agenticlens.models.recommendation import Recommendation

    recs = [Recommendation(title="x", description="y", tokens_saved=50)]
    assert RecommendationEngine.estimated_savings_pct(workflow, recs) == 25.0


def test_estimated_savings_pct_caps_at_100() -> None:
    workflow = Workflow(name="Test", start_time=datetime.now(timezone.utc))
    workflow.steps.append(
        Step(name="Planner", type=StepType.PLANNER, metrics=Metrics(total_tokens=10))
    )
    from agenticlens.models.recommendation import Recommendation

    recs = [Recommendation(title="x", description="y", tokens_saved=999)]
    assert RecommendationEngine.estimated_savings_pct(workflow, recs) == 100.0


def test_engine_adds_budget_impact_and_sorts_recommendations() -> None:
    from agenticlens.models.recommendation import Recommendation

    workflow = Workflow(name="Test", start_time=datetime.now(timezone.utc))
    workflow.steps.append(
        Step(
            name="Planner",
            type=StepType.PLANNER,
            metrics=Metrics(total_tokens=1000, cost=0.10),
        )
    )
    engine = RecommendationEngine(
        recommenders=[],
    )

    recs = engine._with_budget_impact(
        workflow,
        [
            Recommendation(title="Small", description="x", tokens_saved=10),
            Recommendation(title="Large", description="x", tokens_saved=250),
        ],
    )

    assert [rec.title for rec in recs] == ["Large", "Small"]
    assert recs[0].estimated_savings == 25.0
    assert recs[0].estimated_usd_savings == 0.025
    assert recs[0].estimated_monthly_savings == 25.0
    assert recs[0].severity == Severity.CRITICAL
