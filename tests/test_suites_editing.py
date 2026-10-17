"""Suite editors: add, update, remove, tag, review, merge, filter, summarize, diff."""

from pathlib import Path

import pytest
from agentic_evals import TestCase as EvalCase
from agentic_evals import TestSuite as EvalSuite

from agenticlens.suites import (
    add_case,
    case_lineage,
    case_review_status,
    case_source_kind,
    diff_suites,
    filter_suite,
    load_suite_file,
    merge_suites,
    new_suite,
    remove_cases,
    review_cases,
    save_suite_file,
    summarize_suite,
    tag_cases,
    update_case,
)


def _case(case_id: str, text: str = "hello", **extra: object) -> EvalCase:
    return EvalCase.model_validate(
        {"id": case_id, "name": case_id, "input": text, "expected_contains": ["hi"], **extra}
    )


@pytest.fixture
def suite() -> EvalSuite:
    return new_suite(name="support", version="1.0.0", cases=[_case("a"), _case("b")])


def test_add_case_rejects_duplicate_ids_and_keeps_original(suite: EvalSuite) -> None:
    added = add_case(suite, {"id": "c", "name": "c", "expected_output": "x"})
    assert [case.id for case in added.cases] == ["a", "b", "c"]
    assert [case.id for case in suite.cases] == ["a", "b"]
    with pytest.raises(ValueError, match="already has case 'a'"):
        add_case(suite, _case("a"))


def test_add_case_requires_an_expectation(suite: EvalSuite) -> None:
    with pytest.raises(ValueError, match="at least one expectation"):
        add_case(suite, {"id": "c", "name": "c"})


def test_update_case_changes_fields(suite: EvalSuite) -> None:
    updated = update_case(suite, "a", expected_output="hi there")
    assert updated.cases[0].expected_output == "hi there"
    with pytest.raises(KeyError):
        update_case(suite, "missing", expected_output="x")


def test_remove_cases_keeps_at_least_one(suite: EvalSuite) -> None:
    assert [case.id for case in remove_cases(suite, ["a"]).cases] == ["b"]
    with pytest.raises(ValueError, match="at least one case"):
        remove_cases(suite, ["a", "b"])
    with pytest.raises(KeyError, match="no case"):
        remove_cases(suite, ["zzz"])


def test_tag_cases_adds_removes_and_sets_domain(suite: EvalSuite) -> None:
    tagged = tag_cases(suite, case_ids=["a"], add=["smoke", "billing"], domain="billing")
    assert tagged.cases[0].tags == ["smoke", "billing"]
    assert tagged.cases[0].metadata["domain"] == "billing"
    assert tagged.cases[1].tags == []
    untagged = tag_cases(tagged, remove=["smoke"])
    assert untagged.cases[0].tags == ["billing"]


def test_review_cases_records_reviewer_and_rejects_bad_status(suite: EvalSuite) -> None:
    reviewed = review_cases(suite, status="rejected", reviewer="qa", case_ids=["b"], notes="off")
    assert case_review_status(reviewed.cases[0]) == "accepted"
    assert reviewed.cases[1].metadata["review_status"] == "rejected"
    assert reviewed.cases[1].metadata["reviewed_by"] == "qa"
    assert reviewed.cases[1].metadata["review_notes"] == "off"
    again = review_cases(reviewed, status="accepted", reviewer="qa", case_ids=["b"])
    assert "review_notes" not in again.cases[1].metadata
    with pytest.raises(ValueError, match="review status"):
        review_cases(suite, status="maybe", reviewer="qa")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="reviewer"):
        review_cases(suite, status="accepted", reviewer=" ")


def test_merge_suites_conflict_modes(suite: EvalSuite) -> None:
    other = new_suite(name="x", version="9", cases=[_case("b", "changed"), _case("c")])
    with pytest.raises(ValueError, match="exists in both"):
        merge_suites(suite, other)
    skipped = merge_suites(suite, other, on_conflict="skip")
    assert [case.input for case in skipped.cases] == ["hello", "hello", "hello"]
    replaced = merge_suites(suite, other, on_conflict="replace")
    assert replaced.cases[1].input == "changed"
    assert (replaced.name, replaced.version) == ("support", "1.0.0")
    with pytest.raises(ValueError, match="on_conflict"):
        merge_suites(suite, other, on_conflict="merge")


def test_filter_suite_combines_filters(suite: EvalSuite) -> None:
    tagged = tag_cases(suite, case_ids=["a"], add=["smoke"], domain="billing")
    tagged = update_case(tagged, "b", metadata={"split": "test", "domain": "account"})
    assert [c.id for c in filter_suite(tagged, tags=["smoke"]).cases] == ["a"]
    assert [c.id for c in filter_suite(tagged, splits=["test"]).cases] == ["b"]
    assert [c.id for c in filter_suite(tagged, exclude_tags=["smoke"]).cases] == ["b"]
    assert [c.id for c in filter_suite(tagged, domains=["billing", "account"]).cases] == ["a", "b"]
    assert [c.id for c in filter_suite(tagged, review_statuses=["accepted"]).cases] == ["a", "b"]
    with pytest.raises(ValueError, match="no cases match"):
        filter_suite(tagged, tags=["smoke"], splits=["test"])


def test_summarize_suite_counts_metadata(suite: EvalSuite) -> None:
    edited = tag_cases(suite, case_ids=["a"], add=["smoke"], domain="billing")
    edited = update_case(
        edited,
        "b",
        metadata={"split": "test", "source": {"kind": "trace"}, "review_status": "needs_review"},
    )
    summary = summarize_suite(edited)
    assert summary.total_cases == 2
    assert summary.by_split == {"test": 1, "unassigned": 1}
    assert summary.by_domain == {"billing": 1, "uncategorized": 1}
    assert summary.by_source == {"authored": 1, "trace": 1}
    assert summary.by_review_status == {"accepted": 1, "needs_review": 1}
    assert summary.by_tag == {"smoke": 1}


def test_lineage_and_source_helpers() -> None:
    variant = _case("a--typo", metadata={"source": {"kind": "synthetic", "parent_case_id": "a"}})
    assert case_lineage(variant) == "a"
    assert case_source_kind(variant) == "synthetic"
    assert case_lineage(_case("a")) == "a"
    assert case_source_kind(_case("a")) == "authored"


def test_diff_suites_lists_added_removed_changed(suite: EvalSuite) -> None:
    newer = update_case(suite, "a", expected_output="x")
    newer = remove_cases(add_case(newer, _case("c")), ["b"])
    newer = newer.model_copy(update={"version": "1.1.0"})
    diff = diff_suites(suite, newer)
    assert (diff.old, diff.new) == ("support@1.0.0", "support@1.1.0")
    assert diff.added == ["c"] and diff.removed == ["b"]
    assert [(c.case_id, c.fields) for c in diff.changed] == [("a", ["expected_output"])]
    assert diff.unchanged == 0 and not diff.is_empty
    assert diff_suites(suite, suite).is_empty


@pytest.mark.parametrize("suffix", [".json", ".yaml", ".yml"])
def test_save_and_load_round_trip(tmp_path: Path, suite: EvalSuite, suffix: str) -> None:
    path = tmp_path / f"suite{suffix}"
    save_suite_file(suite, path)
    assert load_suite_file(path) == suite
    text = path.read_text("utf-8")
    assert "threshold" not in text  # defaults omitted in drafts
