"""Runs the live (real-API) travel-briefing workflow across all six frameworks.

Companion to benchmark_runner.py, which profiles a fully deterministic
workload. This one calls real, live, free APIs (Open-Meteo, Frankfurter,
Wikipedia) for every tool/retriever step, so token counts stay identical
across frameworks (the LLM steps are still a deterministic fallback without
an OPENAI_API_KEY) but latency genuinely differs run to run and framework to
framework -- it reflects real network conditions, not scripted timings.
"""

import csv
import json
import os
import subprocess
from pathlib import Path

from benchmarks.shared.metrics_collector import summarize_agenticlens_report

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parent

FRAMEWORKS = {
    "native_python": ROOT / "frameworks" / "native_python" / "run_native_live.py",
    "langgraph": ROOT / "frameworks" / "langgraph" / "run_langgraph_live.py",
    "crewai": ROOT / "frameworks" / "crewai" / "run_crewai_live.py",
    "autogen": ROOT / "frameworks" / "autogen" / "run_autogen_live.py",
    "llamaindex": ROOT / "frameworks" / "llamaindex" / "run_llamaindex_live.py",
    "semantic_kernel": ROOT / "frameworks" / "semantic_kernel" / "run_semantic_kernel_live.py",
}

REPORT_DIR = ROOT / "reports"
RESULTS_DIR = ROOT / "results"


def run_framework(framework_name: str, script_path: Path) -> Path | None:
    if not script_path.exists():
        print(f"Skipping {framework_name}: file not found: {script_path}")
        return None

    framework_report_dir = REPORT_DIR / framework_name
    framework_report_dir.mkdir(parents=True, exist_ok=True)

    report_path = framework_report_dir / "live_travel_report.json"

    cmd = ["agenticlens", "profile", str(script_path), "--save", str(report_path)]

    env = os.environ.copy()
    existing_path = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = (
        f"{PROJECT_ROOT}{os.pathsep}{existing_path}" if existing_path else str(PROJECT_ROOT)
    )

    print(f"\nRunning {framework_name} live travel benchmark...")
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
        "# AgenticLens Live Travel Briefing Benchmark",
        "",
        "Use case: real-time trip briefing (weather, currency, destination facts).",
        "",
        "Every tool/retriever step below calls a real, live, free API "
        "(Open-Meteo geocoding + forecast, Frankfurter exchange rates, Wikipedia "
        "REST summary) -- no API key required, no mocking. LLM steps use a "
        "deterministic fallback unless OPENAI_API_KEY is set, so token counts "
        "are stable across frameworks but latency is genuinely live.",
        "",
        "| Framework | Total Tokens | Cost | Latency | Steps | Tool Calls | "
        "Retrieved Chunks | Highest Latency Step |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]

    for row in results:
        lines.append(
            "| {framework} | {total_tokens} | ${total_cost:.6f} | {total_latency:.3f}s | "
            "{step_count} | {tool_calls} | {retrieved_chunks} | "
            "{highest_latency_step} |".format(**row)
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Total tokens and cost are near-identical across frameworks because the "
            "LLM steps are a deterministic fallback (no OPENAI_API_KEY set). Latency "
            "is the meaningful column here: it reflects real network round-trips to "
            "four live APIs, not scripted timings, so it varies between runs and "
            "frameworks based on real network conditions and per-framework overhead.",
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

        report = json.loads(report_path.read_text(encoding="utf-8"))
        highest_latency = max(report.get("steps", []), key=lambda s: s["metrics"]["latency"])
        summary["highest_latency_step"] = highest_latency["name"]
        summary["highest_step_latency"] = round(highest_latency["metrics"]["latency"], 4)

        results.append(summary)

    json_output = RESULTS_DIR / "live_travel_results.json"
    csv_output = RESULTS_DIR / "live_travel_results.csv"
    md_output = RESULTS_DIR / "live_travel_summary.md"

    json_output.write_text(json.dumps(results, indent=2), encoding="utf-8")
    write_csv(results, csv_output)
    write_markdown_summary(results, md_output)

    print("\nLive travel benchmark complete.")
    print(f"JSON: {json_output}")
    print(f"CSV: {csv_output}")
    print(f"Markdown: {md_output}")


if __name__ == "__main__":
    main()
