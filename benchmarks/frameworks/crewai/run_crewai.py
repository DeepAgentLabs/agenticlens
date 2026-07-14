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
    framework = "CrewAI"

    try:
        from crewai import Agent, Crew, Process, Task
    except ImportError as exc:
        raise RuntimeError("CrewAI is not installed. Run: pip install crewai") from exc

    ticket = (
        "My order A123 was delivered 12 days ago. "
        "I opened the package but did not use the item. "
        "Can I get a refund, and how long will it take?"
    )
    order_id = "A123"

    # Framework-specific objects.
    # These make this a CrewAI benchmark adapter, while AgenticLens measures each business step.
    classifier_agent = Agent(
        role="Support Intent Classifier",
        goal="Classify customer support tickets",
        backstory="You classify customer tickets into support intents.",
        verbose=False,
        allow_delegation=False,
    )

    policy_agent = Agent(
        role="Policy Retrieval Agent",
        goal="Find relevant refund and tracking policies",
        backstory="You retrieve policy evidence for support decisions.",
        verbose=False,
        allow_delegation=False,
    )

    refund_agent = Agent(
        role="Refund Decision Agent",
        goal="Decide refund eligibility using order and policy facts",
        backstory="You apply company refund rules to customer orders.",
        verbose=False,
        allow_delegation=False,
    )

    response_agent = Agent(
        role="Customer Response Agent",
        goal="Write clear customer-facing replies",
        backstory="You write helpful support responses.",
        verbose=False,
        allow_delegation=False,
    )

    tasks = [
        Task(
            description="Classify the refund ticket intent.",
            expected_output="Ticket intent and priority.",
            agent=classifier_agent,
        ),
        Task(
            description="Retrieve relevant refund policy chunks.",
            expected_output="Relevant policy evidence.",
            agent=policy_agent,
        ),
        Task(
            description="Check refund eligibility.",
            expected_output="Eligibility decision.",
            agent=refund_agent,
        ),
        Task(
            description="Generate customer reply.",
            expected_output="Customer-facing answer.",
            agent=response_agent,
        ),
    ]

    # We create the CrewAI crew so the benchmark records that this implementation uses CrewAI.
    # We do not call crew.kickoff() in this deterministic benchmark because that would call a live LLM.
    crew = Crew(
        agents=[classifier_agent, policy_agent, refund_agent, response_agent],
        tasks=tasks,
        process=Process.sequential,
        verbose=False,
    )

    with profile("Benchmark - CrewAI - Support Refund"):

        with step(
            "CrewAI - Classify Ticket Intent",
            type="planner",
            provider="openai",
            model="gpt-4o-mini",
            prompt=ticket,
            framework="crewai",
            crew_agents=len(crew.agents),
        ) as s:
            start = time.time()
            response = classify_ticket(ticket, framework)
            s.record(response)
            s.step.metrics.latency = time.time() - start
            intent = response.choices[0].message.content

        with step(
            "CrewAI - Rewrite Query For Retrieval",
            type="llm_call",
            provider="openai",
            model="gpt-4o-mini",
            prompt=ticket,
            framework="crewai",
        ) as s:
            start = time.time()
            response = rewrite_query(ticket, framework)
            s.record(response)
            s.step.metrics.latency = time.time() - start
            query = response.choices[0].message.content

        with step(
            "CrewAI - Retrieve Refund Policy",
            type="retriever",
            query=query,
            framework="crewai",
        ) as s:
            chunks, policy_context, avg_tokens, latency = retrieve_policy(query, top_k=6)
            s.step.metrics.latency = latency
            s.step.metadata["chunk_count"] = len(chunks)
            s.step.metadata["avg_tokens_per_chunk"] = avg_tokens
            s.step.metadata["retrieved_doc_ids"] = [chunk["doc_id"] for chunk in chunks]

        with step(
            "CrewAI - Lookup Order",
            type="tool_call",
            tool_name="lookup_order",
            tool_args={"order_id": order_id},
            framework="crewai",
        ) as s:
            order, latency = lookup_order_tool(order_id)
            s.step.metrics.latency = latency
            s.step.metadata["tool_result"] = order

        with step(
            "CrewAI - Refund Eligibility Check",
            type="llm_call",
            provider="openai",
            model="gpt-4o-mini",
            prompt=policy_context,
            framework="crewai",
        ) as s:
            start = time.time()
            response = check_refund_eligibility(ticket, order, policy_context, framework)
            s.record(response)
            s.step.metrics.latency = time.time() - start
            decision = response.choices[0].message.content
            s.step.metadata["intent"] = intent

        with step(
            "CrewAI - Generate Customer Reply",
            type="final_response",
            provider="openai",
            model="gpt-4o-mini",
            prompt=policy_context,
            framework="crewai",
        ) as s:
            start = time.time()
            response = generate_customer_reply(ticket, order, policy_context, decision, framework)
            s.record(response)
            s.step.metrics.latency = time.time() - start

    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()