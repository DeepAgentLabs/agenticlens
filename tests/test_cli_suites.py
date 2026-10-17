"""CLI: agenticlens suite ..."""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from agenticlens.cli.main import app
from agenticlens.models.trace import Run, RunStatus, Span, SpanType


def _invoke(*args: object) -> tuple[int, str]:
    result = CliRunner().invoke(app, [str(arg) for arg in args])
    return result.exit_code, result.output


def _flat(output: str) -> str:
    return " ".join(output.split())


@pytest.fixture
def csv_file(tmp_path: Path) -> Path:
    path = tmp_path / "cases.csv"
    path.write_text(
        "id,name,input,expected_contains,tags,domain\n"
        "refund,Refund,Refund please; mail jo@example.com,refund,billing,billing\n"
        "reset,Reset,How do I reset my password?,reset link,account,account\n"
        "reset-dup,Reset again,how do i reset my password,reset link,account,account\n",
        encoding="utf-8",
    )
    return path


@pytest.fixture
def draft(tmp_path: Path, csv_file: Path) -> Path:
    path = tmp_path / "draft.yaml"
    code, output = _invoke(
        "suite", "import", csv_file, "--name", "support", "--version", "1.0.0", "--save", path
    )
    assert code == 0, output
    return path


def _cases(path: Path) -> list[dict[str, object]]:
    data = yaml.safe_load(path.read_text("utf-8"))
    return list(data["cases"])


def test_import_masks_pii_by_default(draft: Path, tmp_path: Path, csv_file: Path) -> None:
    assert "[EMAIL]" in str(_cases(draft)[0]["input"])
    raw = tmp_path / "raw.json"
    code, output = _invoke(
        "suite", "import", csv_file, "--name", "s", "--version", "1", "--save", raw, "--no-mask"
    )
    assert code == 0, output
    assert "jo@example.com" in raw.read_text("utf-8")


def test_import_requires_name_and_version_or_into(tmp_path: Path, csv_file: Path) -> None:
    code, output = _invoke("suite", "import", csv_file, "--save", tmp_path / "x.json")
    assert code == 1 and "--name and --version" in _flat(output)


def test_import_into_existing_suite(draft: Path, tmp_path: Path) -> None:
    extra = tmp_path / "extra.json"
    extra.write_text(json.dumps([{"id": "new", "expected_output": "x"}]), "utf-8")
    code, output = _invoke("suite", "import", extra, "--into", draft, "--save", draft)
    assert code == 0, output
    assert [case["id"] for case in _cases(draft)][-1] == "new"
    code, output = _invoke("suite", "import", extra, "--into", draft, "--save", draft)
    assert code == 1 and "exists in both" in _flat(output)


def test_import_reports_bad_files(tmp_path: Path) -> None:
    bad = tmp_path / "bad.csv"
    bad.write_text("id,oops\nx,y\n", "utf-8")
    code, output = _invoke("suite", "import", bad, "--name", "s", "--version", "1", "--save", bad)
    assert code == 1 and "unknown column" in _flat(output)


def test_edit_commands(draft: Path, tmp_path: Path) -> None:
    code, output = _invoke(
        "suite", "add-case", draft, "--id", "new", "--input", '{"q": 1}', "--contains", "ok",
        "--required-tool", "lookup", "--forbidden-tool", "delete", "--max-latency-ms", "900",
        "--max-cost-usd", "0.01", "--tag", "smoke", "--domain", "misc",
    )  # fmt: skip
    assert code == 0, output
    new_case = _cases(draft)[-1]
    assert new_case["input"] == {"q": 1}
    assert new_case["metadata"] == {"domain": "misc"}
    code, output = _invoke("suite", "add-case", draft, "--id", "empty")
    assert code == 1 and "at least one expectation" in _flat(output)

    code, _ = _invoke("suite", "tag", draft, "--case", "new", "--add", "vip", "--remove", "smoke")
    assert code == 0 and _cases(draft)[-1]["tags"] == ["vip"]
    code, _ = _invoke("suite", "tag", draft, "--domain", "support")
    assert code == 0
    assert {case["metadata"]["domain"] for case in _cases(draft)} == {"support"}  # type: ignore[index]

    code, output = _invoke("suite", "tag", draft, "--case", "ghost", "--add", "x")
    assert code == 1 and "ghost" in _flat(output)
    copy = tmp_path / "copy.json"
    code, _ = _invoke("suite", "remove-case", draft, "new", "--save", copy)
    assert code == 0
    assert len(json.loads(copy.read_text("utf-8"))["cases"]) == 3
    assert len(_cases(draft)) == 4  # original untouched with --save


def test_review_command(draft: Path) -> None:
    code, output = _invoke("suite", "review", draft, "--status", "maybe", "--reviewer", "qa")
    assert code == 1 and "--status" in _flat(output)
    code, output = _invoke(
        "suite", "review", draft, "--status", "rejected", "--reviewer", "qa", "--case", "refund",
        "--notes", "stale policy",
    )  # fmt: skip
    assert code == 0, output
    first = _cases(draft)[0]["metadata"]
    assert first["review_status"] == "rejected"  # type: ignore[index]
    assert first["review_notes"] == "stale policy"  # type: ignore[index]


def test_summary_command(draft: Path) -> None:
    code, output = _invoke("suite", "summary", draft)
    assert code == 0 and "support@1.0.0" in _flat(output) and "imported=3" in _flat(output)
    code, output = _invoke("suite", "summary", draft, "--json")
    assert code == 0 and json.loads(output)["by_domain"] == {"account": 2, "billing": 1}
    code, output = _invoke("suite", "summary", draft.with_name("missing.yaml"))
    assert code == 1 and "Unable to load suite" in _flat(output)


def test_mask_command(tmp_path: Path, csv_file: Path) -> None:
    raw = tmp_path / "raw.json"
    _invoke(
        "suite", "import", csv_file, "--name", "s", "--version", "1", "--save", raw, "--no-mask"
    )
    report = tmp_path / "mask.json"
    code, output = _invoke("suite", "mask", raw, "--check", "--report", report)
    assert code == 7 and "refund · input · email" in _flat(output)
    assert json.loads(report.read_text("utf-8"))["applied"] is False
    code, output = _invoke("suite", "mask", raw, "--strategy", "hash", "--salt", "s")
    assert code == 0 and "Masked 1 value(s) (email=1)" in _flat(output)
    assert "[EMAIL:" in raw.read_text("utf-8")
    code, _ = _invoke("suite", "mask", raw, "--check")
    assert code == 0
    code, output = _invoke("suite", "mask", raw, "--strategy", "rot13")
    assert code == 1 and "--strategy" in _flat(output)


def test_dedupe_command(draft: Path, tmp_path: Path) -> None:
    report = tmp_path / "dupes.json"
    code, output = _invoke("suite", "dedupe", draft, "--report", report)
    assert code == 0 and "exact (1.00): reset, reset-dup" in _flat(output)
    assert json.loads(report.read_text("utf-8"))["duplicate_case_ids"] == ["reset-dup"]
    assert len(_cases(draft)) == 3
    code, output = _invoke("suite", "dedupe", draft, "--drop")
    assert code == 0 and [case["id"] for case in _cases(draft)] == ["refund", "reset"]


def test_vary_and_split_commands(draft: Path) -> None:
    code, output = _invoke("suite", "vary", draft, "--per-case", "1", "--kind", "uppercase")
    assert code == 0 and "Added 3 variant(s)" in _flat(output)
    code, output = _invoke("suite", "vary", draft, "--per-case", "1", "--kind", "uppercase")
    assert code == 0 and "No new variations" in _flat(output)
    code, output = _invoke("suite", "vary", draft, "--kind", "paraphrase")
    assert code == 1 and "unknown variation" in _flat(output)
    code, output = _invoke("suite", "split", draft, "--seed", "1")
    assert code == 0, output
    by_id = {case["id"]: case["metadata"]["split"] for case in _cases(draft)}  # type: ignore[index]
    assert by_id["reset"] == by_id["reset--uppercase"]
    code, output = _invoke(
        "suite", "split", draft, "--train", "0.5", "--validation", "0.5", "--test", "0.5"
    )
    assert code == 1 and "add up" in _flat(output)


def test_split_warns_about_empty_split(draft: Path) -> None:
    code, output = _invoke(
        "suite", "split", draft, "--train", "0.98", "--validation", "0.01", "--test", "0.01"
    )
    assert code == 0 and "split is empty" in _flat(output)


def test_filter_command(draft: Path, tmp_path: Path) -> None:
    subset = tmp_path / "subset.json"
    code, output = _invoke("suite", "filter", draft, "--tag", "billing", "--save", subset)
    assert code == 0 and "Saved 1 of 3" in _flat(output)
    code, output = _invoke("suite", "filter", draft, "--domain", "none", "--save", subset)
    assert code == 1 and "no cases match" in _flat(output)


def _trace(tmp_path: Path, run_id: str, *, success: bool = True) -> Path:
    start = datetime(2026, 10, 1, tzinfo=timezone.utc)
    run = Run(
        run_id=run_id,
        application_name="bot",
        started_at=start,
        completed_at=start + timedelta(milliseconds=400),
        status=RunStatus.SUCCEEDED if success else RunStatus.FAILED,
        spans=[
            Span(
                span_id="s1",
                name="lookup",
                span_type=SpanType.TOOL_CALL,
                tool_name="lookup",
                status=RunStatus.SUCCEEDED,
                input_data={"q": f"question {run_id}", "email": "x@y.io"},
            )
        ],
    )
    path = tmp_path / "traces" / f"{run_id}.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(run.model_dump_json(), "utf-8")
    return path


def test_from_traces_and_feedback(tmp_path: Path) -> None:
    _trace(tmp_path, "r1")
    _trace(tmp_path, "r2", success=False)
    suite = tmp_path / "traces.json"
    code, output = _invoke(
        "suite", "from-traces", tmp_path / "traces", "--name", "prod", "--version", "1",
        "--save", suite,
    )  # fmt: skip
    assert code == 0, output
    assert "Converted 1 trace(s)" in _flat(output) and "skipped r2" in _flat(output)
    (case,) = json.loads(suite.read_text("utf-8"))["cases"]
    assert case["input"] == {"q": "question r1", "email": "[SENSITIVE_FIELD]"}
    assert case["required_tools"] == ["lookup"] and case["max_latency_ms"] == 600.0

    feedback = tmp_path / "feedback.json"
    feedback.write_text(
        json.dumps(
            {
                "feedback": [
                    {"feedback_id": "f1", "run_id": "r1", "output": "ok", "rating": "positive"},
                    {"feedback_id": "f2", "input": "q", "output": "bad", "rating": "negative"},
                ]
            }
        ),
        "utf-8",
    )
    code, output = _invoke(
        "suite", "from-feedback", feedback, "--into", suite, "--save", suite,
        "--traces", tmp_path / "traces" / "r1.json",
    )  # fmt: skip
    assert code == 0, output
    assert "Converted 1 feedback record(s)" in _flat(output) and "skipped f2" in _flat(output)
    assert [c["id"] for c in json.loads(suite.read_text("utf-8"))["cases"]] == [
        "trace-r1",
        "feedback-f1",
    ]


def test_from_traces_with_nothing_convertible(tmp_path: Path) -> None:
    path = _trace(tmp_path, "r9", success=False)
    code, output = _invoke(
        "suite", "from-traces", path, "--name", "p", "--version", "1", "--save", tmp_path / "o.json"
    )
    assert code == 1 and "No cases to save" in _flat(output)
    code, output = _invoke(
        "suite", "from-traces", tmp_path / "nope.json", "--name", "p", "--version", "1",
        "--save", tmp_path / "o.json",
    )  # fmt: skip
    assert code == 1 and "Unable to load traces" in _flat(output)


def test_approve_verify_export_diff(draft: Path, tmp_path: Path) -> None:
    store = tmp_path / "store"
    pending = tmp_path / "pending.yaml"
    _invoke("suite", "vary", draft, "--per-case", "1", "--save", pending)
    code, output = _invoke("suite", "approve", pending, "--store", store, "--approver", "qa")
    assert code == 6 and "Approval refused" in _flat(output) and "need review" in _flat(output)

    code, output = _invoke(
        "suite", "approve", draft, "--store", store, "--approver", "qa", "--notes", "first"
    )
    assert code == 0, output
    assert "Approved support@1.0.0 (3 cases" in _flat(output)

    code, output = _invoke("suite", "versions", "--store", store)
    assert code == 0 and "support" in _flat(output) and "qa" in _flat(output)

    exported = tmp_path / "exported.json"
    code, output = _invoke(
        "suite", "export", "support@1.0.0", "--store", store, "--save", exported, "--tag", "account"
    )
    assert code == 0 and "Exported 2 case(s)" in _flat(output)
    data = json.loads(exported.read_text("utf-8"))
    assert data["metadata"]["agenticlens_suite_version"]["approved_by"] == "qa"

    # A new draft version diffs against the stored one.
    _invoke("suite", "remove-case", draft, "reset-dup")
    text = draft.read_text("utf-8").replace("version: 1.0.0", "version: 1.1.0")
    draft.write_text(text, "utf-8")
    code, output = _invoke("suite", "diff", "support@1.0.0", draft, "--store", store)
    assert code == 0 and "1 removed" in _flat(output) and "- reset-dup" in _flat(output)
    code, output = _invoke("suite", "diff", draft, draft, "--json")
    assert code == 0 and json.loads(output)["unchanged"] == 2

    code, output = _invoke(
        "suite", "approve", draft, "--store", store, "--approver", "qa",
        "--parent-version", "1.0.0",
    )  # fmt: skip
    assert code == 0, output
    code, output = _invoke("suite", "verify", "--store", store, "--json")
    assert code == 0 and [r["ok"] for r in json.loads(output)] == [True, True]

    stored = store / "support" / "1.0.0.json"
    stored.write_text(stored.read_text("utf-8").replace("reset link", "RESET"), "utf-8")
    code, output = _invoke("suite", "verify", "support@1.0.0", "--store", store)
    assert code == 6 and "changed after approval" in _flat(output)
    code, output = _invoke("suite", "export", "support@1.0.0", "--store", store, "--save", exported)
    assert code == 6 and "changed after approval" in _flat(output)


def test_store_errors(draft: Path, tmp_path: Path) -> None:
    store = tmp_path / "store"
    code, output = _invoke("suite", "verify", "--store", store)
    assert code == 6 and "No suite versions" in _flat(output)
    code, output = _invoke("suite", "verify", "--store", store, "--json")
    assert code == 6 and json.loads(output) == []
    code, output = _invoke("suite", "verify", "no-version", "--store", store)
    assert code == 6 and "NAME@VERSION" in _flat(output)
    code, output = _invoke(
        "suite", "export", "support@9", "--store", store, "--save", tmp_path / "x.json"
    )
    assert code == 6 and "not in the store" in _flat(output)
    _invoke("suite", "approve", draft, "--store", store, "--approver", "qa")
    _invoke("suite", "tag", draft, "--add", "changed")
    code, output = _invoke("suite", "approve", draft, "--store", store, "--approver", "qa")
    assert code == 6 and "already approved with different content" in _flat(output)


def test_exported_suite_runs_with_evaluate(draft: Path, tmp_path: Path) -> None:
    store = tmp_path / "store"
    _invoke("suite", "approve", draft, "--store", store, "--approver", "qa")
    exported = tmp_path / "suite.json"
    _invoke("suite", "export", "support@1.0.0", "--store", store, "--save", exported)
    samples = tmp_path / "samples.json"
    samples.write_text(
        json.dumps(
            {
                "samples": [
                    {"case_id": "refund", "output": "Your refund is on its way", "trace": {}},
                    {"case_id": "reset", "output": "We sent a reset link", "trace": {}},
                    {"case_id": "reset-dup", "output": "No idea", "trace": {}},
                ]
            }
        ),
        "utf-8",
    )
    report = tmp_path / "evaluation.json"
    code, output = _invoke("evaluate", exported, samples, "--save", report)
    assert code == 0, output
    summary = json.loads(report.read_text("utf-8"))["summary"]
    assert (summary["total_cases"], summary["passed_cases"]) == (3, 2)
