import json
from pathlib import Path

from typer.testing import CliRunner

from agenticlens.cli.main import app
from agenticlens.exporters import JSONExporter
from agenticlens.models import Metrics, Step, StepType, Workflow

runner = CliRunner()

_PROFILE_SCRIPT = """
from agenticlens import profile, step

class Usage:
    prompt_tokens = 100
    completion_tokens = 50

class Response:
    usage = Usage()

with profile("Demo Workflow"):
    with step("Planner", type="planner", provider="openai", model="gpt-4o-mini") as s:
        s.record(Response())
"""


def _sample_workflow() -> Workflow:
    from datetime import datetime, timezone

    workflow = Workflow(name="Saved Workflow", start_time=datetime.now(timezone.utc))
    workflow.steps.append(
        Step(
            name="Planner",
            type=StepType.PLANNER,
            provider="openai",
            model="gpt-4o-mini",
            metrics=Metrics(prompt_tokens=10, completion_tokens=5, total_tokens=15, cost=0.01),
        )
    )
    return workflow


def test_cli_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "agenticlens" in result.output.lower() or "Usage" in result.output


def test_cli_profile_runs_script_and_prints_summary(tmp_path: Path) -> None:
    script = tmp_path / "app.py"
    script.write_text(_PROFILE_SCRIPT)

    result = runner.invoke(app, ["profile", str(script)])

    assert result.exit_code == 0
    assert "Demo Workflow" in result.output
    assert "Planner" in result.output


def test_cli_profile_missing_script() -> None:
    result = runner.invoke(app, ["profile", "does-not-exist.py"])
    assert result.exit_code == 1
    assert "not found" in result.output.lower()


def test_cli_profile_script_without_profile_call_errors(tmp_path: Path) -> None:
    script = tmp_path / "app.py"
    script.write_text("print('hello')")

    result = runner.invoke(app, ["profile", str(script)])

    assert result.exit_code == 1
    assert "no workflow was profiled" in result.output.lower()


def test_cli_profile_saves_workflow(tmp_path: Path) -> None:
    script = tmp_path / "app.py"
    script.write_text(_PROFILE_SCRIPT)
    out = tmp_path / "report.json"

    result = runner.invoke(app, ["profile", str(script), "--save", str(out)])

    assert result.exit_code == 0
    assert out.exists()
    data = json.loads(out.read_text())
    assert data["name"] == "Demo Workflow"


def test_cli_report_displays_saved_workflow(tmp_path: Path) -> None:
    out = tmp_path / "report.json"
    JSONExporter().export(_sample_workflow(), out)

    result = runner.invoke(app, ["report", str(out)])

    assert result.exit_code == 0
    assert "Saved Workflow" in result.output
    assert "Planner" in result.output


def test_cli_report_missing_file() -> None:
    result = runner.invoke(app, ["report", "does-not-exist.json"])
    assert result.exit_code == 1
    assert "not found" in result.output.lower()


def test_cli_analyze_flags_duplicate_tool_calls(tmp_path: Path) -> None:
    from datetime import datetime, timezone

    workflow = Workflow(name="Tool Workflow", start_time=datetime.now(timezone.utc))
    for name in ("Lookup", "Lookup (retry)"):
        workflow.steps.append(
            Step(
                name=name,
                type=StepType.TOOL_CALL,
                metrics=Metrics(prompt_tokens=100, completion_tokens=20, total_tokens=120),
                metadata={"tool_name": "lookup_order", "tool_args": {"order_id": "A123"}},
            )
        )
    out = tmp_path / "workflow.json"
    JSONExporter().export(workflow, out)

    result = runner.invoke(app, ["analyze", str(out)])

    assert result.exit_code == 0
    assert "Duplicate tool call" in result.output
    assert "Estimated Savings" in result.output


def test_cli_analyze_no_recommendations(tmp_path: Path) -> None:
    out = tmp_path / "workflow.json"
    JSONExporter().export(_sample_workflow(), out)

    result = runner.invoke(app, ["analyze", str(out)])

    assert result.exit_code == 0
    assert "no optimization suggestions" in result.output.lower()
