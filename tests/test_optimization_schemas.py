"""Published optimization schemas must match the pydantic models they describe."""

import json
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator

from agenticlens.optimization import (
    OptimizationConfig,
    OptimizationReport,
    OutcomeEvaluation,
    RecommendationDecision,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas" / "optimization"
EXAMPLE = ROOT / "examples" / "optimization"


def _schema(name: str) -> dict:
    return json.loads((SCHEMAS / f"{name}.schema.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    ("name", "model"),
    [
        ("optimization-config", OptimizationConfig),
        ("optimization-report", OptimizationReport),
        ("recommendation-decision", RecommendationDecision),
        ("outcome-evaluation", OutcomeEvaluation),
    ],
)
def test_published_schema_matches_model(name: str, model: type) -> None:
    published = _schema(name)
    generated = model.model_json_schema()  # type: ignore[attr-defined]

    Draft202012Validator.check_schema(published)
    assert published["$id"].endswith(f"/schemas/optimization/{name}.schema.json")
    assert {k: v for k, v in published.items() if k not in {"$schema", "$id"}} == generated


def test_example_artifacts_validate_against_the_schemas() -> None:
    artifacts = EXAMPLE / "artifacts"
    documents = [
        ("optimization-config", yaml.safe_load((EXAMPLE / "optimization.yaml").read_text())),
        ("optimization-report", json.loads((artifacts / "report.json").read_text())),
        ("outcome-evaluation", json.loads((artifacts / "outcome.json").read_text())),
    ]
    documents += [
        ("recommendation-decision", json.loads(line))
        for line in (artifacts / "ledger.jsonl").read_text().splitlines()
    ]
    for name, document in documents:
        Draft202012Validator(_schema(name)).validate(document)
