from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from pydantic import BaseModel, Field
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

DEFAULT_SPEC_VERSION = "0.4"
_RUN_ARTIFACT = "run"
_WORKFLOW_ARTIFACT = "workflow"
_CYCLE_RELATIONSHIP_GROUPS: dict[str, set[str]] = {
    "structural": {"contains", "parent-of"},
    "causal": {"caused", "depends-on"},
    "ordering": {"follows"},
}


class ValidationIssue(BaseModel):
    code: str
    level: str = "error"
    source: str
    message: str
    location: str | None = None


class ConformanceReport(BaseModel):
    spec_version: str
    artifact_type: str
    artifact_path: str
    mode: str
    draft_alignment_claim: str
    schema_valid: bool
    semantic_valid: bool
    aligned: bool
    issues: list[ValidationIssue] = Field(default_factory=list)


@dataclass(frozen=True)
class _ResolvedSpec:
    version: str
    root: Path
    schema_path: Path
    conformance_path: Path


def validate_aios_artifact(
    artifact_path: Path,
    *,
    spec_version: str = DEFAULT_SPEC_VERSION,
    mode: str = "conformance",
    spec_root: Path | None = None,
) -> ConformanceReport:
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    artifact_type = _artifact_type_for(payload)
    resolved_spec = _resolve_spec(
        artifact_type=artifact_type,
        spec_version=spec_version,
        explicit_root=spec_root,
    )
    issues = _schema_issues(payload, resolved_spec.schema_path)
    schema_valid = not issues
    semantic_issues: list[ValidationIssue] = []
    if mode == "conformance" and schema_valid:
        semantic_issues = _semantic_issues(payload)
    semantic_valid = not semantic_issues
    all_issues = [*issues, *semantic_issues]
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
        aligned=schema_valid and semantic_valid,
        issues=all_issues,
    )


def _artifact_type_for(payload: dict[str, Any]) -> str:
    artifact_type = payload.get("artifact_type")
    if artifact_type not in {_RUN_ARTIFACT, _WORKFLOW_ARTIFACT}:
        raise ValueError(
            "artifact_type must be present in the JSON payload and be either "
            "'run' or 'workflow'"
        )
    return artifact_type


def _resolve_spec(
    *,
    artifact_type: str,
    spec_version: str,
    explicit_root: Path | None,
) -> _ResolvedSpec:
    if spec_version != DEFAULT_SPEC_VERSION:
        raise ValueError(
            f"Unsupported AIOS version '{spec_version}'. "
            f"AgenticLens currently supports only v{DEFAULT_SPEC_VERSION}-draft."
        )
    spec_dir_name = f"v{spec_version}"
    candidate_roots: list[Path] = []
    if explicit_root is not None:
        candidate_roots.append(explicit_root)
    current = Path(__file__).resolve()
    candidate_roots.extend(
        [
            current.parents[4] / "ai-operations-spec",
            current.parents[5] / "ai-operations-spec",
        ]
    )
    for root in candidate_roots:
        spec_root = root / "specification" / spec_dir_name
        schema_path = spec_root / "schemas" / f"{artifact_type}.schema.json"
        conformance_path = spec_root / "conformance.md"
        if schema_path.exists() and conformance_path.exists():
            return _ResolvedSpec(
                version=spec_version,
                root=spec_root,
                schema_path=schema_path,
                conformance_path=conformance_path,
            )
    raise ValueError(
        "Unable to locate ai-operations-spec v0.4 draft schemas. "
        "Pass --spec-root with the sibling repo path if it is not checked out next to agenticlens."
    )


def _schema_issues(payload: dict[str, Any], schema_path: Path) -> list[ValidationIssue]:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    registry = _schema_registry(schema_path.parent)
    validator = Draft202012Validator(schema, registry=registry)
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
            )
        )
    return issues


def _schema_registry(schema_dir: Path) -> Registry[Any]:
    registry: Registry[Any] = Registry()
    for schema_file in schema_dir.glob("*.schema.json"):
        schema = json.loads(schema_file.read_text(encoding="utf-8"))
        resource = Resource.from_contents(schema, default_specification=DRAFT202012)
        registry = registry.with_resource(schema_file.as_uri(), resource)
        schema_id = schema.get("$id")
        if isinstance(schema_id, str) and schema_id:
            registry = registry.with_resource(schema_id, resource)
    return registry


def _semantic_issues(payload: dict[str, Any]) -> list[ValidationIssue]:
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
    seen: set[tuple[str, str]] = set()
    for key, fixed_type in object_sets.items():
        for index, item in enumerate(payload.get(key, [])):
            item_type = fixed_type or item.get("type")
            marker = (str(item.get("id")), str(item_type))
            if marker in seen:
                issues.append(
                    ValidationIssue(
                        code="semantic.duplicate-object",
                        source="aios",
                        message=f"Duplicate object identity {marker[0]!r} of type {marker[1]!r}.",
                        location=f"$.{key}.{index}",
                    )
                )
            seen.add(marker)
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
    started_at = payload.get("started_at")
    ended_at = payload.get("ended_at")
    if started_at is not None and ended_at is not None and ended_at < started_at:
        return [
            ValidationIssue(
                code="semantic.invalid-time-range",
                source="aios",
                message="ended_at must not precede started_at.",
                location="$",
            )
        ]
    return []


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
                        f"Step {step_id!r} must appear in exactly one run "
                        "contains relationship."
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
            observed_map[relationship["source"]["id"]] = observed_map.get(
                relationship["source"]["id"], 0
            ) + 1
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
                "workflow_id requires a matching run-of relationship "
                "to the workflow reference."
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
    if workflow_id := payload.get("workflow_id"):
        index[(workflow_id, "workflow")] = {"id": workflow_id, "artifact_type": "workflow"}
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
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        for neighbor in graph.get(node, set()):
            if visit(neighbor):
                return True
        visiting.remove(node)
        visited.add(node)
        return False

    return any(visit(node) for node in graph)
