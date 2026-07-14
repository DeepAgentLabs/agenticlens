import time

from agenticlens import profile, step

from benchmarks.shared.support_tasks import (
    check_refund_eligibility,
    classify_ticket,
    generate_customer_reply,
    lookup_order_tool,
    retrieve_policy,
    rewrite_query,
)


def main() -> None:
    framework = "Semantic Kernel"

    try:
        import semantic_kernel as sk
    except ImportError as exc:
        raise RuntimeError("Semantic Kernel is not installed. Run: pip install semantic-kernel") from exc

    ticket = (
        "My order A123 was delivered 12 days ago. "
        "I opened the package but did not use the item. "
        "Can I get a refund, and how long will it take?"
    )
    order_id = "A123"

    # Framework-specific kernel object.
    # This confirms the implementation is using the Semantic Kernel runtime surface.
    kernel = sk.Kernel()

    with profile("Benchmark - Semantic Kernel - Support Refund"):

        with step(
            "Semantic Kernel - Classify Ticket Intent",
            type="planner",
            provider="openai",
            model="gpt-4o-mini",
            prompt=ticket,
            framework="semantic_kernel",
            kernel_type=type(kernel).__name__,
        ) as s:
            start = time.time()
            response = classify_ticket(ticket, framework)
            s.record(response)
            s.step.metrics.latency = time.time() - start
            intent = response.choices[0].message.content

        with step(
            "Semantic Kernel - Rewrite Query For Retrieval",
            type="llm_call",
            provider="openai",
            model="gpt-4o-mini",
            prompt=ticket,
            framework="semantic_kernel",
        ) as s:
            start = time.time()
            response = rewrite_query(ticket, framework)
            s.record(response)
            s.step.metrics.latency = time.time() - start
            query = response.choices[0].message.content

        with step(
            "Semantic Kernel - Retrieve Refund Policy",
            type="retriever",
            query=query,
            framework="semantic_kernel",
        ) as s:
            chunks, policy_context, avg_tokens, latency = retrieve_policy(query, top_k=6)
            s.step.metrics.latency = latency
            s.step.metadata["chunk_count"] = len(chunks)
            s.step.metadata["avg_tokens_per_chunk"] = avg_tokens
            s.step.metadata["retrieved_doc_ids"] = [chunk["doc_id"] for chunk in chunks]

        with step(
            "Semantic Kernel - Lookup Order",
            type="tool_call",
            tool_name="lookup_order",
            tool_args={"order_id": order_id},
            framework="semantic_kernel",
        ) as s:
            order, latency = lookup_order_tool(order_id)
            s.step.metrics.latency = latency
            s.step.metadata["tool_result"] = order

        with step(
            "Semantic Kernel - Refund Eligibility Check",
            type="llm_call",
            provider="openai",
            model="gpt-4o-mini",
            prompt=policy_context,
            framework="semantic_kernel",
        ) as s:
            start = time.time()
            response = check_refund_eligibility(ticket, order, policy_context, framework)
            s.record(response)
            s.step.metrics.latency = time.time() - start
            decision = response.choices[0].message.content
            s.step.metadata["intent"] = intent

        with step(
            "Semantic Kernel - Generate Customer Reply",
            type="final_response",
            provider="openai",
            model="gpt-4o-mini",
            prompt=policy_context,
            framework="semantic_kernel",
        ) as s:
            start = time.time()
            response = generate_customer_reply(ticket, order, policy_context, decision, framework)
            s.record(response)
            s.step.metrics.latency = time.time() - start

    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()