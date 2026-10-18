"""Recommend a model per support task category from a recorded experiment.

Replays the four-model support experiment in examples/modelfit (no model or
network calls), then runs ModelFit with examples/modelfit/modelfit.yaml and
writes the experiment report, the ModelFit report (JSON and Markdown), and
the task-level model matrix (CSV) to examples/modelfit/artifacts/.

    python examples/modelfit_demo.py

The CLI equivalent:

    agenticlens experiment run examples/modelfit/support-experiment.yaml \\
      examples/modelfit/support-suite.yaml \\
      --save examples/modelfit/artifacts/experiment.json
    agenticlens modelfit recommend examples/modelfit/artifacts/experiment.json \\
      --config examples/modelfit/modelfit.yaml \\
      --manifest examples/modelfit/support-experiment.yaml \\
      --save examples/modelfit/artifacts/modelfit.json \\
      --markdown examples/modelfit/artifacts/modelfit.md \\
      --csv examples/modelfit/artifacts/model-matrix.csv
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agenticlens.experiments import load_experiment_suite, load_manifest, run_experiment
from agenticlens.modelfit import (
    load_experiment_evidence,
    load_modelfit_config,
    recommend_models,
    save_markdown,
    save_matrix_csv,
    save_modelfit_report,
)

EXAMPLE = Path(__file__).resolve().parent / "modelfit"


def main(artifacts: Path | None = None) -> dict[str, Any]:
    artifacts = artifacts or EXAMPLE / "artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)

    manifest = load_manifest(EXAMPLE / "support-experiment.yaml")
    experiment = run_experiment(manifest, load_experiment_suite(EXAMPLE / "support-suite.yaml"))
    experiment_path = artifacts / "experiment.json"
    experiment_path.write_text(experiment.model_dump_json(indent=2) + "\n", encoding="utf-8")

    report = recommend_models(
        [load_experiment_evidence(experiment_path)],
        load_modelfit_config(EXAMPLE / "modelfit.yaml"),
        variant_metadata={variant.id: dict(variant.metadata) for variant in manifest.variants},
    )
    save_modelfit_report(report, artifacts / "modelfit.json")
    save_markdown(report, artifacts / "modelfit.md")
    save_matrix_csv(report, artifacts / "model-matrix.csv")

    recommendations: dict[str, str | None] = {}
    for result in report.categories:
        rec = result.recommendation
        recommendations[result.category.id] = rec.variant_id
        if rec.status != "recommended":
            print(f"{result.category.id:8} {rec.status}")
            continue
        saving = ""
        if rec.savings and rec.savings.projected_monthly_savings_usd is not None:
            saving = f", saves ${rec.savings.projected_monthly_savings_usd:,.2f}/month"
        fallback = rec.fallback.variant_id if rec.fallback else "none"
        print(
            f"{result.category.id:8} {rec.variant_id:10} confidence {rec.confidence:6} "
            f"fallback {fallback}{saving}"
        )
    print(f"Reports written to {artifacts}")
    return {
        "recommendations": recommendations,
        "unfit": report.summary.unfit_category_ids,
        "warnings": report.warnings,
    }


if __name__ == "__main__":
    main()
