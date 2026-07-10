"""Example: RAG chunk utility scoring with reranker, embedding, and citation signals.

Demonstrates how AgenticLens detects low-utility retrieved chunks using
different signal types. Run with:

    uv run agenticlens profile examples/rag_scoring_demo.py --save rag_scoring.json
    uv run agenticlens analyze rag_scoring.json
"""

import time

from agenticlens import profile, step


class FakeUsage:
    def __init__(self, prompt_tokens: int, completion_tokens: int) -> None:
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens


class FakeResponse:
    def __init__(self, prompt_tokens: int, completion_tokens: int) -> None:
        self.usage = FakeUsage(prompt_tokens, completion_tokens)


def main() -> None:
    with profile("RAG Scoring Demo") as workflow:
        # Step 1: Retriever with reranker scores
        with step(
            "Retriever (reranker scored)",
            type="retriever",
            chunk_count=6,
            avg_tokens_per_chunk=80,
            retrieved_chunks=[
                {
                    "text": "Refund policy: Customers can request a refund within 30 days.",
                    "reranker_score": 0.94,
                },
                {
                    "text": "Returns must be in original packaging and unused.",
                    "reranker_score": 0.82,
                },
                {
                    "text": "Refunds are processed to the original payment method.",
                    "reranker_score": 0.76,
                },
                {
                    "text": "Office parking is available on level B2.",
                    "reranker_score": 0.03,
                },
                {
                    "text": "Company holiday schedule for 2025.",
                    "reranker_score": 0.01,
                },
                {
                    "text": "Internal meeting room booking system.",
                    "reranker_score": 0.02,
                },
            ],
        ):
            time.sleep(0.1)

        # Step 2: Retriever with embedding similarity scores
        with step(
            "Retriever (embedding scored)",
            type="retriever",
            chunk_count=4,
            avg_tokens_per_chunk=60,
            retrieved_chunks=[
                {
                    "text": "Shipping takes 5-7 business days for standard delivery.",
                    "cosine_similarity": 0.85,
                },
                {
                    "text": "Express shipping available for 2-3 day delivery.",
                    "cosine_similarity": 0.72,
                },
                {
                    "text": "CEO announced new sustainability initiative.",
                    "cosine_similarity": 0.08,
                },
                {
                    "text": "Cafeteria menu updated for summer.",
                    "embedding_similarity": 0.04,
                },
            ],
        ):
            time.sleep(0.1)

        # Step 3: Retriever with citation signals (post-hoc)
        with step(
            "Retriever (citation tracked)",
            type="retriever",
            chunk_count=5,
            avg_tokens_per_chunk=70,
            retrieved_chunks=[
                {"text": "Refunds may take 5 to 10 business days.", "cited": True},
                {"text": "Contact support for order issues.", "cited": True},
                {"text": "Warehouse inventory management.", "cited": False},
                {"text": "Employee onboarding checklist.", "cited": False},
                {"text": "IT security policy document.", "referenced": False},
            ],
        ):
            time.sleep(0.1)

        # Step 4: Final answer generation
        with step(
            "Final Answer",
            type="final_response",
            provider="openai",
            model="gpt-4o-mini",
            final_answer=(
                "You can request a refund within 30 days if the item is unused "
                "and in original packaging. Refunds are processed to the original "
                "payment method and may take 5 to 10 business days."
            ),
        ) as s:
            s.record(FakeResponse(prompt_tokens=450, completion_tokens=65))

    # Print results
    print(f"Workflow: {workflow.name}")
    print(f"Total tokens: {workflow.total_tokens}")
    print(f"Steps: {len(workflow.steps)}")
    print()

    for s in workflow.steps:
        chunks = s.metadata.get("retrieved_chunks", [])
        if chunks:
            print(f"  {s.name}: {len(chunks)} chunks retrieved")
        else:
            print(f"  {s.name}: {s.metrics.total_tokens} tokens")


if __name__ == "__main__":
    main()
