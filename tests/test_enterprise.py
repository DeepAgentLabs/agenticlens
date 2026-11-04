"""Acceptance and adversarial checks for the opt-in project artifact service."""

import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from agenticlens.enterprise import (
    Credential,
    EnterpriseStore,
    Project,
    RegistryEntry,
    StoragePolicy,
    digest,
)
from agenticlens.enterprise.http import create_enterprise_app
from agenticlens.models.trace import Run, Span, SpanType

PROJECT = Project(organization="demo", name="support")
BASE = "/v1/organizations/demo/projects/support"


def credential(role="admin", project=PROJECT):
    return Credential(subject=f"ci-{role}", token_sha256=digest(role), project=project, role=role)


@pytest.fixture
def service(tmp_path):
    store = EnterpriseStore(tmp_path / "enterprise.db")
    app = create_enterprise_app(store, [credential(role) for role in ("reader", "writer", "admin")])
    return store, TestClient(app)


def headers(role="admin"):
    return {"Authorization": f"Bearer {role}"}


def test_authentication_and_project_isolation(service):
    store, client = service
    assert client.get("/healthz").status_code == 200
    for suffix in ("/traces", "/registry", "/audit", "/compliance"):
        assert client.get(BASE + suffix).status_code == 401
        assert client.get(BASE + suffix, headers=headers("unknown")).status_code == 401
        other = BASE.replace("support", "other")
        assert client.get(other + suffix, headers=headers()).status_code == 403
    assert client.post(BASE + "/traces", json={}, headers=headers("reader")).status_code == 403
    for suffix in ("/audit", "/compliance"):
        assert client.get(BASE + suffix, headers=headers("writer")).status_code == 403
    assert client.post(BASE + "/retention/prune", headers=headers("writer")).status_code == 403
    assert all(r["action"] == "access.denied" for r in store.export_audit(PROJECT)["records"])


def test_redaction_before_storage_and_export(service):
    store, client = service
    run = Run(application_name="test", metadata={"email": "alice@example.com", "api_key": "secret"})
    response = client.post(
        BASE + "/traces", json=run.model_dump(mode="json"), headers=headers("writer")
    )
    assert response.status_code == 200
    assert client.get(
        BASE + "/trace", params={"trace_id": run.trace_id}, headers=headers("reader")
    ).json()["metadata"] == {"email": "[REDACTED_EMAIL]", "api_key": "[REDACTED]"}
    exported = client.get(BASE + "/compliance", headers=headers()).json()
    assert exported["audit"]["integrity"] == "not_verified"
    assert exported["certification"] == "not_assessed"
    assert "alice@example.com" not in json.dumps(exported)
    with sqlite3.connect(store.path) as conn:
        stored = conn.execute("SELECT body FROM project_traces").fetchone()[0]
    assert "alice@example.com" not in stored and '"secret"' not in stored


def test_registry_immutable_and_scoped(service):
    store, client = service
    entry = RegistryEntry(kind="prompt", name="support", version="1", content_sha256="a" * 64)
    for _ in range(2):
        assert (
            client.post(BASE + "/registry", json=entry.model_dump(), headers=headers()).status_code
            == 200
        )
    changed = entry.model_copy(update={"content_sha256": "b" * 64})
    assert (
        client.post(BASE + "/registry", json=changed.model_dump(), headers=headers()).status_code
        == 409
    )
    assert len(store.registry(PROJECT)) == 1
    assert store.registry(Project(organization="other", name="support")) == []
    assert len(store.export_audit(PROJECT)["records"]) == 1


def test_retention_restart_and_expiration(tmp_path):
    path = tmp_path / "enterprise.db"
    store = EnterpriseStore(path)
    policy = StoragePolicy(max_traces=2, max_age_days=1)
    other = Project(organization="other", name="support")
    for i in range(3):
        store.put_run(PROJECT, "ci", Run(trace_id=str(i), application_name="test"), policy)
    store.put_run(other, "ci", Run(trace_id="other", application_name="test"), policy)
    store = EnterpriseStore(path)
    assert [r.trace_id for r in store.runs(PROJECT, policy)] == ["2", "1"]
    with sqlite3.connect(path) as conn:
        conn.execute(
            "UPDATE project_traces SET received='2000-01-01T00:00:00+00:00' WHERE project=?",
            (PROJECT.key,),
        )
    assert store.runs(PROJECT, policy) == []
    assert store.prune(PROJECT, "ci", policy) == 2
    assert len(store.runs(other, policy)) == 1


def test_concurrent_registry_conflict_is_atomic(tmp_path):
    store = EnterpriseStore(tmp_path / "registry.db")
    entry = RegistryEntry(kind="model", name="model", version="1", content_sha256="a" * 64)
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(lambda _: store.register(PROJECT, "ci", entry), range(8)))
    assert len(store.registry(PROJECT)) == 1
    assert len(store.export_audit(PROJECT)["records"]) == 1


def test_invalid_bodies_do_not_echo_payload_or_write_audit(service):
    store, client = service
    response = client.post(BASE + "/registry", json={"secret": "never-echo"}, headers=headers())
    assert response.status_code == 422 and "never-echo" not in response.text
    assert (
        client.post(
            BASE + "/traces", content="x" * (2 * 1024 * 1024 + 1), headers=headers()
        ).status_code
        == 413
    )
    assert store.export_audit(PROJECT)["records"] == []


def test_fail_closed_configuration(tmp_path):
    store = EnterpriseStore(tmp_path / "config.db")
    for credentials in (
        [],
        [credential(), credential()],
        [
            credential().model_copy(
                update={"token_sha256": credential().token_sha256.__class__("bad")}
            )
        ],
    ):
        with pytest.raises(ValueError):
            create_enterprise_app(store, credentials)


def test_gate_reproducibility_and_server_policy(service):
    store, client = service
    # Native recorded report, including its original evaluator versions.
    path = Path(__file__).parents[1] / "examples/suites/artifacts"
    from agenticlens.evaluation import evaluate_suite, load_samples, load_suite

    suite = load_suite(
        Path(__file__).parents[1] / "examples/suites/artifacts/regression-suite.json"
    )
    report = evaluate_suite(suite, load_samples(path / "samples.json"))
    payload = report.model_dump(mode="json")
    first = client.post(BASE + "/gate", json=payload, headers=headers("writer"))
    second = client.post(BASE + "/gate", json=payload, headers=headers("writer"))
    assert first.status_code == 200
    assert first.json() == second.json()
    assert first.json()["policy"]["min_pass_rate"] == 1
    assert first.json()["evidence_authentication"] == "not_verified"
    assert len(store.export_audit(PROJECT)["records"]) == 2


def test_audit_failure_rolls_back_mutation(tmp_path, monkeypatch):
    store = EnterpriseStore(tmp_path / "rollback.db")

    def fail(*args):
        raise RuntimeError("audit unavailable")

    monkeypatch.setattr(EnterpriseStore, "_audit", fail)
    with pytest.raises(RuntimeError, match="audit unavailable"):
        store.put_run(PROJECT, "ci", Run(application_name="test"), StoragePolicy())
    assert store.runs(PROJECT, StoragePolicy()) == []


def test_same_trace_id_cannot_cross_projects(tmp_path):
    store = EnterpriseStore(tmp_path / "isolation.db")
    other = Project(organization="another", name="support")
    for project in (PROJECT, other):
        store.put_run(
            project,
            "ci",
            Run(trace_id="same", application_name=project.organization),
            StoragePolicy(),
        )
    assert store.runs(PROJECT, StoragePolicy())[0].application_name == "demo"
    assert store.runs(other, StoragePolicy())[0].application_name == "another"


def test_service_factory_requires_explicit_configuration(tmp_path, monkeypatch):
    from agenticlens.enterprise.server import create_app

    monkeypatch.delenv("LENS_CONFIG", raising=False)
    with pytest.raises(KeyError):
        create_app()
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"credentials": [credential().model_dump(mode="json")]}))
    # SecretStr intentionally masks exported config; operators must supply actual digests.
    monkeypatch.setenv("LENS_CONFIG", str(path))
    monkeypatch.setenv("LENS_DATABASE", str(tmp_path / "server.db"))
    with pytest.raises(ValueError, match="SHA-256"):
        create_app()
    config = credential().model_dump(mode="json")
    config["token_sha256"] = digest("admin")
    path.write_text(json.dumps({"credentials": [config]}))
    assert TestClient(create_app()).get(BASE + "/traces", headers=headers()).status_code == 200


def test_redaction_preserves_native_usage_and_cleans_nested_payloads(service):
    store, client = service
    run = Run(
        application_name="test",
        spans=[
            Span(
                name="call",
                span_type=SpanType.MODEL_CALL,
                input_tokens=100,
                output_tokens=7,
                input_data={"password": "secret", "text": "alice@example.com"},
                attributes={"authorization": "secret"},
                error_message="alice@example.com",
            )
        ],
    )
    result = client.post(BASE + "/traces", json=run.model_dump(mode="json"), headers=headers())
    assert result.status_code == 200
    clean = store.runs(PROJECT, StoragePolicy())[0]
    assert clean.total_tokens == 107
    assert clean.spans[0].input_data["password"] == "[REDACTED]"
    assert "alice@example.com" not in clean.model_dump_json()


def test_candidate_schema_snapshots_and_offline_example():
    import subprocess
    import sys

    from agenticlens.enterprise.server import ServiceConfig

    root = Path(__file__).parents[1]
    for name, model in (
        ("project", Project),
        ("registry-entry", RegistryEntry),
        ("storage-policy", StoragePolicy),
        ("service-config", ServiceConfig),
    ):
        schema = json.loads((root / f"schemas/enterprise/{name}.json").read_text())
        schema.pop("$schema")
        schema.pop("$id")
        assert schema == model.model_json_schema()
    result = subprocess.run(
        [sys.executable, "examples/enterprise_demo.py"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    assert json.loads(result.stdout) == {
        "project": "demo/support",
        "traces": 1,
        "registry": 1,
        "certification": "not_assessed",
    }


def test_failed_gate_is_not_silently_approved(service):
    from agenticlens.evaluation import EvaluationReport

    _, client = service
    report = EvaluationReport.model_validate_json(
        (Path(__file__).parents[1] / "examples/suites/artifacts/evaluation.json").read_text()
    )
    report.summary.pass_rate = 0.0
    result = client.post(BASE + "/gate", json=report.model_dump(mode="json"), headers=headers())
    assert result.status_code == 200
    assert result.json()["decision"]["passed"] is False
    assert result.json()["decision"]["reasons"]


def test_sensitive_identity_is_rejected_without_overwriting(service):
    store, client = service
    for identifier in ("alice@example.com", "bob@example.com"):
        run = Run(application_name="test", trace_id=identifier)
        result = client.post(BASE + "/traces", json=run.model_dump(mode="json"), headers=headers())
        assert result.status_code == 422
        assert identifier not in result.text
    assert store.runs(PROJECT, StoragePolicy()) == []


def test_bounded_summary_pages_and_scoped_detail(service):
    store, client = service
    for i in range(25):
        store.put_run(
            PROJECT,
            "ci",
            Run(trace_id=str(i), application_name="test", metadata={"payload": "x" * 10000}),
            StoragePolicy(),
        )
    first = client.get(BASE + "/traces", headers=headers()).json()
    second = client.get(BASE + "/traces?offset=20", headers=headers()).json()
    assert len(first) == 20 and len(second) == 5
    assert "metadata" not in first[0]
    assert not {r["trace_id"] for r in first} & {r["trace_id"] for r in second}
    assert client.get(BASE + "/traces?limit=21", headers=headers()).status_code == 422
    assert client.get(BASE + "/trace?trace_id=0", headers=headers()).status_code == 200
    assert client.get(BASE + "/trace?trace_id=missing", headers=headers()).status_code == 404
    assert (
        client.get(
            BASE.replace("support", "other") + "/trace?trace_id=0", headers=headers()
        ).status_code
        == 403
    )
    assert len(store.compliance_export(PROJECT, StoragePolicy())["trace_digests"]) == 25


def test_metadata_exports_are_bounded(service):
    store, client = service
    for i in range(105):
        store.register(
            PROJECT,
            "ci",
            RegistryEntry(kind="model", name=f"model-{i:03}", version="1", content_sha256="a" * 64),
        )
    assert len(store.registry(PROJECT)) == 100
    assert len(store.export_audit(PROJECT)["records"]) == 100
    assert store.export_audit(PROJECT)["page"]["has_more"] is True
    assert len(client.get(BASE + "/registry?limit=10&offset=100", headers=headers()).json()) == 5
    for endpoint in ("registry", "audit", "compliance"):
        assert client.get(BASE + f"/{endpoint}?limit=101", headers=headers()).status_code == 422
    exported = client.get(BASE + "/compliance?limit=5", headers=headers()).json()
    assert len(exported["registry"]) == 5
    assert len(exported["audit"]["records"]) == 5
    assert exported["page"]["consistent_snapshot"] is False


def test_only_health_is_anonymous_and_schema_routes_are_disabled(service):
    _, client = service
    for endpoint in ("/openapi.json", "/docs", "/redoc"):
        assert client.get(endpoint).status_code == 404
