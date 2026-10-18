"""Published ModelFit schemas must match the pydantic models they describe."""

import json
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator

from agenticlens.modelfit import ModelFitConfig, ModelFitReport

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas" / "modelfit"


@pytest.mark.parametrize(
    ("name", "model"),
    [("modelfit-config", ModelFitConfig), ("modelfit-report", ModelFitReport)],
)
def test_published_schema_matches_model(name: str, model: type) -> None:
    published = json.loads((SCHEMAS / f"{name}.schema.json").read_text(encoding="utf-8"))
    generated = model.model_json_schema()  # type: ignore[attr-defined]

    Draft202012Validator.check_schema(published)
    assert published["$id"].endswith(f"/schemas/modelfit/{name}.schema.json")
    assert published.get("$defs") == generated.get("$defs")
    assert published["properties"] == generated["properties"]
    assert published.get("required") == generated.get("required")


def test_example_config_and_report_validate_against_the_schemas() -> None:
    example = ROOT / "examples" / "modelfit"
    config = yaml.safe_load((example / "modelfit.yaml").read_text(encoding="utf-8"))
    report = json.loads((example / "artifacts" / "modelfit.json").read_text(encoding="utf-8"))
    for name, document in (("modelfit-config", config), ("modelfit-report", report)):
        schema = json.loads((SCHEMAS / f"{name}.schema.json").read_text(encoding="utf-8"))
        Draft202012Validator(schema).validate(document)
