"""Local checks for pinned AIOS provenance and operational draft companions.

No repository test code, network access or other ecosystem package is imported.
Reference resolution uses only bytes explicitly supplied by the caller.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from datetime import datetime
from typing import Any

Issue = tuple[str, str]


def instant(value: str) -> datetime:
    return datetime.fromisoformat(value.upper().replace("Z", "+00:00"))


def cyclic(edges: list[tuple[str, str]]) -> bool:
    """Kahn traversal avoids recursion depth failures on long, valid lineages."""
    graph: dict[str, set[str]] = {}
    incoming: dict[str, int] = {}
    for source, target in edges:
        targets = graph.setdefault(source, set())
        incoming.setdefault(source, 0)
        if target not in targets:
            incoming[target] = incoming.get(target, 0) + 1
            targets.add(target)
    pending = [node for node, count in incoming.items() if count == 0]
    visited = 0
    while pending:
        node = pending.pop()
        visited += 1
        for target in graph.get(node, set()):
            incoming[target] -= 1
            if incoming[target] == 0:
                pending.append(target)
    return visited != len(incoming)


def issues(document: dict[str, Any]) -> list[Issue]:
    """Requires schema-valid input; returns every violated semantic rule."""
    if document["spec_version"] == "0.6-draft":
        return provenance_issues(document)
    return operational_issues(document)


def provenance_issues(record: dict[str, Any]) -> list[Issue]:
    found: list[Issue] = []

    def fail(number: int, text: str) -> None:
        found.append((f"AIOS-0.6-R{number:02d}", text))

    groups = ("subjects", "sources", "findings", "lineage")
    identities = [entry["id"] for group in groups for entry in record[group]]
    if len(identities) != len(set(identities)):
        fail(2, "Provenance entry identities must be unique")
    subjects = {entry["id"] for entry in record["subjects"]}
    for entry in record["sources"]:
        if "subject" in entry and entry["subject"] not in subjects:
            fail(3, f"Source {entry['id']} names an undeclared subject")
    for finding in record["findings"]:
        for target in finding.get("targets", []):
            if target["subject"] not in subjects:
                fail(3, f"Finding {finding['id']} names an undeclared subject")
    kinds = {entry["id"]: "source" for entry in record["sources"]}
    kinds.update({entry["id"]: "finding" for entry in record["findings"]})
    endpoints = {
        "derived-from": ({"finding"}, {"source", "finding"}),
        "supports": ({"source", "finding"}, {"finding"}),
        "contradicts": ({"source", "finding"}, {"finding"}),
        "supersedes": ({"finding"}, {"finding"}),
    }
    for edge in record["lineage"]:
        source_kinds, target_kinds = endpoints[edge["type"]]
        if (
            kinds.get(edge["source"]) not in source_kinds
            or kinds.get(edge["target"]) not in target_kinds
        ):
            fail(4, f"Lineage {edge['id']} has a missing or mistyped endpoint")
        if edge["source"] == edge["target"]:
            fail(6, f"Lineage {edge['id']} relates an entry to itself")
    derived = {edge["source"] for edge in record["lineage"] if edge["type"] == "derived-from"}
    for finding in record["findings"]:
        if finding["id"] not in derived:
            fail(5, f"Finding {finding['id']} has no derived-from lineage")
    for kind in ("derived-from", "supersedes"):
        if cyclic(
            [(edge["source"], edge["target"]) for edge in record["lineage"] if edge["type"] == kind]
        ):
            fail(6, f"{kind} lineage must be acyclic")
    for entry in record["sources"]:
        if "captured_at" in entry and instant(entry["captured_at"]) > instant(record["created_at"]):
            fail(7, f"Source {entry['id']} was captured after record creation")
    return found


def operational_issues(document: dict[str, Any]) -> list[Issue]:
    found: list[Issue] = []

    def fail(number: int, text: str) -> None:
        found.append((f"AIOS-0.8-R{number:02d}", text))

    kind = document["artifact_type"]
    created = instant(document["created_at"])
    if kind == "audit_event":
        if instant(document["occurred_at"]) > created:
            fail(4, "Audit occurrence follows recording time")
        if document["id"] in document.get("causal_event_ids", []):
            fail(7, "An audit event cannot cause itself")
        return found
    groups = [document["evidence"]]
    if kind == "investigation_report":
        groups += [document["findings"], document["timeline_entries"]]
    ids = [entry["id"] for group in groups for entry in group]
    if len(ids) != len(set(ids)):
        fail(2, "Evidence, finding and timeline identities must be unique")
    if kind == "verification_signal":
        if document["grounding"]["status"] in {"grounded", "partial"} and not document["evidence"]:
            fail(5, "Assessed grounding needs evidence references")
        return found
    evidence = {entry["id"] for entry in document["evidence"]}
    claims = [document["summary"], *document["findings"]]
    for entry in [*claims, document["recovery"], *document["timeline_entries"]]:
        if not set(entry["evidence_ids"]) <= evidence:
            fail(3, "Citation names undeclared evidence")
    times = [document["incident"]["detected_at"]]
    times += [entry["occurred_at"] for entry in document["timeline_entries"]]
    if any(instant(value) > created for value in times):
        fail(4, "An observed instant follows report creation")
    for entry in claims:
        if entry["certainty"] in {"observed", "contradictory"} and not evidence.intersection(
            entry["evidence_ids"]
        ):
            fail(6, "Observed or contradictory claims need declared citations")
    recovery = document["recovery"]
    if recovery["status"] == "verified" and not evidence.intersection(recovery["evidence_ids"]):
        fail(6, "Verified recovery needs declared citations")
    return found


def object_index(artifact: dict[str, Any]) -> dict[str, str]:
    index = {artifact["id"]: artifact["artifact_type"]}
    for group, kind in (
        ("requests", "request"),
        ("steps", "step"),
        ("agents", "agent"),
        ("incidents", "incident"),
    ):
        index.update((entry["id"], kind) for entry in artifact.get(group, []))
    for group in ("occurrences", "evidence"):
        index.update((entry["id"], entry["type"]) for entry in artifact.get(group, []))
    return index


def resolve(
    record: dict[str, Any],
    held: dict[str, bytes],
    validate: Callable[[dict[str, Any]], bool],
) -> dict[str, Any]:
    """Resolve explicit held subjects; digests and identity are independent states.

    A resolved citation is not a verified digest, authenticated source or true
    finding. Invalid JSON and unsupported subjects stay unresolved, not fetched.
    The caller must validate the provenance record before invoking this helper.
    """
    states: dict[str, dict[str, Any]] = {}
    objects: dict[str, dict[str, str]] = {}
    for subject in record["subjects"]:
        key = subject["id"]
        raw = held.get(key)
        state: dict[str, Any] = {
            "available": raw is not None,
            "valid": None,
            "identity": None,
            "digest": "unchecked" if "digest" in subject else "absent",
        }
        if raw is not None:
            if "digest" in subject:
                digest = subject["digest"]
                measured = hashlib.new(digest["algorithm"].replace("-", ""), raw).hexdigest()
                state["digest"] = "verified" if measured == digest["value"] else "mismatch"
            try:
                artifact = json.loads(raw)
            except (ValueError, UnicodeError):
                artifact = None
            state["valid"] = isinstance(artifact, dict) and validate(artifact)
            matches = isinstance(artifact, dict) and all(
                artifact.get(field) == subject[source]
                for field, source in (
                    ("id", "artifact_id"),
                    ("artifact_type", "artifact_type"),
                    ("spec_version", "spec_version"),
                )
            )
            state["identity"] = "match" if matches else "mismatch"
            if state["valid"] and matches:
                objects[key] = object_index(artifact)
        states[key] = state

    def lookup(subject: str, reference: dict[str, Any]) -> str:
        if subject not in objects:
            return "unresolved"
        actual = objects[subject].get(reference["id"])
        if actual is None:
            return "missing"
        return "resolved" if actual == reference["type"] else "type_mismatch"

    references = {
        entry["id"]: lookup(entry["subject"], entry["object"])
        for entry in record["sources"]
        if entry["kind"] == "aios_object"
    }
    for finding in record["findings"]:
        for position, target in enumerate(finding.get("targets", [])):
            references[f"{finding['id']}/targets/{position}"] = lookup(
                target["subject"], target["object"]
            )
    return {"subjects": states, "references": references}
