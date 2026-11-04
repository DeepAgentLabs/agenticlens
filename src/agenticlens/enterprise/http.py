"""Opt-in authenticated artifact service, separate from the local OTLP dashboard."""

import hmac
import json
from collections.abc import Callable, Sequence
from typing import Annotated, Any

from agentic_evals import EvaluationReport, GateConfig
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from pydantic import BaseModel, ValidationError

from agenticlens.enterprise.gates import release_receipt
from agenticlens.enterprise.models import Credential, RegistryEntry, StoragePolicy, digest
from agenticlens.enterprise.store import EnterpriseStore
from agenticlens.models.trace import Run

_MAX_BODY = 2 * 1024 * 1024


async def _body(request: Request, model: type[BaseModel]) -> BaseModel:
    body = bytearray()
    async for chunk in request.stream():
        body.extend(chunk)
        if len(body) > _MAX_BODY:
            raise HTTPException(413, "Artifact exceeds 2 MiB limit")
    try:
        return model.model_validate_json(body)
    except (ValidationError, ValueError) as exc:
        # Validation errors can echo secret payload values. Return only a generic message.
        raise HTTPException(422, "Invalid artifact") from exc


def create_enterprise_app(
    store: EnterpriseStore,
    credentials: Sequence[Credential],
    *,
    storage_policy: StoragePolicy | None = None,
    gate_policy: GateConfig | None = None,
) -> FastAPI:
    """One configured service policy; credentials bind roles to one organization/project.

    Hosts manage token issuance/rotation and TLS. No anonymous fallback, file loading,
    evaluator imports, outbound requests, or live tool execution is exposed.
    """
    configured = tuple(item.model_copy(deep=True) for item in credentials)
    hashes = [item.token_sha256.get_secret_value() for item in configured]
    if not configured or len(set(hashes)) != len(hashes):
        raise ValueError("Configure at least one credential with unique token digests")
    if any(len(value) != 64 or any(c not in "0123456789abcdef" for c in value) for value in hashes):
        raise ValueError("Token digests must be lowercase SHA-256 hex")
    retention = (storage_policy or StoragePolicy()).model_copy(deep=True)
    policy = (gate_policy or GateConfig()).model_copy(deep=True)
    app = FastAPI(title="AgenticLens Project Artifacts", docs_url=None, redoc_url=None)

    def authorize(role: str) -> Callable[..., Credential]:
        def check(request: Request, organization: str, project: str) -> Credential:
            header = request.headers.get("authorization", "")
            if not header.startswith("Bearer "):
                raise HTTPException(401, "Bearer credential required")
            presented = digest(header[7:])
            principal = None
            for candidate in configured:
                if hmac.compare_digest(candidate.token_sha256.get_secret_value(), presented):
                    principal = candidate
            if principal is None:
                raise HTTPException(401, "Invalid credential")
            allowed = {"reader": 0, "writer": 1, "admin": 2}
            if (
                principal.project.organization != organization
                or principal.project.name != project
                or allowed[principal.role] < allowed[role]
            ):
                store.record(principal.project, principal.subject, "access.denied", role)
                raise HTTPException(403, "Access denied")
            return principal

        return check

    reader = authorize("reader")
    writer = authorize("writer")
    admin = authorize("admin")
    base = "/v1/organizations/{organization}/projects/{project}"

    @app.get("/healthz")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post(base + "/traces")
    async def put_trace(
        request: Request, principal: Annotated[Credential, Depends(writer)]
    ) -> dict[str, str]:
        run = Run.model_validate(await _body(request, Run))
        try:
            store.put_run(principal.project, principal.subject, run, retention)
        except ValueError as exc:
            raise HTTPException(422, "Invalid trace identity or redacted artifact") from exc
        return {"status": "stored"}

    @app.get(base + "/traces")
    def traces(
        principal: Annotated[Credential, Depends(reader)],
        limit: Annotated[int, Query(ge=1, le=20)] = 20,
        offset: Annotated[int, Query(ge=0)] = 0,
    ) -> list[dict[str, Any]]:
        store.record(principal.project, principal.subject, "trace.read", "list")
        return [
            {
                "trace_id": run.trace_id,
                "run_id": run.run_id,
                "application_name": run.application_name,
                "status": run.status.value,
                "span_count": len(run.spans),
                "total_tokens": run.total_tokens,
            }
            for run in store.iter_runs(principal.project, retention, limit=limit, offset=offset)
        ]

    @app.get(base + "/trace")
    def trace(
        principal: Annotated[Credential, Depends(reader)],
        trace_id: str,
    ) -> dict[str, Any]:
        run = store.get_run(principal.project, trace_id, retention)
        if run is None:
            raise HTTPException(404, "Trace not found")
        store.record(principal.project, principal.subject, "trace.read", digest(trace_id))
        return run.model_dump(mode="json")

    @app.post(base + "/registry")
    async def register(
        request: Request, principal: Annotated[Credential, Depends(writer)]
    ) -> dict[str, str]:
        entry = RegistryEntry.model_validate(await _body(request, RegistryEntry))
        try:
            store.register(principal.project, principal.subject, entry)
        except ValueError as exc:
            raise HTTPException(409, str(exc)) from exc
        return {"status": "registered"}

    @app.get(base + "/registry")
    def registry(principal: Annotated[Credential, Depends(reader)]) -> list[dict[str, Any]]:
        store.record(principal.project, principal.subject, "registry.read", "list")
        return [entry.model_dump() for entry in store.registry(principal.project)]

    @app.post(base + "/gate")
    async def gate(
        request: Request, principal: Annotated[Credential, Depends(writer)]
    ) -> dict[str, Any]:
        report = EvaluationReport.model_validate(await _body(request, EvaluationReport))
        receipt = release_receipt(report, policy)
        store.record(principal.project, principal.subject, "release.gate", json.dumps(receipt))
        return receipt

    @app.post(base + "/retention/prune")
    def prune(principal: Annotated[Credential, Depends(admin)]) -> dict[str, int]:
        return {"removed": store.prune(principal.project, principal.subject, retention)}

    @app.get(base + "/audit")
    def audit(principal: Annotated[Credential, Depends(admin)]) -> dict[str, Any]:
        store.record(principal.project, principal.subject, "audit.export", "metadata")
        return store.export_audit(principal.project)

    @app.get(base + "/compliance")
    def compliance(principal: Annotated[Credential, Depends(admin)]) -> dict[str, Any]:
        store.record(principal.project, principal.subject, "compliance.export", "metadata")
        return store.compliance_export(principal.project, retention)

    return app
