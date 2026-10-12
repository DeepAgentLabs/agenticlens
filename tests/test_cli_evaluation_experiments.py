"""CLI coverage for the v0.3 evidence/alerting flags and v0.4 experiment reports."""

import json
import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from agenticlens.cli.main import app

runner = CliRunner()


def _suite(path: Path) -> Path:
    path.write_text(
        json.dumps(
            {
                "name": "cli",
                "version": "1",
                "cases": [
                    {"id": "a", "name": "A", "expected_output": "ok"},
                    {"id": "b", "name": "B", "expected_output": "ok"},
                ],
            }
        ),
        encoding="utf-8",
    )
    return path


def _samples(path: Path, *, with_b: bool = True) -> Path:
    samples = [
        {
            "case_id": "a",
            "output": "ok",
            "trace": {"trace_id": "t-a", "estimated_cost_usd": 0.01, "cost_source": "measured"},
        }
    ]
    if with_b:
        samples.append({"case_id": "b", "output": "no", "trace": {"trace_id": "t-b"}})
    path.write_text(json.dumps({"samples": samples}), encoding="utf-8")
    return path


def test_evaluate_prints_and_saves_evidence_audit(tmp_path: Path) -> None:
    audit = tmp_path / "audit.json"
    result = runner.invoke(
        app,
        [
            "evaluate",
            str(_suite(tmp_path / "suite.json")),
            str(_samples(tmp_path / "samples.json")),
            "--save",
            str(tmp_path / "report.json"),
            "--audit",
            str(audit),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Evidence:" in result.output
    assert "cost 1/2 priced (measured 1)" in " ".join(result.output.split())
    saved = json.loads(audit.read_text())
    assert saved["failed_cases_with_trace"] == 1
    assert saved["passed"] is True


def test_strict_evidence_fails_on_untraceable_failures(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "evaluate",
            str(_suite(tmp_path / "suite.json")),
            str(_samples(tmp_path / "samples.json", with_b=False)),
            "--save",
            str(tmp_path / "report.json"),
            "--strict-evidence",
        ],
    )

    assert result.exit_code == 3
    assert "has no sample" in result.output


class _Hook(BaseHTTPRequestHandler):
    received: list[dict[str, Any]] = []

    def do_POST(self) -> None:  # noqa: N802 - http.server API
        _Hook.received.append(json.loads(self.rfile.read(int(self.headers["Content-Length"]))))
        self.send_response(204)
        self.end_headers()

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        return


@pytest.fixture
def hook_url() -> Iterator[str]:
    _Hook.received = []
    server = ThreadingHTTPServer(("127.0.0.1", 0), _Hook)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}/hook"
    finally:
        server.shutdown()
        server.server_close()


def test_gate_alerts_once_then_respects_cooldown(tmp_path: Path, hook_url: str) -> None:
    report = tmp_path / "report.json"
    runner.invoke(
        app,
        [
            "evaluate",
            str(_suite(tmp_path / "suite.json")),
            str(_samples(tmp_path / "samples.json")),
            "--save",
            str(report),
        ],
    )
    args = [
        "gate",
        str(report),
        "--notify-webhook",
        hook_url,
        "--notify-format",
        "slack",
        "--notify-state",
        str(tmp_path / "state.json"),
    ]

    first = runner.invoke(app, args)
    second = runner.invoke(app, args)

    assert first.exit_code == 2 and second.exit_code == 2
    assert "Alert sent for: pass_rate" in first.output
    assert "suppressed (cooldown)" in second.output
    assert len(_Hook.received) == 1
    assert "release gate failed" in _Hook.received[0]["text"]


def test_gate_alert_failure_does_not_hide_gate_result(tmp_path: Path) -> None:
    report = tmp_path / "report.json"
    runner.invoke(
        app,
        [
            "evaluate",
            str(_suite(tmp_path / "suite.json")),
            str(_samples(tmp_path / "samples.json")),
            "--save",
            str(report),
        ],
    )

    result = runner.invoke(
        app,
        [
            "gate",
            str(report),
            "--notify-webhook",
            "http://127.0.0.1:9/unreachable",
            "--notify-state",
            str(tmp_path / "state.json"),
        ],
    )

    assert result.exit_code == 2
    assert "Gate alert not sent" in result.output


def test_gate_rejects_unknown_notify_format(tmp_path: Path) -> None:
    result = runner.invoke(
        app, ["gate", str(tmp_path / "missing.json"), "--notify-format", "pager"]
    )
    assert result.exit_code == 1


def _calibration_inputs(tmp_path: Path) -> tuple[Path, Path]:
    report = {
        "suite_name": "s",
        "suite_version": "1",
        "summary": {
            "total_cases": 4,
            "passed_cases": 4,
            "failed_cases": 0,
            "pass_rate": 1,
            "average_score": 0.7,
            "average_latency_ms": 0,
        },
        "cases": [
            {
                "case_id": str(i),
                "case_name": str(i),
                "passed": True,
                "output": "",
                "trace_id": f"t{i}",
                "latency_ms": 0,
                "scores": [
                    {
                        "name": "judge",
                        "value": value,
                        "passed": True,
                        "explanation": "",
                        "evaluator_type": "llm_judge",
                    }
                ],
            }
            for i, value in enumerate([0.9, 0.8, 0.6, 0.55])
        ],
    }
    labels = {
        "name": "labels",
        "version": "1",
        "suite_name": "s",
        "suite_version": "1",
        "labels": [{"case_id": str(i), "passed": i < 2} for i in range(4)],
    }
    report_path = tmp_path / "report.json"
    labels_path = tmp_path / "labels.json"
    report_path.write_text(json.dumps(report), encoding="utf-8")
    labels_path.write_text(json.dumps(labels), encoding="utf-8")
    return report_path, labels_path


def test_calibrate_can_tune_the_threshold(tmp_path: Path) -> None:
    report, labels = _calibration_inputs(tmp_path)
    tuning = tmp_path / "tuning.json"

    result = runner.invoke(
        app,
        [
            "calibrate",
            str(report),
            str(labels),
            "--evaluator",
            "judge",
            "--save",
            str(tmp_path / "calibration.json"),
            "--tune-threshold",
            str(tuning),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Recommended threshold: 0.800" in result.output
    assert json.loads(tuning.read_text())["recommended_threshold"] == 0.8


def _experiment(tmp_path: Path) -> tuple[Path, Path]:
    suite = _suite(tmp_path / "suite.json")
    variants = []
    for variant_id, output in (("base", "ok"), ("cand", "no"), ("cand2", "ok")):
        trials = [
            [
                {
                    "case_id": case_id,
                    "output": output,
                    "trace": {"trace_id": f"{variant_id}-{case_id}", "total_latency_ms": 5},
                }
                for case_id in ("a", "b")
            ]
            for _ in range(2)
        ]
        (tmp_path / f"{variant_id}.json").write_text(json.dumps({"trials": trials}))
        variants.append(
            {
                "id": variant_id,
                "name": variant_id,
                "target_kind": "recorded",
                "target": f"{variant_id}.json",
                "factors": {"prompt": variant_id},
            }
        )
    manifest = tmp_path / "experiment.json"
    manifest.write_text(
        json.dumps(
            {
                "name": "cli-exp",
                "version": "1",
                "baseline_variant_id": "base",
                "trial_count": 2,
                "variants": variants,
            }
        )
    )
    return manifest, suite


def test_experiment_run_writes_json_html_and_csv(tmp_path: Path) -> None:
    manifest, suite = _experiment(tmp_path)
    out = tmp_path / "out"

    result = runner.invoke(
        app,
        [
            "experiment",
            "run",
            str(manifest),
            str(suite),
            "--save",
            str(out / "exp.json"),
            "--html",
            str(out / "exp.html"),
            "--csv",
            str(out / "variants.csv"),
            "--cases-csv",
            str(out / "cases.csv"),
        ],
    )

    assert result.exit_code == 0, result.output
    output = " ".join(result.output.split())
    assert "Baseline Deltas" in output
    assert "fewer than 5" in output
    for name in ("exp.json", "exp.html", "variants.csv", "cases.csv"):
        assert (out / name).exists()
    html = (out / "exp.html").read_text()
    assert "pass@2" in html and "prompt: base → cand" in html
    assert "pass_at_2" in (out / "variants.csv").read_text()


def test_experiment_report_re_renders_saved_results(tmp_path: Path) -> None:
    manifest, suite = _experiment(tmp_path)
    saved = tmp_path / "exp.json"
    runner.invoke(app, ["experiment", "run", str(manifest), str(suite), "--save", str(saved)])

    result = runner.invoke(
        app, ["experiment", "report", str(saved), "--html", str(tmp_path / "again.html")]
    )

    assert result.exit_code == 0, result.output
    assert "Experiment · cli-exp" in result.output
    assert "Test-level heatmap" in (tmp_path / "again.html").read_text()


def test_experiment_report_rejects_invalid_file(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{}")
    result = runner.invoke(app, ["experiment", "report", str(bad)])
    assert result.exit_code == 1


def test_evaluate_live_supports_workers_and_html(tmp_path: Path) -> None:
    target = tmp_path / "target.py"
    target.write_text(
        "def run(payload, *, case):\n    return {'output': 'ok', 'trace': {'trace_id': case.id}}\n",
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        [
            "evaluate-live",
            str(_suite(tmp_path / "suite.json")),
            "--target-kind",
            "python",
            "--target",
            f"{target}:run",
            "--max-workers",
            "2",
            "--save",
            str(tmp_path / "live.json"),
            "--html",
            str(tmp_path / "live.html"),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "2/2 cases passed" in result.output
    assert (tmp_path / "live.html").exists()
