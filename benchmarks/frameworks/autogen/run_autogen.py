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
    framework = "AutoGen"

    try:
        from autogen_agentchat.agents import AssistantAgent
    except ImportError as exc:
        raise RuntimeError(
            "AutoGen AgentChat is not installed. Run: pip install autogen-agentchat autogen-core"
        ) from exc

    ticket = (
        "My order A123 was delivered 12 days ago. "
        "I opened the package but did not use the item. "
        "Can I get a refund, and how long will it take?"
    )
    order_id = "A123"

    # Framework-specific agents.
    # We instantiate agents for benchmark identity, but do not call a live model client here.
    classifier_agent = AssistantAgent(
        name="support_intent_classifier",
        model_client=None,
    )
    refund_agent = AssistantAgent(
        name="refund_decision_agent",
        model_client=None,
    )
    response_agent = AssistantAgent(
        name="customer_response_agent",
        model_client=None,
    )

    with profile("Benchmark - AutoGen - Support Refund"):

        with step(
            "AutoGen - Classify Ticket Intent",
            type="planner",
            provider="openai",
            model="gpt-4o-mini",
            prompt=ticket,
            framework="autogen",
            agent_name=classifier_agent.name,
        ) as s:
            start = time.time()
            response = classify_ticket(ticket, framework)
            s.record(response)
            s.step.metrics.latency = time.time() - start
            intent = response.choices[0].message.content

        with step(
            "AutoGen - Rewrite Query For Retrieval",
            type="llm_call",
            provider="openai",
            model="gpt-4o-mini",
            prompt=ticket,
            framework="autogen",
        ) as s:
            start = time.time()
            response = rewrite_query(ticket, framework)
            s.record(response)
            s.step.metrics.latency = time.time() - start
            query = response.choices[0].message.content

        with step(
            "AutoGen - Retrieve Refund Policy",
            type="retriever",
            query=query,
            framework="autogen",
        ) as s:
            chunks, policy_context, avg_tokens, latency = retrieve_policy(query, top_k=6)
            s.step.metrics.latency = latency
            s.step.metadata["chunk_count"] = len(chunks)
            s.step.metadata["avg_tokens_per_chunk"] = avg_tokens
            s.step.metadata["retrieved_doc_ids"] = [chunk["doc_id"] for chunk in chunks]

        with step(
            "AutoGen - Lookup Order",
            type="tool_call",
            tool_name="lookup_order",
            tool_args={"order_id": order_id},
            framework="autogen",
        ) as s:
            order, latency = lookup_order_tool(order_id)
            s.step.metrics.latency = latency
            s.step.metadata["tool_result"] = order

        with step(
            "AutoGen - Refund Eligibility Check",
            type="llm_call",
            provider="openai",
            model="gpt-4o-mini",
            prompt=policy_context,
            framework="autogen",
            agent_name=refund_agent.name,
        ) as s:
            start = time.time()
            response = check_refund_eligibility(ticket, order, policy_context, framework)
            s.record(response)
            s.step.metrics.latency = time.time() - start
            decision = response.choices[0].message.content
            s.step.metadata["intent"] = intent

        with step(
            "AutoGen - Generate Customer Reply",
            type="final_response",
            provider="openai",
            model="gpt-4o-mini",
            prompt=policy_context,
            framework="autogen",
            agent_name=response_agent.name,
        ) as s:
            start = time.time()
            response = generate_customer_reply(ticket, order, policy_context, decision, framework)
            s.record(response)
            s.step.metrics.latency = time.time() - start

    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()