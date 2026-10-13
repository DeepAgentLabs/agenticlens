"""CLI: diagnose, explain, trace show/timeline, attribution-accuracy, score analysis."""

import json
from pathlib import Path

from typer.testing import CliRunner

from agenticlens.cli.main import app

ROOT = Path(__file__).resolve().parents[1]
DIAGNOSIS = ROOT / "examples" / "diagnosis"
INCIDENT = DIAGNOSIS / "artifacts" / "incident.json"
BASELINE = DIAGNOSIS / "artifacts" / "baseline"
EVALUATION = ROOT / "examples" / "advanced_evaluation"


def _invoke(*args: str) -> tuple[int, str]:
    result = CliRunner().invoke(app, list(args))
    return result.exit_code, result.output


def test_diagnose_saves_report_and_narrative(tmp_path: Path) -> None:
    report, narrative = tmp_path / "d.json", tmp_path / "d.md"
    code, output = _invoke(
        "diagnose",
        str(INCIDENT),
        "--baseline",
        str(BASELINE),
        "--save",
        str(report),
        "--markdown",
        str(narrative),
    )
    assert code == 0, output
    assert "issue_refund" in output and "Anomalies: 3" in output
    saved = json.loads(report.read_text("utf-8"))
    assert saved["attribution"]["faulty_step"] == "issue_refund"
    assert "## Root cause" in narrative.read_text("utf-8")


def test_diagnose_matches_the_committed_demo_report(tmp_path: Path) -> None:
    out = tmp_path / "d.json"
    _invoke("diagnose", str(INCIDENT), "--baseline", str(BASELINE), "--save", str(out))
    committed = (DIAGNOSIS / "artifacts" / "diagnosis.json").read_text("utf-8")
    assert json.loads(out.read_text("utf-8")) == json.loads(committed)


def test_diagnose_exit_codes(tmp_path: Path) -> None:
    code, _ = _invoke("diagnose", str(INCIDENT), "--fail-on-unrecovered")
    assert code == 4
    healthy = next(BASELINE.glob("*.json"))
    assert _invoke("diagnose", str(healthy), "--fail-on-unrecovered")[0] == 0
    assert _invoke("diagnose", str(tmp_path / "missing.json"))[0] == 1
    assert _invoke("diagnose", str(INCIDENT), "--baseline", str(tmp_path / "none"))[0] == 1


def test_diagnose_budgets_and_guardrails() -> None:
    healthy = next(BASELINE.glob("*.json"))
    code, output = _invoke("diagnose", str(healthy), "--max-tokens", "100", "--max-spans", "2")
    assert code == 0
    assert "budget_exceeded" in output and "Guardrail: span limit" in output


def test_explain_accepts_traces_reports_and_workflows(tmp_path: Path) -> None:
    code, output = _invoke("explain", str(INCIDENT), "--save", str(tmp_path / "n.md"))
    assert code == 0 and "Investigation" in output
    assert (tmp_path / "n.md").read_text("utf-8").startswith("# Investigation")
    assert _invoke("explain", str(DIAGNOSIS / "artifacts" / "diagnosis.json"))[0] == 0
    workflow = ROOT / "examples" / "artifacts"
    sample = next(
        (p for p in workflow.glob("*.json") if "steps" in json.loads(p.read_text("utf-8"))), None
    )
    if sample is not None:
        assert _invoke("explain", str(sample))[0] == 0
    other = tmp_path / "other.json"
    other.write_text("[]", "utf-8")
    assert _invoke("explain", str(other))[0] == 1
    assert _invoke("explain", str(tmp_path / "missing.json"))[0] == 1


def test_trace_show_and_timeline(tmp_path: Path) -> None:
    code, output = _invoke("trace", "show", str(INCIDENT))
    assert code == 0 and "issue_refund" in output
    code, output = _invoke("trace", "show", str(INCIDENT), "--span", "incident-0042-pay")
    assert code == 0 and "TimeoutError" in output
    assert _invoke("trace", "show", str(INCIDENT), "--span", "nope")[0] == 1
    timeline = tmp_path / "t.json"
    code, output = _invoke("trace", "timeline", str(INCIDENT), "--save", str(timeline))
    assert code == 0 and "ROOT CAUSE" in output
    assert json.loads(timeline.read_text("utf-8"))["root_cause_offset_ms"] is not None


def test_attribution_accuracy_command(tmp_path: Path) -> None:
    out = tmp_path / "a.json"
    code, output = _invoke(
        "attribution-accuracy",
        str(DIAGNOSIS / "controlled_failures"),
        "--save",
        str(out),
        "--min-step-accuracy",
        "0.9",
    )
    assert code == 0 and "40/40" in output
    assert json.loads(out.read_text("utf-8"))["total_cases"] == 40
    single = DIAGNOSIS / "controlled_failures" / "tool-loop-1.json"
    code, _ = _invoke("attribution-accuracy", str(single), "--min-step-accuracy", "1.01")
    assert code != 0
    assert _invoke("attribution-accuracy", str(tmp_path / "missing.json"))[0] == 1


def test_evaluate_uses_trace_evaluators_and_saves_score_analysis(tmp_path: Path) -> None:
    analysis = tmp_path / "analysis.json"
    code, output = _invoke(
        "evaluate",
        str(EVALUATION / "suite.yaml"),
        str(EVALUATION / "samples.json"),
        "--save",
        str(tmp_path / "r.json"),
        "--score-analysis",
        str(analysis),
    )
    assert code == 0, output
    assert "Scores: deterministic 12/15 passed" in output
    saved = json.loads(analysis.read_text("utf-8"))
    assert saved["deterministic"]["evaluators"] == [
        "citation",
        "groundedness",
        "loop",
        "safety",
        "tool_trajectory",
    ]
