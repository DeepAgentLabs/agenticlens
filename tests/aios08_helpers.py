import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource


def assert_schema(document):
    root = Path(__file__).parent / "fixtures/aios-v0.8"
    schemas = [
        json.loads(p.read_text()) for p in root.glob("specification/v*/schemas/*.schema.json")
    ]
    registry = Registry().with_resources((s["$id"], Resource.from_contents(s)) for s in schemas)
    schema = next(
        s
        for s in schemas
        if s.get("properties", {}).get("artifact_type", {}).get("const")
        == document["artifact_type"]
    )
    Draft202012Validator(schema, registry=registry, format_checker=FormatChecker()).validate(
        document
    )
