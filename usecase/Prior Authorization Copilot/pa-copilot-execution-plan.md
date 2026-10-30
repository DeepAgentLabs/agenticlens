# Prior Authorization Copilot — End-to-End Execution Plan
*Agentic Lens (observability/replay) + Agentic Chaos (fault-injection resilience) as core pillars*

> **Disclaimer to state before any demo:** all patient, chart, and payer data used here is synthetic. This is an architecture/observability demo, not a certified clinical or HIPAA-compliant system. Do not point it at real PHI.

---

## 1. Environment Setup
```bash
mkdir pa-copilot && cd pa-copilot
python -m venv venv && source venv/bin/activate
pip install fastapi uvicorn anthropic pydantic httpx
mkdir agents mock_services data traces frontend
touch requirements.txt .env
echo "ANTHROPIC_API_KEY=your_key_here" >> .env
```
Folder structure:
```
pa-copilot/
  agents/        # intake, policy_match, justification, submission, appeal
  mock_services/ # fake EHR + fake payer API
  data/          # synthetic cases, policies
  traces/        # Lens trace store (JSON lines)
  frontend/      # single-page UI: Queue | Lens | Chaos Panel
```

## 2. Compliance Framing (say this out loud, once)
"Every case here is synthetic. This demonstrates the *pattern* — decision traceability and resilience testing for agentic systems in a regulated domain — not a production clinical tool. A real deployment would need HIPAA controls, PHI encryption, and payer BAAs before touching real data."

## 3. Architecture
```
Chart JSON → Intake Agent → Policy Match Agent → Justification Agent
                                                        ↓
                                          Human Review UI (approve/reject)
                                                        ↓
                              Submission Agent → [Chaos Proxy] → Mock Payer API
                                                        ↓
                                        Denial/Appeal Agent → (loop to Human Gate)

Every arrow ⇒ wrapped by trace_step() ⇒ appended to traces/<case_id>.jsonl
```
Single Python process, agents as functions, no microservices today.

## 4. Code Skeleton
```python
# agents/base.py
import time, json, uuid

def trace_step(step_name):
    def decorator(fn):
        def wrapper(case_id, *args, **kwargs):
            start = time.time()
            chaos_flag = kwargs.get("_chaos_injected", False)
            try:
                result = fn(case_id, *args, **kwargs)
                status = "success"
            except Exception as e:
                result, status = {"error": str(e)}, "failed"
            entry = {
                "trace_id": str(uuid.uuid4()), "case_id": case_id,
                "step": step_name, "status": status,
                "latency_ms": round((time.time()-start)*1000, 1),
                "chaos_injected": chaos_flag, "output": result,
                "timestamp": time.time(),
            }
            with open(f"traces/{case_id}.jsonl", "a") as f:
                f.write(json.dumps(entry) + "\n")
            return result
        return wrapper
    return decorator
```
```python
# mock_services/chaos_proxy.py
import random

SCENARIOS = {
    "payer_timeout": lambda: (_ for _ in ()).throw(TimeoutError("payer API timeout")),
    "malformed_json": lambda: "{not valid json",
    "vague_denial": lambda: {"status": "denied", "reason": "does not meet criteria"},
    "missing_field": lambda: {"status": "approved", "chart_field": None},
}

def call_payer_api(payload, active_scenario=None):
    if active_scenario and active_scenario in SCENARIOS:
        return SCENARIOS[active_scenario]()
    return real_mock_payer_call(payload)  # defined in mock_services/payer_api.py
```
Each agent (`intake`, `policy_match`, `justification`, `submission`, `appeal`) follows the same shape: `@trace_step("intake")` wrapping a function that calls the Claude API with a scoped prompt and returns structured JSON (use Pydantic models to force schema).

## 5. Error Handling (non-chaos failures)
- Malformed trace file → catch on read, render "trace corrupted" in UI instead of crashing
- LLM call fails outside a chaos scenario → one retry, then mark case `needs_human_review`
- Frontend fetch fails → show cached last-known state, not a blank screen

## 6. Build Order (today, no dates — just sequence)
1. Synthetic data: 6–8 cases (`data/cases.json`), 2 payer policies (`data/policies.json`), mock payer API (`mock_services/payer_api.py`)
2. Happy-path pipeline: intake → policy_match → justification → submission → status, one clean case, no Lens/Chaos yet
3. Wrap every agent with `trace_step`, confirm `traces/*.jsonl` populates correctly
4. Build the two Lens views (technical JSON dump; clinician plain-language extract) off that same file
5. Add chaos proxy + 4–5 scenarios, wire `chaos_injected` tagging into traces
6. Build the three-tab frontend (Queue / Lens / Chaos Panel) + resilience scorecard (simple pass/fail count table)
7. Denial → appeal loop on one case, using the structured denial-reason field

## 7. Deployment (today-scope)
Local only: `uvicorn main:app --reload`, frontend as a static HTML file opened in browser or served by FastAPI's `StaticFiles`. If you want a shareable link, that's a separate step afterward — not needed for a live demo.

## 8. Feature → Demo Coverage Map
| # | Feature | Demonstrated in step |
|---|---|---|
| Core 1–5 | Intake, fusion, policy match, prediction, justification | Steps 4→2 |
| Core 6–10 | Coding, submission, status, denial parsing, appeal draft | Steps 3, 7 |
| Core 11–20 | Human gate, multi-payer*, SLA, dashboard, confidence, explain-button | Steps 6, 4 (*hardcode one payer today) |
| Lens 21–32 | Trace, replay, pattern view, audit export, diff view | Step 4, 6 |
| Chaos 33–46 | Fault injection, cascading, silent-failure, scorecard | Step 5, 6 |

Anything not explicitly in a step above is a stated cut (multi-payer schema, patient-facing page, real FHIR, auth/security) — mention this openly if asked.

## 9. Demo Script (6 steps, ~4 minutes)
1. Clean case runs end-to-end → appears in Queue
2. Click "Explain this decision" → clinician trace view
3. Switch to technical Lens view → full tool-call trace, latency breakdown
4. Chaos Panel → toggle `payer_timeout` → rerun same case → agent escalates gracefully → new trace, tagged `chaos_injected: true`, shown side-by-side with the clean trace
5. Resilience scorecard updates
6. Denial → auto-drafted appeal on a second case, citing the specific denial reason

## 10. Pitch Script (say before the demo)
"Prior authorization is one of the most hated workflows in healthcare — as of this year, CMS now requires decisions within 7 days, and specific denial reasons instead of boilerplate. Automating it with agents is the easy part; the hard part is trust: can a clinician see *why* the agent made a call, and can the system survive a payer API going down or sending garbage data? That's what this demo shows — every decision is fully traceable, and every failure mode is tested, not hoped away."

## 11. Fallback Plan
Keep one fully-populated `traces/` folder from a successful pre-run, plus 2–3 screenshots of the Lens and Chaos views. If live LLM calls fail during the real demo, switch to replaying the saved traces — the UI can't tell the difference, and the story still lands.

---

## 12. Agent Prompt Intents (role, not code)
| Agent | Reads | Must produce | Guardrail |
|---|---|---|---|
| Intake | Raw chart notes, orders, dictation | Structured clinical summary (diagnosis, procedure requested, supporting evidence) | Never infer a diagnosis not present in the source text |
| Policy Match | Clinical summary + payer policy criteria | List of matched/unmatched criteria, per clause | If a clause is ambiguous, mark "needs human review," never assume compliance |
| Justification | Matched criteria + summary | Submission narrative, suggested CPT/ICD code, confidence score (0–100) | Confidence below a threshold auto-routes to human, not auto-submit |
| Submission | Approved justification | Formatted payer submission payload | No network call without human-gate approval flag set |
| Appeal | Denial reason + original case | Appeal narrative citing the exact denial clause | If denial reason is vague/contradictory, escalate instead of drafting |

## 13. Frontend Wireframe (structure, not implementation)
**Tab 1 — Case Queue**: table of cases (patient ref, procedure, status, SLA countdown, confidence score); row click opens case detail; color-coded urgency (red = near SLA breach).
**Tab 2 — Lens Viewer**: left panel = case list; right panel toggles between "Clinician View" (plain-language reasoning steps) and "Technical View" (raw trace JSON, latency per step, tool calls); a "Replay" button reloads a past trace read-only.
**Tab 3 — Chaos Panel**: list of scenario toggles (payer timeout, malformed JSON, vague denial, missing field, cascading failure); a "Run Selected Case with Chaos" button; below it, the Resilience Scorecard as a simple pass/fail table per scenario.
**Case Detail (shared across tabs)**: header with case status, body with justification narrative, human-gate approve/reject buttons, denial/appeal section if applicable.

## 14. API Contract (routes described, not implemented)
| Method + Path | Purpose |
|---|---|
| `GET /cases` | List all cases with status/SLA summary |
| `GET /cases/{id}` | Full case detail including latest agent outputs |
| `POST /cases/{id}/run` | Trigger the pipeline (intake → justification) for a case |
| `POST /cases/{id}/approve` | Human-gate approval → triggers submission |
| `POST /cases/{id}/reject` | Human-gate rejection → case marked for rework |
| `GET /traces/{id}` | Full trace for a case (feeds Lens views) |
| `POST /chaos/toggle` | Enable/disable a named chaos scenario |
| `POST /cases/{id}/run-with-chaos` | Rerun a case with the active chaos scenario applied |
| `GET /scorecard` | Aggregate pass/fail counts per chaos scenario |

## 15. Synthetic Data Schema (fields, not files)
**Case object**: id, patient_ref, procedure_requested, chart_notes, payer_id, status, sla_deadline, confidence_score.
**Policy object**: payer_id, procedure, inclusion_criteria (list), exclusion_criteria (list), required_documentation (list).
Cover in the sample set: 1 clean/complete case, 1 ambiguous case, 1 missing-field case, 1 case that should predictably deny, 1 case that should predictably approve.

## 16. Human Review Interaction Flow
Case reaches "pending_review" status after Justification Agent runs → reviewer opens Case Detail → sees narrative + confidence score + matched/unmatched criteria → clicks Approve (→ status becomes "submitting," Submission Agent fires) or Reject (→ status becomes "needs_rework," case returns to Intake with reviewer's note attached). No case reaches Submission without this explicit state transition.

## 17. Model/Config Specs (settings, not code)
Use one consistent model across all agents for the demo (avoid mixing model versions — it complicates trace comparison). Low temperature (near-deterministic) for Policy Match and Submission steps, since these need consistency; slightly higher temperature is acceptable for the Justification narrative, since it's prose. Cap output length per step — these are structured, short outputs, not long-form generation.

## 18. Dependencies (names only)
Backend: a web framework (FastAPI-equivalent), an LLM client SDK, a data-validation library (schema enforcement), an HTTP client (for the mock payer calls). Frontend: no framework required for a wireframe — static HTML/CSS/JS is enough to demonstrate the three tabs. No database — flat JSON files are sufficient for today's scope.

## 19. Verification Checkpoints (per build stage)
- After synthetic data: confirm each case/policy file parses and has all required fields
- After happy-path pipeline: one clean case reaches "submitted" status with no errors
- After Lens wiring: trace file exists per case, both views render from the same source without duplication
- After chaos wiring: each scenario, when toggled, visibly changes agent behavior (not just the payer response) and is tagged in the trace
- After frontend: all three tabs load without a backend call failing silently
- Before demo: run the full 6-step script once, uninterrupted, timed
