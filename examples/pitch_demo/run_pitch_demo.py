"""Generate a trace, evaluation result, release decision, and HTML pitch report."""

import json
from pathlib import Path

from examples.reference_workflows.langgraph_supervisor import run_workflow

from agenticlens.evaluation import (
    EvaluationSample,
    GateConfig,
    evaluate_gate,
    evaluate_suite,
    load_suite,
    save_html_report,
)


def main() -> None:
    output_dir = Path("examples/pitch_demo/artifacts")
    output_dir.mkdir(parents=True, exist_ok=True)
    state, recording = run_workflow()
    recording.save(output_dir / "trace.json")

    suite = load_suite(Path("examples/pitch_demo/support-suite.yaml"))
    sample = EvaluationSample(
        case_id="regional-case-total",
        output=state["answer"],
        trace=recording.run,
    )
    (output_dir / "samples.json").write_text(
        json.dumps({"samples": [sample.model_dump(mode="json")]}, indent=2),
        encoding="utf-8",
    )
    report = evaluate_suite(suite, [sample])
    (output_dir / "evaluation.json").write_text(
        report.model_dump_json(indent=2),
        encoding="utf-8",
    )
    save_html_report(report, output_dir / "evaluation.html")
    decision = evaluate_gate(report, GateConfig())
    print(state["answer"])
    print(f"Evaluation: {report.summary.pass_rate:.0%} pass rate")
    print(f"Release gate: {'PASSED' if decision.passed else 'FAILED'}")
    print(f"Report: {output_dir / 'evaluation.html'}")
    if not decision.passed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
