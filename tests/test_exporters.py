import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from tokenlens.exporters import CSVExporter, JSONExporter
from tokenlens.models import Metrics, Step, StepType, Workflow


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
