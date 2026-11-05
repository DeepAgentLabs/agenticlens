"""Offline native-to-AIOS projection; grants no authority or stable conformance."""

import json
from datetime import datetime, timezone

from agentic_evals import Score

from agenticlens.exporters.verification import export_verification_signal

score = Score(
    name="judge",
    value=0.5,
    passed=False,
    explanation="Native assessment",
    evaluator_type="llm_judge",
    metadata={
        "judge_verdict": {
            "verdict": "partially_agree",
            "confidence": 0.8,
            "unsupported_claims": ["A synthetic unsupported statement"],
        }
    },
)
reference = {"id": "output", "producer": "example", "artifact_id": "run-1", "format": "0.4-draft"}
print(
    json.dumps(
        export_verification_signal(
            score,
            source_id="judge-1",
            subject=reference,
            evidence=[reference],
            created_at=datetime(2026, 11, 4, 18, tzinfo=timezone.utc),
            method_version="1",
        ),
        indent=2,
    )
)
