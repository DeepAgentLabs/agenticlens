"""
mock_services/chaos_proxy.py
----------------------------
Fault-injection layer using the official DeepAgentLabs agentic-chaos library.

Available fault names (passed as strings to set_active_chaos):
  "token_timeout"       — TokenTimeoutFault:     hangs call, raises TokenTimeoutError
  "rate_limit_storm"    — RateLimitStormFault:   simulates burst of 429/backoff cascades
  "handoff_corruption"  — HandoffCorruptionFault: corrupts the payer payload before delivery
  "silent_degradation"  — SilentDegradationFault: silently returns a degraded/empty result
  "tool_call_failure"   — ToolCallFailureFault:   raises on the payer API tool call
"""

from agentic_chaos import (
    chaos_session,
    chaos_call,
    TokenTimeoutFault,
    RateLimitStormFault,
    HandoffCorruptionFault,
    SilentDegradationFault,
    ToolCallFailureFault,
)

from mock_services.payer_api import real_mock_payer_call

# ---------------------------------------------------------------------------
# Map string scenario names → agentic_chaos Fault instances
# ---------------------------------------------------------------------------
FAULT_MAP = {
    "token_timeout": TokenTimeoutFault(hang_seconds=5.0, mode="raise"),
    "rate_limit_storm": RateLimitStormFault(burst_count=3, retry_after=1.0),
    "handoff_corruption": HandoffCorruptionFault(mode="corrupt"),
    "silent_degradation": SilentDegradationFault(),
    "tool_call_failure": ToolCallFailureFault(tool_name="payer_api"),
}

# Domain aliases for UI scenarios
FAULT_MAP["payer_timeout"] = FAULT_MAP["token_timeout"]
FAULT_MAP["malformed_json"] = FAULT_MAP["handoff_corruption"]
FAULT_MAP["corrupted_response"] = FAULT_MAP["handoff_corruption"]
FAULT_MAP["vague_denial"] = FAULT_MAP["silent_degradation"]
FAULT_MAP["missing_field"] = FAULT_MAP["tool_call_failure"]
FAULT_MAP["payer_500"] = FAULT_MAP["tool_call_failure"]

ACTIVE_CHAOS_SCENARIO: str | None = None


def set_active_chaos(scenario_name: str | None):
    global ACTIVE_CHAOS_SCENARIO
    if scenario_name is None or scenario_name in FAULT_MAP:
        ACTIVE_CHAOS_SCENARIO = scenario_name
        return True
    return False


def get_active_chaos() -> str | None:
    return ACTIVE_CHAOS_SCENARIO


def call_payer_api(payload: dict, active_scenario: str | None = None) -> dict:
    """
    Proxy that routes through the agentic-chaos fault injection layer.

    If no chaos scenario is active, calls the mock payer directly.
    If a scenario is active, wraps the call inside chaos_session + chaos_call
    so the fault fires exactly as the real agentic-chaos library defines it.
    """
    scenario = active_scenario or ACTIVE_CHAOS_SCENARIO

    if not scenario or scenario not in FAULT_MAP:
        # Clean path — no chaos
        return real_mock_payer_call(payload)

    fault = FAULT_MAP[scenario]

    try:
        with chaos_session([fault]):
            result = chaos_call(
                real_mock_payer_call,
                payload,
                step_name="payer_api_submission",
                faults=[fault.name],
            )
        return result
    except Exception as e:
        # agentic_chaos raised a fault error — re-raise so the agent handles it
        raise e
