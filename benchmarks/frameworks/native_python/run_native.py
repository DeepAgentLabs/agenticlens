import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from agenticlens import profile, step  # noqa: E402
from benchmarks.shared.support_data import (  # noqa: E402
    build_policy_context,
    estimate_avg_tokens_per_chunk,
    lookup_order,
    simple_retrieve,
)


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


def classify_ticket(ticket: str) -> FakeResponse:
    return FakeResponse(
        content="intent=refund_request; priority=normal",
        prompt_tokens=180,
        completion_tokens=25,
    )


def rewrite_query(ticket: str) -> FakeResponse:
    return FakeResponse(
        content=(
            "refund eligibility delivered order opened package unused item refund processing time"
        ),
        prompt_tokens=220,
        completion_tokens=35,
    )


def check_refund_eligibility(ticket: str, order: dict, policy_context: str) -> FakeResponse:
    return FakeResponse(
        content=(
            "The order is within the 30-day refund window. "
            "The item was not used, but the package was opened, so manual review may be required."
        ),
        prompt_tokens=720,
        completion_tokens=95,
    )


def generate_customer_reply(
    ticket: str, order: dict, policy_context: str, decision: str
) -> FakeResponse:
    return FakeResponse(
        content=(
            "Your order is within the 30-day refund window. Since the package was opened, "
            "the refund may need manual review. Because the item was not used, you may "
            "still be eligible. If approved, the refund will return to your original "
            "payment method and may take 5 to 10 business days."
        ),
        prompt_tokens=850,
        completion_tokens=130,
    )


def main() -> None:
    ticket = (
        "My order A123 was delivered 12 days ago. "
        "I opened the package but did not use the item. "
        "Can I get a refund, and how long will it take?"
    )
    order_id = "A123"

    with profile("Benchmark - Native Python - Support Refund"):
        with step(
            "Classify Ticket Intent",
            type="planner",
            provider="openai",
            model="gpt-4o-mini",
            prompt=ticket,
        ) as s:
            start = time.time()
            response = classify_ticket(ticket)
            s.record(response)
            s.step.metrics.latency = time.time() - start
            intent = response.choices[0].message.content

        with step(
            "Rewrite Query For Retrieval",
            type="llm_call",
            provider="openai",
            model="gpt-4o-mini",
            prompt=ticket,
        ) as s:
            start = time.time()
            response = rewrite_query(ticket)
            s.record(response)
            s.step.metrics.latency = time.time() - start
            query = response.choices[0].message.content

        with step(
            "Retrieve Refund Policy",
            type="retriever",
            query=query,
        ) as s:
            start = time.time()
            chunks = simple_retrieve(query, top_k=6)
            s.step.metrics.latency = time.time() - start
            s.step.metadata["chunk_count"] = len(chunks)
            s.step.metadata["avg_tokens_per_chunk"] = estimate_avg_tokens_per_chunk(chunks)
            s.step.metadata["retrieved_doc_ids"] = [chunk["doc_id"] for chunk in chunks]
            policy_context = build_policy_context(chunks)

        with step(
            "Lookup Order",
            type="tool_call",
            tool_name="lookup_order",
            tool_args={"order_id": order_id},
        ) as s:
            start = time.time()
            order = lookup_order(order_id)
            s.step.metrics.latency = time.time() - start
            s.step.metadata["tool_result"] = order

        with step(
            "Refund Eligibility Check",
            type="llm_call",
            provider="openai",
            model="gpt-4o-mini",
            prompt=policy_context,
        ) as s:
            start = time.time()
            response = check_refund_eligibility(ticket, order, policy_context)
            s.record(response)
            s.step.metrics.latency = time.time() - start
            decision = response.choices[0].message.content
            s.step.metadata["intent"] = intent

        with step(
            "Generate Customer Reply",
            type="final_response",
            provider="openai",
            model="gpt-4o-mini",
            prompt=policy_context,
        ) as s:
            start = time.time()
            response = generate_customer_reply(ticket, order, policy_context, decision)
            s.record(response)
            s.step.metrics.latency = time.time() - start

    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
