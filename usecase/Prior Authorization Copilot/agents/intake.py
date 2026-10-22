"""
agents/intake.py
----------------
Intake Agent — uses Google Gemini (google-genai SDK, AQ. key compatible) to
extract a structured clinical summary from raw EHR chart notes.

Guardrail: Prompt explicitly forbids the model from inferring diagnoses or
clinical facts not present verbatim in the source text.
"""

import os
import json
from dotenv import load_dotenv
from agents.base import run_agent_step
from agents import gemini_client

load_dotenv()

_SYSTEM_INSTRUCTION = (
    "You are a clinical intake specialist AI for a Prior Authorization Copilot system. "
    "Your ONLY job is to extract structured clinical data from raw EHR chart notes. "
    "STRICT GUARDRAILS: NEVER infer, assume, or add any clinical fact not explicitly "
    "stated in the source text. If a field is not mentioned, use null. "
    "Do not synthesize or interpret. Only extract. "
    "You must respond ONLY with a valid JSON object and no other text."
)

_EXTRACTION_PROMPT = """Extract structured clinical information from the following EHR chart notes.

Patient Reference: {patient_ref}
Procedure Requested: {procedure_requested}
Physician: {physician}
CPT Code: {cpt_code}
ICD-10: {icd_10}

--- CHART NOTES START ---
{chart_notes}
--- CHART NOTES END ---

Return a JSON object with exactly these fields:
{{
  "extracted_symptoms": ["list of symptoms explicitly mentioned"],
  "extracted_treatments": ["list of conservative treatments tried, including duration if stated"],
  "extracted_imaging": ["list of imaging studies documented"],
  "extracted_neurological_findings": ["neurological findings on exam if mentioned, else []"],
  "missing_evidence_flags": ["list of required documentation items that appear absent"],
  "pain_score": "numeric pain score if mentioned, else null",
  "symptom_duration": "duration of symptoms if mentioned, else null",
  "bmi": "BMI value if mentioned, else null",
  "summary_text": "1-2 sentence plain English summary of the clinical picture",
  "guardrail_verification": "Strict extraction mode: All findings mapped directly from source clinical chart without inference."
}}"""


def _run_intake(case_id: str, case_data: dict, active_chaos: str = None) -> dict:
    prompt = _EXTRACTION_PROMPT.format(
        patient_ref=case_data.get("patient_ref", ""),
        procedure_requested=case_data.get("procedure_requested", ""),
        physician=case_data.get("physician", ""),
        cpt_code=case_data.get("cpt_code", ""),
        icd_10=case_data.get("icd_10", ""),
        chart_notes=case_data.get("chart_notes", ""),
    )

    raw = gemini_client.generate(
        prompt=prompt,
        system_instruction=_SYSTEM_INSTRUCTION,
        temperature=0.0,
        max_tokens=1024,
    )
    extracted = gemini_client.parse_json_response(raw)

    return {
        "case_id": case_id,
        "patient_ref": case_data.get("patient_ref"),
        "procedure_requested": case_data.get("procedure_requested"),
        "cpt_code": case_data.get("cpt_code"),
        "icd_10": case_data.get("icd_10"),
        "physician": case_data.get("physician"),
        **extracted,
    }


def run_intake_agent(case_id: str, case_data: dict, active_chaos: str = None) -> dict:
    """Entry point — wraps _run_intake inside agenticlens observability."""
    return run_agent_step("intake", case_id, _run_intake, case_data, active_chaos=active_chaos)
