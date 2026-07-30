"""Offline LangGraph supervisor workflow instrumented with AgenticLens.

Based on the supervisor and state-graph patterns published by LangChain.
This example is deterministic and does not require an API key.

Run:
    uv sync --extra langgraph
    uv run python examples/reference_workflows/langgraph_supervisor.py
    uv run agenticlens inspect examples/reference_workflows/artifacts/langgraph-supervisor.json
"""

from pathlib import Path
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from agenticlens import SpanType, trace


class WorkflowState(TypedDict):
    question: str
    research: str
    calculation: int
    answer: str
    next_agent: Literal["research_agent", "math_agent", "reviewer_agent", "done"]


def supervisor(state: WorkflowState) -> dict[str, str]:
    if not state.get("research"):
        return {"next_agent": "research_agent"}
    if not state.get("calculation"):
        return {"next_agent": "math_agent"}
    if not state.get("answer"):
        return {"next_agent": "reviewer_agent"}
    return {"next_agent": "done"}


def research_agent(state: WorkflowState) -> dict[str, str]:
    return {
        "research": ("Reference data: North region resolved 18 cases and South region resolved 24.")
    }


def math_agent(state: WorkflowState) -> dict[str, int]:
    return {"calculation": 18 + 24}


def reviewer_agent(state: WorkflowState) -> dict[str, str]:
    return {
        "answer": (
            f"{state['research']} The combined number of resolved cases is {state['calculation']}."
        )
    }


def route(state: WorkflowState) -> str:
    return state["next_agent"]


def build_graph(recording):
    def traced_supervisor(state: WorkflowState) -> dict[str, str]:
        destination = supervisor(state)
        with recording.span(
            f"supervisor-to-{destination['next_agent']}",
            SpanType.DELEGATION,
            agent_name="supervisor",
            handoff_to=destination["next_agent"],
        ):
            return destination

    def traced_research(state: WorkflowState) -> dict[str, str]:
        with recording.span(
            "research-agent",
            SpanType.RETRIEVAL,
            agent_name="research_agent",
        ) as span:
            result = research_agent(state)
            span.record_tokens(input_tokens=12, output_tokens=16)
            return result

    def traced_math(state: WorkflowState) -> dict[str, int]:
        with recording.span(
            "math-agent",
            SpanType.TOOL_CALL,
            agent_name="math_agent",
            tool_name="add",
        ):
            return math_agent(state)

    def traced_reviewer(state: WorkflowState) -> dict[str, str]:
        with recording.span(
            "reviewer-agent",
            SpanType.FINAL_RESPONSE,
            agent_name="reviewer_agent",
        ) as span:
            result = reviewer_agent(state)
            span.record_tokens(input_tokens=28, output_tokens=30)
            return result

    builder = StateGraph(WorkflowState)
    builder.add_node("supervisor", traced_supervisor)
    builder.add_node("research_agent", traced_research)
    builder.add_node("math_agent", traced_math)
    builder.add_node("reviewer_agent", traced_reviewer)
    builder.add_edge(START, "supervisor")
    builder.add_conditional_edges(
        "supervisor",
        route,
        {
            "research_agent": "research_agent",
            "math_agent": "math_agent",
            "reviewer_agent": "reviewer_agent",
            "done": END,
        },
    )
    for agent in ("research_agent", "math_agent", "reviewer_agent"):
        builder.add_edge(agent, "supervisor")
    return builder.compile()


def run_workflow():
    initial: WorkflowState = {
        "question": "How many support cases were resolved across both regions?",
        "research": "",
        "calculation": 0,
        "answer": "",
        "next_agent": "research_agent",
    }

    with trace(
        "langgraph-supervisor-reference",
        framework="langgraph",
        pattern="supervisor",
        source="official-langgraph-pattern",
    ) as recording:
        graph = build_graph(recording)
        state = graph.invoke(initial)
    return state, recording


def main() -> None:
    state, recording = run_workflow()
    output = Path("examples/reference_workflows/artifacts/langgraph-supervisor.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    recording.save(output)
    print(state["answer"])
    print(f"Trace saved to {output}")


if __name__ == "__main__":
    main()
