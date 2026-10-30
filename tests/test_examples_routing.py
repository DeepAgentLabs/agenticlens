"""The routing example demonstrates every execution acceptance boundary offline."""

import json
import runpy
from pathlib import Path

from jsonschema import Draft202012Validator

from agenticlens.routing import RouteDecision, RoutingPolicy, RoutingResult

ROOT = Path(__file__).resolve().parents[1]


def test_routing_demo_and_published_schemas(tmp_path):
    module = runpy.run_path(str(ROOT / "examples/routing_demo.py"))
    result = module["main"](tmp_path)
    assert result == {
        "failover_served": "mid-b",
        "failover_statuses": ["retryable_error", "succeeded"],
        "shadow_served": "mid-b",
        "shadow_pairs": 1,
        "shadow_cost_delta_usd": -0.003,
        "unknown_task": "escalated",
    }
    for filename, model in [
        ("policy", RoutingPolicy),
        ("decision", RouteDecision),
        ("result", RoutingResult),
    ]:
        schema = json.loads((ROOT / f"schemas/routing/{filename}.schema.json").read_text())
        assert schema == model.model_json_schema()
        Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(RoutingResult.model_json_schema())
    for filename in ["failover.json", "shadow.json"]:
        validator.validate(json.loads((tmp_path / filename).read_text()))
    records = [json.loads(line) for line in (tmp_path / "routing.jsonl").read_text().splitlines()]
    assert records[0]["event"] == "decision"
    assert records[-1]["event"] == "result"
