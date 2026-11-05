"""Source-preserving, text-redacted AIOS 0.8-draft judge-score projections."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any

from agentic_evals import Score
from agentic_evals.judging import is_judge_score, is_unavailable

from agenticlens import __version__
from agenticlens.evaluation.judging import judge_verdict
from agenticlens.exporters._aios import identifier, reference, timestamp


def export_verification_signal(
    score: Score,
    *,
    source_id: str,
    subject: Mapping[str, Any],
    evidence: Sequence[Mapping[str, Any]],
    created_at: datetime,
    method_version: str,
) -> dict[str, Any]:
    """Export an actual structured judge score or explicit unavailable/skipped score.

    Native free text, private metadata, usage and arguments are never copied.
    Grounding detail is represented by redacted items preserving native counts;
    safety stays not_checked because JudgeVerdict carries no safety assessment.
    Public identifiers and evidence attribution are the trusted host's inputs.
    """
    source_id = identifier(source_id)
    references = [reference(item) for item in evidence]
    if len({item["id"] for item in references}) != len(references):
        raise ValueError("Evidence reference ids must be unique")
    if not is_judge_score(score):
        raise ValueError("Only native judge scores can be projected as model verification")
    unavailable = is_unavailable(score)
    verdict = None if unavailable or score.skipped else judge_verdict(score)
    projected: str | None
    confidence: float | None
    if unavailable or score.skipped:
        status = "unavailable" if unavailable else "skipped"
        projected = None
        confidence = None
        unsupported: list[str] = []
        missed: list[str] = []
        grounding = "not_checked"
        native_value = status
    elif verdict is not None:
        status = "completed"
        projected = {
            "agree": "supports",
            "partially_agree": "partially_supports",
            "disagree": "contradicts",
        }[verdict.verdict]
        confidence = verdict.confidence
        unsupported = [
            f"Redacted unsupported claim {i + 1}" for i in range(len(verdict.unsupported_claims))
        ]
        missed = [
            f"Redacted missed evidence item {i + 1}" for i in range(len(verdict.evidence_missed))
        ]
        # Missing evidence never becomes an assessed grounding claim.
        grounding = "partial" if references and (unsupported or missed) else "not_checked"
        native_value = verdict.verdict
    else:
        raise ValueError(
            "A structured judge verdict or explicit unavailable/skipped score is required"
        )
    return {
        "spec_version": "0.8-draft",
        "artifact_type": "verification_signal",
        "id": f"lens:verification:{source_id}",
        "created_at": timestamp(created_at),
        "producer": {"name": "agenticlens", "version": __version__},
        "source": {
            "id": "native-score",
            "producer": "agenticlens",
            "artifact_id": source_id,
            "format": "agenticlens.judge-score",
        },
        "subject": reference(subject),
        "method": {
            "kind": "model",
            "name": identifier(score.evaluator or score.name),
            "version": identifier(method_version),
        },
        "status": status,
        "verdict": projected,
        "confidence": confidence,
        "rationale": "Projected native judge assessment; source text is withheld.",
        "evidence": references,
        "grounding": {
            "status": grounding,
            "unsupported_claims": unsupported,
            "missed_evidence_items": missed,
        },
        "safety": {"status": "not_checked", "concerns": []},
        "native_outcome": {"format": "agenticlens.judge-score", "value": native_value},
        "attributes": {"text_redacted": True},
    }
