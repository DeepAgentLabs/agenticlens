"""
agents/submission.py
--------------------
Submission Agent — formats the payer submission payload and calls the
payer gateway through the agentic-chaos fault injection proxy.

Guardrail: Will NOT transmit without the explicit human_approved flag.
All payer API responses are validated before updating case state.
"""

import json
from agents.base import run_agent_step
from mock_services.chaos_proxy import call_payer_api


def _run_submission(case_id: str, justification_data: dict, match_result: dict,
                    active_chaos: str = None) -> dict:
    """Core submission logic — called via run_agent_step for observability."""

    # --- Human approval gate (non-negotiable) ---
    if not justification_data.get("human_approved", False):
        return {
            "status": "blocked",
            "error": "Submission blocked: Human approval gate not set. "
                     "A clinician must approve before network transmission.",
            "handled_gracefully": True,
        }

    payload = {
        "case_id": case_id,
        "procedure_requested": justification_data.get("procedure_requested"),
        "cpt_code": justification_data.get("cpt_code"),
        "icd_10": justification_data.get("icd_10"),
        "confidence_score": justification_data.get("confidence_score"),
        "matched_criteria": match_result.get("matched_criteria", []),
        "unmatched_criteria": match_result.get("unmatched_criteria", []),
        "justification_text": justification_data.get("justification_narrative"),
    }

    try:
        # call_payer_api routes through the agentic_chaos fault proxy
        payer_response = call_payer_api(payload, active_scenario=active_chaos)

        # Handle malformed string response
        if isinstance(payer_response, str):
            try:
                payer_response = json.loads(payer_response)
            except Exception:
                return {
                    "status": "failed_handled",
                    "error": "Payer returned malformed non-JSON payload.",
                    "raw_corrupted_payload": str(payer_response)[:500],
                    "escalated_to_human": True,
                    "handled_gracefully": True,
                }

        # Handle missing auth number on approval
        if payer_response.get("status") == "approved" and not payer_response.get("authorization_number"):
            return {
                "status": "needs_human_review",
                "validation_error": "Missing required authorization token in payer response.",
                "payer_raw_response": payer_response,
                "escalated_to_human": True,
                "handled_gracefully": True,
            }

        # Handle vague denial
        if (payer_response.get("status") == "denied"
                and payer_response.get("denial_code") in ("DEN-UNKNOWN", None)
                and len(payer_response.get("reason", "")) < 40):
            return {
                "status": "vague_denial_flagged",
                "payer_response": payer_response,
                "escalation_note": "Payer returned a non-specific denial. "
                                   "Auto-escalated to Appeal Agent.",
                "handled_gracefully": True,
            }

        return {
            "status": "submitted",
            "payer_adjudication": payer_response,
            "handled_gracefully": True,
        }

    except TimeoutError as te:
        return {
            "status": "needs_human_review",
            "error": f"Payer API Timeout: {te}",
            "escalated_to_human": True,
            "handled_gracefully": True,
            "fallback_action": "Queued for manual portal submission",
        }
    except Exception as e:
        # Catches agentic_chaos fault errors (TokenTimeoutError, RateLimitStormError, etc.)
        return {
            "status": "needs_human_review",
            "error": f"Payer Integration Fault: {e}",
            "exception_type": type(e).__name__,
            "escalated_to_human": True,
            "handled_gracefully": True,
        }


def run_submission_agent(case_id: str, justification_data: dict,
                         match_result: dict, active_chaos: str = None) -> dict:
    """Entry point — wraps _run_submission inside agenticlens observability."""
    return run_agent_step(
        "submission", case_id, _run_submission,
        justification_data, match_result, active_chaos=active_chaos
    )
