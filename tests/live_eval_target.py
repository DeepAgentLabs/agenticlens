from datetime import datetime, timedelta, timezone


def run_case(payload, *, case):
    started = datetime.now(timezone.utc)
    trace = {
        "application_name": "live-target",
        "started_at": started.isoformat(),
        "completed_at": (started + timedelta(milliseconds=25)).isoformat(),
        "status": "succeeded",
        "task_success": True,
        "metadata": {"turn_count": 1},
        "spans": [
            {
                "name": "tool",
                "span_type": "tool_call",
                "status": "succeeded",
                "tool_name": "add",
                "attributes": {"tool_args": {"a": 40, "b": 2}},
            }
        ],
    }
    return {"output": payload["response"], "trace": trace}
