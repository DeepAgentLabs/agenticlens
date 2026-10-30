"""CSV, JSON, JSON Lines, and YAML case imports."""

import json
from pathlib import Path

import pytest

from agenticlens.suites import SuiteImportError, import_cases, import_csv, import_json, import_suite


def _write(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def test_import_csv_maps_columns(tmp_path: Path) -> None:
    path = _write(
        tmp_path / "cases.csv",
        "id,name,input,expected_contains,required_tools,max_latency_ms,max_turns,tags,domain,"
        "split,metadata.owner\n"
        'r1,Refund,"{""order"": 7}",refund| 30 days ,lookup|refund,1500,3,billing|smoke,billing,'
        "test,ops\n"
        "r2,,plain text,hi,,,,,,,\n",
    )
    first, second = import_csv(path)
    assert first.input == {"order": 7}
    assert first.expected_contains == ["refund", "30 days"]
    assert first.required_tools == ["lookup", "refund"]
    assert first.max_latency_ms == 1500.0 and first.max_turns == 3
    assert first.tags == ["billing", "smoke"]
    assert first.metadata["domain"] == "billing" and first.metadata["split"] == "test"
    assert first.metadata["owner"] == "ops"
    assert first.metadata["source"] == {"kind": "imported", "file": "cases.csv", "row": 1}
    assert second.name == "r2" and second.input == "plain text"


def test_import_csv_keeps_invalid_json_input_as_text(tmp_path: Path) -> None:
    path = _write(tmp_path / "c.csv", 'id,input,expected_output\nx,"{not json",ok\n')
    assert import_csv(path)[0].input == "{not json"


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("name,input\nx,y\n", "'id' column"),
        ("id,expected_output\n", "no data rows"),
        ("id,expectd_output\nx,y\n", "unknown column"),
        ("id,input\nx,y\n", "row 1"),
        ("id,max_latency_ms,expected_output\nx,fast,y\n", "row 1"),
    ],
)
def test_import_csv_rejects_bad_files(tmp_path: Path, text: str, message: str) -> None:
    with pytest.raises(SuiteImportError, match=message):
        import_csv(_write(tmp_path / "bad.csv", text))


def test_import_json_formats(tmp_path: Path) -> None:
    record = {"id": "a", "input": "q", "expected_output": "x", "metadata": {"domain": "d"}}
    as_list = _write(tmp_path / "a.json", json.dumps([record]))
    as_object = _write(tmp_path / "b.json", json.dumps({"cases": [record]}))
    as_lines = _write(tmp_path / "c.jsonl", json.dumps(record) + "\n\n")
    as_yaml = _write(tmp_path / "d.yaml", "cases:\n- id: a\n  input: q\n  expected_output: x\n")
    for path in (as_list, as_object, as_lines, as_yaml):
        (case,) = import_cases(path)
        assert case.id == "a" and case.name == "a"
        assert case.metadata["source"]["kind"] == "imported"
    assert import_json(as_list)[0].metadata["domain"] == "d"


def test_import_json_errors(tmp_path: Path) -> None:
    with pytest.raises(SuiteImportError, match="expected a list"):
        import_json(_write(tmp_path / "a.json", '{"x": 1}'))
    with pytest.raises(SuiteImportError, match="expected an object"):
        import_json(_write(tmp_path / "b.json", "[1]"))
    with pytest.raises(SuiteImportError, match="record 1"):
        import_json(_write(tmp_path / "c.json", '[{"id": "a"}]'))
    with pytest.raises(SuiteImportError, match="no records"):
        import_json(_write(tmp_path / "d.json", "[]"))


def test_import_suite_builds_named_suite(tmp_path: Path) -> None:
    path = _write(tmp_path / "c.csv", "id,expected_output\na,x\n")
    suite = import_suite(path, name="s", version="2", description="d")
    assert (suite.name, suite.version, suite.description) == ("s", "2", "d")
