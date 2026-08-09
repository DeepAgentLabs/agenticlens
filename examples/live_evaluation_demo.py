from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from agenticlens.evaluation import PythonTarget, TestCase, TestSuite, run_live_suite


def run_case(payload, *, case):
    """Trusted Python target for `agenticlens evaluate-live`.

    The callable returns the same structure expected by `EvaluationSample`
    minus `case_id`, which AgenticLens supplies from the suite.
    """
    started = datetime.now(timezone.utc)
    answer = {
        "answer": f"Refund for order {payload['order_id']} is in progress.",
        "meta": {"confidence": 0.94},
    }
    trace = {
        "application_name": "live-demo",
        "started_at": started.isoformat(),
        "completed_at": (started + timedelta(milliseconds=35)).isoformat(),
        "status": "succeeded",
        "task_success": True,
        "metadata": {"turn_count": 1, "case_name": case.name},
        "spans": [
            {
                "name": "lookup refund",
                "span_type": "tool_call",
                "status": "succeeded",
                "tool_name": "lookup_refund",
                "estimated_cost_usd": 0.002,
                "attributes": {"tool_args": {"order_id": payload["order_id"]}},
            }
        ],
    }
    return {"output": json.dumps(answer), "trace": trace}


def main() -> None:
    suite = TestSuite(
        name="live-evaluation-demo",
        version="1",
        cases=[
            TestCase(
                id="refund-1",
                name="Refund answer stays structured",
                input={"order_id": "A123"},
                required_tools=["lookup_refund"],
                required_tool_arguments={"lookup_refund": ["order_id"]},
                output_json_schema={
                    "type": "object",
                    "required": ["answer", "meta"],
                    "properties": {
                        "answer": {"type": "string"},
                        "meta": {
                            "type": "object",
                            "required": ["confidence"],
                        },
                    },
                },
                required_output_fields=["meta.confidence"],
                max_turns=1,
                max_latency_ms=250,
                max_cost_usd=0.01,
            )
        ],
    )

    report = run_live_suite(
        suite,
        PythonTarget(callable_path="examples/live_evaluation_demo.py:run_case"),
    )
    print(report.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
