import time
from typing import Any

from benchmarks.shared.support_data import (
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


def classify_ticket(ticket: str, framework: str) -> FakeResponse:
    return FakeResponse(
        content=f"framework={framework}; intent=refund_request; priority=normal",
        prompt_tokens=180,
        completion_tokens=25,
    )


def rewrite_query(ticket: str, framework: str) -> FakeResponse:
    return FakeResponse(
        content="refund eligibility delivered order opened package unused item refund processing time",
        prompt_tokens=220,
        completion_tokens=35,
    )


def retrieve_policy(query: str, top_k: int = 6) -> tuple[list[dict[str, Any]], str, int, float]:
    start = time.time()
    chunks = simple_retrieve(query, top_k=top_k)
    latency = time.time() - start
    policy_context = build_policy_context(chunks)
    avg_tokens = estimate_avg_tokens_per_chunk(chunks)
    return chunks, policy_context, avg_tokens, latency


def lookup_order_tool(order_id: str) -> tuple[dict[str, Any], float]:
    start = time.time()
    order = lookup_order(order_id)
    latency = time.time() - start
    return order, latency


def check_refund_eligibility(
    ticket: str,
    order: dict[str, Any],
    policy_context: str,
    framework: str,
) -> FakeResponse:
    return FakeResponse(
        content=(
            f"{framework}: The order is within the 30-day refund window. "
            "The item was not used, but the package was opened, so manual review may be required."
        ),
        prompt_tokens=720,
        completion_tokens=95,
    )


def generate_customer_reply(
    ticket: str,
    order: dict[str, Any],
    policy_context: str,
    decision: str,
    framework: str,
) -> FakeResponse:
    return FakeResponse(
        content=(
            f"[{framework}] Your order is within the 30-day refund window. "
            "Since the package was opened, the refund may need manual review. "
            "Because the item was not used, you may still be eligible. "
            "If approved, the refund will return to your original payment method and may take 5 to 10 business days."
        ),
        prompt_tokens=850,
        completion_tokens=130,
    )