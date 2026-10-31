"""`agenticlens optimize` analyzes, records decisions, and evaluates outcomes."""

import json
from pathlib import Path

from typer.testing import CliRunner

from agenticlens.cli.main import app
from agenticlens.cli.optimize import REGRESSION_EXIT

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "optimization"
runner = CliRunner()


def _analyze(tmp_path: Path) -> tuple[Path, dict]:
    report = tmp_path / "report.json"
    result = runner.invoke(
        app,
        [
            "optimize",
            "analyze",
            str(EXAMPLE / "traces/before"),
            "--config",
            str(EXAMPLE / "optimization.yaml"),
            "--baseline-variant",
            "large",
            "--save",
            str(report),
            "--markdown",
            str(tmp_path / "report.md"),
        ],
    )
    assert result.exit_code == 0, result.output
    return report, json.loads(report.read_text())


def _id(payload: dict, kind: str) -> str:
    return next(o["opportunity_id"] for o in payload["opportunities"] if o["kind"] == kind)


def test_analyze_decide_status_and_outcome(tmp_path: Path) -> None:
    report, payload = _analyze(tmp_path)
    assert "# Optimization opportunities" in (tmp_path / "report.md").read_text()
    ledger = tmp_path / "ledger.jsonl"
    target = _id(payload, "tool_result_caching")
    for status in ("accepted", "adopted"):
        result = runner.invoke(
            app,
            [
                "optimize",
                "decide",
                str(report),
                target,
                "--status",
                status,
                "--by",
                "ci",
                "--ledger",
                str(ledger),
                "--change",
                "pr-1",
            ],
        )
        assert result.exit_code == 0, result.output

    result = runner.invoke(app, ["optimize", "status", str(report), "--ledger", str(ledger)])
    assert result.exit_code == 0
    assert json.loads(result.output)["statuses"][target] == "adopted"

    saved = tmp_path / "outcome.json"
    result = runner.invoke(
        app,
        [
            "optimize",
            "outcome",
            str(report),
            target,
            "--before",
            str(EXAMPLE / "traces/before"),
            "--after",
            str(EXAMPLE / "traces/after"),
            "--ledger",
            str(ledger),
            "--save",
            str(saved),
            "--markdown",
            str(tmp_path / "o.md"),
            "--fail-on-regression",
        ],
    )
    assert result.exit_code == 0, result.output
    assert json.loads(saved.read_text())["status"] == "realized"


def test_invalid_decisions_exit_one(tmp_path: Path) -> None:
    report, payload = _analyze(tmp_path)
    target = _id(payload, "retry_policy")
    ledger = str(tmp_path / "ledger.jsonl")
    for args in (
        [target, "--status", "maybe"],
        [target, "--status", "adopted"],
        ["no-such-id", "--status", "accepted"],
    ):
        result = runner.invoke(
            app, ["optimize", "decide", str(report), *args, "--by", "ci", "--ledger", ledger]
        )
        assert result.exit_code == 1, args


def test_outcome_regression_exit_code(tmp_path: Path) -> None:
    # Default thresholds allow a 5% success drop; the small variant loses 25%.
    before, after = tmp_path / "large", tmp_path / "small"
    before.mkdir()
    after.mkdir()
    for path in (EXAMPLE / "traces/before").glob("*.json"):
        target = before if "large" in path.name else after
        target.joinpath(path.name).write_text(path.read_text())
    report = tmp_path / "report.json"
    result = runner.invoke(app, ["optimize", "analyze", str(before), "--save", str(report)])
    assert result.exit_code == 0, result.output
    payload = json.loads(report.read_text())
    args = ["optimize", "outcome", str(report), _id(payload, "tool_result_caching")]
    args += ["--before", str(before), "--after", str(after)]
    assert runner.invoke(app, args).exit_code == 0
    result = runner.invoke(app, [*args, "--fail-on-regression"])
    assert result.exit_code == REGRESSION_EXIT, result.output


def test_analyze_reports_missing_traces(tmp_path: Path) -> None:
    result = runner.invoke(app, ["optimize", "analyze", str(tmp_path / "missing.json")])
    assert result.exit_code == 1
