from datetime import datetime, timezone

from agenticlens.config.settings import RecommenderConfig
from agenticlens.models import Metrics, Step, StepType, Workflow
from agenticlens.recommenders import (
    DuplicateToolCallsRecommender,
    ExcessiveChunksRecommender,
    LongHistoryRecommender,
    RAGChunkUtilityRecommender,
    RepeatedSystemPromptRecommender,
)

CONFIG = RecommenderConfig()


def _workflow(*steps: Step) -> Workflow:
    workflow = Workflow(name="Test", start_time=datetime.now(timezone.utc))
    workflow.steps.extend(steps)
    return workflow


def test_repeated_system_prompt_flags_second_occurrence() -> None:
    prompt = "You are a helpful assistant. " * 20
    workflow = _workflow(
        Step(
            name="Planner",
            type=StepType.PLANNER,
            metrics=Metrics(prompt_tokens=900),
            metadata={"prompt": prompt + "Plan this."},
        ),
        Step(
            name="Final Response",
            type=StepType.FINAL_RESPONSE,
            metrics=Metrics(prompt_tokens=850),
            metadata={"prompt": prompt + "Respond now."},
        ),
    )

    recs = RepeatedSystemPromptRecommender().evaluate(workflow, CONFIG)

    assert len(recs) == 1
    assert recs[0].title == "Repeated system prompt"
    assert recs[0].tokens_saved > 0


def test_repeated_system_prompt_no_flag_when_prompts_differ() -> None:
    workflow = _workflow(
        Step(
            name="Planner",
            type=StepType.PLANNER,
            metrics=Metrics(prompt_tokens=900),
            metadata={"prompt": "Plan the trip to Paris."},
        ),
        Step(
            name="Final Response",
            type=StepType.FINAL_RESPONSE,
            metrics=Metrics(prompt_tokens=850),
            metadata={"prompt": "Summarize the weather report."},
        ),
    )

    assert RepeatedSystemPromptRecommender().evaluate(workflow, CONFIG) == []


def test_excessive_chunks_flags_over_limit() -> None:
    workflow = _workflow(
        Step(
            name="Retriever",
            type=StepType.RETRIEVER,
            metadata={"chunk_count": 12, "avg_tokens_per_chunk": 80},
        )
    )

    recs = ExcessiveChunksRecommender().evaluate(workflow, CONFIG)

    assert len(recs) == 1
    assert recs[0].tokens_saved == (12 - CONFIG.max_chunks) * 80


def test_excessive_chunks_no_flag_under_limit() -> None:
    workflow = _workflow(
        Step(
            name="Retriever",
            type=StepType.RETRIEVER,
            metadata={"chunk_count": 4, "avg_tokens_per_chunk": 80},
        )
    )

    assert ExcessiveChunksRecommender().evaluate(workflow, CONFIG) == []


def test_long_history_flags_over_limit() -> None:
    workflow = _workflow(
        Step(
            name="Memory",
            type=StepType.MEMORY,
            metadata={"history_tokens": 6000},
        )
    )

    recs = LongHistoryRecommender().evaluate(workflow, CONFIG)

    assert len(recs) == 1
    assert recs[0].tokens_saved == 6000 - CONFIG.history_token_limit


def test_long_history_no_flag_under_limit() -> None:
    workflow = _workflow(
        Step(
            name="Memory",
            type=StepType.MEMORY,
            metadata={"history_tokens": 1000},
        )
    )

    assert LongHistoryRecommender().evaluate(workflow, CONFIG) == []


def test_duplicate_tool_calls_flags_second_occurrence() -> None:
    args = {"tool_name": "lookup_order", "tool_args": {"order_id": "A123"}}
    workflow = _workflow(
        Step(
            name="Lookup",
            type=StepType.TOOL_CALL,
            metrics=Metrics(prompt_tokens=100, completion_tokens=20),
            metadata=args,
        ),
        Step(
            name="Lookup (retry)",
            type=StepType.TOOL_CALL,
            metrics=Metrics(prompt_tokens=100, completion_tokens=20),
            metadata=args,
        ),
    )

    recs = DuplicateToolCallsRecommender().evaluate(workflow, CONFIG)

    assert len(recs) == 1
    assert recs[0].tokens_saved == 120


def test_duplicate_tool_calls_no_flag_for_different_args() -> None:
    workflow = _workflow(
        Step(
            name="Lookup A",
            type=StepType.TOOL_CALL,
            metadata={"tool_name": "lookup_order", "tool_args": {"order_id": "A123"}},
        ),
        Step(
            name="Lookup B",
            type=StepType.TOOL_CALL,
            metadata={"tool_name": "lookup_order", "tool_args": {"order_id": "B456"}},
        ),
    )

    assert DuplicateToolCallsRecommender().evaluate(workflow, CONFIG) == []


def test_rag_chunk_utility_flags_chunks_not_used_in_answer() -> None:
    workflow = _workflow(
        Step(
            name="Retriever",
            type=StepType.RETRIEVER,
            metadata={
                "avg_tokens_per_chunk": 50,
                "retrieved_chunks": [
                    "Refunds are processed to the original payment method.",
                    "Refunds may take 5 to 10 business days.",
                    "Warehouse robots sort inventory by aisle number.",
                    "Gift cards cannot be exchanged for cash.",
                ],
            },
        ),
        Step(
            name="Final Response",
            type=StepType.FINAL_RESPONSE,
            metadata={
                "final_answer": (
                    "Refunds are processed to the original payment method and "
                    "may take 5 to 10 business days."
                )
            },
        ),
    )

    recs = RAGChunkUtilityRecommender().evaluate(workflow, CONFIG)

    assert len(recs) == 1
    assert recs[0].title == "Low-utility retrieved chunks"
    assert recs[0].tokens_saved == 100
    assert recs[0].confidence is not None
    assert recs[0].quality_risk == "medium"


def test_rag_chunk_utility_skips_when_no_answer_or_scores() -> None:
    workflow = _workflow(
        Step(
            name="Retriever",
            type=StepType.RETRIEVER,
            metadata={"retrieved_chunks": ["A plain chunk", "Another plain chunk"]},
        )
    )

    assert RAGChunkUtilityRecommender().evaluate(workflow, CONFIG) == []
