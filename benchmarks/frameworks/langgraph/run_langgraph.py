import time
from typing import Any, TypedDict

from agenticlens import profile, step
from benchmarks.shared.support_data import (
    build_policy_context,
    estimate_avg_tokens_per_chunk,
    lookup_order,
    simple_retrieve,
)


class SupportState(TypedDict, total=False):
    ticket: str
    order_id: str
    intent: str
    query: str
    chunks: list[dict[str, Any]]
    policy_context: str
    order: dict[str, Any]
    decision: str
    final_answer: str


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


def classify_ticket_llm(ticket: str) -> FakeResponse:
    return FakeResponse(
        content="intent=refund_request; priority=normal",
        prompt_tokens=190,
        completion_tokens=30,
    )


def rewrite_query_llm(ticket: str) -> FakeResponse:
    return FakeResponse(
        content=(
            "refund eligibility delivered order opened package unused item refund processing time"
        ),
        prompt_tokens=240,
        completion_tokens=40,
    )


def refund_decision_llm(ticket: str, order: dict, policy_context: str) -> FakeResponse:
    return FakeResponse(
        content=(
            "The order is within the 30-day refund window. "
            "The item was not used, but the package was opened, so manual review may be required."
        ),
        prompt_tokens=780,
        completion_tokens=110,
    )


def final_response_llm(
    ticket: str, order: dict, policy_context: str, decision: str
) -> FakeResponse:
    return FakeResponse(
        content=(
            "Your order is within the 30-day refund window. Since the package was opened, "
            "the refund may need manual review. Because the item was not used, you may "
            "still be eligible. If approved, the refund will return to your original "
            "payment method and may take 5 to 10 business days."
        ),
        prompt_tokens=920,
        completion_tokens=150,
    )


def classify_ticket_node(state: SupportState) -> SupportState:
    with step(
        "LangGraph - Classify Ticket Intent",
        type="planner",
        provider="openai",
        model="gpt-4o-mini",
        prompt=state["ticket"],
    ) as s:
        start = time.time()
        response = classify_ticket_llm(state["ticket"])
        s.record(response)
        s.step.metrics.latency = time.time() - start

    state["intent"] = response.choices[0].message.content
    return state


def rewrite_query_node(state: SupportState) -> SupportState:
    with step(
        "LangGraph - Rewrite Query For Retrieval",
        type="llm_call",
        provider="openai",
        model="gpt-4o-mini",
        prompt=state["ticket"],
    ) as s:
        start = time.time()
        response = rewrite_query_llm(state["ticket"])
        s.record(response)
        s.step.metrics.latency = time.time() - start

    state["query"] = response.choices[0].message.content
    return state


def retrieve_policy_node(state: SupportState) -> SupportState:
    with step(
        "LangGraph - Retrieve Refund Policy",
        type="retriever",
        query=state["query"],
    ) as s:
        start = time.time()
        chunks = simple_retrieve(state["query"], top_k=6)
        s.step.metrics.latency = time.time() - start
        s.step.metadata["chunk_count"] = len(chunks)
        s.step.metadata["avg_tokens_per_chunk"] = estimate_avg_tokens_per_chunk(chunks)
        s.step.metadata["retrieved_doc_ids"] = [chunk["doc_id"] for chunk in chunks]

    state["chunks"] = chunks
    state["policy_context"] = build_policy_context(chunks)
    return state


def lookup_order_node(state: SupportState) -> SupportState:
    with step(
        "LangGraph - Lookup Order",
        type="tool_call",
        tool_name="lookup_order",
        tool_args={"order_id": state["order_id"]},
    ) as s:
        start = time.time()
        order = lookup_order(state["order_id"])
        s.step.metrics.latency = time.time() - start
        s.step.metadata["tool_result"] = order

    state["order"] = order
    return state


def refund_decision_node(state: SupportState) -> SupportState:
    with step(
        "LangGraph - Refund Eligibility Check",
        type="llm_call",
        provider="openai",
        model="gpt-4o-mini",
        prompt=state["policy_context"],
    ) as s:
        start = time.time()
        response = refund_decision_llm(
            state["ticket"],
            state["order"],
            state["policy_context"],
        )
        s.record(response)
        s.step.metrics.latency = time.time() - start

    state["decision"] = response.choices[0].message.content
    return state


def final_response_node(state: SupportState) -> SupportState:
    with step(
        "LangGraph - Generate Customer Reply",
        type="final_response",
        provider="openai",
        model="gpt-4o-mini",
        prompt=state["policy_context"],
    ) as s:
        start = time.time()
        response = final_response_llm(
            state["ticket"],
            state["order"],
            state["policy_context"],
            state["decision"],
        )
        s.record(response)
        s.step.metrics.latency = time.time() - start

    state["final_answer"] = response.choices[0].message.content
    return state


def main() -> None:
    try:
        from langgraph.graph import END, StateGraph
    except ImportError as exc:
        raise RuntimeError("LangGraph is not installed. Run: pip install langgraph") from exc

    ticket = (
        "My order A123 was delivered 12 days ago. "
        "I opened the package but did not use the item. "
        "Can I get a refund, and how long will it take?"
    )

    initial_state: SupportState = {
        "ticket": ticket,
        "order_id": "A123",
    }

    graph = StateGraph(SupportState)

    graph.add_node("classify_ticket", classify_ticket_node)
    graph.add_node("rewrite_query", rewrite_query_node)
    graph.add_node("retrieve_policy", retrieve_policy_node)
    graph.add_node("lookup_order", lookup_order_node)
    graph.add_node("refund_decision", refund_decision_node)
    graph.add_node("final_response", final_response_node)

    graph.set_entry_point("classify_ticket")
    graph.add_edge("classify_ticket", "rewrite_query")
    graph.add_edge("rewrite_query", "retrieve_policy")
    graph.add_edge("retrieve_policy", "lookup_order")
    graph.add_edge("lookup_order", "refund_decision")
    graph.add_edge("refund_decision", "final_response")
    graph.add_edge("final_response", END)

    app = graph.compile()

    with profile("Benchmark - LangGraph - Support Refund"):
        final_state = app.invoke(initial_state)

    print(final_state["final_answer"])


if __name__ == "__main__":
    main()
