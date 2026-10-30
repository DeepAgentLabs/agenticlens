"""Duplicate and near-duplicate detection over case inputs.

Inputs are normalised (case-folded, punctuation dropped, whitespace
collapsed; structured inputs are compared as canonical JSON). Exact
duplicates share a normalised input. Near duplicates have a Jaccard
similarity of word unigrams and bigrams at or above the threshold. Groups
are formed transitively. A group is `conflicting` when its cases expect
different results for the same input, which usually means a labeling error.

Synthetic variants of the same original are near-duplicates by design and
are ignored unless `include_variants` is set. Comparison is pairwise
(quadratic in suite size); it is meant for suites of thousands of cases.
"""

import json
import re
from typing import Any

from agentic_evals import TestCase, TestSuite

from agenticlens.suites.editing import case_lineage, remove_cases
from agenticlens.suites.models import DuplicateGroup, DuplicateReport

_NON_WORD = re.compile(r"[^\w\s]")
_SPACE = re.compile(r"\s+")
_EXPECTATION_FIELDS = (
    "expected_output",
    "expected_contains",
    "output_json_schema",
    "required_output_fields",
    "required_tools",
    "forbidden_tools",
    "required_tool_arguments",
    "expected_tool_arguments",
    "required_tool_order",
)


def normalize_input(value: Any) -> str:
    text = value if isinstance(value, str) else json.dumps(value, sort_keys=True, default=str)
    return _SPACE.sub(" ", _NON_WORD.sub(" ", text.casefold())).strip()


def _shingles(text: str) -> frozenset[str]:
    words = text.split()
    return frozenset(words + [f"{a} {b}" for a, b in zip(words, words[1:], strict=False)])


def _jaccard(left: frozenset[str], right: frozenset[str]) -> float:
    if not left and not right:
        return 1.0
    return len(left & right) / len(left | right)


def _expectations(case: TestCase) -> str:
    data = case.model_dump(mode="json", include=set(_EXPECTATION_FIELDS))
    return json.dumps(data, sort_keys=True)


def _has_conflict(indices: list[int], normalized: list[str], cases: list[TestCase]) -> bool:
    """True when cases with the same normalised input expect different results.

    Near duplicates with distinct inputs may legitimately expect different
    results, so they never conflict.
    """
    by_input: dict[str, set[str]] = {}
    for index in indices:
        by_input.setdefault(normalized[index], set()).add(_expectations(cases[index]))
    return any(len(expectations) > 1 for expectations in by_input.values())


def find_duplicates(
    suite: TestSuite, *, threshold: float = 0.85, include_variants: bool = False
) -> DuplicateReport:
    if not 0 < threshold <= 1:
        raise ValueError("threshold must be in (0, 1]")
    cases = suite.cases
    normalized = [normalize_input(case.input) for case in cases]
    shingles = [_shingles(text) for text in normalized]
    lineage = [case_lineage(case) for case in cases]

    parent = list(range(len(cases)))

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    pair_similarity: dict[tuple[int, int], float] = {}
    for i in range(len(cases)):
        for j in range(i + 1, len(cases)):
            if not include_variants and lineage[i] == lineage[j]:
                continue
            similarity = (
                1.0 if normalized[i] == normalized[j] else _jaccard(shingles[i], shingles[j])
            )
            if similarity >= threshold:
                pair_similarity[(i, j)] = similarity
                root_i, root_j = find(i), find(j)
                if root_i != root_j:
                    parent[max(root_i, root_j)] = min(root_i, root_j)

    members: dict[int, list[int]] = {}
    for index in range(len(cases)):
        members.setdefault(find(index), []).append(index)

    groups: list[DuplicateGroup] = []
    for indices in members.values():
        if len(indices) < 2:
            continue
        similarities = [
            value for (i, j), value in pair_similarity.items() if i in indices and j in indices
        ]
        exact = len({normalized[index] for index in indices}) == 1
        groups.append(
            DuplicateGroup(
                kind="exact" if exact else "near",
                case_ids=[cases[index].id for index in indices],
                keep=cases[indices[0]].id,
                similarity=round(min(similarities), 6),
                conflicting=_has_conflict(indices, normalized, cases),
            )
        )
    return DuplicateReport(
        suite_name=suite.name,
        threshold=threshold,
        total_cases=len(cases),
        groups=groups,
        duplicate_case_ids=[case_id for group in groups for case_id in group.case_ids[1:]],
        conflicting_groups=sum(1 for group in groups if group.conflicting),
    )


def drop_duplicates(suite: TestSuite, report: DuplicateReport) -> TestSuite:
    """Remove every grouped case except the first of each group."""
    if not report.duplicate_case_ids:
        return suite
    return remove_cases(suite, report.duplicate_case_ids)
