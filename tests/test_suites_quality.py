"""Synthetic variations, duplicate detection, and stable splits."""

import pytest
from agentic_evals import TestCase as EvalCase
from agentic_evals import TestSuite as EvalSuite

from agenticlens.suites import (
    VARIATIONS,
    assign_splits,
    drop_duplicates,
    find_duplicates,
    generate_variations,
    merge_suites,
    new_suite,
    normalize_input,
    vary_case,
)


def _case(case_id: str, text: object, **extra: object) -> EvalCase:
    return EvalCase.model_validate(
        {"id": case_id, "name": case_id, "input": text, "expected_contains": ["ok"], **extra}
    )


def _suite(*cases: EvalCase) -> EvalSuite:
    return new_suite(name="s", version="1", cases=list(cases))


@pytest.mark.parametrize("kind", sorted(VARIATIONS))
def test_each_variation_changes_text_and_records_lineage(kind: str) -> None:
    parent = _case(
        "q1",
        {"question": "Where is my parcel, please?", "n": 3},
        metadata={"split": "test", "reviewed_by": "qa", "domain": "shipping"},
        tags=["smoke"],
    )
    variant = vary_case(parent, kind, seed=1)
    assert variant is not None
    assert variant.id == f"q1--{kind}"
    assert variant.input["question"] != parent.input["question"]
    assert variant.input["n"] == 3
    assert variant.expected_contains == parent.expected_contains
    assert variant.metadata["split"] == "test"  # never leaks into another split
    assert variant.metadata["domain"] == "shipping"
    assert "reviewed_by" not in variant.metadata
    assert variant.metadata["review_status"] == "needs_review"
    assert variant.metadata["source"] == {
        "kind": "synthetic",
        "parent_case_id": "q1",
        "variation": kind,
        "seed": 1,
    }
    assert variant.tags == ["smoke", "synthetic", f"variation:{kind}"]
    assert vary_case(parent, kind, seed=1) == variant  # deterministic


def test_vary_case_returns_none_when_unchanged_and_rejects_unknown() -> None:
    assert vary_case(_case("n", 42), "typo") is None
    assert vary_case(_case("l", "already lower"), "lowercase") is None
    with pytest.raises(ValueError, match="unknown variation"):
        vary_case(_case("x", "text"), "paraphrase")


def test_generate_variations_limits_and_skips_synthetic() -> None:
    suite = _suite(_case("a", "Reset my password now."), _case("b", "Cancel my order today!"))
    variants = generate_variations(suite, per_case=2, seed=3)
    assert len(variants) == 4
    assert {v.metadata["source"]["parent_case_id"] for v in variants} == {"a", "b"}
    assert generate_variations(suite, per_case=2, seed=3) == variants
    extended = merge_suites(suite, _suite(*variants))
    again = generate_variations(extended, per_case=2, seed=3)
    assert again == []  # existing variant IDs skipped, variants not re-varied
    only_upper = generate_variations(suite, kinds=["uppercase"], per_case=3)
    assert [v.id for v in only_upper] == ["a--uppercase", "b--uppercase"]
    with pytest.raises(ValueError, match="per_case"):
        generate_variations(suite, per_case=0)
    with pytest.raises(ValueError, match="unknown variation"):
        generate_variations(suite, kinds=["nope"])


def test_normalize_input() -> None:
    assert normalize_input("  Hello,   WORLD! ") == "hello world"
    assert normalize_input({"b": 1, "a": "X"}) == normalize_input({"a": "X", "b": 1})


def test_find_duplicates_exact_near_and_conflicting() -> None:
    suite = _suite(
        _case("a", "How do I reset my password?"),
        _case("b", "how do i reset my password"),
        _case("c", "How do I reset my password?", expected_output="different"),
        _case("d", "Where is my refund for order 1234 placed last week?"),
        _case("e", "Where is my refund for order 1234 placed last week"),
        _case("f", "Completely unrelated question about shipping times"),
    )
    report = find_duplicates(suite)
    groups = {tuple(group.case_ids): group for group in report.groups}
    assert set(groups) == {("a", "b", "c"), ("d", "e")}
    assert groups[("a", "b", "c")].kind == "exact"
    assert groups[("a", "b", "c")].conflicting is True
    assert groups[("d", "e")].conflicting is False
    assert report.duplicate_case_ids == ["b", "c", "e"]
    assert report.conflicting_groups == 1
    deduped = drop_duplicates(suite, report)
    assert [case.id for case in deduped.cases] == ["a", "d", "f"]


def test_find_duplicates_near_threshold_and_variants() -> None:
    a = _case("a", "please refund my last order from the shop")
    b = _case("b", "please refund my last order from the store")
    assert find_duplicates(_suite(a, b), threshold=0.6).groups[0].kind == "near"
    assert find_duplicates(_suite(a, b), threshold=0.95).groups == []
    variant = vary_case(a, "lowercase")
    assert variant is None  # already lower case
    variant = vary_case(a, "prefix")
    assert variant is not None
    suite = _suite(a, variant)
    assert find_duplicates(suite, threshold=0.5).groups == []
    assert len(find_duplicates(suite, threshold=0.5, include_variants=True).groups) == 1
    assert drop_duplicates(suite, find_duplicates(suite)) is suite
    with pytest.raises(ValueError, match="threshold"):
        find_duplicates(suite, threshold=0)


def test_assign_splits_is_stable_and_lineage_aware() -> None:
    cases = [_case(f"case-{index}", f"question number {index}") for index in range(60)]
    suite = _suite(*cases)
    split = assign_splits(suite, seed=7)
    by_id = {case.id: case.metadata["split"] for case in split.cases}
    assert set(by_id.values()) == {"train", "validation", "test"}
    # Adding cases never moves existing ones.
    grown = assign_splits(merge_suites(suite, _suite(_case("new", "brand new question"))), seed=7)
    assert all(by_id[c.id] == c.metadata["split"] for c in grown.cases if c.id != "new")
    # Variants of a case land in the same split even without inheriting it.
    variant = vary_case(cases[0], "uppercase")
    assert variant is not None
    with_variant = assign_splits(merge_suites(suite, _suite(variant)), seed=7)
    assert with_variant.cases[-1].metadata["split"] == by_id["case-0"]


def test_assign_splits_preserves_existing_unless_overwrite() -> None:
    suite = _suite(_case("a", "x", metadata={"split": "test"}), _case("b", "y"))
    kept = assign_splits(suite, train_ratio=1.0, validation_ratio=0.0, test_ratio=0.0)
    assert [c.metadata["split"] for c in kept.cases] == ["test", "train"]
    forced = assign_splits(
        suite, train_ratio=1.0, validation_ratio=0.0, test_ratio=0.0, overwrite=True
    )
    assert [c.metadata["split"] for c in forced.cases] == ["train", "train"]


@pytest.mark.parametrize(
    ("ratios", "message"),
    [((0.5, 0.5, 0.5), "add up"), ((1.2, -0.1, -0.1), "non-negative")],
)
def test_assign_splits_validates_ratios(ratios: tuple[float, float, float], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        assign_splits(
            _suite(_case("a", "x")),
            train_ratio=ratios[0],
            validation_ratio=ratios[1],
            test_ratio=ratios[2],
        )


def test_variations_leave_masked_values_alone() -> None:
    from agenticlens.suites import mask_suite

    case = _case("acct", {"question": "Cancel my plan", "account_email": "ana@example.org"})
    masked, _ = mask_suite(_suite(case))
    for kind in ("prefix", "uppercase", "typo", "whitespace"):
        variant = vary_case(masked.cases[0], kind)
        assert variant is not None
        assert variant.input["account_email"] == "[SENSITIVE_FIELD]"


def test_masked_values_with_added_text_are_not_reported_again() -> None:
    from agenticlens.suites import PIIMasker

    masked, found = PIIMasker().mask_value({"email": "Hello! [SENSITIVE_FIELD]"})
    assert masked == {"email": "Hello! [SENSITIVE_FIELD]"} and found == []
