import os
import re
import sqlite3
import time
from pathlib import Path
from typing import Any

from agenticlens import profile, step

USE_REAL_OPENAI = bool(os.getenv("OPENAI_API_KEY"))

if USE_REAL_OPENAI:
    from openai import OpenAI
    client = OpenAI()


POLICY_DOCS = [
    {
        "id": "refund_001",
        "text": "Customers can request a refund within 30 days of delivery.",
    },
    {
        "id": "refund_002",
        "text": "Items must be unused and in original packaging to qualify for a standard refund.",
    },
    {
        "id": "refund_003",
        "text": "Opened items may require manual review unless the item is defective.",
    },
    {
        "id": "refund_004",
        "text": "Refunds are processed to the original payment method.",
    },
    {
        "id": "refund_005",
        "text": "Refunds may take 5 to 10 business days after approval.",
    },
    {
        "id": "shipping_001",
        "text": "Delivered orders are eligible for return review if the delivery date is within the return window.",
    },
]


SYSTEM_PROMPT = """
You are a customer support copilot.
Use only the provided policy and order information.
Do not invent refund rules.
If manual review is needed, clearly say so.
"""


class FakeUsage:
    def __init__(self, prompt_tokens: int, completion_tokens: int):
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens


class FakeMessage:
    def __init__(self, content: str):
        self.content = content


class FakeChoice:
    def __init__(self, content: str):
        self.message = FakeMessage(content)


class FakeResponse:
    def __init__(self, content: str, prompt_tokens: int, completion_tokens: int):
        self.usage = FakeUsage(prompt_tokens, completion_tokens)
        self.choices = [FakeChoice(content)]


def setup_order_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.execute(
        """
        CREATE TABLE orders (
            order_id TEXT PRIMARY KEY,
            status TEXT,
            delivered_days_ago INTEGER,
            package_opened INTEGER,
            item_used INTEGER,
            payment_method TEXT
        )
        """
    )
    conn.execute(
        """
        INSERT INTO orders VALUES
        ('A123', 'delivered', 12, 1, 0, 'Visa ending 4242')
        """
    )
    return conn


def extract_order_id(text: str) -> str | None:
    match = re.search(r"\b[A-Z]\d{3}\b", text)
    return match.group(0) if match else None


def retrieve_policy_chunks(query: str, top_k: int = 6) -> list[dict[str, str]]:
    query_words = set(query.lower().replace("?", "").replace(".", "").split())

    scored = []
    for doc in POLICY_DOCS:
        doc_words = set(doc["text"].lower().replace(".", "").split())
        score = len(query_words.intersection(doc_words))
        scored.append((score, doc))

    scored.sort(reverse=True, key=lambda x: x[0])
    return [doc for score, doc in scored[:top_k] if score > 0]


def lookup_order(conn: sqlite3.Connection, order_id: str) -> dict[str, Any]:
    row = conn.execute(
        """
        SELECT order_id, status, delivered_days_ago, package_opened, item_used, payment_method
        FROM orders
        WHERE order_id = ?
        """,
        (order_id,),
    ).fetchone()

    if not row:
        return {"found": False, "order_id": order_id}

    return {
        "found": True,
        "order_id": row[0],
        "status": row[1],
        "delivered_days_ago": row[2],
        "package_opened": bool(row[3]),
        "item_used": bool(row[4]),
        "payment_method": row[5],
    }


def fake_llm(task: str, prompt: str) -> FakeResponse:
    if task == "classify":
        return FakeResponse(
            content="intent: refund_request; urgency: normal",
            prompt_tokens=180,
            completion_tokens=20,
        )

    if task == "rewrite":
        return FakeResponse(
            content="refund eligibility delivered order opened package unused item processing time",
            prompt_tokens=220,
            completion_tokens=30,
        )

    if task == "decision":
        return FakeResponse(
            content=(
                "The order is within the 30-day window and the item is unused. "
                "However, because the package was opened, manual review may be required."
            ),
            prompt_tokens=520,
            completion_tokens=70,
        )

    return FakeResponse(
        content=(
            "Your order A123 was delivered 12 days ago, so it is within the 30-day refund window. "
            "Because the package was opened, the refund may need manual review, but since the item was not used, "
            "you may still be eligible. If approved, the refund will go back to your original payment method and "
            "may take 5 to 10 business days after approval."
        ),
        prompt_tokens=850,
        completion_tokens=120,
    )


def call_llm(task: str, prompt: str):
    if not USE_REAL_OPENAI:
        return fake_llm(task, prompt)

    return client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )


def main() -> None:
    conn = setup_order_db()

    ticket = {
        "ticket_id": "TCK-1001",
        "tenant_id": "retail-us",
        "customer_id": "CUST-789",
        "message": (
            "My order A123 was delivered 12 days ago. "
            "I opened the package but did not use the item. "
            "Can I get a refund, and how long will it take?"
        ),
    }

    with profile("Practical Support Copilot - Refund Ticket") as workflow:

        with step(
            "Classify Ticket Intent",
            type="planner",
            provider="openai",
            model="gpt-4o-mini",
            prompt=ticket["message"],
            ticket_id=ticket["ticket_id"],
            tenant_id=ticket["tenant_id"],
        ) as s:
            start = time.time()
            classify_response = call_llm(
                "classify",
                f"Classify this support ticket:\n{ticket['message']}",
            )
            s.record(classify_response)
            s.step.metrics.latency = time.time() - start
            intent = classify_response.choices[0].message.content

        with step(
            "Rewrite Query For Retrieval",
            type="llm_call",
            provider="openai",
            model="gpt-4o-mini",
            prompt=ticket["message"],
        ) as s:
            start = time.time()
            rewrite_response = call_llm(
                "rewrite",
                f"Rewrite this ticket as a search query for refund policy retrieval:\n{ticket['message']}",
            )
            s.record(rewrite_response)
            s.step.metrics.latency = time.time() - start
            search_query = rewrite_response.choices[0].message.content

        with step(
            "Retrieve Refund Policy",
            type="retriever",
            chunk_count=6,
            avg_tokens_per_chunk=35,
            query=search_query,
        ) as s:
            start = time.time()
            policy_chunks = retrieve_policy_chunks(search_query, top_k=6)
            s.step.metrics.latency = time.time() - start
            s.step.metadata["chunk_count"] = len(policy_chunks)
            s.step.metadata["retrieved_doc_ids"] = [doc["id"] for doc in policy_chunks]
            s.step.metadata["retrieved_chunks"] = [doc["text"] for doc in policy_chunks]

        order_id = extract_order_id(ticket["message"])

        with step(
            "Lookup Order System",
            type="tool_call",
            tool_name="lookup_order",
            tool_args={"order_id": order_id},
        ) as s:
            start = time.time()
            order = lookup_order(conn, order_id)
            s.step.metrics.latency = time.time() - start
            s.step.metadata["tool_result"] = order

        with step(
            "Refund Eligibility Decision",
            type="llm_call",
            provider="openai",
            model="gpt-4o-mini",
            prompt=SYSTEM_PROMPT,
        ) as s:
            start = time.time()
            decision_response = call_llm(
                "decision",
                f"""
Ticket:
{ticket["message"]}

Intent:
{intent}

Order:
{order}

Policy:
{[doc["text"] for doc in policy_chunks]}

Decide refund eligibility and whether human review is needed.
""",
            )
            s.record(decision_response)
            s.step.metrics.latency = time.time() - start
            decision = decision_response.choices[0].message.content

        with step(
            "Generate Customer Reply",
            type="final_response",
            provider="openai",
            model="gpt-4o-mini",
            prompt=SYSTEM_PROMPT,
        ) as s:
            start = time.time()
            final_response = call_llm(
                "final",
                f"""
Customer message:
{ticket["message"]}

Order:
{order}

Policy:
{[doc["text"] for doc in policy_chunks]}

Eligibility decision:
{decision}

Write the final customer-facing response.
""",
            )
            s.record(final_response)
            s.step.metrics.latency = time.time() - start
            answer = final_response.choices[0].message.content

    print("\nFinal customer reply:\n")
    print(answer)

    print("\nWorkflow summary:")
    print("Total tokens:", workflow.total_tokens)
    print("Total cost:", workflow.total_cost)

    print("\nStep summary:")
    for st in workflow.steps:
        print(
            f"- {st.name}: "
            f"{st.metrics.total_tokens or 0} tokens, "
            f"${st.metrics.cost or 0:.6f}, "
            f"{st.metrics.latency or 0:.3f}s"
        )


if __name__ == "__main__":
    main()