import pytest

from agenticlens import profile, step
from agenticlens.models import StepType
from agenticlens.profiler.context import current_workflow


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


def test_cost_is_applied_when_provider_and_model_known() -> None:
    class Usage:
        prompt_tokens = 1000
        completion_tokens = 1000

    class Response:
        usage = Usage()

    with (
        profile("Test") as workflow,
        step("LLM Call", type="llm_call", provider="openai", model="gpt-4o-mini") as s,
    ):
        s.record(Response())

    assert workflow.steps[0].metrics.cost == pytest.approx(0.00015 + 0.0006)


def test_cost_stays_none_when_provider_or_model_missing() -> None:
    with profile("Test") as workflow, step("Planner", type="planner"):
        pass

    assert workflow.steps[0].metrics.cost is None


def test_record_sets_ttft_when_provided() -> None:
    class Usage:
        prompt_tokens = 10
        completion_tokens = 5

    class Response:
        usage = Usage()

    with profile("Test"), step("LLM Call", type="llm_call") as s:
        s.record(Response(), ttft=0.42)
        assert s.step.metrics.ttft == 0.42
