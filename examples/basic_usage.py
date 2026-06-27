"""Minimal example of instrumenting a workflow with AgenticLens."""

from agenticlens import profile, step


class FakeUsage:
    def __init__(self, prompt_tokens: int, completion_tokens: int) -> None:
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens


class FakeResponse:
    def __init__(self, prompt_tokens: int, completion_tokens: int) -> None:
        self.usage = FakeUsage(prompt_tokens, completion_tokens)


def planner_llm_invoke(prompt: str) -> FakeResponse:
    return FakeResponse(prompt_tokens=120, completion_tokens=40)


def main() -> None:
    with (
        profile("Customer Support") as workflow,
        step("Planner", type="planner", provider="openai", model="gpt-4o-mini") as s,
    ):
        response = planner_llm_invoke("How do I reset my password?")
        s.record(response)

    for s in workflow.steps:
        print(f"{s.name}: {s.metrics.total_tokens} tokens, {s.metrics.latency:.4f}s")


if __name__ == "__main__":
    main()
