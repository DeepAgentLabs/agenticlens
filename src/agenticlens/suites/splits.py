"""Stable train/validation/test split assignment for suites.

Each case is placed by hashing its lineage (the original case for synthetic
variants) with the seed, so:

- a case keeps its split when other cases are added or removed, which keeps
  later suite versions from moving test cases into training data
- every variant lands in the same split as the case it came from

The cost of stability is that split sizes match the ratios only on average;
small suites can end up with an empty split, which callers should check.
"""

import hashlib

from agentic_evals import TestCase, TestSuite

from agenticlens.suites.editing import case_lineage
from agenticlens.suites.models import SPLIT_KEY


def _bucket(seed: int, lineage: str) -> float:
    digest = hashlib.sha256(f"{seed}:{lineage}".encode()).digest()
    return int.from_bytes(digest[:8], "big") / 2**64


def assign_splits(
    suite: TestSuite,
    *,
    train_ratio: float = 0.7,
    validation_ratio: float = 0.15,
    test_ratio: float = 0.15,
    seed: int = 0,
    overwrite: bool = False,
) -> TestSuite:
    """Write `metadata["split"]` on every case that has none (all when `overwrite`)."""
    ratios = (train_ratio, validation_ratio, test_ratio)
    if min(ratios) < 0:
        raise ValueError("split ratios must be non-negative")
    if abs(sum(ratios) - 1.0) > 1e-9:
        raise ValueError("split ratios must add up to 1.0")
    cases: list[TestCase] = []
    for case in suite.cases:
        if case.metadata.get(SPLIT_KEY) and not overwrite:
            cases.append(case)
            continue
        position = _bucket(seed, case_lineage(case))
        split = (
            "train"
            if position < train_ratio
            else "validation"
            if position < train_ratio + validation_ratio
            else "test"
        )
        cases.append(case.model_copy(update={"metadata": {**case.metadata, SPLIT_KEY: split}}))
    return TestSuite.model_validate({**suite.model_dump(mode="json"), "cases": cases})
