import os
import json
import time
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

load_dotenv()

from agents.base import get_trace, clear_trace, get_all_scorecards
from agents.intake import run_intake_agent
from agents.policy_match import run_policy_match_agent
from agents.justification import run_justification_agent
from agents.submission import run_submission_agent
from agents.appeal import run_appeal_agent
from mock_services.chaos_proxy import set_active_chaos, get_active_chaos

app = FastAPI(
    title="Prior Authorization Copilot API",
    description="Agentic Lens & Chaos Observability Platform for PA Automation",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
CASES_FILE = os.path.join(DATA_DIR, "cases.json")
INITIAL_CASES_FILE = os.path.join(DATA_DIR, "cases.json")

def load_cases_data() -> list:
    if os.path.exists(CASES_FILE):
        with open(CASES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_cases_data(cases: list):
    with open(CASES_FILE, "w", encoding="utf-8") as f:
        json.dump(cases, f, indent=2)

@app.get("/api/cases")
def get_cases():
    """Returns summary list of all cases."""
    cases = load_cases_data()
    return [{"case_id": c["case_id"],
             "patient_ref": c.get("patient_ref"),
             "procedure_requested": c.get("procedure_requested"),
             "cpt_code": c.get("cpt_code"),
             "status": c.get("status", "ready_for_intake"),
             "sla_hours_remaining": c.get("sla_hours_remaining", 48),
             "confidence_score": c.get("confidence_score", 0),
             "payer_id": c.get("payer_id")} for c in cases]

@app.get("/api/cases/{case_id}")
def get_case_detail(case_id: str):
    """Returns complete case record."""
    cases = load_cases_data()
    case = next((c for c in cases if c["case_id"] == case_id), None)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@app.post("/api/cases/{case_id}/run")
def run_case_pipeline(case_id: str, active_chaos: Optional[str] = None):
    """
    Triggers agent pipeline (Intake -> Policy Match -> Justification).
    """
    cases = load_cases_data()
    case = next((c for c in cases if c["case_id"] == case_id), None)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    chaos_to_use = active_chaos or get_active_chaos()

    # Step 1: Intake Agent
    intake_res = run_intake_agent(case_id, case, active_chaos=chaos_to_use)
    
    # Step 2: Policy Match Agent
    policy_res = run_policy_match_agent(case_id, intake_res, case.get("payer_id"), active_chaos=chaos_to_use)
    
    # Step 3: Justification Agent
    just_res = run_justification_agent(case_id, intake_res, policy_res, case, active_chaos=chaos_to_use)

    # Update case state in DB
    case["status"] = just_res.get("routing_status", "pending_human_approval")
    case["confidence_score"] = just_res.get("confidence_score", 0)
    case["latest_intake"] = intake_res
    case["latest_policy_match"] = policy_res
    case["latest_justification"] = just_res
    save_cases_data(cases)

    return {
        "case_id": case_id,
        "status": case["status"],
        "confidence_score": case["confidence_score"],
        "intake": intake_res,
        "policy_match": policy_res,
        "justification": just_res
    }

@app.post("/api/cases/{case_id}/approve")
def approve_human_gate(case_id: str):
    """
    Human Review Gate Approval: Triggers Submission Agent.
    """
    cases = load_cases_data()
    case = next((c for c in cases if c["case_id"] == case_id), None)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    just_res = case.get("latest_justification", {})
    policy_res = case.get("latest_policy_match", {})
    # Deep-copy so we don't mutate the persisted case record
    just_res_approved = {**just_res, "human_approved": True}

    active_chaos = get_active_chaos()
    sub_res = run_submission_agent(case_id, just_res_approved, policy_res, active_chaos=active_chaos)
    
    if sub_res.get("status") == "submitted":
        case["status"] = "approved"
        case["authorization_number"] = sub_res.get("payer_adjudication", {}).get("authorization_number")
    elif sub_res.get("status") == "vague_denial_flagged":
        case["status"] = "denied"
        case["denial_reason"] = "Payer returned non-specific vague denial."
    elif sub_res.get("status") == "needs_human_review":
        case["status"] = "needs_human_review"
    else:
        case["status"] = "submission_failed"

    case["latest_submission"] = sub_res
    save_cases_data(cases)
    
    return {"case_id": case_id, "status": case["status"], "submission_result": sub_res}

@app.post("/api/cases/{case_id}/reject")
def reject_human_gate(case_id: str, reason: str = Body(default="Clinician rejected submission narrative.", embed=True)):
    """Human Review Gate Rejection."""
    cases = load_cases_data()
    case = next((c for c in cases if c["case_id"] == case_id), None)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    case["status"] = "needs_rework"
    case["rejection_reason"] = reason
    save_cases_data(cases)
    return {"case_id": case_id, "status": "needs_rework", "reason": reason}

@app.post("/api/cases/{case_id}/appeal")
def trigger_appeal(case_id: str):
    """Triggers Appeal Agent for denied cases."""
    cases = load_cases_data()
    case = next((c for c in cases if c["case_id"] == case_id), None)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    denial_info = {"reason": case.get("denial_reason", "Policy Criteria CRIT-2 Not Satisfied")}
    active_chaos = get_active_chaos()
    appeal_res = run_appeal_agent(case_id, case, denial_info, active_chaos=active_chaos)
    
    case["latest_appeal"] = appeal_res
    if appeal_res.get("status") == "appeal_drafted":
        case["status"] = "appeal_submitted"
    save_cases_data(cases)
    
    return {"case_id": case_id, "status": case["status"], "appeal_result": appeal_res}

@app.get("/api/traces/{case_id}")
def get_case_trace(case_id: str):
    """Feeds Agentic Lens view."""
    traces = get_trace(case_id)
    return {"case_id": case_id, "trace_count": len(traces), "traces": traces}

@app.post("/api/chaos/toggle")
def toggle_chaos(scenario: Optional[str] = Body(default=None, embed=True)):
    """Enables or disables active chaos fault injection."""
    set_active_chaos(scenario)
    return {"active_chaos": get_active_chaos()}

@app.get("/api/chaos/status")
def get_chaos_status():
    return {"active_chaos": get_active_chaos()}

@app.post("/api/cases/{case_id}/run-with-chaos")
def run_case_with_chaos(case_id: str, scenario: str = Body(..., embed=True)):
    """Runs end-to-end pipeline with explicit chaos injection."""
    set_active_chaos(scenario)
    
    # Clear past trace to see fresh chaos trace
    clear_trace(case_id)
    
    # Run pipeline
    pipeline_res = run_case_pipeline(case_id, active_chaos=scenario)
    
    # Auto-attempt submission if pipeline produced output
    cases = load_cases_data()
    case = next((c for c in cases if c["case_id"] == case_id), None)
    
    sub_res = None
    if case and case.get("latest_justification"):
        just_data = {**case["latest_justification"], "human_approved": True}
        sub_res = run_submission_agent(
            case_id,
            just_data,
            case.get("latest_policy_match", {}),
            active_chaos=scenario
        )
        case["latest_submission"] = sub_res
        save_cases_data(cases)
        
    return {
        "case_id": case_id,
        "scenario_injected": scenario,
        "pipeline_result": pipeline_res,
        "submission_result": sub_res,
        "trace": get_trace(case_id)
    }

@app.get("/api/scorecard")
def get_scorecard():
    """Returns aggregated resilience scorecard."""
    return get_all_scorecards()

@app.post("/api/reset")
def reset_demo():
    """Resets cases and clears trace files."""
    initial_cases = [
      {
        "case_id": "CASE-001", "patient_ref": "PT-88391 (John Doe)", "age": 64, "gender": "Male",
        "payer_id": "POL-AETNA-2026-KNEE", "procedure_requested": "Total Knee Arthroplasty (Right Knee)",
        "cpt_code": "27447", "icd_10": "M17.11", "physician": "Dr. Aris Thorne, MD (Orthopedic Surgery)",
        "sla_hours_remaining": 48, "status": "ready_for_intake", "confidence_score": 0,
        "chart_notes": "64-year-old male with severe right knee osteoarthritis ongoing for 14 months. Patient reports constant pain (8/10) impairing walking > 50 feet. Failed conservative treatment including 14 weeks of structured physical therapy (attendance log verified), daily Meloxicam, and two triamcinolone intra-articular injections with transient relief only. Weight-bearing X-ray (dated 15 days ago) demonstrates severe medial joint space obliteration and Kellgren-Lawrence Grade 4 changes. Height: 5'10\", Weight: 185 lbs (BMI 26.5 kg/m²). No active infections. Recommended for Right Total Knee Arthroplasty."
      },
      {
        "case_id": "CASE-002", "patient_ref": "PT-44209 (Jane Smith)", "age": 42, "gender": "Female",
        "payer_id": "POL-BCBS-2026-MRI-LUMBAR", "procedure_requested": "Lumbar Spine MRI (Without Contrast)",
        "cpt_code": "72148", "icd_10": "M54.16", "physician": "Dr. Elena Rostova, MD (Neurology)",
        "sla_hours_remaining": 24, "status": "needs_human_review", "confidence_score": 68,
        "chart_notes": "42-year-old female presenting with L5-S1 radicular pain radiating down the left leg for 5 weeks. Physical exam shows mild sensory loss along the L5 dermatome, 4+/5 left dorsiflexion strength, and positive straight leg raise test at 45 degrees. Patient completed 4 weeks of outpatient physical therapy and a 10-day course of oral Methylprednisolone. Pain persists at 6/10. Ordering Lumbar MRI to rule out disc herniation before epidural steroid injection."
      },
      {
        "case_id": "CASE-003", "patient_ref": "PT-90112 (Robert Johnson)", "age": 58, "gender": "Male",
        "payer_id": "POL-AETNA-2026-KNEE", "procedure_requested": "Total Knee Arthroplasty (Left Knee)",
        "cpt_code": "27447", "icd_10": "M17.12", "physician": "Dr. Marcus Vance, MD (Orthopedics)",
        "sla_hours_remaining": 72, "status": "ready_for_intake", "confidence_score": 0,
        "chart_notes": "58-year-old male with chronic left knee stiffness and pain. Patient reports taking over-the-counter Tylenol occasionally. Exam shows moderate joint effusion. Patient tried home exercises for 3 weeks. X-ray standing view report not attached in chart. Height/Weight unrecorded in initial intake note. Physician requests prior authorization for left knee replacement."
      },
      {
        "case_id": "CASE-004", "patient_ref": "PT-11843 (Emily Davis)", "age": 51, "gender": "Female",
        "payer_id": "POL-UHC-2026-CARD-CATH", "procedure_requested": "Diagnostic Left Heart Catheterization",
        "cpt_code": "93458", "icd_10": "I25.10", "physician": "Dr. Sterling Hayes, MD (Cardiology)",
        "sla_hours_remaining": 36, "status": "ready_for_intake", "confidence_score": 0,
        "chart_notes": "51-year-old female with atypical chest tightness occurring during strenuous exercise. Resting ECG shows normal sinus rhythm without ischemic changes. Patient has not undergone stress testing or echocardiogram. Baseline LVEF is 60%. Currently managed on low-dose aspirin and statin therapy. Physician requests diagnostic cardiac catheterization."
      },
      {
        "case_id": "CASE-005", "patient_ref": "PT-77210 (Michael Brown)", "age": 49, "gender": "Male",
        "payer_id": "POL-BCBS-2026-MRI-LUMBAR", "procedure_requested": "Lumbar Spine MRI (Without Contrast)",
        "cpt_code": "72148", "icd_10": "M54.16", "physician": "Dr. Elena Rostova, MD (Neurology)",
        "sla_hours_remaining": 8, "status": "pending_human_approval", "confidence_score": 92,
        "chart_notes": "49-year-old male presenting with acute onset severe L4-L5 radiculopathy and progressive right foot drop (dorsiflexion weakness 2/5) over the past 8 days following heavy lifting. Patient completed 8 weeks of physical therapy previously for chronic low back pain. Absent right patellar reflex on examination. Urgent MRI requested to evaluate acute cauda equina / severe root compression."
      },
      {
        "case_id": "CASE-006", "patient_ref": "PT-60481 (Sarah Connor)", "age": 37, "gender": "Female",
        "payer_id": "POL-BCBS-2026-MRI-LUMBAR", "procedure_requested": "Lumbar Spine MRI (Without Contrast)",
        "cpt_code": "72148", "icd_10": "M54.5", "physician": "Dr. Aris Thorne, MD (Spine Clinic)",
        "sla_hours_remaining": 16, "status": "denied", "confidence_score": 55,
        "denial_reason": "Policy POL-BCBS-2026-MRI-LUMBAR Criterion CRIT-2 Not Met: Submitted documentation did not include verified 6-week Physical Therapy attendance logs or physician progress notes verifying conservative treatment failure.",
        "chart_notes": "37-year-old female with persistent lower back pain and left leg numbness for 10 weeks. Initial submission was denied by BCBS for lack of PT records. UPDATED ATTACHMENT: Verified Physical Therapy Completion Log attached confirming 12 sessions of supervised PT between June 1 and July 20 (7 weeks duration), demonstrating no symptomatic improvement. Requesting immediate appeal for Lumbar MRI approval."
      },
      {
        "case_id": "CASE-007", "patient_ref": "PT-31092 (Carlos Mendez)", "age": 55, "gender": "Male",
        "payer_id": "POL-UHC-2026-CARD-CATH", "procedure_requested": "Diagnostic Left Heart Catheterization",
        "cpt_code": "93458", "icd_10": "I25.10", "physician": "Dr. Sterling Hayes, MD (Cardiology)",
        "sla_hours_remaining": 14, "status": "pending_human_approval", "confidence_score": 94,
        "chart_notes": "55-year-old male with refractory unstable angina pectoris despite dual antiplatelet and maximal beta-blocker therapy. Nuclear exercise stress test (completed 4 days ago) revealed moderate-to-severe reversible anterolateral wall ischemia. Baseline Echocardiogram demonstrates LVEF of 45%. Urgent diagnostic cardiac catheterization indicated."
      },
      {
        "case_id": "CASE-008", "patient_ref": "PT-19402 (Samantha Reed)", "age": 34, "gender": "Female",
        "payer_id": "POL-BCBS-2026-MRI-LUMBAR", "procedure_requested": "Lumbar Spine MRI (Without Contrast)",
        "cpt_code": "72148", "icd_10": "M54.16", "physician": "Dr. Elena Rostova, MD (Neurology)",
        "sla_hours_remaining": 30, "status": "approved", "authorization_number": "AUTH-BCBS-88219", "confidence_score": 95,
        "chart_notes": "34-year-old female with severe low back pain radiating down right leg (sciatica) for 9 weeks. Completed 7 weeks of supervised physical therapy with no improvement. Neurological exam reveals diminished right Achilles reflex and L5 numbness. Diagnostic Lumbar MRI approved."
      },
      {
        "case_id": "CASE-009", "patient_ref": "PT-55120 (David Miller)", "age": 67, "gender": "Male",
        "payer_id": "POL-AETNA-2026-KNEE", "procedure_requested": "Total Knee Arthroplasty (Left Knee)",
        "cpt_code": "27447", "icd_10": "M17.12", "physician": "Dr. Marcus Vance, MD (Orthopedics)",
        "sla_hours_remaining": 18, "status": "ready_for_intake", "confidence_score": 0,
        "chart_notes": "67-year-old male with chronic end-stage left knee osteoarthritis. Pain 7/10 for 16 months. Completed 14 weeks of physical therapy and received 2 cortisone injections. Weight-bearing X-ray shows Kellgren-Lawrence Grade 3-4 joint narrowing. BMI 31.2 kg/m². Scheduled for Left TKA."
      },
      {
        "case_id": "CASE-010", "patient_ref": "PT-82319 (Anita Patel)", "age": 48, "gender": "Female",
        "payer_id": "POL-BCBS-2026-MRI-LUMBAR", "procedure_requested": "Lumbar Spine MRI (Without Contrast)",
        "cpt_code": "72148", "icd_10": "M54.5", "physician": "Dr. Aris Thorne, MD (Spine Clinic)",
        "sla_hours_remaining": 52, "status": "needs_rework", "confidence_score": 40,
        "chart_notes": "48-year-old female with mild lower back pain for 2 weeks following gardening. No radicular symptoms, normal motor and reflex exam. Patient has not tried physical therapy or prescription NSAIDs. Physician requested Lumbar MRI."
      },
      {
        "case_id": "CASE-011", "patient_ref": "PT-66014 (James Wilson)", "age": 71, "gender": "Male",
        "payer_id": "POL-UHC-2026-CARD-CATH", "procedure_requested": "Diagnostic Left Heart Catheterization",
        "cpt_code": "93458", "icd_10": "I25.10", "physician": "Dr. Sterling Hayes, MD (Cardiology)",
        "sla_hours_remaining": 10, "status": "needs_human_review", "confidence_score": 62,
        "chart_notes": "71-year-old male presenting with exertional shortness of breath and mild chest pressure for 3 months. ECG shows nonspecific T-wave inversions. Non-invasive stress test report pending from outside hospital. Physician requests direct cardiac catheterization."
      },
      {
        "case_id": "CASE-012", "patient_ref": "PT-20981 (Linda Taylor)", "age": 60, "gender": "Female",
        "payer_id": "POL-AETNA-2026-KNEE", "procedure_requested": "Total Knee Arthroplasty (Right Knee)",
        "cpt_code": "27447", "icd_10": "M17.11", "physician": "Dr. Aris Thorne, MD (Orthopedic Surgery)",
        "sla_hours_remaining": 64, "status": "approved", "authorization_number": "AUTH-AETNA-34901", "confidence_score": 96,
        "chart_notes": "60-year-old female with severe right knee pain for 18 months. Verified 16 weeks of PT attendance log attached. Standing X-rays demonstrate complete joint space obliteration. BMI 28.4 kg/m². Prior auth approved."
      }
    ]
    save_cases_data(initial_cases)
    
    # Clear traces
    traces_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "traces")
    if os.path.exists(traces_dir):
        for f in os.listdir(traces_dir):
            if f.endswith(".jsonl"):
                os.remove(os.path.join(traces_dir, f))
                
    set_active_chaos(None)
    return {"status": "reset_successful"}

# Mount usecases documentation & architecture guide
usecases_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "usecases")
if os.path.exists(usecases_path):
    app.mount("/usecases", StaticFiles(directory=usecases_path, html=True), name="usecases")

# Mount website (landing page & storytelling)
website_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "website")
if os.path.exists(website_path):
    app.mount("/website", StaticFiles(directory=website_path, html=True), name="website")

# Mount static frontend
frontend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
