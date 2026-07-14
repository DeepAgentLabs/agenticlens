

from agenticlens import profile, step


SYSTEM_PROMPT = (
    "You are a careful travel support assistant. "
    "Use only verified policy, booking, and refund information. "
    "Avoid guessing. Explain next steps clearly. "
) * 20


class FakeUsage:
    def __init__(self, prompt_tokens: int, completion_tokens: int) -> None:
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens


class FakeResponse:
    def __init__(self, prompt_tokens: int, completion_tokens: int) -> None:
        self.usage = FakeUsage(prompt_tokens, completion_tokens)


def main() -> None:
    user_question = (
        "My flight was cancelled. I booked a hotel and airport taxi. "
        "Can I get a refund and what should I do next?"
    )

    with profile("Multi-Agent Travel Refund Edge Case Workflow"):

        # Edge case 1: large repeated system prompt
        with step(
            "Planner Agent",
            type="planner",
            provider="openai",
            model="gpt-4o-mini",
            prompt=SYSTEM_PROMPT + user_question,
        ) as s:
            s.record(FakeResponse(prompt_tokens=1200, completion_tokens=180))

        # Edge case 2: excessive retrieved chunks
        # Default recommender limit is usually 8. This sends 14 chunks.
        with step(
            "Policy Retriever Agent",
            type="retriever",
            chunk_count=14,
            avg_tokens_per_chunk=90,
        ):
            pass

        # Edge case 3: long memory history
        with step(
            "Memory Agent",
            type="memory",
            provider="openai",
            model="gpt-4o-mini",
            history_tokens=7200,
        ) as s:
            s.record(FakeResponse(prompt_tokens=7400, completion_tokens=0))

        # Edge case 4: normal tool call
        with step(
            "Tool Agent - Lookup Booking",
            type="tool_call",
            provider="openai",
            model="gpt-4o-mini",
            tool_name="lookup_booking",
            tool_args={"booking_id": "TRV-8842"},
        ) as s:
            s.record(FakeResponse(prompt_tokens=220, completion_tokens=60))

        # Edge case 5: duplicate tool call with same args
        with step(
            "Tool Agent - Lookup Booking Retry",
            type="tool_call",
            provider="openai",
            model="gpt-4o-mini",
            tool_name="lookup_booking",
            tool_args={"booking_id": "TRV-8842"},
        ) as s:
            s.record(FakeResponse(prompt_tokens=220, completion_tokens=60))

        # Another tool call, not duplicate because tool and args are different
        with step(
            "Tool Agent - Check Refund Eligibility",
            type="tool_call",
            provider="openai",
            model="gpt-4o-mini",
            tool_name="check_refund_eligibility",
            tool_args={
                "booking_id": "TRV-8842",
                "reason": "flight_cancelled",
                "hotel_used": False,
                "taxi_used": False,
            },
        ) as s:
            s.record(FakeResponse(prompt_tokens=300, completion_tokens=80))

        # Writer agent adds useful value, but also adds token cost
        with step(
            "Writer Agent",
            type="llm_call",
            provider="openai",
            model="gpt-4o-mini",
            prompt="Write a customer-friendly refund explanation.",
        ) as s:
            s.record(FakeResponse(prompt_tokens=950, completion_tokens=260))

        # Reviewer agent adds quality control cost
        with step(
            "Reviewer Agent",
            type="llm_call",
            provider="openai",
            model="gpt-4o-mini",
            prompt="Review the answer for policy accuracy and missing next steps.",
        ) as s:
            s.record(FakeResponse(prompt_tokens=780, completion_tokens=160))

        # Edge case 6: repeated system prompt again
        with step(
            "Final Response Agent",
            type="final_response",
            provider="anthropic",
            model="claude-3-5-sonnet",
            prompt=SYSTEM_PROMPT + "Give the final customer-facing answer.",
        ) as s:
            s.record(FakeResponse(prompt_tokens=1100, completion_tokens=240))


if __name__ == "__main__":
    main()