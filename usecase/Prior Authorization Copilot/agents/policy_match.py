"""
agents/policy_match.py
----------------------
Policy Match Agent — uses Google Gemini (google-genai SDK, AQ. key compatible)
to evaluate each payer policy inclusion criterion against extracted clinical evidence.

Guardrail: Ambiguous or partially documented criteria are flagged as UNMATCHED
with a human review flag — never assumed compliant.
"""

import json
import os

from dotenv import load_dotenv

from agents import gemini_client
from agents.base import run_agent_step

load_dotenv()
_POLICIES_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "policies.json"
)

_SYSTEM_INSTRUCTION = (
    "You are a Prior Authorization Policy Compliance Analyst. Your job is to "
    "evaluate each insurance policy criterion against extracted clinical "
    "evidence. STRICT GUARDRAILS: If evidence is ambiguous, partial, or "
    "missing, mark the criterion as NOT SATISFIED. Never assume compliance. "
    "Always prefer 'needs_human_review' over 'satisfied' when in doubt. "
    "Respond ONLY with valid JSON and no other text."
)

_MATCH_PROMPT = """Evaluate the following payer policy criteria against the clinical evidence.

=== PAYER POLICY ===
Policy ID: {policy_id}
Payer: {payer_name}
Procedure: {procedure_name}

Inclusion Criteria:
{criteria_json}

=== EXTRACTED CLINICAL EVIDENCE ===
{clinical_summary_json}

For each criterion, determine whether the clinical evidence satisfies it.
Return a JSON object with this exact structure:
{{
  "policy_id": "{policy_id}",
  "payer_name": "{payer_name}",
  "procedure_name": "{procedure_name}",
  "evaluated_criteria": [
    {{
      "id": "CRIT-1",
      "description": "criterion text",
      "required": true,
      "is_satisfied": true,
      "evidence_note": "Specific quote or finding from clinical evidence satisfying \
or failing this criterion",
      "review_flag": null
    }}
  ],
  "compliance_notes": "Overall summary of policy compliance status"
}}

For each criterion:
- Set is_satisfied to true ONLY if evidence clearly satisfies it.
- Set review_flag to "needs_human_review" if evidence is partial or ambiguous.
- evidence_note must cite the specific clinical finding, not generic statements."""


def _load_policies() -> dict:
    with open(_POLICIES_PATH, encoding="utf-8") as f:
        policies = json.load(f)
    return {p["policy_id"]: p for p in policies}


def _run_policy_match(
    case_id: str, clinical_summary: dict, policy_id: str, active_chaos: str = None
) -> dict:
    policies = _load_policies()
    policy = policies.get(policy_id)

    if not policy:
        return {
            "error": f"Policy ID {policy_id} not found in policies.json",
            "matched_criteria": [],
            "unmatched_criteria": [],
            "policy_match_status": "error",
        }

    criteria_json = json.dumps(policy.get("inclusion_criteria", []), indent=2)
    summary_json = json.dumps(clinical_summary, indent=2)

    prompt = _MATCH_PROMPT.format(
        policy_id=policy_id,
        payer_name=policy.get("payer_name", ""),
        procedure_name=policy.get("procedure_name", ""),
        criteria_json=criteria_json,
        clinical_summary_json=summary_json,
    )

    raw = gemini_client.generate(
        prompt=prompt,
        system_instruction=_SYSTEM_INSTRUCTION,
        temperature=0.0,
        max_tokens=2048,
    )
    llm_result = gemini_client.parse_json_response(raw)

    matched = []
    unmatched = []
    for crit in llm_result.get("evaluated_criteria", []):
        entry = {
            "id": crit.get("id"),
            "description": crit.get("description"),
            "required": crit.get("required", True),
            "evidence_note": crit.get("evidence_note", ""),
            "review_flag": crit.get("review_flag"),
        }
        if crit.get("is_satisfied"):
            matched.append(entry)
        else:
            unmatched.append(entry)

    total = len(llm_result.get("evaluated_criteria", []))
    compliance = round((len(matched) / total) * 100, 1) if total > 0 else 0

    return {
        "policy_id": policy_id,
        "payer_name": policy.get("payer_name"),
        "procedure_name": policy.get("procedure_name"),
        "matched_criteria": matched,
        "unmatched_criteria": unmatched,
        "total_criteria_count": total,
        "compliance_score": compliance,
        "compliance_notes": llm_result.get("compliance_notes", ""),
        "policy_match_status": (
            "full_match"
            if len(unmatched) == 0
            else ("partial_match" if len(matched) > 0 else "no_match")
        ),
    }


def run_policy_match_agent(
    case_id: str, clinical_summary: dict, policy_id: str, active_chaos: str = None
) -> dict:
    return run_agent_step(
        "policy_match",
        case_id,
        _run_policy_match,
        clinical_summary,
        policy_id,
        active_chaos=active_chaos,
    )
