"""CLI: agenticlens modelfit ..."""

import csv
import json
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from agenticlens.cli.main import app
from modelfit_support import DEFAULT_CASES, Spec, build_report, passes, uniform


def _invoke(*args: object) -> tuple[int, str]:
    result = CliRunner().invoke(app, [str(arg) for arg in args])
    return result.exit_code, result.output


@pytest.fixture
def experiment(tmp_path: Path) -> Path:
    report = build_report(
        tmp_path,
        {
            "big": Spec(uniform(DEFAULT_CASES, passes(6)), cost=0.005),
            "mid": Spec(uniform(DEFAULT_CASES, passes(5, 1)), cost=0.002),
            "tiny": Spec(uniform(DEFAULT_CASES, passes(2, 4)), cost=0.0002),
        },
    )
    path = tmp_path / "experiment.json"
    path.write_text(report.model_dump_json(), encoding="utf-8")
    return path


@pytest.fixture
def config(tmp_path: Path) -> Path:
    path = tmp_path / "modelfit.yaml"
    path.write_text(
        yaml.safe_dump(
            {
                "name": "cli-test",
                "minimum_attempts": 5,
                "defaults": {"min_pass_rate": 0.8},
                "categories": [
                    {"id": "policy", "tags": ["policy"], "monthly_volume": 100},
                    {
                        "id": "orders",
                        "tags": ["orders"],
                        "constraints": {"allowed_providers": ["provider-x"]},
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    return path


def test_recommend_writes_json_markdown_and_matrix(
    tmp_path: Path, experiment: Path, config: Path
) -> None:
    save, markdown, matrix = tmp_path / "fit.json", tmp_path / "fit.md", tmp_path / "matrix.csv"
    code, output = _invoke(
        "modelfit", "recommend", experiment, "--config", config,
        "--save", save, "--markdown", markdown, "--csv", matrix,
    )  # fmt: skip

    assert code == 0, output
    assert "ModelFit: cli-test" in output
    report = json.loads(save.read_text("utf-8"))
    assert [c["category"]["id"] for c in report["categories"]] == ["all", "policy", "orders"]
    assert report["sources"][0]["file"] == "experiment.json"
    assert markdown.read_text("utf-8").startswith("# ModelFit: cli-test")
    rows = list(csv.DictReader(matrix.open(encoding="utf-8")))
    assert len(rows) == 9
    assert {row["role"] for row in rows if row["category_id"] == "orders"} == {"infeasible"}


def test_recommend_json_output(experiment: Path) -> None:
    code, output = _invoke("modelfit", "recommend", experiment, "--json")
    assert code == 0, output
    report = json.loads(output)
    assert report["summary"]["candidates"] == 3


def test_fail_on_unfit_exits_8(experiment: Path, config: Path) -> None:
    code, output = _invoke("modelfit", "recommend", experiment, "--config", config)
    assert code == 0, output

    code, output = _invoke(
        "modelfit", "recommend", experiment, "--config", config, "--fail-on-unfit"
    )
    assert code == 8
    assert "No feasible model for: orders" in output


def test_fail_on_low_confidence_exits_8(experiment: Path, tmp_path: Path) -> None:
    strict = tmp_path / "strict.json"
    strict.write_text(json.dumps({"minimum_attempts": 1000}), encoding="utf-8")
    code, output = _invoke(
        "modelfit", "recommend", experiment, "--config", strict, "--fail-on-low-confidence"
    )
    assert code == 8
    assert "Low-confidence recommendations for:" in output


def test_manifest_metadata_supplies_providers(experiment: Path, tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.yaml"
    manifest.write_text(
        yaml.safe_dump(
            {
                "name": "m",
                "version": "1",
                "baseline_variant_id": "big",
                "variants": [
                    {
                        "id": variant,
                        "name": variant,
                        "target_kind": "recorded",
                        "target": f"{variant}.json",
                        "metadata": {"provider": f"provider-{variant}"},
                    }
                    for variant in ("big", "mid", "tiny")
                ],
            }
        ),
        encoding="utf-8",
    )
    code, output = _invoke("modelfit", "recommend", experiment, "--manifest", manifest, "--json")
    assert code == 0, output
    report = json.loads(output)
    providers = {row["variant_id"]: row["provider"] for row in report["matrix"]}
    assert providers == {"big": "provider-big", "mid": "provider-mid", "tiny": "provider-tiny"}


def test_matrix_renders_a_saved_report(tmp_path: Path, experiment: Path) -> None:
    save = tmp_path / "fit.json"
    assert _invoke("modelfit", "recommend", experiment, "--save", save)[0] == 0
    matrix, markdown = tmp_path / "m.csv", tmp_path / "m.md"

    code, output = _invoke("modelfit", "matrix", save, "--csv", matrix, "--markdown", markdown)

    assert code == 0, output
    assert "Task-level model matrix" in output
    assert matrix.read_text("utf-8").startswith("category_id,")
    assert "## Task-level model matrix" in markdown.read_text("utf-8")


def test_taxonomy_lists_categories(experiment: Path, config: Path) -> None:
    code, output = _invoke("modelfit", "taxonomy", experiment, "--config", config, "--json")
    assert code == 0, output
    taxonomy = json.loads(output)
    assert [(c["id"], c["case_ids"]) for c in taxonomy["categories"]] == [
        ("all", ["p1", "p2", "o1", "s1"]),
        ("policy", ["p1", "p2"]),
        ("orders", ["o1"]),
    ]
    assert taxonomy["uncategorized_case_ids"] == ["s1"]

    code, output = _invoke("modelfit", "taxonomy", experiment)
    assert code == 0 and "Task taxonomy" in output


def test_unusable_input_exits_1(tmp_path: Path, experiment: Path) -> None:
    code, output = _invoke("modelfit", "recommend", tmp_path / "missing.json")
    assert code == 1 and "Unable to load experiment report" in output

    bad = tmp_path / "bad.yaml"
    bad.write_text("weights: {quality: 0, cost: 0, latency: 0, reliability: 0}\n", "utf-8")
    code, output = _invoke("modelfit", "recommend", experiment, "--config", bad)
    assert code == 1 and "Unable to load ModelFit config" in output

    ref = tmp_path / "ref.json"
    ref.write_text(json.dumps({"reference_variant_id": "ghost"}), "utf-8")
    code, output = _invoke("modelfit", "recommend", experiment, "--config", ref)
    assert code == 1 and "not a candidate" in output

    code, output = _invoke("modelfit", "matrix", tmp_path / "missing.json")
    assert code == 1 and "Unable to load ModelFit report" in output
