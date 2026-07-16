from datetime import datetime, timezone

from agenticlens.config.settings import RecommenderConfig
from agenticlens.models import Metrics, Step, StepType, Workflow
from agenticlens.recommenders import (
    DuplicateToolCallsRecommender,
    ExcessiveChunksRecommender,
    HandoffBloatRecommender,
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


def test_handoff_bloat_flags_large_agent_context() -> None:
    workflow = _workflow(
        Step(
            name="Research handoff",
            type=StepType.LLM_CALL,
            agent_name="research_agent",
            handoff_from="planner_agent",
            metadata={"handoff_tokens": 5200},
        )
    )

    recs = HandoffBloatRecommender().evaluate(workflow, CONFIG)

    assert len(recs) == 1
    assert recs[0].title == "Large agent handoff context"
    assert recs[0].optimization_type == "agent_handoff_summarization"
    assert recs[0].step_name == "Research handoff"
    assert recs[0].metadata["agent_name"] == "research_agent"
    assert recs[0].metadata["handoff_from"] == "planner_agent"
    assert recs[0].tokens_saved == 5200 - CONFIG.handoff_token_limit


def test_handoff_bloat_no_flag_under_limit() -> None:
    workflow = _workflow(
        Step(
            name="Research handoff",
            type=StepType.LLM_CALL,
            metadata={"handoff_tokens": 500},
        )
    )

    assert HandoffBloatRecommender().evaluate(workflow, CONFIG) == []


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
    assert recs[0].optimization_type == "rag_chunk_pruning"
    assert recs[0].step_name == "Retriever"
    assert recs[0].step_type == "retriever"
    assert recs[0].metadata["low_utility_chunks"] == 2
    assert recs[0].metadata["low_utility_chunk_indexes"] == [2, 3]
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


def test_rag_chunk_utility_uses_reranker_scores() -> None:
    workflow = _workflow(
        Step(
            name="Retriever",
            type=StepType.RETRIEVER,
            metadata={
                "avg_tokens_per_chunk": 60,
                "retrieved_chunks": [
                    {"text": "Relevant chunk", "reranker_score": 0.85},
                    {"text": "Another relevant", "reranker_score": 0.72},
                    {"text": "Low quality chunk", "reranker_score": 0.02},
                    {"text": "Noise chunk", "reranker_score": 0.01},
                ],
            },
        ),
    )

    recs = RAGChunkUtilityRecommender().evaluate(workflow, CONFIG)

    assert len(recs) == 1
    assert recs[0].tokens_saved == 120
    assert recs[0].metadata["signal_quality"] == "rich"
    assert recs[0].quality_risk == "low"
    assert recs[0].confidence is not None and recs[0].confidence >= 0.65


def test_rag_chunk_utility_uses_embedding_similarity() -> None:
    workflow = _workflow(
        Step(
            name="Retriever",
            type=StepType.RETRIEVER,
            metadata={
                "avg_tokens_per_chunk": 40,
                "retrieved_chunks": [
                    {"text": "Highly similar", "cosine_similarity": 0.92},
                    {"text": "Low similarity", "cosine_similarity": 0.03},
                    {"text": "Very low", "embedding_similarity": 0.01},
                ],
            },
        ),
    )

    recs = RAGChunkUtilityRecommender().evaluate(workflow, CONFIG)

    assert len(recs) == 1
    assert recs[0].tokens_saved == 80
    assert recs[0].quality_risk == "low"


def test_rag_chunk_utility_uses_citation_signals() -> None:
    workflow = _workflow(
        Step(
            name="Retriever",
            type=StepType.RETRIEVER,
            metadata={
                "avg_tokens_per_chunk": 50,
                "retrieved_chunks": [
                    {"text": "Used chunk", "cited": True},
                    {"text": "Not cited 1", "cited": False},
                    {"text": "Not cited 2", "cited": False},
                    {"text": "Also cited", "referenced": True},
                ],
            },
        ),
    )

    recs = RAGChunkUtilityRecommender().evaluate(workflow, CONFIG)

    assert len(recs) == 1
    assert recs[0].tokens_saved == 100
    assert recs[0].quality_risk == "low"


def test_rag_chunk_utility_mixed_signals_prefer_explicit() -> None:
    """When explicit signals exist, word-overlap fallback is not used."""
    workflow = _workflow(
        Step(
            name="Retriever",
            type=StepType.RETRIEVER,
            metadata={
                "avg_tokens_per_chunk": 50,
                "retrieved_chunks": [
                    {"text": "Good chunk with overlap words", "reranker_score": 0.9},
                    {"text": "Bad chunk despite overlap words", "reranker_score": 0.01},
                    {"text": "Another bad one", "reranker_score": 0.02},
                ],
            },
        ),
        Step(
            name="Final Response",
            type=StepType.FINAL_RESPONSE,
            metadata={"final_answer": "overlap words in the answer"},
        ),
    )

    recs = RAGChunkUtilityRecommender().evaluate(workflow, CONFIG)

    assert len(recs) == 1
    # Reranker scores should be used, not word overlap
    assert recs[0].quality_risk == "low"
