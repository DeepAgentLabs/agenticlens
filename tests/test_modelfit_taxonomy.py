"""Task taxonomy resolution: tags, domains, case IDs, derived and overall categories."""

from agenticlens.modelfit import ModelFitConfig, TaskCategory, derive_categories, resolve_taxonomy
from agenticlens.modelfit.evidence import CaseEvidence


def _cases() -> dict[str, CaseEvidence]:
    return {
        "p1": CaseEvidence("p1", tags=["policy"], domain="billing"),
        "p2": CaseEvidence("p2", tags=["policy", "safety"]),
        "o1": CaseEvidence("o1", tags=["orders"]),
        "x1": CaseEvidence("x1"),
    }


def test_categories_are_derived_from_case_tags_when_none_are_configured() -> None:
    categories = derive_categories(_cases())
    assert [(c.id, c.tags) for c in categories] == [
        ("orders", ["orders"]),
        ("policy", ["policy"]),
        ("safety", ["safety"]),
    ]


def test_derived_category_ids_are_sanitised() -> None:
    cases = {"a": CaseEvidence("a", tags=["needs review", "_x", "needs-review"])}
    assert [(c.id, c.name) for c in derive_categories(cases)] == [
        ("x", "_x"),
        ("needs-review", "needs review"),
        ("needs-review-2", "needs-review"),
    ]


def test_a_tag_named_all_does_not_collide_with_the_overall_category() -> None:
    cases = {"a": CaseEvidence("a", tags=["all"])}
    resolved, _, _ = resolve_taxonomy(ModelFitConfig(), cases)
    assert [c.id for c, _ in resolved] == ["all", "all-2"]


def test_cases_match_by_tag_domain_or_id_and_may_belong_to_several() -> None:
    config = ModelFitConfig(
        include_overall=False,
        categories=[
            TaskCategory(id="billing", domains=["billing"]),
            TaskCategory(id="sensitive", tags=["safety"], case_ids=["o1"]),
        ],
    )
    resolved, uncategorized, warnings = resolve_taxonomy(config, _cases())

    assert [(c.id, ids) for c, ids in resolved] == [
        ("billing", ["p1"]),
        ("sensitive", ["p2", "o1"]),
    ]
    assert uncategorized == ["x1"]
    assert warnings == []


def test_overall_category_comes_first_and_covers_every_case() -> None:
    resolved, uncategorized, _ = resolve_taxonomy(ModelFitConfig(), _cases())

    assert resolved[0][0].id == "all"
    assert resolved[0][1] == ["p1", "p2", "o1", "x1"]
    assert uncategorized == ["x1"]


def test_unknown_case_ids_and_empty_categories_are_warned() -> None:
    config = ModelFitConfig(
        categories=[
            TaskCategory(id="ghosts", case_ids=["missing"]),
        ]
    )
    _, _, warnings = resolve_taxonomy(config, _cases())

    assert any("lists case IDs no experiment ran: missing" in w for w in warnings)
    assert any("'ghosts' matches no cases" in w for w in warnings)


def test_no_tags_and_no_categories_is_warned() -> None:
    cases = {"x1": CaseEvidence("x1")}
    resolved, uncategorized, warnings = resolve_taxonomy(ModelFitConfig(), cases)

    assert [c.id for c, _ in resolved] == ["all"]
    assert uncategorized == ["x1"]
    assert any("no case carries a tag" in w for w in warnings)


def test_non_ascii_tags_derive_valid_ascii_ids() -> None:
    cases = {"a": CaseEvidence("a", tags=["café", "日本"])}
    assert [(c.id, c.name) for c in derive_categories(cases)] == [
        ("caf-", "café"),
        ("tag", "日本"),
    ]
