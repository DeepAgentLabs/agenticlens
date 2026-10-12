"""Replay the recorded support experiment and write JSON, HTML, and CSV reports.

Uses only saved outputs in ./recorded (see record_trials.py), so the result is
the same on every machine and needs no model or network access.

    python examples/experiments/run_recorded_experiment.py

The CLI equivalent:

    agenticlens experiment run examples/experiments/support-experiment.yaml \\
      examples/experiments/support-suite.yaml \\
      --save examples/experiments/artifacts/support-experiment.json \\
      --html examples/experiments/artifacts/support-experiment.html \\
      --csv examples/experiments/artifacts/support-experiment-variants.csv \\
      --cases-csv examples/experiments/artifacts/support-experiment-cases.csv
"""

from pathlib import Path

from agenticlens.experiments import (
    load_experiment_suite,
    load_manifest,
    run_experiment,
    save_case_matrix_csv,
    save_experiment_html,
    save_variant_csv,
)

HERE = Path(__file__).resolve().parent
ARTIFACTS = HERE / "artifacts"


def main() -> None:
    report = run_experiment(
        load_manifest(HERE / "support-experiment.yaml"),
        load_experiment_suite(HERE / "support-suite.yaml"),
    )
    ARTIFACTS.mkdir(exist_ok=True)
    (ARTIFACTS / "support-experiment.json").write_text(report.model_dump_json(indent=2) + "\n")
    save_experiment_html(report, ARTIFACTS / "support-experiment.html")
    save_variant_csv(report, ARTIFACTS / "support-experiment-variants.csv")
    save_case_matrix_csv(report, ARTIFACTS / "support-experiment-cases.csv")

    for comparison in report.comparisons:
        delta = comparison.case_pass_rate_delta or 0.0
        print(
            f"{comparison.candidate_variant_id:20} {delta:+.1%} vs baseline "
            f"(p={comparison.case_pass_rate_p_value:.3f}), changed {comparison.changed_factors}"
        )
    print(f"Pareto frontier: {', '.join(report.pareto_frontier_variant_ids)}")
    print(f"Reports written to {ARTIFACTS}")


if __name__ == "__main__":
    main()
