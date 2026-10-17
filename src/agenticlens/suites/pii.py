"""PII detection and masking for test cases, applied before a suite is stored.

Detected in text: email addresses, phone numbers (7-15 digits), payment card
numbers (Luhn-checked), US social security numbers, IPv4 addresses, and
secrets (bearer tokens and `sk-`/`ghp_`-style API keys). Values under keys
that name secrets or personal fields (password, token, email, phone, ssn,
address, date_of_birth, ...) are masked whole.

Strategies:

- `redact` replaces a value with its type, e.g. `[EMAIL]`
- `hash` replaces it with its type and a salted SHA-256 prefix, e.g.
  `[EMAIL:3f2a9c1e]`, so equal values stay equal (useful for duplicate
  detection) without storing them

Pattern detection is a safeguard, not a guarantee: names, street addresses in
free text, and locale-specific identifiers are not detected. Reports list
where and what kind of value was masked, never the value itself.
"""

import hashlib
import re
from collections import Counter
from collections.abc import Callable, Iterable
from typing import Any

from agentic_evals import TestCase, TestSuite

from agenticlens.suites.models import (
    MaskedLocation,
    MaskingReport,
    MaskingStrategy,
    PIIType,
)

_EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
_BEARER = re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{8,}", re.IGNORECASE)
_API_KEY = re.compile(r"\b(?:sk|pk|rk)-[A-Za-z0-9_-]{16,}\b|\bgh[pousr]_[A-Za-z0-9]{20,}\b")
_SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_CARD = re.compile(r"(?<![\d-])\d(?:[ -]?\d){12,18}(?![\d-])")
_IPV4 = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
# Not inside identifiers: UUID segments such as 1234-5678 are not phone numbers.
_PHONE = re.compile(r"(?<![\w+])(?<!\w-)\+?\(?\d[\d ().-]{5,}\d(?!\w|-\w)")

DEFAULT_SENSITIVE_KEYS = (
    "password",
    "passwd",
    "secret",
    "token",
    "api_key",
    "apikey",
    "authorization",
    "cookie",
    "email",
    "phone",
    "ssn",
    "social_security",
    "address",
    "date_of_birth",
    "dob",
    "credit_card",
    "card_number",
    "iban",
)

# Placeholders this module writes; never re-detected as PII.
_PLACEHOLDER = re.compile(r"\[[A-Z_]+(?::[0-9a-f]{8})?\]")


def _luhn(digits: str) -> bool:
    total = 0
    for index, char in enumerate(reversed(digits)):
        value = int(char)
        if index % 2 == 1:
            value *= 2
            if value > 9:
                value -= 9
        total += value
    return total % 10 == 0


def _valid_card(match: str) -> bool:
    digits = re.sub(r"\D", "", match)
    return 13 <= len(digits) <= 19 and _luhn(digits)


def _valid_ipv4(match: str) -> bool:
    return all(int(part) <= 255 for part in match.split("."))


def _valid_phone(match: str) -> bool:
    digits = re.sub(r"\D", "", match)
    if not 7 <= len(digits) <= 15:
        return False
    # Dates and plain decimals are not phone numbers.
    return not re.fullmatch(r"\d{4}-\d{2}-\d{2}|\d+\.\d+", match.strip())


# Order matters: more specific patterns run first.
_DETECTORS: tuple[tuple[PIIType, re.Pattern[str], Callable[[str], bool] | None], ...] = (
    ("secret", _BEARER, None),
    ("secret", _API_KEY, None),
    ("email", _EMAIL, None),
    ("us_ssn", _SSN, None),
    ("credit_card", _CARD, _valid_card),
    ("ipv4", _IPV4, _valid_ipv4),
    ("phone", _PHONE, _valid_phone),
)


class PIIMasker:
    """Masks PII in strings and nested JSON-like values."""

    def __init__(
        self,
        *,
        strategy: MaskingStrategy = "redact",
        salt: str = "",
        sensitive_keys: Iterable[str] = DEFAULT_SENSITIVE_KEYS,
    ) -> None:
        if strategy not in ("redact", "hash"):
            raise ValueError("strategy must be 'redact' or 'hash'")
        self.strategy: MaskingStrategy = strategy
        self.salt = salt
        keys = sorted({key.lower() for key in sensitive_keys}, key=len, reverse=True)
        # Whole words of snake/kebab/dotted keys: `customer_email` matches, `input_tokens` does not.
        self._sensitive_key = (
            re.compile(
                r"(?:^|[_\-.\s])(?:"
                + "|".join(re.escape(key) for key in keys)
                + r")(?:$|[_\-.\s])",
                re.IGNORECASE,
            )
            if keys
            else None
        )

    def placeholder(self, pii_type: PIIType, value: str) -> str:
        label = pii_type.upper()
        if self.strategy == "redact":
            return f"[{label}]"
        digest = hashlib.sha256(f"{self.salt}\x00{value}".encode()).hexdigest()[:8]
        return f"[{label}:{digest}]"

    def mask_text(self, text: str) -> tuple[str, list[PIIType]]:
        """Masked text and the type of each value masked, in detection order."""
        found: list[PIIType] = []
        for pii_type, pattern, validate in _DETECTORS:

            def replace(
                match: re.Match[str],
                pii_type: PIIType = pii_type,
                validate: Callable[[str], bool] | None = validate,
            ) -> str:
                value = match.group()
                if _PLACEHOLDER.fullmatch(value) or (validate and not validate(value)):
                    return value
                found.append(pii_type)
                return self.placeholder(pii_type, value)

            text = pattern.sub(replace, text)
        return text, found

    def is_sensitive_key(self, key: str) -> bool:
        return bool(self._sensitive_key and self._sensitive_key.search(key))

    def mask_value(self, value: Any, path: str = "") -> tuple[Any, list[tuple[str, PIIType]]]:
        """Masked copy of `value` and the (path, type) of each masked value."""
        if isinstance(value, str):
            masked, types = self.mask_text(value)
            return masked, [(path, pii_type) for pii_type in types]
        if isinstance(value, dict):
            result: dict[Any, Any] = {}
            found: list[tuple[str, PIIType]] = []
            for key, item in value.items():
                child = f"{path}.{key}" if path else str(key)
                if child in _SKIPPED_PATHS:
                    result[key] = item
                elif (
                    self.is_sensitive_key(str(key))
                    and isinstance(item, (str, int))
                    and not isinstance(item, bool)
                    and item != ""
                    and not (isinstance(item, str) and _PLACEHOLDER.fullmatch(item))
                ):
                    result[key] = self.placeholder("sensitive_field", str(item))
                    found.append((child, "sensitive_field"))
                else:
                    result[key], nested = self.mask_value(item, child)
                    found.extend(nested)
            return result, found
        if isinstance(value, list):
            items: list[Any] = []
            found = []
            for index, item in enumerate(value):
                masked_item, nested = self.mask_value(item, f"{path}[{index}]")
                items.append(masked_item)
                found.extend(nested)
            return items, found
        return value, []


# Case lineage written by agenticlens.suites (trace, run, and feedback IDs).
_SKIPPED_PATHS = frozenset({"metadata.source"})

_MASKED_FIELDS = (
    "input",
    "expected_output",
    "expected_contains",
    "expected_tool_arguments",
    "metadata",
)


def mask_case(case: TestCase, masker: PIIMasker) -> tuple[TestCase, list[MaskedLocation]]:
    updates: dict[str, Any] = {}
    locations: list[MaskedLocation] = []
    for field in _MASKED_FIELDS:
        masked, found = masker.mask_value(getattr(case, field), field)
        if found:
            updates[field] = masked
            locations.extend(
                MaskedLocation(case_id=case.id, field=path, pii_type=pii_type)
                for path, pii_type in found
            )
    return (case.model_copy(update=updates, deep=True) if updates else case), locations


def mask_suite(
    suite: TestSuite, masker: PIIMasker | None = None, *, apply: bool = True
) -> tuple[TestSuite, MaskingReport]:
    """Mask every case. With `apply=False` the suite is returned unchanged (a scan)."""
    masker = masker or PIIMasker()
    cases: list[TestCase] = []
    locations: list[MaskedLocation] = []
    for case in suite.cases:
        masked, found = mask_case(case, masker)
        cases.append(masked if apply else case)
        locations.extend(found)
    report = MaskingReport(
        suite_name=suite.name,
        strategy=masker.strategy,
        applied=apply,
        total=len(locations),
        counts=dict(sorted(Counter(location.pii_type for location in locations).items())),
        locations=locations,
    )
    if not apply or not locations:
        return suite, report
    return TestSuite.model_validate({**suite.model_dump(mode="json"), "cases": cases}), report


def scan_suite(suite: TestSuite, masker: PIIMasker | None = None) -> MaskingReport:
    """Report unmasked PII without changing the suite."""
    return mask_suite(suite, masker, apply=False)[1]
