import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

REPORTS = {
    "Native Python": "benchmarks/reports/native_python/support_refund_report.json",
    "LangGraph": "benchmarks/reports/langgraph/support_refund_report.json",
    "CrewAI": "benchmarks/reports/crewai/support_refund_report.json",
    "AutoGen": "benchmarks/reports/autogen/support_refund_report.json",
    "LlamaIndex": "benchmarks/reports/llamaindex/support_refund_report.json",
    "Semantic Kernel": "benchmarks/reports/semantic_kernel/support_refund_report.json",
}

RESULTS_DIR = Path("benchmarks/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def load_report(path: str | Path) -> dict:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Report not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def summarize_report(framework: str, report: dict) -> dict:
    steps = report.get("steps", [])

    total_tokens = 0
    prompt_tokens = 0
    completion_tokens = 0
    total_cost = 0.0
    total_latency = 0.0
    tool_calls = 0
    retrieved_chunks = 0

    highest_token_step = None
    highest_step_tokens = -1

    highest_cost_step = None
    highest_step_cost = -1.0

    for step in steps:
        metrics = step.get("metrics") or {}
        metadata = step.get("metadata") or {}

        step_tokens = metrics.get("total_tokens") or 0
        step_prompt_tokens = metrics.get("prompt_tokens") or 0
        step_completion_tokens = metrics.get("completion_tokens") or 0
        step_cost = metrics.get("cost") or 0.0
        step_latency = metrics.get("latency") or 0.0

        total_tokens += step_tokens
        prompt_tokens += step_prompt_tokens
        completion_tokens += step_completion_tokens
        total_cost += step_cost
        total_latency += step_latency

        if step.get("type") == "tool_call":
            tool_calls += 1

        if step.get("type") == "retriever":
            retrieved_chunks += metadata.get("chunk_count") or 0

        if step_tokens > highest_step_tokens:
            highest_step_tokens = step_tokens
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
        "total_cost_usd": round(total_cost, 8),
        "total_latency_sec": round(total_latency, 8),
        "tool_calls": tool_calls,
        "retrieved_chunks": retrieved_chunks,
        "highest_token_step": highest_token_step,
        "highest_step_tokens": highest_step_tokens,
        "highest_cost_step": highest_cost_step,
        "highest_step_cost_usd": round(highest_step_cost, 8),
    }


def extract_step_rows(framework: str, report: dict) -> list[dict]:
    rows = []

    for step in report.get("steps", []):
        metrics = step.get("metrics") or {}
        metadata = step.get("metadata") or {}

        rows.append(
            {
                "framework": framework,
                "workflow_name": report.get("name"),
                "step_name": step.get("name"),
                "step_type": step.get("type"),
                "provider": step.get("provider"),
                "model": step.get("model"),
                "prompt_tokens": metrics.get("prompt_tokens") or 0,
                "completion_tokens": metrics.get("completion_tokens") or 0,
                "total_tokens": metrics.get("total_tokens") or 0,
                "cost_usd": metrics.get("cost") or 0.0,
                "latency_sec": metrics.get("latency") or 0.0,
                "chunk_count": metadata.get("chunk_count"),
                "tool_name": metadata.get("tool_name"),
            }
        )

    return rows


def create_markdown_summary(summary_df: pd.DataFrame, output_path: Path) -> None:
    lines = [
        "# AgenticLens Framework Benchmark Comparison",
        "",
        "Use case: Practical customer support refund workflow.",
        "",
        "The workflow includes:",
        "",
        "- ticket intent classification",
        "- query rewriting",
        "- refund policy retrieval",
        "- order lookup",
        "- refund eligibility check",
        "- customer reply generation",
        "",
        "## Summary Results",
        "",
        "| Framework | Total Tokens | Prompt Tokens | Completion Tokens | Cost USD | "
        "Latency Sec | Steps | Tool Calls | Retrieved Chunks | Highest Token Step |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]

    for _, row in summary_df.iterrows():
        lines.append(
            f"| {row['framework']} | "
            f"{row['total_tokens']} | "
            f"{row['prompt_tokens']} | "
            f"{row['completion_tokens']} | "
            f"${row['total_cost_usd']:.8f} | "
            f"{row['total_latency_sec']:.8f} | "
            f"{row['step_count']} | "
            f"{row['tool_calls']} | "
            f"{row['retrieved_chunks']} | "
            f"{row['highest_token_step']} |"
        )

    lines.extend(
        [
            "",
            "## Key Finding",
            "",
            "The final customer reply step is the highest token-consuming step across "
            "the benchmark runs.",
            "",
            "## Important Note",
            "",
            "These results are workload-specific. They should not be treated as a "
            "universal ranking of frameworks.",
            "The purpose is to show how AgenticLens can normalize and compare token, "
            "cost, latency, retrieval, and tool-call metrics across framework "
            "implementations.",
        ]
    )

    output_path.write_text("\n".join(lines), encoding="utf-8")


def plot_total_tokens(summary_df: pd.DataFrame) -> None:
    plt.figure(figsize=(10, 5))
    plt.bar(summary_df["framework"], summary_df["total_tokens"])
    plt.title("AgenticLens Benchmark: Total Tokens by Framework")
    plt.xlabel("Framework")
    plt.ylabel("Total Tokens")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()

    output = RESULTS_DIR / "benchmark_tokens_chart.png"
    plt.savefig(output)
    plt.close()

    print(f"Saved token chart: {output}")


def plot_total_cost(summary_df: pd.DataFrame) -> None:
    plt.figure(figsize=(10, 5))
    plt.bar(summary_df["framework"], summary_df["total_cost_usd"])
    plt.title("AgenticLens Benchmark: Estimated Cost by Framework")
    plt.xlabel("Framework")
    plt.ylabel("Estimated Cost USD")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()

    output = RESULTS_DIR / "benchmark_cost_chart.png"
    plt.savefig(output)
    plt.close()

    print(f"Saved cost chart: {output}")


def main() -> None:
    summary_rows = []
    step_rows = []

    for framework, report_path in REPORTS.items():
        path = Path(report_path)

        if not path.exists():
            print(f"Skipping {framework}: report not found at {report_path}")
            continue

        report = load_report(path)

        summary_rows.append(summarize_report(framework, report))
        step_rows.extend(extract_step_rows(framework, report))

    if not summary_rows:
        raise RuntimeError("No reports found. Run AgenticLens profile commands first.")

    summary_df = pd.DataFrame(summary_rows)
    step_df = pd.DataFrame(step_rows)

    summary_df = summary_df.sort_values(by=["total_tokens", "framework"])

    summary_csv = RESULTS_DIR / "benchmark_results.csv"
    step_csv = RESULTS_DIR / "benchmark_step_breakdown.csv"
    summary_md = RESULTS_DIR / "benchmark_summary.md"

    summary_df.to_csv(summary_csv, index=False)
    step_df.to_csv(step_csv, index=False)
    create_markdown_summary(summary_df, summary_md)

    plot_total_tokens(summary_df)
    plot_total_cost(summary_df)

    print("\nBenchmark comparison complete.")
    print(f"Summary CSV: {summary_csv}")
    print(f"Step breakdown CSV: {step_csv}")
    print(f"Markdown summary: {summary_md}")

    print("\nSummary:")
    print(summary_df.to_string(index=False))


if __name__ == "__main__":
    main()
