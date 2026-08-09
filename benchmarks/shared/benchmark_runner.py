import csv
import json
import os
import subprocess
from pathlib import Path

from benchmarks.shared.metrics_collector import summarize_agenticlens_report

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parent

FRAMEWORKS = {
    "native_python": ROOT / "frameworks" / "native_python" / "run_native.py",
    "langgraph": ROOT / "frameworks" / "langgraph" / "run_langgraph.py",
    "crewai": ROOT / "frameworks" / "crewai" / "run_crewai.py",
    "autogen": ROOT / "frameworks" / "autogen" / "run_autogen.py",
    "llamaindex": ROOT / "frameworks" / "llamaindex" / "run_llamaindex.py",
    "semantic_kernel": ROOT / "frameworks" / "semantic_kernel" / "run_semantic_kernel.py",
}

REPORT_DIR = ROOT / "reports"
RESULTS_DIR = ROOT / "results"


def run_framework(framework_name: str, script_path: Path) -> Path | None:
    if not script_path.exists():
        print(f"Skipping {framework_name}: file not found: {script_path}")
        return None

    framework_report_dir = REPORT_DIR / framework_name
    framework_report_dir.mkdir(parents=True, exist_ok=True)

    report_path = framework_report_dir / "support_refund_report.json"

    cmd = [
        "agenticlens",
        "profile",
        str(script_path),
        "--save",
        str(report_path),
    ]

    # Each framework script does `from benchmarks.shared...`, which only resolves
    # if the project root is importable in the subprocess -- add it to PYTHONPATH
    # rather than relying on each script to patch sys.path itself.
    env = os.environ.copy()
    existing_path = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = (
        f"{PROJECT_ROOT}{os.pathsep}{existing_path}" if existing_path else str(PROJECT_ROOT)
    )

    print(f"\nRunning {framework_name} benchmark...")
    subprocess.run(cmd, check=True, env=env)

    return report_path


def write_csv(results: list[dict], output_path: Path) -> None:
    if not results:
        return

    fieldnames = list(results[0].keys())

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def write_markdown_summary(results: list[dict], output_path: Path) -> None:
    lines = [
        "# AgenticLens Practical Benchmark Summary",
        "",
        "Use case: Customer Support Refund Copilot",
        "",
        "This benchmark profiles the same practical support workflow across multiple "
        "agentic implementations.",
        "",
        "| Framework | Total Tokens | Cost | Latency | Steps | Tool Calls | "
        "Retrieved Chunks | Highest Token Step | Highest Cost Step |",
        "|---|---:|---:|---:|---:|---:|---:|---|---|",
    ]

    for row in results:
        lines.append(
            "| {framework} | {total_tokens} | ${total_cost:.6f} | {total_latency:.3f}s | "
            "{step_count} | {tool_calls} | {retrieved_chunks} | {highest_token_step} | "
            "{highest_cost_step} |".format(**row)
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "These results are workload-specific. They should not be read as a "
            "universal ranking of frameworks.",
            "The goal is to show how AgenticLens makes token usage, cost, latency, "
            "retrieval behavior, and tool activity visible across workflows.",
        ]
    )

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    results = []

    for framework_name, script_path in FRAMEWORKS.items():
        report_path = run_framework(framework_name, script_path)

        if report_path is None:
            continue

        summary = summarize_agenticlens_report(framework_name, report_path)
        results.append(summary)

    json_output = RESULTS_DIR / "benchmark_results.json"
    csv_output = RESULTS_DIR / "benchmark_results.csv"
    md_output = RESULTS_DIR / "benchmark_summary.md"

    json_output.write_text(json.dumps(results, indent=2), encoding="utf-8")
    write_csv(results, csv_output)
    write_markdown_summary(results, md_output)

    print("\nBenchmark complete.")
    print(f"JSON: {json_output}")
    print(f"CSV: {csv_output}")
    print(f"Markdown: {md_output}")


if __name__ == "__main__":
    main()
