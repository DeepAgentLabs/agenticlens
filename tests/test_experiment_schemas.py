"""Published experiment schemas must match the pydantic models they describe."""

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from agenticlens.experiments import ExperimentManifest, ExperimentReport

SCHEMAS = Path(__file__).resolve().parents[1] / "schemas" / "experiments"


@pytest.mark.parametrize(
    ("name", "model"),
    [("experiment-report", ExperimentReport), ("experiment-manifest", ExperimentManifest)],
)
def test_published_schema_matches_model(name: str, model: type) -> None:
    published = json.loads((SCHEMAS / f"{name}.schema.json").read_text(encoding="utf-8"))
    generated = model.model_json_schema()  # type: ignore[attr-defined]

    Draft202012Validator.check_schema(published)
    assert published["$defs"] == generated.get("$defs")
    assert published["properties"] == generated["properties"]
    assert published.get("required") == generated.get("required")


def test_saved_example_report_validates_against_schema() -> None:
    schema = json.loads((SCHEMAS / "experiment-report.schema.json").read_text(encoding="utf-8"))
    example = Path(__file__).resolve().parents[1] / (
        "examples/experiments/artifacts/support-experiment.json"
    )
    Draft202012Validator(schema).validate(json.loads(example.read_text(encoding="utf-8")))
