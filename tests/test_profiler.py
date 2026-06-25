import pytest

from tokenlens import profile, step
from tokenlens.models import StepType
from tokenlens.profiler.context import current_workflow


def test_profile_creates_workflow_and_records_steps() -> None:
    with profile("Customer Support") as workflow:
        with step("Planner", type=StepType.PLANNER):
            pass
        with step("Retriever", type="retriever"):
            pass

    assert workflow.name == "Customer Support"
    assert workflow.end_time is not None
    assert [s.name for s in workflow.steps] == ["Planner", "Retriever"]
    assert workflow.steps[1].type == StepType.RETRIEVER


def test_step_outside_profile_raises() -> None:
    with pytest.raises(RuntimeError), step("Planner", type="planner"):
        pass


def test_nested_profile_raises() -> None:
    with profile("Outer"), pytest.raises(RuntimeError), profile("Inner"):
        pass


def test_context_var_resets_after_profile() -> None:
    with profile("Customer Support"):
        pass
    assert current_workflow.get() is None


def test_step_record_attaches_usage_from_openai_like_response() -> None:
    class Usage:
        prompt_tokens = 10
        completion_tokens = 5

    class Response:
        usage = Usage()

    with profile("Test"), step("LLM Call", type="llm_call") as s:
        s.record(Response())
        assert s.step.metrics.prompt_tokens == 10
        assert s.step.metrics.completion_tokens == 5
        assert s.step.metrics.total_tokens == 15
