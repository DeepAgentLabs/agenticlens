from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from jsonschema import Draft202012Validator, FormatChecker
from pydantic import BaseModel, Field
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

from agenticlens.validation import companions

DEFAULT_SPEC_VERSION = "0.4"
#: AIOS versions this release can validate. Per AIOS-0.5-V03, an artifact that
#: declares any other version is rejected rather than checked against 0.4.
SUPPORTED_SPEC_VERSIONS = ("0.4", "0.6", "0.8")
_ARTIFACT_VERSIONS = {
    "run": "0.4",
    "workflow": "0.4",
    "provenance": "0.6",
    "verification_signal": "0.8",
    "audit_event": "0.8",
    "investigation_report": "0.8",
}
_CATALOGS = {
    "0.4": "conformance-rules.json",
    "0.6": "provenance-rules.json",
    "0.8": "operational-rules.json",
}
_SPEC_VERSION_PATTERN = re.compile(r"^(0\.[1-9][0-9]*|[1-9][0-9]*\.(0|[1-9][0-9]*))(-draft)?$")
_RULES_CATALOG = "conformance-rules.json"

#: Issue code -> AIOS rule ID in `conformance-rules.json`.
ISSUE_RULES: dict[str, str] = {
    "schema.invalid": "AIOS-0.4-P01",
    "semantic.duplicate-object": "AIOS-0.4-P02",
    "semantic.duplicate-relationship": "AIOS-0.4-P03",
    "semantic.duplicate-event": "AIOS-0.4-P03",
    "semantic.invalid-time-range": "AIOS-0.4-P04",
    "semantic.unresolved-reference": "AIOS-0.4-P05",
    "semantic.step-membership": "AIOS-0.4-P06",
    "semantic.observed-in": "AIOS-0.4-P07",
    "semantic.evaluation-target": "AIOS-0.4-P08",
    "semantic.workflow-link": "AIOS-0.4-P09",
    "semantic.event-target": "AIOS-0.4-P10",
    "semantic.self-relationship": "AIOS-0.4-P11",
    "semantic.structural-cycle": "AIOS-0.4-P11",
    "semantic.causal-cycle": "AIOS-0.4-P11",
    "semantic.ordering-cycle": "AIOS-0.4-P11",
    "semantic.retry": "AIOS-0.4-P12",
    "semantic.unmarked-external": "AIOS-0.4-X01",
}
_RUN_ARTIFACT = "run"
_WORKFLOW_ARTIFACT = "workflow"
_CYCLE_RELATIONSHIP_GROUPS: dict[str, set[str]] = {
    "structural": {"contains", "parent-of"},
    "causal": {"caused", "depends-on", "follows"},
    "ordering": {"follows"},
}
_FORMAT_CHECKER = FormatChecker()


class ValidationIssue(BaseModel):
    code: str
    level: str = "error"
    source: str
    message: str
    location: str | None = None
    rule_id: str | None = Field(
        default=None, description="AIOS conformance rule this issue violates, when known."
    )


class RuleResult(BaseModel):
    """Outcome of one AIOS conformance rule for this artifact.

    `not_checked` marks process rules (behavioral obligations an artifact
    alone cannot prove) and semantic rules skipped because schema
    validation failed or only `validate` mode ran.
    """

    rule_id: str
    role: str
    level: str
    check: str
    requirement: str
    result: Literal["pass", "fail", "not_checked"]
    issues: int = 0


class ConformanceSummary(BaseModel):
    status: Literal["aligned", "schema_valid", "schema_invalid", "semantic_invalid"]
    schema_issues: int = 0
    semantic_issues: int = 0
    issue_codes: dict[str, int] = Field(default_factory=dict)
    rules_passed: int = 0
    rules_failed: int = 0
    rules_not_checked: int = 0
    failed_rules: list[str] = Field(default_factory=list)


class ConformanceReport(BaseModel):
    spec_version: str
    artifact_type: str
    artifact_path: str
    mode: str
    draft_alignment_claim: str
    schema_valid: bool
    semantic_valid: bool
    aligned: bool
    semantic_checked: bool = False
    issues: list[ValidationIssue] = Field(default_factory=list)
    declared_spec_version: str | None = Field(
        default=None, description="The artifact's own spec_version marker, if any."
    )
    rules_catalog: str | None = Field(
        default=None, description="Path of the conformance-rules.json catalog used, if found."
    )
    rules: list[RuleResult] = Field(default_factory=list)
    summary: ConformanceSummary | None = None


class SpecUnavailableError(ValueError):
    """Required local validation resources are not installed or accessible."""


@dataclass(frozen=True)
class _ResolvedSpec:
    version: str
    root: Path
    schema_path: Path
    conformance_path: Path


def validate_aios_artifact(
    artifact_path: Path,
    *,
    spec_version: str | None = None,
    mode: str = "conformance",
    spec_root: Path | None = None,
) -> ConformanceReport:
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("AIOS-0.5-V03: artifact must be a JSON object")
    if mode not in {"validate", "conformance"}:
        raise ValueError("mode must be validate or conformance")
    artifact_type = _artifact_type_for(payload)
    declared = payload.get("spec_version")
    spec_version = normalize_spec_version(
        spec_version or (declared if isinstance(declared, str) else DEFAULT_SPEC_VERSION)
    )
    if spec_version not in SUPPORTED_SPEC_VERSIONS:
        raise ValueError(f"Unsupported AIOS version {spec_version!r}; AIOS-0.5-V03")
    if _ARTIFACT_VERSIONS[artifact_type] != spec_version:
        raise ValueError("AIOS-0.5-V03: no schema for this artifact type under its declared marker")
    resolved_spec = _resolve_spec(
        artifact_type=artifact_type,
        spec_version=spec_version,
        explicit_root=spec_root,
    )
    if isinstance(declared, str) and normalize_spec_version(declared) != spec_version:
        raise ValueError(
            f"Artifact declares spec_version {declared!r} but validation was requested for "
            f"v{spec_version}-draft. AIOS-0.5-V03: validate against the artifact's declared "
            "version; never fall back to a different draft's schema."
        )
    issues = _schema_issues(payload, resolved_spec.schema_path)
    schema_valid = not issues
    semantic_issues: list[ValidationIssue] = []
    if mode == "conformance" and schema_valid:
        semantic_issues = _semantic_issues(payload)
    semantic_valid = not semantic_issues
    all_issues = [*issues, *semantic_issues]
    for issue in all_issues:
        issue.rule_id = issue.rule_id or ISSUE_RULES.get(issue.code)
    catalog_path = resolved_spec.root / _CATALOGS[spec_version]
    rules = _rule_results(
        catalog_path,
        artifact_type=artifact_type,
        issues=all_issues,
        semantic_checked=mode == "conformance" and schema_valid,
    )
    status: Literal["aligned", "schema_valid", "schema_invalid", "semantic_invalid"] = (
        "schema_invalid"
        if not schema_valid
        else "schema_valid"
        if mode != "conformance"
        else "aligned"
        if semantic_valid
        else "semantic_invalid"
    )
    codes: dict[str, int] = {}
    for issue in all_issues:
        codes[issue.code] = codes.get(issue.code, 0) + 1
    summary = ConformanceSummary(
        status=status,
        schema_issues=len(issues),
        semantic_issues=len(semantic_issues),
        issue_codes=codes,
        rules_passed=sum(r.result == "pass" for r in rules),
        rules_failed=sum(r.result == "fail" for r in rules),
        rules_not_checked=sum(r.result == "not_checked" for r in rules),
        failed_rules=sorted(
            {r.rule_id for r in rules if r.result == "fail"}
            | {i.rule_id for i in all_issues if i.rule_id}
        ),
    )
    return ConformanceReport(
        spec_version=spec_version,
        artifact_type=artifact_type,
        artifact_path=str(artifact_path),
        mode=mode,
        draft_alignment_claim=(
            f"Aligned with AI Operations Specification v{spec_version}-draft "
            "when schema and semantic checks both pass."
        ),
        schema_valid=schema_valid,
        semantic_valid=semantic_valid,
        aligned=schema_valid and semantic_valid and mode == "conformance",
        semantic_checked=schema_valid and mode == "conformance",
        issues=all_issues,
        declared_spec_version=declared if isinstance(declared, str) else None,
        rules_catalog=str(catalog_path) if catalog_path.exists() else None,
        rules=rules,
        summary=summary,
    )


def normalize_spec_version(version: str) -> str:
    """``0.4-draft`` and ``v0.4`` both normalize to ``0.4``; rejects malformed markers."""
    marker = version.strip().removeprefix("v")
    if not _SPEC_VERSION_PATTERN.match(marker):
        raise ValueError(f"Malformed AIOS spec version {version!r}.")
    return marker.removesuffix("-draft")


def available_spec_versions(spec_root: Path | None = None) -> list[str]:
    """Supported AIOS versions whose schemas can be found locally."""
    found: list[str] = []
    for version in SUPPORTED_SPEC_VERSIONS:
        try:
            _resolve_spec(
                artifact_type=next(
                    kind for kind, value in _ARTIFACT_VERSIONS.items() if value == version
                ),
                spec_version=version,
                explicit_root=spec_root,
            )
        except ValueError:
            continue
        found.append(version)
    return found


def _rule_results(
    catalog_path: Path,
    *,
    artifact_type: str,
    issues: list[ValidationIssue],
    semantic_checked: bool,
) -> list[RuleResult]:
    """Pass/fail/not-checked for every catalog rule that applies to this artifact."""
    if not catalog_path.exists():
        return []
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    failures: dict[str, int] = {}
    for issue in issues:
        if issue.rule_id:
            failures[issue.rule_id] = failures.get(issue.rule_id, 0) + 1
    results: list[RuleResult] = []
    for rule in catalog.get("rules", []):
        if artifact_type not in rule.get("applies_to", []):
            continue
        rule_id = str(rule["id"])
        check = str(rule.get("check", "process"))
        if rule_id in failures:
            result: Literal["pass", "fail", "not_checked"] = "fail"
        elif (check == "schema" and not any(i.code.startswith("schema.") for i in issues)) or (
            check == "semantic"
            and semantic_checked
            and (
                rule_id in ISSUE_RULES.values() or rule_id.startswith(("AIOS-0.6-R", "AIOS-0.8-R"))
            )
        ):
            result = "pass"
        else:
            result = "not_checked"
        results.append(
            RuleResult(
                rule_id=rule_id,
                role=str(rule.get("role", "")),
                level=str(rule.get("level", "")),
                check=check,
                requirement=str(rule.get("requirement", "")),
                result=result,
                issues=failures.get(rule_id, 0),
            )
        )
    return results


def _artifact_type_for(payload: dict[str, Any]) -> str:
    artifact_type = payload.get("artifact_type")
    if not isinstance(artifact_type, str) or artifact_type not in _ARTIFACT_VERSIONS:
        raise ValueError("AIOS-0.5-V03: artifact_type has no supported schema")
    if not isinstance(artifact_type, str):
        raise ValueError(
            "artifact_type must be present in the JSON payload and be either 'run' or 'workflow'"
        )
    return artifact_type


def _resolve_spec(
    *,
    artifact_type: str,
    spec_version: str,
    explicit_root: Path | None,
) -> _ResolvedSpec:
    if spec_version not in SUPPORTED_SPEC_VERSIONS:
        supported = ", ".join(f"v{v}-draft" for v in SUPPORTED_SPEC_VERSIONS)
        raise ValueError(
            f"Unsupported AIOS version '{spec_version}'. "
            f"AgenticLens currently supports {supported}."
        )
    spec_dir_name = f"v{spec_version}"
    candidate_roots: list[Path] = []
    if explicit_root is not None:
        candidate_roots.append(explicit_root)
    current = Path(__file__).resolve()
    if explicit_root is None:
        candidate_roots.extend(
            [
                current.parents[1] / "schemas" / "aios",
                current.parents[3] / "schemas" / "aios",
                current.parents[4] / "ai-operations-spec",
                current.parents[5] / "ai-operations-spec",
            ]
        )
    for root in candidate_roots:
        spec_root = root / "specification" / spec_dir_name
        schema_path = spec_root / "schemas" / f"{artifact_type}.schema.json"
        conformance_path = spec_root / (
            "provenance.md" if spec_version == "0.6" else "conformance.md"
        )
        if schema_path.exists() and conformance_path.exists():
            return _ResolvedSpec(
                version=spec_version,
                root=spec_root,
                schema_path=schema_path,
                conformance_path=conformance_path,
            )
    raise SpecUnavailableError(
        f"Unable to locate ai-operations-spec v{spec_version} draft schemas. "
        "Pass --spec-root with the sibling repo path if it is not checked out next to agenticlens."
    )


def _schema_issues(payload: dict[str, Any], schema_path: Path) -> list[ValidationIssue]:
    try:
        json.dumps(payload, allow_nan=False)
    except (TypeError, ValueError):
        rule = {"0.6-draft": "AIOS-0.6-R01", "0.8-draft": "AIOS-0.8-R01"}.get(
            payload.get("spec_version", ""), "AIOS-0.4-P01"
        )
        return [
            ValidationIssue(
                code="schema.invalid",
                source="aios",
                message="Artifact is not a finite JSON value",
                rule_id=rule,
            )
        ]
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    registry = _schema_registry(schema_path.parent)
    validator = Draft202012Validator(
        schema,
        registry=registry,
        format_checker=_FORMAT_CHECKER,
    )
    issues: list[ValidationIssue] = []
    for error in sorted(validator.iter_errors(payload), key=lambda item: list(item.absolute_path)):
        location = "$"
        if error.absolute_path:
            location = "$." + ".".join(str(part) for part in error.absolute_path)
        issues.append(
            ValidationIssue(
                code="schema.invalid",
                source="aios",
                message=error.message,
                location=location,
                rule_id={"provenance": "AIOS-0.6-R01"}.get(
                    payload["artifact_type"],
                    "AIOS-0.8-R01"
                    if payload.get("spec_version") == "0.8-draft"
                    else "AIOS-0.4-P01",
                ),
            )
        )
    return issues


def _schema_registry(schema_dir: Path) -> Registry[Any]:
    registry: Registry[Any] = Registry()
    for schema_file in schema_dir.parents[1].glob("v*/schemas/*.schema.json"):
        schema = json.loads(schema_file.read_text(encoding="utf-8"))
        resource = Resource.from_contents(schema, default_specification=DRAFT202012)
        registry = registry.with_resource(schema_file.as_uri(), resource)
        schema_id = schema.get("$id")
        if isinstance(schema_id, str) and schema_id:
            registry = registry.with_resource(schema_id, resource)
    return registry


def _semantic_issues(payload: dict[str, Any]) -> list[ValidationIssue]:
    if payload.get("spec_version") in {"0.6-draft", "0.8-draft"}:
        return [
            ValidationIssue(code="semantic.companion", source="aios", message=text, rule_id=rule)
            for rule, text in companions.issues(payload)
        ]
    if payload.get("artifact_type") == "workflow":
        return [
            ValidationIssue(
                code="semantic.unmarked-external",
                source="aios",
                message="Workflow references must be external",
                rule_id="AIOS-0.4-X01",
            )
            for reference in payload.get("references", [])
            if not reference.get("external")
        ]
    if payload.get("artifact_type") != _RUN_ARTIFACT:
        return []
    issues: list[ValidationIssue] = []
    issues.extend(_unique_identity_issues(payload))
    issues.extend(_timestamp_issues(payload))
    issues.extend(_relationship_resolution_issues(payload))
    issues.extend(_step_membership_issues(payload))
    issues.extend(_observed_in_issues(payload))
    issues.extend(_evaluation_target_issues(payload))
    issues.extend(_workflow_link_issues(payload))
    issues.extend(_event_target_issues(payload))
    issues.extend(_relationship_shape_issues(payload))
    issues.extend(
        ValidationIssue(code="semantic.retry", source="aios", message=message, rule_id=rule)
        for rule, message in _retry_issues(payload, payload.get("relationships", []))
    )
    return issues


def _unique_identity_issues(payload: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    object_sets = {
        "requests": "request",
        "steps": "step",
        "agents": "agent",
        "occurrences": None,
        "evidence": None,
        "incidents": "incident",
    }
    seen: set[str] = {str(payload["id"])}
    for key, fixed_type in object_sets.items():
        for index, item in enumerate(payload.get(key, [])):
            item_type = fixed_type or item.get("type")
            marker = (str(item.get("id")), str(item_type))
            if marker[0] in seen:
                issues.append(
                    ValidationIssue(
                        code="semantic.duplicate-object",
                        source="aios",
                        message=f"Duplicate object identity {marker[0]!r} of type {marker[1]!r}.",
                        location=f"$.{key}.{index}",
                    )
                )
            seen.add(marker[0])
    for key in ("relationships", "events"):
        seen_ids: set[str] = set()
        id_field = "id" if key == "relationships" else "event_id"
        for index, item in enumerate(payload.get(key, [])):
            item_id = str(item.get(id_field))
            if item_id in seen_ids:
                issues.append(
                    ValidationIssue(
                        code=f"semantic.duplicate-{key[:-1]}",
                        source="aios",
                        message=f"Duplicate {key[:-1]} id {item_id!r}.",
                        location=f"$.{key}.{index}",
                    )
                )
            seen_ids.add(item_id)
    return issues


def _timestamp_issues(payload: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    issues.extend(
        _time_range_issue(
            started_at=payload.get("started_at"),
            ended_at=payload.get("ended_at"),
            location="$",
        )
    )
    for index, step in enumerate(payload.get("steps", [])):
        issues.extend(
            _time_range_issue(
                started_at=step.get("started_at"),
                ended_at=step.get("ended_at"),
                location=f"$.steps.{index}",
            )
        )
    return issues


def _time_range_issue(
    *,
    started_at: Any,
    ended_at: Any,
    location: str,
) -> list[ValidationIssue]:
    if started_at is None or ended_at is None:
        return []
    started = _parse_timestamp(started_at)
    ended = _parse_timestamp(ended_at)
    if started is None or ended is None or ended >= started:
        return []
    return [
        ValidationIssue(
            code="semantic.invalid-time-range",
            source="aios",
            message="ended_at must not precede started_at.",
            location=location,
        )
    ]


def _parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    normalized = value.upper().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def _relationship_resolution_issues(payload: dict[str, Any]) -> list[ValidationIssue]:
    index = _object_index(payload)
    issues: list[ValidationIssue] = []
    for rel_index, relationship in enumerate(payload.get("relationships", [])):
        for endpoint_name in ("source", "target"):
            endpoint = relationship[endpoint_name]
            if endpoint.get("external") is True:
                continue
            key = (endpoint["id"], endpoint["type"])
            if key not in index:
                if not any(object_id == endpoint["id"] for object_id, _kind in index):
                    issues.append(
                        ValidationIssue(
                            code="semantic.unmarked-external",
                            source="aios",
                            message="Reference has no local object and is not marked external",
                            rule_id="AIOS-0.4-X01",
                        )
                    )
                issues.append(
                    ValidationIssue(
                        code="semantic.unresolved-reference",
                        source="aios",
                        message=(
                            f"Relationship {relationship['id']!r} {endpoint_name} "
                            f"does not resolve to a local {endpoint['type']!r} object."
                        ),
                        location=f"$.relationships.{rel_index}.{endpoint_name}",
                    )
                )
    return issues


def _step_membership_issues(payload: dict[str, Any]) -> list[ValidationIssue]:
    run_id = payload.get("id")
    step_ids = {step["id"] for step in payload.get("steps", [])}
    contains_targets = [
        relationship["target"]["id"]
        for relationship in payload.get("relationships", [])
        if relationship["type"] == "contains"
        and relationship["source"]["id"] == run_id
        and relationship["source"]["type"] == "run"
        and relationship["target"]["type"] == "step"
    ]
    issues: list[ValidationIssue] = []
    for step_id in sorted(step_ids):
        count = contains_targets.count(step_id)
        if count != 1:
            issues.append(
                ValidationIssue(
                    code="semantic.step-membership",
                    source="aios",
                    message=(
                        f"Step {step_id!r} must appear in exactly one run contains relationship."
                    ),
                    location="$",
                )
            )
    return issues


def _observed_in_issues(payload: dict[str, Any]) -> list[ValidationIssue]:
    observed_map: dict[str, int] = {}
    step_ids = {step["id"] for step in payload.get("steps", [])}
    for relationship in payload.get("relationships", []):
        if relationship["type"] != "observed-in":
            continue
        if relationship["source"]["type"] in {
            "model_interaction",
            "prompt",
            "context",
            "tool_invocation",
            "rag_retrieval",
            "memory_operation",
        }:
            observed_map[relationship["source"]["id"]] = (
                observed_map.get(relationship["source"]["id"], 0) + 1
            )
            if (
                relationship["target"]["id"] not in step_ids
                or relationship["target"]["type"] != "step"
            ):
                observed_map[relationship["source"]["id"]] += 1000
    issues: list[ValidationIssue] = []
    for occurrence in payload.get("occurrences", []):
        count = observed_map.get(occurrence["id"], 0)
        if count != 1:
            issues.append(
                ValidationIssue(
                    code="semantic.observed-in",
                    source="aios",
                    message=(
                        f"Occurrence {occurrence['id']!r} must connect to exactly one step "
                        "through observed-in."
                    ),
                    location="$",
                )
            )
    return issues


def _evaluation_target_issues(payload: dict[str, Any]) -> list[ValidationIssue]:
    evaluates: dict[str, int] = {}
    for relationship in payload.get("relationships", []):
        if relationship["type"] == "evaluates" and relationship["source"]["type"] == "evaluation":
            source_id = relationship["source"]["id"]
            evaluates[source_id] = evaluates.get(source_id, 0) + 1
    issues: list[ValidationIssue] = []
    for evidence in payload.get("evidence", []):
        if evidence["type"] != "evaluation":
            continue
        if evaluates.get(evidence["id"], 0) < 1:
            issues.append(
                ValidationIssue(
                    code="semantic.evaluation-target",
                    source="aios",
                    message=f"Evaluation {evidence['id']!r} must evaluate at least one target.",
                    location="$",
                )
            )
    return issues


def _workflow_link_issues(payload: dict[str, Any]) -> list[ValidationIssue]:
    workflow_id = payload.get("workflow_id")
    if workflow_id is None:
        return []
    for relationship in payload.get("relationships", []):
        if (
            relationship["type"] == "run-of"
            and relationship["source"]["type"] == "run"
            and relationship["source"]["id"] == payload.get("id")
            and relationship["target"]["type"] == "workflow"
            and relationship["target"]["id"] == workflow_id
        ):
            return []
    return [
        ValidationIssue(
            code="semantic.workflow-link",
            source="aios",
            message=(
                "workflow_id requires a matching run-of relationship to the workflow reference."
            ),
            location="$",
        )
    ]


def _event_target_issues(payload: dict[str, Any]) -> list[ValidationIssue]:
    index = _object_index(payload)
    issues: list[ValidationIssue] = []
    for event_index, event in enumerate(payload.get("events", [])):
        key = (event["object_id"], event["object_type"])
        if key not in index:
            issues.append(
                ValidationIssue(
                    code="semantic.event-target",
                    source="aios",
                    message=(
                        f"Event {event['event_id']!r} points to unresolved object "
                        f"{event['object_id']!r} of type {event['object_type']!r}."
                    ),
                    location=f"$.events.{event_index}",
                )
            )
    return issues


def _relationship_shape_issues(payload: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    relationships = payload.get("relationships", [])
    for index, relationship in enumerate(relationships):
        if relationship["source"]["id"] == relationship["target"]["id"]:
            issues.append(
                ValidationIssue(
                    code="semantic.self-relationship",
                    source="aios",
                    message=f"Relationship {relationship['id']!r} must not reference itself.",
                    location=f"$.relationships.{index}",
                )
            )
    for group_name, relation_types in _CYCLE_RELATIONSHIP_GROUPS.items():
        edges = [
            relationship
            for relationship in relationships
            if relationship["type"] in relation_types
            and relationship["source"].get("external") is not True
            and relationship["target"].get("external") is not True
        ]
        graph: dict[str, set[str]] = {}
        for relationship in edges:
            source = f"{relationship['source']['type']}:{relationship['source']['id']}"
            target = f"{relationship['target']['type']}:{relationship['target']['id']}"
            graph.setdefault(source, set()).add(target)
        if _has_cycle(graph):
            issues.append(
                ValidationIssue(
                    code=f"semantic.{group_name}-cycle",
                    source="aios",
                    message=f"{group_name.capitalize()} relationships must be acyclic.",
                    location="$.relationships",
                )
            )
    return issues


def _object_index(payload: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    index: dict[tuple[str, str], dict[str, Any]] = {
        (payload["id"], payload["artifact_type"]): payload,
    }
    for request in payload.get("requests", []):
        index[(request["id"], "request")] = request
    for step in payload.get("steps", []):
        index[(step["id"], "step")] = step
    for agent in payload.get("agents", []):
        index[(agent["id"], "agent")] = agent
    for occurrence in payload.get("occurrences", []):
        index[(occurrence["id"], occurrence["type"])] = occurrence
    for evidence in payload.get("evidence", []):
        index[(evidence["id"], evidence["type"])] = evidence
    for incident in payload.get("incidents", []):
        index[(incident["id"], "incident")] = incident
    return index


def _has_cycle(graph: dict[str, set[str]]) -> bool:
    return companions.cyclic(
        [(source, target) for source, targets in graph.items() for target in targets]
    )


def resolve_provenance(
    record: dict[str, Any], subjects: dict[str, bytes], *, spec_root: Path | None = None
) -> dict[str, Any]:
    """Validate a provenance record and resolve only caller-supplied subject bytes."""

    def valid(document: dict[str, Any]) -> bool:
        try:
            kind = _artifact_type_for(document)
            version = normalize_spec_version(str(document.get("spec_version", "")))
            if _ARTIFACT_VERSIONS[kind] != version:
                return False
            schema = _resolve_spec(
                artifact_type=kind, spec_version=version, explicit_root=spec_root
            )
            return not _schema_issues(document, schema.schema_path) and not _semantic_issues(
                document
            )
        except (ValueError, KeyError, TypeError):
            return False

    if record.get("artifact_type") != "provenance" or not valid(record):
        raise ValueError("A schema- and semantically valid provenance record is required")
    return companions.resolve(record, subjects, valid)


def _retry_issues(
    artifact: dict[str, Any], relationships: list[dict[str, Any]]
) -> list[tuple[str, str]]:
    """Rule P12: distinct identities per retry attempt, each linked to the prior attempt."""
    issues: list[tuple[str, str]] = []
    occurrence_by_id = {item["id"]: item for item in artifact.get("occurrences", [])}
    evidence_by_id = {item["id"]: item for item in artifact.get("evidence", [])}

    attempt_signal_targets: dict[str, list[int]] = {}
    for relationship in relationships:
        if relationship["type"] != "signals-on":
            continue
        source = evidence_by_id.get(relationship["source"]["id"])
        if not source or source.get("type") != "reliability_event":
            continue
        attempt = source.get("attributes", {}).get("attempt")
        if not isinstance(attempt, int):
            continue
        target_id = relationship["target"]["id"]
        attempt_signal_targets.setdefault(target_id, []).append(attempt)
        occurrence = occurrence_by_id.get(target_id)
        if occurrence:
            occurrence_attempt = occurrence.get("attributes", {}).get("attempt")
            if isinstance(occurrence_attempt, int) and occurrence_attempt != attempt:
                issues.append(
                    (
                        "AIOS-0.4-P12",
                        f"Retry evidence {source['id']} must target attempt {attempt}, "
                        f"not occurrence attempt {occurrence_attempt}",
                    )
                )
    for target_id, attempts in attempt_signal_targets.items():
        if len(attempts) > 1:
            ordered = ", ".join(str(attempt) for attempt in sorted(attempts))
            issues.append(
                (
                    "AIOS-0.4-P12",
                    f"Retry attempts {ordered} must not all signal the same occurrence {target_id}",
                )
            )

    retry_groups: dict[str, dict[int, str]] = {}
    for occurrence in artifact.get("occurrences", []):
        attributes = occurrence.get("attributes", {})
        activity = attributes.get("logical_activity_id")
        attempt = attributes.get("attempt")
        if not isinstance(activity, str) or not isinstance(attempt, int):
            continue
        group = retry_groups.setdefault(activity, {})
        if attempt in group:
            message = f"Retry activity {activity} duplicates attempt {attempt}"
            issues.append(("AIOS-0.4-P12", message))
            continue
        group[attempt] = occurrence["id"]
    for activity, attempt_ids in retry_groups.items():
        ordered_attempts = sorted(attempt_ids.items())
        for (_attempt, source_id), (next_attempt, target_id) in zip(
            ordered_attempts, ordered_attempts[1:], strict=False
        ):
            linked = any(
                edge["type"] == "follows"
                and edge["source"]["id"] == source_id
                and edge["target"]["id"] == target_id
                for edge in relationships
            ) or any(
                edge["type"] == "caused"
                and edge["source"]["id"] == source_id
                and edge["target"]["id"] == target_id
                for edge in relationships
            )
            if not linked:
                issues.append(
                    (
                        "AIOS-0.4-P12",
                        f"Retry activity {activity} must link attempt {_attempt} to attempt "
                        f"{next_attempt}",
                    )
                )
    return issues
