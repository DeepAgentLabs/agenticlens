import time

from agenticlens import profile, step
from benchmarks.shared.support_data import load_policy_docs
from benchmarks.shared.support_tasks import (
    check_refund_eligibility,
    classify_ticket,
    generate_customer_reply,
    lookup_order_tool,
    retrieve_policy,
    rewrite_query,
)


def main() -> None:
    framework = "LlamaIndex"

    try:
        from llama_index.core import Document
    except ImportError as exc:
        raise RuntimeError("LlamaIndex is not installed. Run: pip install llama-index") from exc

    ticket = (
        "My order A123 was delivered 12 days ago. "
        "I opened the package but did not use the item. "
        "Can I get a refund, and how long will it take?"
    )
    order_id = "A123"

    # Framework-specific indexing object.
    # This builds a LlamaIndex document collection, but the deterministic benchmark
    # uses shared retrieval so results stay comparable with other framework runs.
    policy_docs = load_policy_docs()
    documents = [
        Document(text=doc["text"], metadata={"doc_id": doc["doc_id"], "category": doc["category"]})
        for doc in policy_docs
    ]

    # Do not build a real embedding index in the deterministic run because it may
    # require model configuration. Keep this object as the framework-specific
    # document representation.
    index_metadata = {
        "framework_documents": len(documents),
        "index_type": "llamaindex_documents",
    }

    with profile("Benchmark - LlamaIndex - Support Refund"):
        with step(
            "LlamaIndex - Classify Ticket Intent",
            type="planner",
            provider="openai",
            model="gpt-4o-mini",
            prompt=ticket,
            framework="llamaindex",
            **index_metadata,
        ) as s:
            start = time.time()
            response = classify_ticket(ticket, framework)
            s.record(response)
            s.step.metrics.latency = time.time() - start
            intent = response.choices[0].message.content

        with step(
            "LlamaIndex - Rewrite Query For Retrieval",
            type="llm_call",
            provider="openai",
            model="gpt-4o-mini",
            prompt=ticket,
            framework="llamaindex",
        ) as s:
            start = time.time()
            response = rewrite_query(ticket, framework)
            s.record(response)
            s.step.metrics.latency = time.time() - start
            query = response.choices[0].message.content

        with step(
            "LlamaIndex - Retrieve Refund Policy",
            type="retriever",
            query=query,
            framework="llamaindex",
            index_type="Document collection",
        ) as s:
            chunks, policy_context, avg_tokens, latency = retrieve_policy(query, top_k=6)
            s.step.metrics.latency = latency
            s.step.metadata["chunk_count"] = len(chunks)
            s.step.metadata["avg_tokens_per_chunk"] = avg_tokens
            s.step.metadata["retrieved_doc_ids"] = [chunk["doc_id"] for chunk in chunks]

        with step(
            "LlamaIndex - Lookup Order",
            type="tool_call",
            tool_name="lookup_order",
            tool_args={"order_id": order_id},
            framework="llamaindex",
        ) as s:
            order, latency = lookup_order_tool(order_id)
            s.step.metrics.latency = latency
            s.step.metadata["tool_result"] = order

        with step(
            "LlamaIndex - Refund Eligibility Check",
            type="llm_call",
            provider="openai",
            model="gpt-4o-mini",
            prompt=policy_context,
            framework="llamaindex",
        ) as s:
            start = time.time()
            response = check_refund_eligibility(ticket, order, policy_context, framework)
            s.record(response)
            s.step.metrics.latency = time.time() - start
            decision = response.choices[0].message.content
            s.step.metadata["intent"] = intent

        with step(
            "LlamaIndex - Generate Customer Reply",
            type="final_response",
            provider="openai",
            model="gpt-4o-mini",
            prompt=policy_context,
            framework="llamaindex",
        ) as s:
            start = time.time()
            response = generate_customer_reply(ticket, order, policy_context, decision, framework)
            s.record(response)
            s.step.metrics.latency = time.time() - start

    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
