"""Load traces and configs; save and reload optimization artifacts."""

import json
from collections.abc import Sequence
from pathlib import Path

import yaml

from agenticlens.models.trace import Run
from agenticlens.optimization.models import OptimizationConfig, OptimizationReport


def load_traces(paths: Sequence[Path]) -> list[Run]:
    """Load trace JSON files; a directory contributes its `*.json` files in name order."""
    files: list[Path] = []
    for path in paths:
        files.extend(sorted(path.glob("*.json")) if path.is_dir() else [path])
    if not files:
        raise ValueError("no trace JSON files found")
    return [Run.model_validate_json(file.read_text(encoding="utf-8")) for file in files]


def load_optimization_config(path: Path) -> OptimizationConfig:
    """YAML or JSON. Unknown keys are rejected so a typo cannot drop a threshold."""
    text = path.read_text(encoding="utf-8")
    raw = json.loads(text) if path.suffix == ".json" else yaml.safe_load(text)
    return OptimizationConfig.model_validate(raw or {})


def save_optimization_report(report: OptimizationReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report.model_dump_json(indent=2) + "\n", encoding="utf-8")


def load_optimization_report(path: Path) -> OptimizationReport:
    return OptimizationReport.model_validate_json(path.read_text(encoding="utf-8"))
