"""
agents/appeal.py
----------------
Appeal Agent — uses Google Gemini (google-genai SDK, AQ. key compatible)
to draft a targeted, evidence-backed clinical appeal letter.

Guardrail: Vague denials (no specific clause cited, < 40 chars) are escalated
to peer-to-peer medical director review instead of auto-drafting.
"""

from dotenv import load_dotenv

from agents import gemini_client
from agents.base import run_agent_step

load_dotenv()

_SYSTEM_INSTRUCTION = (
    "You are a clinical appeals specialist writing formal Prior Authorization"
    " reconsideration letters for denied insurance claims. Your appeal must: "
    "(1) Directly address and rebut the specific denial reason. (2) Cite all "
    "available clinical evidence satisfying the unmet criteria. (3) Use "
    "precise medical language for peer-to-peer medical review. (4) Be "
    "professional and evidence-based. Respond ONLY with valid JSON and no "
    "other text."
)

_APPEAL_PROMPT = """Draft a formal Prior Authorization appeal letter for the following denied case.

=== DENIAL INFORMATION ===
Denial Reason: {denial_reason}
Payer: {payer_id}

=== PATIENT & CASE INFORMATION ===
Patient: {patient_ref}
Attending Physician: {physician}
Procedure Requested: {procedure_requested}
CPT Code: {cpt_code}
ICD-10: {icd_10}

=== CHART NOTES (use as supplemental evidence) ===
{chart_notes}

Return a JSON object with exactly this structure:
{{
  "status": "appeal_drafted",
  "appeal_letter_narrative": "Full formal appeal letter text (3-5 paragraphs)",
  "key_rebuttal_points": ["List of specific clinical facts rebutting the denial"],
  "attached_supplements": ["List of documentation items being attached"],
  "recommended_next_step": "Specific next action (e.g. Submit Level 1 appeal via \
payer portal within 30 days)",
  "handled_gracefully": true
}}"""


def _run_appeal(case_id: str, case_data: dict, denial_info: dict, active_chaos: str = None) -> dict:
    denial_reason = (
        denial_info.get("reason")
        or case_data.get("denial_reason")
        or "Policy criteria not satisfied"
    )

    # Guardrail: escalate vague denials
    is_vague = (
        len(denial_reason.strip()) < 40
        and "crit" not in denial_reason.lower()
        and "criterion" not in denial_reason.lower()
        and "section" not in denial_reason.lower()
    )
    if is_vague:
        return {
            "status": "escalated_vague_denial",
            "escalation_target": "Medical Director / Peer-to-Peer Desk",
            "reason": (
                f"Denial reason is non-specific ({repr(denial_reason)}). "
                "Auto-appeal suppressed per guardrails. "
                "Scheduling Peer-to-Peer clinical review."
            ),
            "handled_gracefully": True,
        }

    prompt = _APPEAL_PROMPT.format(
        denial_reason=denial_reason,
        payer_id=case_data.get("payer_id", ""),
        patient_ref=case_data.get("patient_ref", ""),
        physician=case_data.get("physician", ""),
        procedure_requested=case_data.get("procedure_requested", ""),
        cpt_code=case_data.get("cpt_code", ""),
        icd_10=case_data.get("icd_10", ""),
        chart_notes=case_data.get("chart_notes", ""),
    )

    raw = gemini_client.generate(
        prompt=prompt,
        system_instruction=_SYSTEM_INSTRUCTION,
        temperature=0.4,
        max_tokens=2048,
    )
    llm_result = gemini_client.parse_json_response(raw)

    return {
        "case_id": case_id,
        "denial_reason_cited": denial_reason,
        **llm_result,
    }


def run_appeal_agent(
    case_id: str, case_data: dict, denial_info: dict, active_chaos: str = None
) -> dict:
    return run_agent_step(
        "appeal", case_id, _run_appeal, case_data, denial_info, active_chaos=active_chaos
    )
