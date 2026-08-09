import os
import time

from openai import OpenAI

from agenticlens import profile, step

client = OpenAI()

DOCS = [
    "Refund policy: Customers can request a refund within 30 days of delivery.",
    "Refund policy: Items must be unused and in original packaging.",
    "Shipping policy: Standard shipping takes 5 to 7 business days.",
    "Order tracking: Customers can track orders using their order ID.",
    "Order tracking: If tracking is not updated for 48 hours, contact support.",
    "Payment policy: Refunds are processed to the original payment method.",
    "Payment policy: Refunds may take 5 to 10 business days.",
]

SYSTEM_PROMPT = "You are a helpful customer support assistant. Use only the provided context."


def retrieve_context(query: str, top_k: int = 6):
    query_words = set(query.lower().split())
    scored_docs = []

    for doc in DOCS:
        doc_words = set(doc.lower().split())
        score = len(query_words.intersection(doc_words))
        scored_docs.append((score, doc))

    scored_docs.sort(reverse=True, key=lambda x: x[0])
    return [doc for score, doc in scored_docs[:top_k] if score > 0]


def lookup_order(order_id: str):
    time.sleep(0.2)
    return {
        "order_id": order_id,
        "status": "Delivered",
        "delivered_days_ago": 12,
        "eligible_for_refund": True,
    }


def call_llm(agent_name: str, prompt: str):
    messages = [
        {
            "role": "system",
            "content": f"You are the {agent_name} in a multi-agent customer support workflow.",
        },
        {"role": "user", "content": prompt},
    ]

    return client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0,
    )


def main():
    user_question = "My order A123 was delivered. Can I get a refund and how long will it take?"

    with profile("Multi-Agent Customer Support Workflow") as workflow:
        with step(
            "Planner Agent",
            type="planner",
            provider="openai",
            model="gpt-4o-mini",
            prompt=user_question,
        ) as s:
            start = time.time()
            response = call_llm(
                "Planner Agent",
                f"""
User question:
{user_question}

Decide which agents should be used:
- Retriever Agent
- Tool Agent
- Writer Agent
- Reviewer Agent
""",
            )
            s.record(response)
            s.step.metrics.latency = time.time() - start
            plan = response.choices[0].message.content

        with step(
            "Retriever Agent",
            type="retriever",
            chunk_count=6,
            avg_tokens_per_chunk=35,
        ) as s:
            start = time.time()
            chunks = retrieve_context(user_question, top_k=6)
            s.step.metrics.latency = time.time() - start
            s.step.metadata["retrieved_chunks"] = chunks
            s.step.metadata["chunk_count"] = len(chunks)

        with step(
            "Tool Agent - Lookup Order",
            type="tool_call",
            provider="openai",
            model="gpt-4o-mini",
            tool_name="lookup_order",
            tool_args={"order_id": "A123"},
        ) as s:
            start = time.time()
            order_info = lookup_order("A123")
            s.step.metrics.latency = time.time() - start
            s.step.metadata["tool_result"] = order_info

        with step(
            "Writer Agent",
            type="llm_call",
            provider="openai",
            model="gpt-4o-mini",
            prompt=SYSTEM_PROMPT,
        ) as s:
            start = time.time()
            response = call_llm(
                "Writer Agent",
                f"""
User question:
{user_question}

Planner output:
{plan}

Retrieved policy context:
{chunks}

Order lookup result:
{order_info}

Write a helpful answer.
""",
            )
            s.record(response)
            s.step.metrics.latency = time.time() - start
            draft_answer = response.choices[0].message.content

        with step(
            "Reviewer Agent",
            type="llm_call",
            provider="openai",
            model="gpt-4o-mini",
            prompt=SYSTEM_PROMPT,
        ) as s:
            start = time.time()
            response = call_llm(
                "Reviewer Agent",
                f"""
Review this answer for accuracy.

User question:
{user_question}

Policy context:
{chunks}

Order info:
{order_info}

Draft answer:
{draft_answer}

Say whether the answer is correct. If needed, suggest improvements.
""",
            )
            s.record(response)
            s.step.metrics.latency = time.time() - start
            review = response.choices[0].message.content

        with step(
            "Final Response Agent",
            type="final_response",
            provider="openai",
            model="gpt-4o-mini",
            prompt=SYSTEM_PROMPT,
        ) as s:
            start = time.time()
            response = call_llm(
                "Final Response Agent",
                f"""
User question:
{user_question}

Draft answer:
{draft_answer}

Reviewer feedback:
{review}

Give the final customer-facing answer.
""",
            )
            s.record(response)
            s.step.metrics.latency = time.time() - start
            final_answer = response.choices[0].message.content

    print("\nFinal Answer:")
    print(final_answer)

    print("\nWorkflow Summary:")
    print("Total tokens:", workflow.total_tokens)
    print("Total cost:", workflow.total_cost)

    print("\nStep Breakdown:")
    for st in workflow.steps:
        print(
            f"- {st.name}: {st.metrics.total_tokens} tokens, "
            f"${st.metrics.cost or 0:.6f}, {st.metrics.latency:.2f}s"
        )


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Please set OPENAI_API_KEY before running this demo.")
    main()
