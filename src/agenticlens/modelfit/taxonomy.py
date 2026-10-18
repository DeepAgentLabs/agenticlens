"""Task taxonomy: which suite cases belong to which task category."""

from collections.abc import Iterable

from agenticlens.modelfit.evidence import CandidateEvidence, CaseEvidence
from agenticlens.modelfit.models import OVERALL_CATEGORY_ID, ModelFitConfig, TaskCategory


def case_index(candidates: list[CandidateEvidence]) -> dict[str, CaseEvidence]:
    """Every case seen by any candidate, with the first tags and domain recorded for it."""
    index: dict[str, CaseEvidence] = {}
    for candidate in candidates:
        for case_id, case in candidate.cases.items():
            known = index.get(case_id)
            if known is None:
                index[case_id] = CaseEvidence(case_id=case_id, tags=case.tags, domain=case.domain)
                continue
            if not known.tags and case.tags:
                known.tags = case.tags
            if known.domain is None and case.domain is not None:
                known.domain = case.domain
    return index


def matches(category: TaskCategory, case: CaseEvidence) -> bool:
    if category.id == OVERALL_CATEGORY_ID and not (
        category.tags or category.domains or category.case_ids
    ):
        return True
    return (
        case.case_id in category.case_ids
        or any(tag in category.tags for tag in case.tags)
        or (case.domain is not None and case.domain in category.domains)
    )


def derive_categories(
    cases: dict[str, CaseEvidence], reserved: Iterable[str] = ()
) -> list[TaskCategory]:
    """One category per distinct case tag, in alphabetical order.

    IDs that sanitise to one already taken (or `reserved`) get a numeric suffix.
    """
    tags = sorted({tag for case in cases.values() for tag in case.tags})
    categories: list[TaskCategory] = []
    used: set[str] = set(reserved)
    for tag in tags:
        base = _category_id(tag)
        category_id = base
        suffix = 2
        while category_id in used:
            category_id = f"{base}-{suffix}"
            suffix += 1
        used.add(category_id)
        categories.append(TaskCategory(id=category_id, name=tag, tags=[tag]))
    return categories


def _category_id(tag: str) -> str:
    cleaned = "".join(char if char.isalnum() or char in "_.:-" else "-" for char in tag)
    cleaned = cleaned.lstrip("_.:-") or "tag"
    return cleaned


def resolve_taxonomy(
    config: ModelFitConfig, cases: dict[str, CaseEvidence]
) -> tuple[list[tuple[TaskCategory, list[str]]], list[str], list[str]]:
    """Return (category, case IDs) pairs, uncategorized case IDs, and warnings.

    The `all` category, when enabled, is listed first and does not count
    towards uncategorized cases.
    """
    reserved = {OVERALL_CATEGORY_ID} if config.include_overall else set()
    categories = list(config.categories) or derive_categories(cases, reserved)
    warnings: list[str] = []
    if not config.categories and not categories:
        warnings.append("No task categories were configured and no case carries a tag.")
    resolved: list[tuple[TaskCategory, list[str]]] = []
    categorized: set[str] = set()
    for category in categories:
        case_ids = [case_id for case_id, case in cases.items() if matches(category, case)]
        unknown = sorted(set(category.case_ids) - set(cases))
        if unknown:
            warnings.append(
                f"Category {category.id!r} lists case IDs no experiment ran: {', '.join(unknown)}"
            )
        if not case_ids:
            warnings.append(f"Category {category.id!r} matches no cases.")
        categorized.update(case_ids)
        resolved.append((category, case_ids))
    uncategorized = [case_id for case_id in cases if case_id not in categorized]
    if config.include_overall:
        overall = TaskCategory(
            id=OVERALL_CATEGORY_ID,
            name="All tasks",
            description="Every case in the experiment suites.",
        )
        resolved.insert(0, (overall, list(cases)))
    return resolved, uncategorized, warnings
