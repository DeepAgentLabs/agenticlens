"""Import test cases from CSV and JSON (array, `{"cases": [...]}`, or JSON Lines).

CSV columns map onto agentic-evals `TestCase` fields. List columns
(`expected_contains`, `required_tools`, `forbidden_tools`,
`required_tool_order`, `tags`) are `|`-separated. `input` is parsed as JSON
when it is a JSON object or array, and kept as text otherwise. `domain` and
`split` go to case metadata; any column prefixed `metadata.` does too.
Unknown columns are rejected so a typo does not silently drop an expectation.
"""

import csv
import json
from pathlib import Path
from typing import Any

import yaml
from agentic_evals import TestCase, TestSuite
from pydantic import ValidationError

from agenticlens.suites.models import DOMAIN_KEY, SOURCE_KEY, SPLIT_KEY, CaseSource

_LIST_COLUMNS = {
    "expected_contains",
    "required_tools",
    "forbidden_tools",
    "required_tool_order",
    "tags",
}
_FLOAT_COLUMNS = {"max_latency_ms", "max_cost_usd"}
_INT_COLUMNS = {"max_turns"}
_TEXT_COLUMNS = {"id", "name", "expected_output"}
_METADATA_COLUMNS = {"domain": DOMAIN_KEY, "split": SPLIT_KEY}
_KNOWN_COLUMNS = (
    _LIST_COLUMNS
    | _FLOAT_COLUMNS
    | _INT_COLUMNS
    | _TEXT_COLUMNS
    | {"input"}
    | set(_METADATA_COLUMNS)
)


class SuiteImportError(ValueError):
    """A row or record could not be converted into a test case."""


def _parse_input(value: str) -> Any:
    stripped = value.strip()
    if stripped.startswith(("{", "[")):
        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            return value
    return value


def _row_to_case(row: dict[str, str], *, source: CaseSource) -> TestCase:
    unknown = [
        column
        for column in row
        if column is not None
        and column not in _KNOWN_COLUMNS
        and not column.startswith("metadata.")
    ]
    if unknown:
        raise SuiteImportError(f"unknown column(s): {', '.join(sorted(unknown))}")
    data: dict[str, Any] = {}
    metadata: dict[str, Any] = {SOURCE_KEY: source.model_dump(exclude_none=True)}
    for column, raw in row.items():
        if column is None or raw is None or raw.strip() == "":
            continue
        value = raw.strip()
        if column in _LIST_COLUMNS:
            data[column] = [item.strip() for item in value.split("|") if item.strip()]
        elif column in _FLOAT_COLUMNS:
            data[column] = float(value)
        elif column in _INT_COLUMNS:
            data[column] = int(value)
        elif column == "input":
            data[column] = _parse_input(raw)
        elif column in _METADATA_COLUMNS:
            metadata[_METADATA_COLUMNS[column]] = value
        elif column.startswith("metadata."):
            metadata[column.removeprefix("metadata.")] = value
        else:
            data[column] = value
    data.setdefault("name", data.get("id", ""))
    data["metadata"] = metadata
    return TestCase.model_validate(data)


def import_csv(path: Path) -> list[TestCase]:
    """Read test cases from a CSV file with a header row."""
    cases: list[TestCase] = []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or "id" not in reader.fieldnames:
            raise SuiteImportError(f"{path.name}: CSV needs a header row with an 'id' column")
        for row_number, row in enumerate(reader, start=1):
            source = CaseSource(kind="imported", file=path.name, row=row_number)
            try:
                cases.append(_row_to_case(row, source=source))
            except (ValidationError, ValueError) as exc:
                raise SuiteImportError(f"{path.name} row {row_number}: {exc}") from exc
    if not cases:
        raise SuiteImportError(f"{path.name}: no data rows")
    return cases


def _records(path: Path) -> list[Any]:
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix == ".jsonl":
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    data = json.loads(text) if suffix == ".json" else yaml.safe_load(text)
    if isinstance(data, dict) and isinstance(data.get("cases"), list):
        return list(data["cases"])
    if isinstance(data, list):
        return data
    raise SuiteImportError(f"{path.name}: expected a list of cases or an object with 'cases'")


def import_json(path: Path) -> list[TestCase]:
    """Read test cases from JSON, JSON Lines (`.jsonl`), or YAML."""
    cases: list[TestCase] = []
    for number, record in enumerate(_records(path), start=1):
        if not isinstance(record, dict):
            raise SuiteImportError(f"{path.name} record {number}: expected an object")
        source = CaseSource(kind="imported", file=path.name, row=number)
        metadata = {SOURCE_KEY: source.model_dump(exclude_none=True), **record.get("metadata", {})}
        payload = {**record, "metadata": metadata}
        payload.setdefault("name", payload.get("id", ""))
        try:
            cases.append(TestCase.model_validate(payload))
        except ValidationError as exc:
            raise SuiteImportError(f"{path.name} record {number}: {exc}") from exc
    if not cases:
        raise SuiteImportError(f"{path.name}: no records")
    return cases


def import_cases(path: Path) -> list[TestCase]:
    """Import by file extension: `.csv` or JSON/JSONL/YAML."""
    return import_csv(path) if path.suffix.lower() == ".csv" else import_json(path)


def import_suite(path: Path, *, name: str, version: str, description: str = "") -> TestSuite:
    return TestSuite(name=name, version=version, description=description, cases=import_cases(path))
