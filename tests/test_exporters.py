import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

from agenticlens.exporters import CSVExporter, JiraExporter, JSONExporter, MarkdownExporter
from agenticlens.models import Metrics, Step, StepType, Workflow
from agenticlens.models.enums import Severity
from agenticlens.models.recommendation import Recommendation


def _sample_workflow() -> Workflow:
    workflow = Workflow(name="Test Workflow", start_time=datetime.now(timezone.utc))
    workflow.steps.append(
        Step(
            name="Planner",
            type=StepType.PLANNER,
            provider="openai",
            model="gpt-4o-mini",
            metrics=Metrics(prompt_tokens=10, completion_tokens=5, total_tokens=15),
        )
    )
    return workflow


def test_json_exporter_writes_valid_json(tmp_path: Path) -> None:
    out = tmp_path / "workflow.json"
    JSONExporter().export(_sample_workflow(), out)

    data = json.loads(out.read_text())
    assert data["name"] == "Test Workflow"
    assert data["steps"][0]["name"] == "Planner"


def test_csv_exporter_writes_step_rows(tmp_path: Path) -> None:
    out = tmp_path / "steps.csv"
    CSVExporter().export(_sample_workflow(), out)

    with out.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 1
    assert rows[0]["step_name"] == "Planner"
    assert rows[0]["total_tokens"] == "15"


def test_markdown_exporter_writes_report(tmp_path: Path) -> None:
    out = tmp_path / "report.md"
    MarkdownExporter().export(_sample_workflow(), out)

    content = out.read_text(encoding="utf-8")
    assert "# Workflow Report: Test Workflow" in content
    assert "| Total Tokens | 15 |" in content
    assert "| Planner |" in content
    assert "planner" in content


def test_markdown_exporter_handles_none_cost(tmp_path: Path) -> None:
    out = tmp_path / "report.md"
    MarkdownExporter().export(_sample_workflow(), out)

    content = out.read_text(encoding="utf-8")
    assert "| Total Cost | - |" in content


def test_jira_exporter_builds_comment() -> None:
    exporter = JiraExporter(
        base_url="https://test.atlassian.net",
        user_email="user@example.com",
        api_token="fake-token",
        issue_key="PROJ-123",
    )
    comment = exporter._build_comment(_sample_workflow())

    assert "*AgenticLens Workflow Report: Test Workflow*" in comment
    assert "|Total Tokens|15|" in comment
    assert "|Planner|" in comment


@patch("agenticlens.exporters.jira_exporter.urlopen")
def test_jira_exporter_posts_comment(mock_urlopen: MagicMock, tmp_path: Path) -> None:
    mock_response = MagicMock()
    mock_response.read.return_value = b'{"id": "12345"}'
    mock_response.__enter__.return_value = mock_response
    mock_response.__exit__.return_value = False
    mock_urlopen.return_value = mock_response

    exporter = JiraExporter(
        base_url="https://test.atlassian.net",
        user_email="user@example.com",
        api_token="fake-token",
        issue_key="PROJ-123",
    )
    out = tmp_path / "comment.txt"
    exporter.export(_sample_workflow(), out)

    mock_urlopen.assert_called_once()
    req = mock_urlopen.call_args.args[0]
    assert req.full_url == "https://test.atlassian.net/rest/api/2/issue/PROJ-123/comment"
    assert req.get_header("Authorization").startswith("Basic ")
    assert mock_urlopen.call_args.kwargs["timeout"] == 10
    assert out.exists()
    assert "AgenticLens" in out.read_text()


def _sample_recommendations() -> list[Recommendation]:
    return [
        Recommendation(
            title="Low-utility retrieved chunks",
            description="Step 'Retriever' retrieved 2 chunks that appear unlikely to influence the answer.",
            severity=Severity.WARNING,
            tokens_saved=100,
            confidence=0.85,
            quality_risk="low",
        ),
    ]


def test_markdown_exporter_includes_recommendations(tmp_path: Path) -> None:
    out = tmp_path / "report.md"
    MarkdownExporter().export(_sample_workflow(), out, recommendations=_sample_recommendations())

    content = out.read_text(encoding="utf-8")
    assert "## Optimization Recommendations" in content
    assert "Low-utility retrieved chunks" in content
    assert "Tokens Saved:** 100" in content
    assert "Confidence:** 85%" in content
    assert "Quality Risk:** low" in content


def test_json_exporter_includes_recommendations(tmp_path: Path) -> None:
    out = tmp_path / "workflow.json"
    JSONExporter().export(_sample_workflow(), out, recommendations=_sample_recommendations())

    data = json.loads(out.read_text())
    assert "recommendations" in data
    assert len(data["recommendations"]) == 1
    assert data["recommendations"][0]["title"] == "Low-utility retrieved chunks"
    assert data["recommendations"][0]["tokens_saved"] == 100


def test_csv_exporter_writes_recommendations_file(tmp_path: Path) -> None:
    out = tmp_path / "steps.csv"
    CSVExporter().export(_sample_workflow(), out, recommendations=_sample_recommendations())

    rec_path = tmp_path / "steps_recommendations.csv"
    assert rec_path.exists()

    with rec_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 1
    assert rows[0]["title"] == "Low-utility retrieved chunks"
    assert rows[0]["tokens_saved"] == "100"
    assert rows[0]["severity"] == "warning"


def test_exporters_work_without_recommendations(tmp_path: Path) -> None:
    """Backward compatibility: exporters still work without recommendations."""
    md_out = tmp_path / "report.md"
    MarkdownExporter().export(_sample_workflow(), md_out)
    assert "## Optimization Recommendations" not in md_out.read_text()

    json_out = tmp_path / "workflow.json"
    JSONExporter().export(_sample_workflow(), json_out)
    data = json.loads(json_out.read_text())
    assert "recommendations" not in data

    csv_out = tmp_path / "steps.csv"
    CSVExporter().export(_sample_workflow(), csv_out)
    assert not (tmp_path / "steps_recommendations.csv").exists()
