"""Suite editors: load, save, and change draft suites without leaving them invalid.

Every function returns a new `TestSuite`; inputs are never mutated. Suites
stay plain agentic-evals suites, so a draft can be evaluated at any point.
"""

import json
from collections import Counter
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import yaml
from agentic_evals import TestCase, TestSuite

from agenticlens.suites.models import (
    DOMAIN_KEY,
    REVIEW_NOTES_KEY,
    REVIEW_STATUS_KEY,
    REVIEWED_BY_KEY,
    SOURCE_KEY,
    SPLIT_KEY,
    CaseChange,
    ReviewStatus,
    SuiteDiff,
    SuiteSummary,
)

_REVIEW_STATUSES = ("needs_review", "accepted", "rejected")


def load_suite_file(path: Path) -> TestSuite:
    """Load a JSON or YAML suite (`.json` is JSON, anything else YAML)."""
    text = path.read_text(encoding="utf-8")
    data = json.loads(text) if path.suffix.lower() == ".json" else yaml.safe_load(text)
    return TestSuite.model_validate(data)


def suite_to_data(suite: TestSuite) -> dict[str, Any]:
    """Compact JSON-ready form: fields left at their defaults are omitted."""
    return suite.model_dump(mode="json", exclude_defaults=True)


def save_suite_file(suite: TestSuite, path: Path) -> None:
    """Save as YAML for `.yaml`/`.yml` paths and JSON otherwise."""
    path.parent.mkdir(parents=True, exist_ok=True)
    data = suite_to_data(suite)
    if path.suffix.lower() in {".yaml", ".yml"}:
        text = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
    else:
        text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    path.write_text(text, encoding="utf-8")


def _replace_cases(suite: TestSuite, cases: list[TestCase]) -> TestSuite:
    return TestSuite.model_validate({**suite.model_dump(mode="json"), "cases": cases})


def _case_index(suite: TestSuite, case_id: str) -> int:
    for index, case in enumerate(suite.cases):
        if case.id == case_id:
            return index
    raise KeyError(f"suite {suite.name!r} has no case {case_id!r}")


def _resolve_ids(suite: TestSuite, case_ids: Iterable[str] | None) -> set[str]:
    if case_ids is None:
        return {case.id for case in suite.cases}
    wanted = set(case_ids)
    missing = wanted - {case.id for case in suite.cases}
    if missing:
        raise KeyError(f"suite {suite.name!r} has no case(s): {', '.join(sorted(missing))}")
    return wanted


def new_suite(
    *, name: str, version: str, cases: list[TestCase], description: str = ""
) -> TestSuite:
    return TestSuite(name=name, version=version, description=description, cases=cases)


def add_case(suite: TestSuite, case: TestCase | dict[str, Any]) -> TestSuite:
    """Append a case; its ID must be new to the suite."""
    validated = case if isinstance(case, TestCase) else TestCase.model_validate(case)
    if any(existing.id == validated.id for existing in suite.cases):
        raise ValueError(f"suite {suite.name!r} already has case {validated.id!r}")
    return _replace_cases(suite, [*suite.cases, validated])


def update_case(suite: TestSuite, case_id: str, **changes: Any) -> TestSuite:
    """Change fields of one case. Changing `id` to an existing ID is rejected."""
    index = _case_index(suite, case_id)
    updated = TestCase.model_validate({**suite.cases[index].model_dump(mode="json"), **changes})
    cases = list(suite.cases)
    cases[index] = updated
    return _replace_cases(suite, cases)


def remove_cases(suite: TestSuite, case_ids: Iterable[str]) -> TestSuite:
    """Remove cases by ID. A suite must keep at least one case."""
    doomed = _resolve_ids(suite, list(case_ids))
    return _replace_cases(suite, [case for case in suite.cases if case.id not in doomed])


def tag_cases(
    suite: TestSuite,
    *,
    case_ids: Iterable[str] | None = None,
    add: Iterable[str] = (),
    remove: Iterable[str] = (),
    domain: str | None = None,
) -> TestSuite:
    """Add or remove tags and set the domain category on cases (all when `case_ids` is None)."""
    targets = _resolve_ids(suite, case_ids)
    added, removed = list(add), set(remove)
    cases: list[TestCase] = []
    for case in suite.cases:
        if case.id not in targets:
            cases.append(case)
            continue
        tags = [tag for tag in case.tags if tag not in removed]
        tags.extend(tag for tag in added if tag not in tags)
        metadata = dict(case.metadata)
        if domain is not None:
            metadata[DOMAIN_KEY] = domain
        cases.append(case.model_copy(update={"tags": tags, "metadata": metadata}))
    return _replace_cases(suite, cases)


def review_cases(
    suite: TestSuite,
    *,
    status: ReviewStatus,
    reviewer: str,
    case_ids: Iterable[str] | None = None,
    notes: str = "",
) -> TestSuite:
    """Record a review decision on cases (all when `case_ids` is None)."""
    if status not in _REVIEW_STATUSES:
        raise ValueError(f"review status must be one of {', '.join(_REVIEW_STATUSES)}")
    if not reviewer.strip():
        raise ValueError("reviewer must not be empty")
    targets = _resolve_ids(suite, case_ids)
    cases: list[TestCase] = []
    for case in suite.cases:
        if case.id in targets:
            metadata = {**case.metadata, REVIEW_STATUS_KEY: status, REVIEWED_BY_KEY: reviewer}
            if notes:
                metadata[REVIEW_NOTES_KEY] = notes
            else:
                metadata.pop(REVIEW_NOTES_KEY, None)
            case = case.model_copy(update={"metadata": metadata})
        cases.append(case)
    return _replace_cases(suite, cases)


def merge_suites(base: TestSuite, *others: TestSuite, on_conflict: str = "error") -> TestSuite:
    """Append the cases of `others` to `base`, keeping `base`'s name and version.

    `on_conflict` decides what happens to a case whose ID is already present:
    `error` (default), `skip` (keep the existing case), or `replace`.
    """
    if on_conflict not in {"error", "skip", "replace"}:
        raise ValueError("on_conflict must be error, skip, or replace")
    cases = {case.id: case for case in base.cases}
    for other in others:
        for case in other.cases:
            if case.id in cases:
                if on_conflict == "error":
                    raise ValueError(f"case {case.id!r} exists in both suites")
                if on_conflict == "skip":
                    continue
            cases[case.id] = case
    return _replace_cases(base, list(cases.values()))


def case_review_status(case: TestCase) -> str:
    """`accepted` for authored cases without a recorded review."""
    return str(case.metadata.get(REVIEW_STATUS_KEY, "accepted"))


def case_source_kind(case: TestCase) -> str:
    source = case.metadata.get(SOURCE_KEY)
    if isinstance(source, dict) and source.get("kind"):
        return str(source["kind"])
    return "authored"


def case_lineage(case: TestCase) -> str:
    """The original case a synthetic variation descends from (itself otherwise)."""
    source = case.metadata.get(SOURCE_KEY)
    if isinstance(source, dict) and source.get("parent_case_id"):
        return str(source["parent_case_id"])
    return case.id


def filter_suite(
    suite: TestSuite,
    *,
    tags: Iterable[str] = (),
    exclude_tags: Iterable[str] = (),
    domains: Iterable[str] = (),
    splits: Iterable[str] = (),
    review_statuses: Iterable[str] = (),
) -> TestSuite:
    """Keep cases matching every given filter (any value within one filter)."""
    wanted_tags, unwanted = set(tags), set(exclude_tags)
    wanted_domains, wanted_splits = set(domains), set(splits)
    wanted_reviews = set(review_statuses)
    kept = [
        case
        for case in suite.cases
        if (not wanted_tags or wanted_tags & set(case.tags))
        and not unwanted & set(case.tags)
        and (not wanted_domains or case.metadata.get(DOMAIN_KEY) in wanted_domains)
        and (not wanted_splits or case.metadata.get(SPLIT_KEY) in wanted_splits)
        and (not wanted_reviews or case_review_status(case) in wanted_reviews)
    ]
    if not kept:
        raise ValueError("no cases match the filter")
    return _replace_cases(suite, kept)


def summarize_suite(suite: TestSuite) -> SuiteSummary:
    def counts(values: Iterable[str]) -> dict[str, int]:
        return dict(sorted(Counter(values).items()))

    return SuiteSummary(
        name=suite.name,
        version=suite.version,
        total_cases=len(suite.cases),
        by_split=counts(str(case.metadata.get(SPLIT_KEY, "unassigned")) for case in suite.cases),
        by_domain=counts(
            str(case.metadata.get(DOMAIN_KEY, "uncategorized")) for case in suite.cases
        ),
        by_tag=counts(tag for case in suite.cases for tag in case.tags),
        by_source=counts(case_source_kind(case) for case in suite.cases),
        by_review_status=counts(case_review_status(case) for case in suite.cases),
    )


def diff_suites(old: TestSuite, new: TestSuite) -> SuiteDiff:
    """Cases added, removed, and changed (with the changed field names) between suites."""
    old_cases = {case.id: case.model_dump(mode="json") for case in old.cases}
    new_cases = {case.id: case.model_dump(mode="json") for case in new.cases}
    changed: list[CaseChange] = []
    for case_id in old_cases.keys() & new_cases.keys():
        before, after = old_cases[case_id], new_cases[case_id]
        fields = sorted(
            key for key in before.keys() | after.keys() if before.get(key) != after.get(key)
        )
        if fields:
            changed.append(CaseChange(case_id=case_id, fields=fields))
    return SuiteDiff(
        old=f"{old.name}@{old.version}",
        new=f"{new.name}@{new.version}",
        added=[case_id for case_id in new_cases if case_id not in old_cases],
        removed=[case_id for case_id in old_cases if case_id not in new_cases],
        changed=sorted(changed, key=lambda change: change.case_id),
        unchanged=len(old_cases.keys() & new_cases.keys()) - len(changed),
    )
