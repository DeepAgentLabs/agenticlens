"""The v0.5 examples must reproduce their committed artifacts from a clean checkout."""

import json
import runpy
from pathlib import Path
from typing import Any

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
#: Wall-clock measurements that legitimately differ between runs.
MEASURED = {"judge_latency_ms", "latency_ms"}


def _without_measured(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _without_measured(v) for k, v in value.items() if k not in MEASURED}
    if isinstance(value, list):
        return [_without_measured(item) for item in value]
    if isinstance(value, float):
        return round(value, 9)
    return value


def _load(path: Path) -> Any:
    return json.loads(path.read_text("utf-8"))


def test_diagnosis_demo_reproduces_saved_artifacts(tmp_path: Path) -> None:
    module = runpy.run_path(str(EXAMPLES / "diagnosis_demo.py"))
    module["main"](tmp_path)
    saved = EXAMPLES / "diagnosis" / "artifacts"
    assert _load(tmp_path / "diagnosis.json") == _load(saved / "diagnosis.json")
    assert (tmp_path / "investigation.md").read_text("utf-8") == (
        saved / "investigation.md"
    ).read_text("utf-8")
    for trace in (saved / "baseline").glob("*.json"):
        assert _load(tmp_path / "baseline" / trace.name) == _load(trace)


def test_advanced_evaluation_demo_reproduces_saved_artifacts(tmp_path: Path) -> None:
    module = runpy.run_path(str(EXAMPLES / "advanced_evaluation_demo.py"))
    module["main"](tmp_path / "artifacts")
    saved = EXAMPLES / "advanced_evaluation"
    for name in ("evaluation.json", "score-analysis.json"):
        produced = _load(tmp_path / "artifacts" / name)
        assert _without_measured(produced) == _without_measured(_load(saved / "artifacts" / name))
    assert _load(tmp_path / "samples.json") == _load(saved / "samples.json")
    assert "Score analysis" in (tmp_path / "artifacts" / "evaluation.html").read_text("utf-8")
