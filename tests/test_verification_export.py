from datetime import datetime, timezone

import pytest
from agentic_evals import Score

from agenticlens.exporters.verification import export_verification_signal
from aios08_helpers import assert_schema

NOW = datetime(2026, 11, 4, 18, tzinfo=timezone.utc)
REF = {"id": "subject", "producer": "agenticlens", "artifact_id": "run-1", "format": "0.4-draft"}


def export(score, evidence=()):
    return export_verification_signal(
        score,
        source_id="score-1",
        subject=REF,
        evidence=evidence,
        created_at=NOW,
        method_version="1",
    )


def test_native_partial_verdict_retains_meaning_without_private_text():
    score = Score(
        name="judge",
        value=0.5,
        passed=False,
        explanation="secret",
        evaluator_type="llm_judge",
        metadata={
            "judge_verdict": {
                "verdict": "partially_agree",
                "confidence": 0.8,
                "rationale": "private secret",
                "unsupported_claims": ["secret"],
                "evidence_missed": ["private"],
            },
            "private_context": "secret",
        },
    )
    result = export(score, [REF])
    assert_schema(result)
    assert result["verdict"] == "partially_supports" and result["confidence"] == 0.8
    assert result["grounding"]["status"] == "partial"
    assert result["safety"] == {"status": "not_checked", "concerns": []}
    assert "secret" not in str(result) and "private" not in str(result)
    assert result["source"]["artifact_id"] == "score-1"


def test_unavailable_never_exports_as_a_pass_even_with_stale_verdict():
    score = Score(
        name="judge",
        value=1,
        passed=True,
        explanation="stale",
        evaluator_type="llm_judge",
        metadata={"judge_status": "unavailable", "judge_verdict": {"bad": "stale"}},
    )
    result = export(score)
    assert_schema(result)
    assert (
        result["status"] == "unavailable"
        and result["verdict"] is None
        and result["confidence"] is None
    )


def test_rejects_non_judge_scores_and_unknown_reference_fields():
    score = Score(name="contains", value=1, passed=True, explanation="deterministic")
    with pytest.raises(ValueError, match="Only native judge"):
        export(score)
    with pytest.raises(ValueError, match="Reference fields"):
        export(score, [{**REF, "arguments": "secret"}])
