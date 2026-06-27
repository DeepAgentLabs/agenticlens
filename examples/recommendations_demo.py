"""Workflow that deliberately triggers all 4 MVP recommendation rules.

Run with: `agenticlens analyze` against a saved report, e.g.:

    agenticlens profile examples/recommendations_demo.py --save /tmp/wf.json
    agenticlens analyze /tmp/wf.json
"""

from agenticlens import profile, step

SYSTEM_PROMPT = "You are a helpful customer support assistant. " * 20


class FakeUsage:
    def __init__(self, prompt_tokens: int, completion_tokens: int) -> None:
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens


class FakeResponse:
    def __init__(self, prompt_tokens: int, completion_tokens: int) -> None:
        self.usage = FakeUsage(prompt_tokens, completion_tokens)


def main() -> None:
    with profile("Support Agent (worst case)"):
        # Triggers: repeated system prompt (same prefix as the Final Response step).
        with step(
            "Planner",
            type="planner",
            provider="openai",
            model="gpt-4o-mini",
            prompt=SYSTEM_PROMPT + "What's the user's issue?",
        ) as s:
            s.record(FakeResponse(prompt_tokens=900, completion_tokens=100))

        # Triggers: excessive retrieved chunks (12 > default max_chunks of 8).
        with step(
            "Retriever",
            type="retriever",
            chunk_count=12,
            avg_tokens_per_chunk=80,
        ):
            pass

        # Triggers: long conversation history (6000 > default history_token_limit of 4000).
        with step(
            "Memory",
            type="memory",
            provider="openai",
            model="gpt-4o-mini",
            history_tokens=6000,
        ) as s:
            s.record(FakeResponse(prompt_tokens=6200, completion_tokens=0))

        # Triggers: duplicate tool call (same tool + args as below).
        with step(
            "Tool Call - Lookup Order",
            type="tool_call",
            provider="openai",
            model="gpt-4o-mini",
            tool_name="lookup_order",
            tool_args={"order_id": "A123"},
        ) as s:
            s.record(FakeResponse(prompt_tokens=150, completion_tokens=30))

        with step(
            "Tool Call - Lookup Order (retry)",
            type="tool_call",
            provider="openai",
            model="gpt-4o-mini",
            tool_name="lookup_order",
            tool_args={"order_id": "A123"},
        ) as s:
            s.record(FakeResponse(prompt_tokens=150, completion_tokens=30))

        # Triggers: repeated system prompt prefix.
        with step(
            "Final Response",
            type="final_response",
            provider="anthropic",
            model="claude-3-5-sonnet",
            prompt=SYSTEM_PROMPT + "Here is the answer.",
        ) as s:
            s.record(FakeResponse(prompt_tokens=850, completion_tokens=200))


if __name__ == "__main__":
    main()
