import random
import time
import uuid


def real_mock_payer_call(payload: dict) -> dict:
    """
    Simulates a production Payer Adjudication Engine response.
    Evaluates clinical criteria, confidence scores, and missing documentation.
    """
    time.sleep(0.3)  # simulate network roundtrip

    procedure = payload.get("procedure_requested", "")
    confidence = payload.get("confidence_score", 0)
    unmatched_criteria = payload.get("unmatched_criteria", [])

    # Specific case rules or general rules
    if len(unmatched_criteria) == 0 and confidence >= 70:
        auth_code = f"AUTH-{uuid.uuid4().hex[:8].upper()}"
        return {
            "status": "approved",
            "authorization_number": auth_code,
            "payer_case_id": f"PAYER-REF-{random.randint(10000, 99999)}",
            "effective_date": "2026-09-25",
            "expiration_date": "2026-12-25",
            "adjudication_notes": (
                f"Prior authorization approved for {procedure}. "
                "Criteria CRIT-1 through CRIT-4 satisfied."
            ),
            "decision_timestamp": time.time(),
        }
    else:
        reasons = [c.get("description", "Criterion failed") for c in unmatched_criteria]
        reason_str = (
            "; ".join(reasons)
            if reasons
            else "Clinical documentation does not meet policy criteria threshold."
        )
        return {
            "status": "denied",
            "denial_code": "DEN-CLINICAL-INSUFFICIENT",
            "reason": f"Authorization request denied. Reason(s): {reason_str}",
            "appeal_eligible": True,
            "appeal_deadline_days": 30,
            "decision_timestamp": time.time(),
        }
