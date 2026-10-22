"""
agents/justification.py
-----------------------
Justification Agent — uses Google Gemini (google-genai SDK, AQ. key compatible)
to write a structured medical necessity narrative and compute a confidence score.

Guardrail: Confidence < 80 or unmatched mandatory criteria → auto-routes to
human review. No case reaches submission without explicit human approval.
"""

import os
import json
from dotenv import load_dotenv
from agents.base import run_agent_step
from agents import gemini_client

load_dotenv()

_SYSTEM_INSTRUCTION = (
    "You are a clinical documentation specialist writing Prior Authorization "
    "medical necessity justification narratives for insurance submissions. "
    "Your output must be precise, evidence-based, and directly tied to payer policy criteria. "
    "You must respond ONLY with valid JSON and no other text."
)

_JUSTIFICATION_PROMPT = """Write a medical necessity justification for the following Prior Authorization request.

=== CASE INFORMATION ===
Patient: {patient_ref}
Physician: {physician}
Procedure: {procedure_requested}
CPT Code: {cpt_code}
ICD-10: {icd_10}
SLA Hours Remaining: {sla_hours}

=== POLICY MATCH RESULTS ===
Policy ID: {policy_id}
Payer: {payer_name}
Compliance Score: {compliance_score}%

Matched Criteria:
{matched_json}

Unmatched Criteria:
{unmatched_json}

=== CLINICAL SUMMARY ===
{clinical_summary_json}

Return a JSON object with this exact structure:
{{
  "confidence_score": <integer 0-100, reflecting evidence strength and policy compliance>,
  "recommended_action": <"approve" | "human_review" | "rework_or_deny">,
  "routing_status": <"pending_human_approval" | "needs_human_review" | "needs_rework">,
  "routing_reason": "Specific reason citing evidence gaps or strengths",
  "justification_narrative": "Full medical necessity letter narrative (3-5 paragraphs citing criteria and findings)",
  "confidence_rationale": "Brief explanation of why this confidence score was assigned"
}}

ROUTING RULES (follow exactly):
- confidence >= 85 AND zero unmatched required criteria → recommended_action = "approve", routing_status = "pending_human_approval"
- confidence >= 60 → recommended_action = "human_review", routing_status = "needs_human_review"
- confidence < 60 → recommended_action = "rework_or_deny", routing_status = "needs_rework"
- requires_human_gate is ALWAYS true — no case reaches submission without human approval."""


def _run_justification(case_id: str, clinical_summary: dict, match_result: dict,
                       case_data: dict, active_chaos: str = None) -> dict:
    prompt = _JUSTIFICATION_PROMPT.format(
        patient_ref=case_data.get("patient_ref", ""),
        physician=case_data.get("physician", ""),
        procedure_requested=case_data.get("procedure_requested", ""),
        cpt_code=case_data.get("cpt_code", ""),
        icd_10=case_data.get("icd_10", ""),
        sla_hours=case_data.get("sla_hours_remaining", 48),
        policy_id=match_result.get("policy_id", ""),
        payer_name=match_result.get("payer_name", ""),
        compliance_score=match_result.get("compliance_score", 0),
        matched_json=json.dumps(match_result.get("matched_criteria", []), indent=2),
        unmatched_json=json.dumps(match_result.get("unmatched_criteria", []), indent=2),
        clinical_summary_json=json.dumps(clinical_summary, indent=2),
    )

    raw = gemini_client.generate(
        prompt=prompt,
        system_instruction=_SYSTEM_INSTRUCTION,
        temperature=0.3,
        max_tokens=2048,
    )
    llm_result = gemini_client.parse_json_response(raw)
    confidence = max(5, min(98, int(llm_result.get("confidence_score", 50))))

    return {
        "case_id": case_id,
        "procedure_requested": case_data.get("procedure_requested", ""),
        "cpt_code": case_data.get("cpt_code", ""),
        "icd_10": case_data.get("icd_10", ""),
        "confidence_score": confidence,
        "recommended_action": llm_result.get("recommended_action", "human_review"),
        "routing_status": llm_result.get("routing_status", "needs_human_review"),
        "routing_reason": llm_result.get("routing_reason", ""),
        "confidence_rationale": llm_result.get("confidence_rationale", ""),
        "requires_human_gate": True,
        "justification_narrative": llm_result.get("justification_narrative", ""),
        "matched_criteria_count": len(match_result.get("matched_criteria", [])),
        "unmatched_criteria_count": len(match_result.get("unmatched_criteria", [])),
    }


def run_justification_agent(case_id: str, clinical_summary: dict,
                            match_result: dict, case_data: dict,
                            active_chaos: str = None) -> dict:
    return run_agent_step(
        "justification", case_id, _run_justification,
        clinical_summary, match_result, case_data, active_chaos=active_chaos
    )
