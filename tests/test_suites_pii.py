"""PII detection and masking before storage."""

import pytest
from agentic_evals import TestCase as EvalCase

from agenticlens.suites import PIIMasker, mask_case, mask_suite, new_suite, scan_suite


@pytest.mark.parametrize(
    ("text", "masked", "types"),
    [
        ("mail jo.doe+x@example.co.uk now", "mail [EMAIL] now", ["email"]),
        ("call +1 (555) 123-4567.", "call [PHONE].", ["phone"]),
        ("call 020 7946 0958", "call [PHONE]", ["phone"]),
        ("card 4111 1111 1111 1111", "card [CREDIT_CARD]", ["credit_card"]),
        ("card 4111-1111-1111-1111", "card [CREDIT_CARD]", ["credit_card"]),
        ("ssn 123-45-6789", "ssn [US_SSN]", ["us_ssn"]),
        ("from 192.168.10.255", "from [IPV4]", ["ipv4"]),
        ("Authorization: Bearer abc.def-ghi_jkl", "Authorization: [SECRET]", ["secret"]),
        ("key sk-proj1234567890abcdef", "key [SECRET]", ["secret"]),
        ("token ghp_abcdefghijklmnopqrstuvwx", "token [SECRET]", ["secret"]),
    ],
)
def test_mask_text_detects_pii(text: str, masked: str, types: list[str]) -> None:
    assert PIIMasker().mask_text(text) == (masked, types)


@pytest.mark.parametrize(
    "text",
    [
        "released 2026-10-17",
        "total 1234.56 USD",
        "order 4111 1111 1111 1112",  # fails Luhn
        "version 999.1.1.1",  # not a valid IPv4
        "run a1b2c3d4-1234-5678-9abc-def012345678",
        "ticket 12345",
        "[EMAIL] and [PHONE:0a1b2c3d]",
    ],
)
def test_mask_text_ignores_non_pii(text: str) -> None:
    assert PIIMasker().mask_text(text) == (text, [])


def test_hash_strategy_is_stable_and_salted() -> None:
    masker = PIIMasker(strategy="hash", salt="s1")
    text, _ = masker.mask_text("a@b.io and a@b.io and c@d.io")
    parts = text.split(" and ")
    assert parts[0] == parts[1] != parts[2]
    assert parts[0].startswith("[EMAIL:") and len(parts[0]) == len("[EMAIL:12345678]")
    other_salt, _ = PIIMasker(strategy="hash", salt="s2").mask_text("a@b.io")
    assert other_salt != parts[0]
    with pytest.raises(ValueError, match="strategy"):
        PIIMasker(strategy="encrypt")  # type: ignore[arg-type]


def test_mask_value_masks_sensitive_keys_by_word() -> None:
    value = {
        "customer_email": "x",
        "Phone-Number": 5551234,
        "input_tokens": 12,
        "tokenizer": "bpe",
        "verified_email": True,
        "notes": None,
        "nested": [{"password": "hunter2"}, "write to a@b.io"],
        "address": {"city": "Paris"},
    }
    masked, found = PIIMasker().mask_value(value)
    assert masked["customer_email"] == "[SENSITIVE_FIELD]"
    assert masked["Phone-Number"] == "[SENSITIVE_FIELD]"
    assert masked["input_tokens"] == 12 and masked["tokenizer"] == "bpe"
    assert masked["verified_email"] is True and masked["notes"] is None
    assert masked["nested"] == [{"password": "[SENSITIVE_FIELD]"}, "write to [EMAIL]"]
    assert masked["address"] == {"city": "Paris"}  # containers are walked, not replaced
    assert sorted(found) == [
        ("Phone-Number", "sensitive_field"),
        ("customer_email", "sensitive_field"),
        ("nested[0].password", "sensitive_field"),
        ("nested[1]", "email"),
    ]
    assert PIIMasker(sensitive_keys=()).mask_value({"email": "x"}) == ({"email": "x"}, [])


def test_mask_case_covers_expectations_and_skips_lineage() -> None:
    case = EvalCase(
        id="c1",
        name="Contact a@b.io",
        input="I am a@b.io",
        expected_output="We emailed a@b.io",
        expected_contains=["a@b.io"],
        expected_tool_arguments={"send": {"to": "a@b.io"}},
        metadata={"source": {"kind": "trace", "trace_id": "555-123-4567"}, "note": "a@b.io"},
    )
    masked, locations = mask_case(case, PIIMasker())
    assert masked.input == "I am [EMAIL]"
    assert masked.expected_output == "We emailed [EMAIL]"
    assert masked.expected_contains == ["[EMAIL]"]
    assert masked.expected_tool_arguments == {"send": {"to": "[EMAIL]"}}
    assert masked.metadata["source"]["trace_id"] == "555-123-4567"
    assert masked.name == "Contact a@b.io"  # names are not masked
    assert [loc.field for loc in locations] == [
        "input",
        "expected_output",
        "expected_contains[0]",
        "expected_tool_arguments.send.to",
        "metadata.note",
    ]
    assert mask_case(masked, PIIMasker()) == (masked, [])


def test_mask_suite_and_scan() -> None:
    suite = new_suite(
        name="s",
        version="1",
        cases=[
            EvalCase(id="a", name="a", input="call 555-123-4567", expected_output="x"),
            EvalCase(id="b", name="b", input="clean", expected_output="x"),
        ],
    )
    report = scan_suite(suite)
    assert (report.total, report.counts, report.applied) == (1, {"phone": 1}, False)
    assert "555" not in report.model_dump_json()  # reports never carry the value
    masked, applied = mask_suite(suite)
    assert applied.applied and masked.cases[0].input == "call [PHONE]"
    assert masked.cases[1] == suite.cases[1]
    assert scan_suite(masked).total == 0
    unchanged, empty = mask_suite(masked)
    assert unchanged is masked and empty.total == 0
