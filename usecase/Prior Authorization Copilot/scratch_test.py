import sys
import os

# Add root directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import app, load_cases_data, run_case_pipeline, approve_human_gate, trigger_appeal, run_case_with_chaos, reset_demo
from agents.base import get_trace, get_all_scorecards

def test_full_pipeline():
    print("=== STARTING PRE-FLIGHT VERIFICATION ===")
    
    # 1. Reset state
    print("1. Resetting demo state...")
    reset_res = reset_demo()
    print("   Reset result:", reset_res)
    
    # 2. Run Happy-Path Pipeline for CASE-001
    print("\n2. Executing pipeline for CASE-001 (Clean Knee Replacement Case)...")
    res1 = run_case_pipeline("CASE-001")
    print(f"   Status: {res1['status']} | Confidence: {res1['confidence_score']}%")
    print("   Routing reason:", res1['justification']['routing_reason'])
    
    # 3. Approve Human Gate for CASE-001
    print("\n3. Approving Human Gate for CASE-001...")
    app_res = approve_human_gate("CASE-001")
    print("   Submission Status:", app_res['status'])
    print("   Payer Auth #:", app_res['submission_result'].get('payer_adjudication', {}).get('authorization_number'))

    # 4. Verify Trace File for CASE-001
    print("\n4. Checking Agentic Lens trace log for CASE-001...")
    traces = get_trace("CASE-001")
    print(f"   Captured trace steps: {len(traces)}")
    for t in traces:
        print(f"   - Step: {t['step']:<15} | Status: {t['status']:<8} | Latency: {t['latency_ms']}ms")

    # 5. Execute Chaos Scenario: payer_timeout on CASE-002
    print("\n5. Executing Chaos Scenario (payer_timeout) on CASE-002...")
    chaos_res = run_case_with_chaos("CASE-002", "payer_timeout")
    print(f"   Chaos Run Status: {chaos_res['submission_result'].get('status')}")
    print(f"   Gracefully handled error: {chaos_res['submission_result'].get('error')}")

    # 6. Draft Appeal for CASE-006
    print("\n6. Drafting Appeal for CASE-006 (Denied MRI Case)...")
    appeal_res = trigger_appeal("CASE-006")
    print("   Appeal Status:", appeal_res['status'])
    print("   Letter summary snippet:\n", appeal_res['appeal_result']['appeal_letter_narrative'][:250], "...")

    # 7. Check Scorecard
    print("\n7. Checking Resilience Scorecard...")
    scorecard = get_all_scorecards()
    for sc, val in scorecard.items():
        print(f"   - Scenario: {sc:<20} | Tested: {val['tested']} | Passed: {val['passed']} | Result: {val['last_result']}")

    print("\n=== VERIFICATION COMPLETE: ALL SYSTEMS GO ===")

if __name__ == "__main__":
    test_full_pipeline()
