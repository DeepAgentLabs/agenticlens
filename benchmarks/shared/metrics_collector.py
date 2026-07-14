import json
from pathlib import Path
from typing import Any


def load_report(report_path: str | Path) -> dict[str, Any]:
    path = Path(report_path)
    return json.loads(path.read_text(encoding="utf-8"))


def summarize_agenticlens_report(framework: str, report_path: str | Path) -> dict[str, Any]:
    report = load_report(report_path)
    steps = report.get("steps", [])

    total_tokens = 0
    prompt_tokens = 0
    completion_tokens = 0
    total_cost = 0.0
    total_latency = 0.0
    tool_calls = 0
    retriever_steps = 0
    retrieved_chunks = 0
    memory_tokens = 0

    highest_token_step = None
    highest_step_tokens = -1

    highest_cost_step = None
    highest_step_cost = -1.0

    for step in steps:
        metrics = step.get("metrics") or {}
        metadata = step.get("metadata") or {}
        step_type = step.get("type")

        step_total_tokens = metrics.get("total_tokens") or 0
        step_prompt_tokens = metrics.get("prompt_tokens") or 0
        step_completion_tokens = metrics.get("completion_tokens") or 0
        step_cost = metrics.get("cost") or 0.0
        step_latency = metrics.get("latency") or 0.0

        total_tokens += step_total_tokens
        prompt_tokens += step_prompt_tokens
        completion_tokens += step_completion_tokens
        total_cost += step_cost
        total_latency += step_latency

        if step_type == "tool_call":
            tool_calls += 1

        if step_type == "retriever":
            retriever_steps += 1
            retrieved_chunks += metadata.get("chunk_count") or 0

        if step_type == "memory":
            memory_tokens += metadata.get("history_tokens") or step_prompt_tokens

        if step_total_tokens > highest_step_tokens:
            highest_step_tokens = step_total_tokens
            highest_token_step = step.get("name")

        if step_cost > highest_step_cost:
            highest_step_cost = step_cost
            highest_cost_step = step.get("name")

    return {
        "framework": framework,
        "workflow_name": report.get("name"),
        "step_count": len(steps),
        "total_tokens": total_tokens,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_cost": round(total_cost, 8),
        "total_latency": round(total_latency, 4),
        "tool_calls": tool_calls,
        "retriever_steps": retriever_steps,
        "retrieved_chunks": retrieved_chunks,
        "memory_tokens": memory_tokens,
        "highest_token_step": highest_token_step,
        "highest_cost_step": highest_cost_step,
        "report_path": str(report_path),
    }