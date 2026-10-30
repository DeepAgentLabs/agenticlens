"""Load ModelFit configs and reports, and save reports."""

import json
from pathlib import Path
from typing import Any

import yaml

from agenticlens.modelfit.models import ModelFitConfig, ModelFitReport


def _load_data(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        return yaml.safe_load(text)
    return json.loads(text)


def load_modelfit_config(path: Path) -> ModelFitConfig:
    """Load a ModelFit config from YAML or JSON."""
    return ModelFitConfig.model_validate(_load_data(path) or {})


def load_modelfit_report(path: Path) -> ModelFitReport:
    return ModelFitReport.model_validate_json(path.read_text(encoding="utf-8"))


def save_modelfit_report(report: ModelFitReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report.model_dump_json(indent=2) + "\n", encoding="utf-8")
