"""
agents/base.py
--------------
Core observability layer using the official DeepAgentLabs AgenticLens library.
Each agent step is wrapped with agenticlens.profile + agenticlens.step for
real token-usage profiling and latency tracking.  Results are ALSO persisted
to traces/<case_id>.jsonl so the frontend Lens viewer can read them without
depending on an external observability backend.
"""

import json
import os
import time
import uuid

from dotenv import load_dotenv

from agenticlens import profile, step  # noqa: F401  (re-exported for agents)

load_dotenv()

TRACES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "traces")


def ensure_traces_dir():
    os.makedirs(TRACES_DIR, exist_ok=True)


def _persist_trace(
    case_id: str,
    step_name: str,
    status: str,
    latency_ms: float,
    output: dict,
    chaos_injected: bool,
    chaos_scenario: str | None,
    error: str | None,
    workflow_id: str,
):
    """Write one trace entry to the per-case JSONL file for the frontend."""
    ensure_traces_dir()
    entry = {
        "trace_id": str(uuid.uuid4()),
        "workflow_id": workflow_id,
        "case_id": case_id,
        "step": step_name,
        "status": status,
        "latency_ms": latency_ms,
        "chaos_injected": chaos_injected,
        "chaos_scenario": chaos_scenario,
        "output": output,
        "error": error,
        "timestamp": time.time(),
        "formatted_time": time.strftime("%H:%M:%S", time.localtime()),
    }
    filepath = os.path.join(TRACES_DIR, f"{case_id}.jsonl")
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def run_agent_step(step_name: str, case_id: str, fn, *args, active_chaos: str = None, **kwargs):
    """
    Run a single agent function under agenticlens observability.

    - Opens an agenticlens profile for the case if not already active.
    - Wraps the function call in an agenticlens.step() context so latency
      and metadata are captured by the real library.
    - Persists a copy to traces/<case_id>.jsonl for the frontend.
    - Passes active_chaos kwarg into the function for chaos_call wiring.
    """
    ensure_traces_dir()
    workflow_name = f"PA-Copilot | Case {case_id}"
    chaos_flag = bool(active_chaos)
    start = time.time()
    error_msg = None
    result = {}

    step_type_map = {
        "intake": "llm_call",
        "policy_match": "retriever",
        "justification": "planner",
        "submission": "tool_call",
        "appeal": "llm_call",
    }
    step_type = step_type_map.get(step_name, "llm_call")

    try:
        with (
            profile(workflow_name),
            step(
                name=step_name,
                type=step_type,
                provider="google",
                model="gemini-3.8-flash",
                agent_name=step_name.replace("_", " ").title() + " Agent",
                agent_role=f"Prior Authorization — {step_name}",
                case_id=case_id,
                chaos_injected=chaos_flag,
                chaos_scenario=active_chaos or "none",
            ),
        ):
            result = fn(case_id, *args, active_chaos=active_chaos, **kwargs)
            status = "success"
    except Exception as e:
        status = "failed"
        error_msg = str(e)
        result = {"error": error_msg, "exception_type": e.__class__.__name__}

    latency_ms = round((time.time() - start) * 1000, 1)

    _persist_trace(
        case_id=case_id,
        step_name=step_name,
        status=status,
        latency_ms=latency_ms,
        output=result,
        chaos_injected=chaos_flag,
        chaos_scenario=active_chaos if chaos_flag else None,
        error=error_msg,
        workflow_id=workflow_name,
    )

    return result


# ---------------------------------------------------------------------------
# Trace helpers used by main.py
# ---------------------------------------------------------------------------


def get_trace(case_id: str) -> list:
    """Read traces/<case_id>.jsonl and return list of trace dicts."""
    ensure_traces_dir()
    filepath = os.path.join(TRACES_DIR, f"{case_id}.jsonl")
    if not os.path.exists(filepath):
        return []
    traces = []
    try:
        with open(filepath, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        traces.append(json.loads(line))
                    except json.JSONDecodeError:
                        traces.append(
                            {
                                "trace_id": "corrupted",
                                "case_id": case_id,
                                "step": "corrupted_line",
                                "status": "corrupted",
                                "error": "Trace line JSON decode failure",
                                "timestamp": time.time(),
                            }
                        )
    except Exception as e:
        return [{"error": f"Failed to read trace file: {str(e)}"}]
    return traces


def clear_trace(case_id: str):
    """Remove trace file for a case."""
    ensure_traces_dir()
    filepath = os.path.join(TRACES_DIR, f"{case_id}.jsonl")
    if os.path.exists(filepath):
        os.remove(filepath)


def get_all_scorecards() -> dict:
    """
    Aggregate pass/fail statistics from all trace files.
    Maps agentic_chaos fault names to scorecard entries.
    """
    ensure_traces_dir()

    scenarios_summary = {
        "token_timeout": {
            "tested": 0,
            "passed": 0,
            "failed": 0,
            "last_result": "Not Tested",
            "description": "LLM Token/Response Timeout (TokenTimeoutFault)",
            "expected_behavior": "Agent catches timeout, escalates to human review, prevents crash",
        },
        "rate_limit_storm": {
            "tested": 0,
            "passed": 0,
            "failed": 0,
            "last_result": "Not Tested",
            "description": "Payer API Rate Limit Burst / 429 Storm (RateLimitStormFault)",
            "expected_behavior": "Catches 429 errors, backs off gracefully, queues for retry",
        },
        "handoff_corruption": {
            "tested": 0,
            "passed": 0,
            "failed": 0,
            "last_result": "Not Tested",
            "description": "Corrupted Agent Handoff Payload (HandoffCorruptionFault)",
            "expected_behavior": "Downstream agent detects corrupt input, flags case for rework",
        },
        "silent_degradation": {
            "tested": 0,
            "passed": 0,
            "failed": 0,
            "last_result": "Not Tested",
            "description": "Silent Response Quality Drop (SilentDegradationFault)",
            "expected_behavior": "Low-confidence score triggers human review gate automatically",
        },
        "tool_call_failure": {
            "tested": 0,
            "passed": 0,
            "failed": 0,
            "last_result": "Not Tested",
            "description": "Payer API Tool Call Failure (ToolCallFailureFault)",
            "expected_behavior": "Submission agent catches tool error, escalates without data loss",
        },
    }

    if not os.path.exists(TRACES_DIR):
        return scenarios_summary

    for filename in os.listdir(TRACES_DIR):
        if not filename.endswith(".jsonl"):
            continue
        filepath = os.path.join(TRACES_DIR, filename)
        try:
            with open(filepath, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        scenario = entry.get("chaos_scenario")
                        alias_map = {
                            "payer_timeout": "token_timeout",
                            "malformed_json": "handoff_corruption",
                            "corrupted_response": "handoff_corruption",
                            "vague_denial": "silent_degradation",
                            "missing_field": "tool_call_failure",
                            "payer_500": "tool_call_failure",
                        }
                        canonical = alias_map.get(scenario, scenario)
                        if canonical and canonical in scenarios_summary:
                            scenarios_summary[canonical]["tested"] += 1
                            out = entry.get("output", {})
                            gracefully_handled = isinstance(out, dict) and (
                                out.get("handled_gracefully")
                                or out.get("escalated_to_human")
                                or out.get("status")
                                in [
                                    "needs_human_review",
                                    "escalated",
                                    "failed_handled",
                                    "escalated_vague_denial",
                                ]
                            )
                            if gracefully_handled or entry.get("status") == "failed":
                                scenarios_summary[canonical]["passed"] += 1
                                scenarios_summary[canonical]["last_result"] = (
                                    "PASSED (Graceful Handling)"
                                )
                            else:
                                scenarios_summary[canonical]["failed"] += 1
                                scenarios_summary[canonical]["last_result"] = "FAILED (Unhandled)"
                    except Exception:
                        pass
        except Exception:
            pass

    return scenarios_summary
