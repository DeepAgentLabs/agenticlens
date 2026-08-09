"""Example: step-level token optimization in a multi-agent workflow.

Run with:

    uv run agenticlens profile examples/multiagent_token_optimization_demo.py --save multiagent.json
    uv run agenticlens analyze multiagent.json
"""

from agenticlens import profile, step


class FakeUsage:
    def __init__(self, prompt_tokens: int, completion_tokens: int) -> None:
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens


class FakeResponse:
    def __init__(self, prompt_tokens: int, completion_tokens: int) -> None:
        self.usage = FakeUsage(prompt_tokens, completion_tokens)


def main() -> None:
    shared_system_prompt = "You are an enterprise support workflow agent. " * 80

    with profile("Multi-Agent Token Optimization Demo"):
        with step(
            "Plan support workflow",
            type="planner",
            agent_name="planner_agent",
            agent_role="planner",
            provider="openai",
            model="gpt-4o-mini",
            prompt=shared_system_prompt + "Plan the customer support workflow.",
        ) as s:
            s.record(FakeResponse(prompt_tokens=950, completion_tokens=220))

        with step(
            "Retrieve policy context",
            type="retriever",
            agent_name="research_agent",
            agent_role="researcher",
            chunk_count=10,
            avg_tokens_per_chunk=120,
            retrieved_chunks=[
                {"text": "Refunds are processed to the original payment method.", "cited": True},
                {"text": "Refunds may take 5 to 10 business days.", "cited": True},
                {"text": "Items must be unused and in original packaging.", "cited": True},
                {"text": "Warehouse robot maintenance schedule.", "cited": False},
                {"text": "Office parking is available on level B2.", "cited": False},
                {"text": "Cafeteria menu for summer.", "cited": False},
                {"text": "Internal room booking instructions.", "cited": False},
                {"text": "Company holiday calendar.", "cited": False},
                {"text": "Laptop replacement policy.", "cited": False},
                {"text": "Badge access troubleshooting guide.", "cited": False},
            ],
        ):
            pass

        with step(
            "Research answer",
            type="llm_call",
            agent_name="research_agent",
            agent_role="researcher",
            handoff_from="planner_agent",
            handoff_to="answer_agent",
            handoff_tokens=5200,
            provider="openai",
            model="gpt-4o-mini",
            prompt=shared_system_prompt + "Use the retrieved policy context.",
        ) as s:
            s.record(FakeResponse(prompt_tokens=6200, completion_tokens=700))

        with step(
            "Customer lookup",
            type="tool_call",
            agent_name="tool_agent",
            agent_role="executor",
            tool_name="lookup_customer",
            tool_args={"customer_id": "C123"},
        ) as s:
            s.record(FakeResponse(prompt_tokens=180, completion_tokens=40))

        with step(
            "Customer lookup retry",
            type="tool_call",
            agent_name="tool_agent",
            agent_role="executor",
            tool_name="lookup_customer",
            tool_args={"customer_id": "C123"},
        ) as s:
            s.record(FakeResponse(prompt_tokens=180, completion_tokens=40))

        with step(
            "Final answer",
            type="final_response",
            agent_name="answer_agent",
            agent_role="responder",
            provider="openai",
            model="gpt-4o-mini",
            final_answer=(
                "Refunds are processed to the original payment method and may take "
                "5 to 10 business days."
            ),
        ) as s:
            s.record(FakeResponse(prompt_tokens=1300, completion_tokens=180))


if __name__ == "__main__":
    main()
