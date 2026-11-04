"""Reproducible release receipts, delegating score and gate semantics to Evals."""

import json
from importlib.metadata import version
from typing import Any

from agentic_evals import EvaluationReport, GateConfig, evaluate_gate

from agenticlens import __version__
from agenticlens.enterprise.models import digest


def release_receipt(report: EvaluationReport, policy: GateConfig) -> dict[str, Any]:
    # Canonicalize JSON object order, preserving case/score order and original evidence.
    canonical = json.dumps(report.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
    return {
        "schema_version": "lens.enterprise.gate/1-candidate",
        "lens_version": __version__,
        "evals_version": version("agentic-evals"),
        "report_sha256": digest(canonical),
        "policy": policy.model_dump(mode="json"),
        "decision": evaluate_gate(report, policy).model_dump(mode="json"),
        "evidence_authentication": "not_verified",
    }
