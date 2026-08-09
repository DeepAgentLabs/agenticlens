import json
from pathlib import Path

from typer.testing import CliRunner

from agenticlens.cli.main import app
from agenticlens.exporters import JSONExporter
from agenticlens.models import Metrics, Step, StepType, Workflow


def test_inspect_trace(tmp_path):
    trace_file = tmp_path / "trace.json"
    trace_file.write_text(
        '{"application_name":"demo","status":"succeeded","spans":[]}',
        encoding="utf-8",
    )
    result = CliRunner().invoke(app, ["inspect", str(trace_file)])
    assert result.exit_code == 0
    assert "Run Summary" in result.output
    assert "demo" in result.output


def test_inspect_trace_can_save_markdown(tmp_path):
    trace_file = tmp_path / "trace.json"
    markdown_file = tmp_path / "trace.md"
    trace_file.write_text(
        '{"application_name":"demo","status":"succeeded","spans":[]}',
        encoding="utf-8",
    )
    result = CliRunner().invoke(app, ["inspect", str(trace_file), "--save", str(markdown_file)])
    assert result.exit_code == 0
    assert markdown_file.exists()
    assert "Trace Report" in markdown_file.read_text(encoding="utf-8")


def test_compare_trace_directories(tmp_path):
    baseline = tmp_path / "baseline"
    candidate = tmp_path / "candidate"
    baseline.mkdir()
    candidate.mkdir()
    payload = '{"application_name":"demo","status":"succeeded","task_success":true,"spans":[]}'
    (baseline / "run.json").write_text(payload, encoding="utf-8")
    (candidate / "run.json").write_text(payload, encoding="utf-8")
    report_file = tmp_path / "comparison.json"

    result = CliRunner().invoke(
        app,
        ["compare", str(baseline), str(candidate), "--save", str(report_file)],
    )

    assert result.exit_code == 0
    assert "No regressions detected" in result.output
    assert report_file.exists()


def test_compare_can_save_markdown(tmp_path):
    baseline = tmp_path / "baseline"
    candidate = tmp_path / "candidate"
    baseline.mkdir()
    candidate.mkdir()
    payload = '{"application_name":"demo","status":"succeeded","task_success":true,"spans":[]}'
    (baseline / "run.json").write_text(payload, encoding="utf-8")
    (candidate / "run.json").write_text(payload, encoding="utf-8")
    report_file = tmp_path / "comparison.md"

    result = CliRunner().invoke(
        app,
        ["compare", str(baseline), str(candidate), "--save", str(report_file), "--format", "md"],
    )

    assert result.exit_code == 0
    assert "Sample Size Guidance" in report_file.read_text(encoding="utf-8")


def test_compare_can_enforce_min_samples(tmp_path):
    baseline = tmp_path / "baseline"
    candidate = tmp_path / "candidate"
    baseline.mkdir()
    candidate.mkdir()
    payload = '{"application_name":"demo","status":"succeeded","task_success":true,"spans":[]}'
    (baseline / "run.json").write_text(payload, encoding="utf-8")
    (candidate / "run.json").write_text(payload, encoding="utf-8")

    result = CliRunner().invoke(
        app,
        ["compare", str(baseline), str(candidate), "--min-samples", "2"],
    )

    assert result.exit_code == 3
    assert "sample size requirement not met" in result.output.lower()


runner = CliRunner()


def _spec_root() -> Path:
    sibling_repo = Path(__file__).resolve().parents[2] / "ai-operations-spec"
    if sibling_repo.exists():
        return sibling_repo
    return Path(__file__).resolve().parent / "fixtures" / "ai-operations-spec"


SPEC_ROOT = _spec_root()

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
            agent_name="planner_agent",
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
    assert "Agent Token Summary" in result.output
    assert "planner_agent" in result.output
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


def test_evaluate_live_python_target(tmp_path: Path) -> None:
    suite_file = tmp_path / "suite.json"
    report_file = tmp_path / "evaluation.json"
    suite_file.write_text(
        json.dumps(
            {
                "name": "live",
                "version": "1",
                "cases": [
                    {
                        "id": "case-1",
                        "name": "Live target",
                        "input": {"response": '{"answer":"42","meta":{"confidence":0.9}}'},
                        "output_json_schema": {"type": "object", "required": ["answer"]},
                        "required_tool_arguments": {"add": ["a", "b"]},
                        "max_turns": 1,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        [
            "evaluate-live",
            str(suite_file),
            "--target-kind",
            "python",
            "--target",
            "tests/live_eval_target.py:run_case",
            "--save",
            str(report_file),
        ],
    )

    assert result.exit_code == 0
    assert report_file.exists()
    assert "Live evaluation complete" in result.output


def test_evaluate_live_help_mentions_trusted_targets() -> None:
    result = runner.invoke(app, ["evaluate-live", "--help"])
    assert result.exit_code == 0
    assert "trusted live python or http target" in result.output.lower()


def test_validate_accepts_valid_aios_workflow_fixture() -> None:
    artifact = SPEC_ROOT / "specification" / "v0.4" / "examples" / "valid" / "workflow.json"

    result = runner.invoke(
        app,
        ["validate", str(artifact), "--spec-root", str(SPEC_ROOT)],
    )

    assert result.exit_code == 0
    assert "Draft alignment" in result.output
    assert "No AIOS issues detected" in result.output


def test_validate_rejects_invalid_aios_fixture() -> None:
    artifact = (
        SPEC_ROOT / "specification" / "v0.4" / "examples" / "invalid" / "workflow-missing-name.json"
    )

    result = runner.invoke(
        app,
        ["validate", str(artifact), "--spec-root", str(SPEC_ROOT)],
    )

    assert result.exit_code == 2
    assert "schema.invalid" in result.output


def test_conformance_rejects_semantically_invalid_aios_fixture() -> None:
    artifact = (
        SPEC_ROOT
        / "specification"
        / "v0.4"
        / "examples"
        / "semantic-invalid"
        / "dangling-reference.json"
    )

    result = runner.invoke(
        app,
        ["conformance", str(artifact), "--spec-root", str(SPEC_ROOT)],
    )

    assert result.exit_code == 2
    assert "semantic.unresolved-reference" in result.output


def test_conformance_accepts_valid_aios_run_fixture_and_can_save_report(tmp_path: Path) -> None:
    artifact = SPEC_ROOT / "specification" / "v0.4" / "examples" / "valid" / "run.json"
    report_file = tmp_path / "conformance.json"

    result = runner.invoke(
        app,
        [
            "conformance",
            str(artifact),
            "--spec-root",
            str(SPEC_ROOT),
            "--save",
            str(report_file),
        ],
    )

    assert result.exit_code == 0
    assert report_file.exists()
    report = json.loads(report_file.read_text(encoding="utf-8"))
    assert report["aligned"] is True
    assert report["mode"] == "conformance"


def test_finding_schema_v2_artifact_exists() -> None:
    schema_path = Path("schemas/v2/finding.schema.json")
    assert schema_path.exists()
    data = json.loads(schema_path.read_text(encoding="utf-8"))
    assert (
        data["$id"] == "https://deepagentlabs.github.io/agenticlens/schemas/v2/finding.schema.json"
    )
