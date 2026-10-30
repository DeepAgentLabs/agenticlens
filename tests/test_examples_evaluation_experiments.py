"""The v0.3/v0.4 examples must keep running from a clean checkout."""

import json
import runpy
import shutil
from pathlib import Path
from typing import Any

import pytest
from agentic_evals import __version__ as evals_version

from agenticlens.experiments import load_experiment_suite, load_manifest, run_experiment

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


def _rounded(value: Any) -> Any:
    """Round floats so summation-order noise across Python versions compares equal."""
    if isinstance(value, float):
        return round(value, 9)
    if isinstance(value, dict):
        return {key: _rounded(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_rounded(item) for item in value]
    return value


@pytest.mark.parametrize("script", ["structured_judge_demo.py", "gate_alert_demo.py"])
def test_example_runs(script: str, capsys: pytest.CaptureFixture[str]) -> None:
    runpy.run_path(str(EXAMPLES / script), run_name="__main__")
    assert capsys.readouterr().out


def test_recorded_experiment_reproduces_saved_results(tmp_path: Path) -> None:
    source = EXAMPLES / "experiments"
    copy = tmp_path / "experiments"
    shutil.copytree(source, copy, ignore=shutil.ignore_patterns("artifacts", "__pycache__"))

    report = run_experiment(
        load_manifest(copy / "support-experiment.yaml"),
        load_experiment_suite(copy / "support-suite.yaml"),
    )
    saved = json.loads((source / "artifacts" / "support-experiment.json").read_text())

    fresh = json.loads(report.model_dump_json())
    # Saved examples retain the producer version they were generated with.
    # Assert current provenance independently before comparing stable results.
    for variant in fresh["variants"]:
        for trial in variant["trials"]:
            if trial["report"]:
                for case in trial["report"]["cases"]:
                    for score in case["scores"]:
                        if score["evaluator"] == "agentic_evals.builtin":
                            assert score["evaluator_version"] == evals_version
    for document in (fresh, saved):
        document.pop("created_at")
        for variant in document["variants"]:
            for trial in variant["trials"]:
                if trial["report"]:
                    trial["report"].pop("created_at")
                    for case in trial["report"]["cases"]:
                        for score in case["scores"]:
                            if score["evaluator"] == "agentic_evals.builtin":
                                assert score.pop("evaluator_version")
    assert _rounded(fresh) == _rounded(saved)
