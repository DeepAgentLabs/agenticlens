"""Published suite schemas must match the pydantic models they describe."""

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from agenticlens.suites import DuplicateReport, FeedbackBatch, MaskingReport, SuiteVersion

SCHEMAS = Path(__file__).resolve().parents[1] / "schemas" / "suites"


@pytest.mark.parametrize(
    ("name", "model"),
    [
        ("suite-version", SuiteVersion),
        ("feedback-batch", FeedbackBatch),
        ("duplicate-report", DuplicateReport),
        ("masking-report", MaskingReport),
    ],
)
def test_published_schema_matches_model(name: str, model: type) -> None:
    published = json.loads((SCHEMAS / f"{name}.schema.json").read_text(encoding="utf-8"))
    generated = model.model_json_schema()  # type: ignore[attr-defined]

    Draft202012Validator.check_schema(published)
    assert published["$id"].endswith(f"/schemas/suites/{name}.schema.json")
    assert published.get("$defs") == generated.get("$defs")
    assert published["properties"] == generated["properties"]
    assert published.get("required") == generated.get("required")
