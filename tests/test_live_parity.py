"""Python and HTTP live targets must produce the same report for the same outputs.

Targets here return AgenticLens `Run`-shaped traces, so this also covers the
`to_eval_trace_dict` adapter on both paths (closing the v0.3 parity criterion).
"""

import json
import threading
from collections.abc import Iterator
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import pytest

from agenticlens.evaluation import HTTPTarget, PythonTarget, run_live_suite
from agenticlens.evaluation import TestCase as EvalCase
from agenticlens.evaluation import TestSuite as EvalSuite

SUITE = EvalSuite(
    name="parity",
    version="1",
    cases=[
        EvalCase(
            id="refund",
            name="Refund answer",
            input={"question": "refund?"},
            expected_contains=["refund"],
            required_tools=["policy_lookup"],
            max_latency_ms=200,
            max_cost_usd=0.01,
        ),
        EvalCase(
            id="escalate",
            name="Escalation answer",
            input={"question": "angry customer"},
            expected_output="escalated",
            forbidden_tools=["issue_refund"],
        ),
        EvalCase(
            id="slow",
            name="Slow answer",
            input={"question": "slow"},
            max_latency_ms=10,
        ),
    ],
)

STARTED = datetime(2026, 10, 1, tzinfo=timezone.utc)


def _run_payload(question: str, case_id: str) -> dict[str, Any]:
    latency = 50 if question == "slow" else 20
    tool = "issue_refund" if question == "angry customer" else "policy_lookup"
    output = "Your refund is approved." if question == "refund?" else "escalated"
    return {
        "output": output,
        "trace": {
            "trace_id": f"trace-{case_id}",
            "application_name": "parity",
            "started_at": STARTED.isoformat(),
            "completed_at": (STARTED + timedelta(milliseconds=latency)).isoformat(),
            "status": "succeeded",
            "metadata": {"cost_source": "measured"},
            "spans": [
                {
                    "name": tool,
                    "span_type": "tool_call",
                    "tool_name": tool,
                    "estimated_cost_usd": 0.002,
                }
            ],
        },
    }


def run_case(payload: dict[str, Any], *, case: EvalCase) -> dict[str, Any]:
    return _run_payload(payload["question"], case.id)


class _Handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:  # noqa: N802 - http.server API
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        data = json.dumps(_run_payload(body["input"]["question"], body["case_id"])).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        return


@pytest.fixture
def http_url() -> Iterator[str]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}/agent"
    finally:
        server.shutdown()
        server.server_close()


def _signature(report: Any) -> list[Any]:
    return [
        (
            case.case_id,
            case.passed,
            case.trace_id,
            case.latency_ms,
            case.cost_usd,
            case.cost_source,
            [(s.name, s.value, s.passed, s.evaluator) for s in case.scores],
        )
        for case in report.cases
    ]


@pytest.mark.parametrize("max_workers", [1, 3])
def test_python_and_http_targets_produce_identical_reports(http_url: str, max_workers: int) -> None:
    python_report = run_live_suite(
        SUITE,
        PythonTarget(callable_path=f"{Path(__file__)}:run_case"),
        max_workers=max_workers,
    )
    http_report = run_live_suite(SUITE, HTTPTarget(url=http_url), max_workers=max_workers)

    assert _signature(python_report) == _signature(http_report)
    assert python_report.summary.model_dump() == http_report.summary.model_dump()


def test_parity_suite_exercises_pass_fail_latency_and_cost(http_url: str) -> None:
    report = run_live_suite(SUITE, HTTPTarget(url=http_url))

    by_id = {case.case_id: case for case in report.cases}
    assert by_id["refund"].passed
    assert not by_id["escalate"].passed  # forbidden refund tool was called
    assert not by_id["slow"].passed  # 50 ms exceeds the 10 ms limit
    assert by_id["refund"].latency_ms == 20
    assert by_id["refund"].cost_source == "measured"
    assert report.summary.total_cost_usd == pytest.approx(0.006)
