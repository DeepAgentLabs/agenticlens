"""Every default recommender's output must point back at a step in the analyzed workflow.

Downstream consumers (e.g. deep-agentic-core-mcp's `lens.analyze_workflow`)
promise that each finding carries source provenance. That only holds if the
recommenders themselves record which step they are about.
"""

from datetime import datetime, timezone

from agenticlens.models import Metrics, Step, StepType, Workflow
from agenticlens.recommenders import RecommendationEngine


def _rich_workflow() -> Workflow:
    workflow = Workflow(name="Provenance", start_time=datetime.now(timezone.utc))
    workflow.steps.extend(
        [
            Step(
                id="retrieve",
                name="Retriever",
                type=StepType.RETRIEVER,
                metrics=Metrics(prompt_tokens=100, completion_tokens=20, total_tokens=120),
                metadata={"chunk_count": 12, "avg_tokens_per_chunk": 50},
            ),
            Step(
                id="answer",
                name="Answer",
                type=StepType.LLM_CALL,
                provider="anthropic",
                model="claude-3-5-sonnet",
                metrics=Metrics(prompt_tokens=1000, completion_tokens=1000, total_tokens=2000),
            ),
        ]
    )
    workflow.chaos_events.append(
        {
            "id": "chaos-1",
            "fault_type": "token_timeout",
            "step_id": "answer",
            "outcome": "errored",
            "message": "timed out",
        }
    )
    return workflow


def test_every_default_recommendation_resolves_to_a_workflow_step() -> None:
    workflow = _rich_workflow()
    step_ids = {step.id for step in workflow.steps}

    recs = RecommendationEngine().run(workflow)

    optimization_types = {rec.optimization_type for rec in recs}
    assert {"model_swap", "resilience"} <= optimization_types
    assert len(optimization_types) >= 3
    for rec in recs:
        assert rec.step_id in step_ids, rec.title
        assert rec.step_type is not None, rec.title
        assert rec.evidence, rec.title
        assert all(evidence.span_id == rec.step_id for evidence in rec.evidence), rec.title
