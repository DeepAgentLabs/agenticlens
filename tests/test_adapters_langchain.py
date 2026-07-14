from uuid import uuid4

import pytest
from langchain_core.documents import Document
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, Generation, LLMResult

from agenticlens import profile
from agenticlens.adapters.langchain import AgenticLensCallbackHandler
from agenticlens.models.enums import StepType
from agenticlens.recommenders import RecommendationEngine


def test_llm_call_records_usage_from_message_metadata() -> None:
    handler = AgenticLensCallbackHandler()
    run_id = uuid4()

    with profile("Test") as workflow:
        handler.on_chat_model_start({"name": "ChatOpenAI"}, [[]], run_id=run_id)
        result = LLMResult(
            generations=[
                [
                    ChatGeneration(
                        message=AIMessage(
                            content="hi",
                            usage_metadata={
                                "input_tokens": 10,
                                "output_tokens": 5,
                                "total_tokens": 15,
                            },
                        )
                    )
                ]
            ]
        )
        handler.on_llm_end(result, run_id=run_id)

    assert len(workflow.steps) == 1
    step = workflow.steps[0]
    assert step.type == StepType.LLM_CALL
    assert step.metrics.prompt_tokens == 10
    assert step.metrics.completion_tokens == 5
    assert step.metrics.total_tokens == 15
    assert step.metrics.latency >= 0


def test_llm_call_falls_back_to_llm_output_token_usage() -> None:
    handler = AgenticLensCallbackHandler()
    run_id = uuid4()

    with profile("Test") as workflow:
        handler.on_llm_start({"name": "OpenAI"}, ["hello"], run_id=run_id)
        result = LLMResult(
            generations=[[Generation(text="hi")]],
            llm_output={
                "token_usage": {"prompt_tokens": 20, "completion_tokens": 8},
                "model_name": "gpt-4o-mini",
            },
        )
        handler.on_llm_end(result, run_id=run_id)

    step = workflow.steps[0]
    assert step.metrics.prompt_tokens == 20
    assert step.metrics.completion_tokens == 8
    assert step.metadata["prompt"] == "hello"
    assert step.model == "gpt-4o-mini"


def test_llm_error_finishes_step_without_tokens() -> None:
    handler = AgenticLensCallbackHandler()
    run_id = uuid4()

    with profile("Test") as workflow:
        handler.on_llm_start({"name": "OpenAI"}, ["hello"], run_id=run_id)
        handler.on_llm_error(RuntimeError("boom"), run_id=run_id)

    step = workflow.steps[0]
    assert step.metrics.prompt_tokens == 0
    assert step.metrics.latency >= 0


def test_tool_call_records_name_and_args() -> None:
    handler = AgenticLensCallbackHandler()
    run_id = uuid4()

    with profile("Test") as workflow:
        handler.on_tool_start(
            {"name": "lookup_order"},
            '{"order_id": "A123"}',
            run_id=run_id,
            inputs={"order_id": "A123"},
        )
        handler.on_tool_end("found", run_id=run_id)

    step = workflow.steps[0]
    assert step.type == StepType.TOOL_CALL
    assert step.metadata["tool_name"] == "lookup_order"
    assert step.metadata["tool_args"] == {"order_id": "A123"}


def test_retriever_records_chunk_count_and_avg_tokens() -> None:
    handler = AgenticLensCallbackHandler()
    run_id = uuid4()

    with profile("Test") as workflow:
        handler.on_retriever_start({"name": "Retriever"}, "refund policy", run_id=run_id)
        handler.on_retriever_end(
            [Document(page_content="x" * 40), Document(page_content="x" * 20)],
            run_id=run_id,
        )

    step = workflow.steps[0]
    assert step.type == StepType.RETRIEVER
    assert step.metadata["chunk_count"] == 2
    assert step.metadata["avg_tokens_per_chunk"] == 8  # (40 + 20) / 2 / 4 chars-per-token


def test_duplicate_tool_calls_detected_from_adapter_metadata() -> None:
    handler = AgenticLensCallbackHandler()

    with profile("Test") as workflow:
        for _ in range(2):
            run_id = uuid4()
            handler.on_tool_start(
                {"name": "lookup_order"},
                "",
                run_id=run_id,
                inputs={"order_id": "A123"},
            )
            handler.on_tool_end("found", run_id=run_id)

    recs = RecommendationEngine().run(workflow)
    assert any(r.title == "Duplicate tool call" for r in recs)


def test_finish_on_unknown_run_id_is_a_noop() -> None:
    handler = AgenticLensCallbackHandler()
    with profile("Test"):
        handler.on_llm_end(LLMResult(generations=[]), run_id=uuid4())


def test_handler_outside_profile_raises() -> None:
    handler = AgenticLensCallbackHandler()
    with pytest.raises(RuntimeError):
        handler.on_llm_start({"name": "OpenAI"}, ["hello"], run_id=uuid4())
