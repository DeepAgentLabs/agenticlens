"""Deterministic synthetic variations of test-case inputs.

Variations are surface perturbations (case, whitespace, punctuation, a typo,
a conversational prefix) applied to every string in a case's input. They test
robustness to how a request is typed, not to what it means: they are not
paraphrases, and nothing here calls a model. Each variant keeps its parent's
expectations, inherits its split so a variant of a test case never lands in
training data, and is marked `needs_review`.
"""

import random
import re
from collections.abc import Callable, Iterable
from typing import Any

from agentic_evals import TestCase, TestSuite

from agenticlens.suites.models import (
    REVIEW_NOTES_KEY,
    REVIEW_STATUS_KEY,
    REVIEWED_BY_KEY,
    SOURCE_KEY,
    CaseSource,
)

_PREFIXES = ("Hi, ", "Hello! ", "Quick question: ", "Please help: ", "Hey there, ")
_WORD = re.compile(r"[A-Za-z]{4,}")


def _lowercase(text: str, rng: random.Random) -> str:
    return text.lower()


def _uppercase(text: str, rng: random.Random) -> str:
    return text.upper()


def _whitespace(text: str, rng: random.Random) -> str:
    return "  " + re.sub(r" ", "  ", text.strip()) + " "


def _punctuation(text: str, rng: random.Random) -> str:
    return re.sub(r"[.,!?;:]", "", text)


def _typo(text: str, rng: random.Random) -> str:
    words = list(_WORD.finditer(text))
    if not words:
        return text
    match = words[rng.randrange(len(words))]
    word = match.group()
    position = rng.randrange(len(word) - 1)
    swapped = word[:position] + word[position + 1] + word[position] + word[position + 2 :]
    return text[: match.start()] + swapped + text[match.end() :]


def _prefix(text: str, rng: random.Random) -> str:
    return _PREFIXES[rng.randrange(len(_PREFIXES))] + text


VARIATIONS: dict[str, Callable[[str, random.Random], str]] = {
    "lowercase": _lowercase,
    "uppercase": _uppercase,
    "whitespace": _whitespace,
    "punctuation": _punctuation,
    "typo": _typo,
    "prefix": _prefix,
}


def _apply(value: Any, transform: Callable[[str, random.Random], str], rng: random.Random) -> Any:
    if isinstance(value, str):
        return transform(value, rng)
    if isinstance(value, dict):
        return {key: _apply(item, transform, rng) for key, item in value.items()}
    if isinstance(value, list):
        return [_apply(item, transform, rng) for item in value]
    return value


def vary_case(case: TestCase, kind: str, *, seed: int = 0) -> TestCase | None:
    """One variant of `case`, or None when the variation leaves the input unchanged."""
    if kind not in VARIATIONS:
        raise ValueError(f"unknown variation {kind!r}; choose from {', '.join(VARIATIONS)}")
    rng = random.Random(f"{seed}:{case.id}:{kind}")
    varied = _apply(case.input, VARIATIONS[kind], rng)
    if varied == case.input:
        return None
    metadata = {
        key: value
        for key, value in case.metadata.items()
        if key not in {REVIEWED_BY_KEY, REVIEW_NOTES_KEY}
    }
    metadata[SOURCE_KEY] = CaseSource(
        kind="synthetic", parent_case_id=case.id, variation=kind, seed=seed
    ).model_dump(exclude_none=True)
    metadata[REVIEW_STATUS_KEY] = "needs_review"
    tags = list(dict.fromkeys([*case.tags, "synthetic", f"variation:{kind}"]))
    return case.model_copy(
        update={
            "id": f"{case.id}--{kind}",
            "name": f"{case.name} ({kind})",
            "input": varied,
            "tags": tags,
            "metadata": metadata,
        },
        deep=True,
    )


def generate_variations(
    suite: TestSuite,
    *,
    per_case: int = 2,
    kinds: Iterable[str] | None = None,
    seed: int = 0,
    include_synthetic: bool = False,
) -> list[TestCase]:
    """New variants so each original has up to `per_case`, chosen reproducibly from `kinds`.

    Variants already in the suite count toward `per_case`, so running this
    again on its own output adds nothing. Variants of variants are not
    generated unless `include_synthetic` is set.
    """
    if per_case < 1:
        raise ValueError("per_case must be at least 1")
    allowed = list(kinds) if kinds is not None else list(VARIATIONS)
    for kind in allowed:
        if kind not in VARIATIONS:
            raise ValueError(f"unknown variation {kind!r}; choose from {', '.join(VARIATIONS)}")
    existing = {case.id for case in suite.cases}
    have: dict[str, int] = {}
    for case in suite.cases:
        source = case.metadata.get(SOURCE_KEY)
        if isinstance(source, dict) and source.get("kind") == "synthetic":
            parent = str(source.get("parent_case_id"))
            have[parent] = have.get(parent, 0) + 1
    variants: list[TestCase] = []
    for case in suite.cases:
        source = case.metadata.get(SOURCE_KEY)
        if not include_synthetic and isinstance(source, dict) and source.get("kind") == "synthetic":
            continue
        order = list(allowed)
        random.Random(f"{seed}:{case.id}").shuffle(order)
        made = have.get(case.id, 0)
        for kind in order:
            if made >= per_case:
                break
            variant = vary_case(case, kind, seed=seed)
            if variant is None or variant.id in existing:
                continue
            existing.add(variant.id)
            variants.append(variant)
            made += 1
    return variants
