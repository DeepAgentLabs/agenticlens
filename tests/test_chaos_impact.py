from datetime import datetime, timezone

from agenticlens.config.settings import RecommenderConfig
from agenticlens.models import Metrics, Severity, Step, StepType, Workflow
from agenticlens.recommenders import ChaosImpactRecommender, RecommendationEngine


def _workflow_with_step(step_id: str = "step-1") -> Workflow:
    workflow = Workflow(name="Test", start_time=datetime.now(timezone.utc))
    workflow.steps.append(
        Step(
            id=step_id,
            name="Planner",
            type=StepType.PLANNER,
            metrics=Metrics(total_tokens=100, cost=0.01),
        )
    )
    return workflow


def test_no_chaos_events_returns_no_recommendations() -> None:
    workflow = _workflow_with_step()
    assert ChaosImpactRecommender().evaluate(workflow, RecommenderConfig()) == []


def test_errored_event_produces_critical_recommendation() -> None:
    workflow = _workflow_with_step()
    workflow.chaos_events.append(
        {
            "fault_type": "token_timeout",
            "step_id": "step-1",
            "outcome": "errored",
            "message": "call hung for 5s then raised TokenTimeoutError",
        }
    )

    recs = ChaosImpactRecommender().evaluate(workflow, RecommenderConfig())

    assert len(recs) == 1
    assert recs[0].severity == Severity.CRITICAL
    assert "Planner" in recs[0].title
    assert recs[0].tokens_saved == 0


def test_degraded_event_produces_critical_recommendation() -> None:
    workflow = _workflow_with_step()
    workflow.chaos_events.append(
        {
            "fault_type": "silent_degradation",
            "step_id": "step-1",
            "outcome": "degraded",
            "message": "output replaced with garbage text",
        }
    )

    recs = ChaosImpactRecommender().evaluate(workflow, RecommenderConfig())

    assert len(recs) == 1
    assert recs[0].severity == Severity.CRITICAL
    assert "quality" in recs[0].description.lower()


def test_events_grouped_by_step_fault_and_outcome() -> None:
    workflow = _workflow_with_step()
    for _ in range(3):
        workflow.chaos_events.append(
            {
                "fault_type": "rate_limit_storm",
                "step_id": "step-1",
                "outcome": "errored",
                "message": "429 Too Many Requests",
            }
        )

    recs = ChaosImpactRecommender().evaluate(workflow, RecommenderConfig())

    assert len(recs) == 1
    assert "3 times" in recs[0].description


def test_falls_back_to_step_name_when_step_id_unresolved() -> None:
    workflow = _workflow_with_step()
    workflow.chaos_events.append(
        {
            "fault_type": "token_timeout",
            "step_id": "unknown-id",
            "step_name": "Detached Step",
            "outcome": "errored",
            "message": "boom",
        }
    )

    recs = ChaosImpactRecommender().evaluate(workflow, RecommenderConfig())

    assert "Detached Step" in recs[0].title


def test_engine_preserves_chaos_severity_despite_zero_token_savings() -> None:
    workflow = _workflow_with_step()
    workflow.chaos_events.append(
        {
            "fault_type": "token_timeout",
            "step_id": "step-1",
            "outcome": "errored",
            "message": "boom",
        }
    )

    engine = RecommendationEngine()
    recs = engine.run(workflow)

    chaos_recs = [r for r in recs if r.title.startswith("Chaos impact")]
    assert len(chaos_recs) == 1
    assert chaos_recs[0].severity == Severity.CRITICAL
    assert chaos_recs[0].estimated_savings == 0.0


def test_recommendation_carries_step_id_and_per_event_evidence() -> None:
    workflow = _workflow_with_step()
    for attempt in (1, 2):
        workflow.chaos_events.append(
            {
                "id": f"event-{attempt}",
                "fault_type": "rate_limit_storm",
                "step_id": "step-1",
                "outcome": "errored",
                "message": "429 Too Many Requests",
                "timestamp": f"2026-10-13T12:00:0{attempt}Z",
            }
        )

    recs = ChaosImpactRecommender().evaluate(workflow, RecommenderConfig())

    assert recs[0].step_id == "step-1"
    assert recs[0].step_type == "planner"
    assert [e.details["chaos_event_id"] for e in recs[0].evidence] == ["event-1", "event-2"]
    assert all(e.source == "workflow.chaos_event" for e in recs[0].evidence)
    assert all(e.span_id == "step-1" for e in recs[0].evidence)
    assert recs[0].evidence[0].timestamp == datetime(2026, 10, 13, 12, 0, 1, tzinfo=timezone.utc)


def test_step_resolved_by_name_when_event_has_no_step_id() -> None:
    workflow = _workflow_with_step()
    workflow.chaos_events.append(
        {"fault_type": "token_timeout", "step_name": "Planner", "outcome": "errored"}
    )

    recs = ChaosImpactRecommender().evaluate(workflow, RecommenderConfig())

    assert recs[0].step_id == "step-1"
    assert recs[0].evidence[0].timestamp is None


def test_unresolved_step_keeps_the_producer_step_id() -> None:
    workflow = _workflow_with_step()
    workflow.chaos_events.append(
        {
            "fault_type": "token_timeout",
            "step_id": "unknown-id",
            "step_name": "Detached Step",
            "outcome": "errored",
            "timestamp": "not-a-timestamp",
        }
    )

    recs = ChaosImpactRecommender().evaluate(workflow, RecommenderConfig())

    assert recs[0].step_id == "unknown-id"
    assert recs[0].step_type is None
    assert recs[0].evidence[0].timestamp is None


def _workflow_with_duplicate_names() -> Workflow:
    workflow = Workflow(name="Dupes", start_time=datetime.now(timezone.utc))
    for step_id in ("call-a", "call-b"):
        workflow.steps.append(Step(id=step_id, name="LLM Call", type=StepType.LLM_CALL))
    return workflow


def test_same_named_steps_stay_separate_when_events_carry_ids() -> None:
    workflow = _workflow_with_duplicate_names()
    for step_id in ("call-a", "call-b"):
        workflow.chaos_events.append(
            {
                "fault_type": "token_timeout",
                "step_id": step_id,
                "step_name": "LLM Call",
                "outcome": "errored",
            }
        )

    recs = ChaosImpactRecommender().evaluate(workflow, RecommenderConfig())

    assert sorted(rec.step_id or "" for rec in recs) == ["call-a", "call-b"]
    for rec in recs:
        assert all(evidence.span_id == rec.step_id for evidence in rec.evidence)


def test_ambiguous_name_only_event_is_not_attributed_to_an_arbitrary_step() -> None:
    workflow = _workflow_with_duplicate_names()
    workflow.chaos_events.append(
        {"fault_type": "token_timeout", "step_name": "LLM Call", "outcome": "errored"}
    )

    recs = ChaosImpactRecommender().evaluate(workflow, RecommenderConfig())

    assert recs[0].step_id is None
    assert recs[0].step_type is None
    assert recs[0].evidence[0].span_id is None
    assert "LLM Call" in recs[0].title
