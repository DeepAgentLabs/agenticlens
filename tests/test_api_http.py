import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient  # noqa: E402

from agenticlens.api.http import create_app  # noqa: E402
from agenticlens.api.store import LiveTraceStore  # noqa: E402


def _otlp_payload(trace_id: str, application_name: str = "support-agent") -> dict:
    return {
        "resourceSpans": [
            {
                "resource": {
                    "attributes": [
                        {"key": "service.name", "value": {"stringValue": application_name}}
                    ]
                },
                "scopeSpans": [
                    {
                        "scope": {"name": "test"},
                        "spans": [
                            {
                                "traceId": trace_id,
                                "spanId": "1" * 16,
                                "parentSpanId": "",
                                "name": "chat gpt-4o-mini",
                                "kind": 3,
                                "startTimeUnixNano": "1700000000000000000",
                                "endTimeUnixNano": "1700000000500000000",
                                "attributes": [
                                    {
                                        "key": "gen_ai.operation.name",
                                        "value": {"stringValue": "chat"},
                                    },
                                    {
                                        "key": "gen_ai.usage.input_tokens",
                                        "value": {"intValue": "120"},
                                    },
                                ],
                                "status": {"code": 1},
                            }
                        ],
                    }
                ],
            }
        ]
    }


def test_post_traces_then_list_and_get() -> None:
    client = TestClient(create_app(LiveTraceStore()))
    trace_id = "a" * 32

    response = client.post("/v1/traces", json=_otlp_payload(trace_id))

    assert response.status_code == 200
    assert response.json() == {}

    listed = client.get("/v1/traces").json()
    assert len(listed) == 1
    assert listed[0]["trace_id"] == trace_id
    assert listed[0]["application_name"] == "support-agent"

    detail = client.get(f"/v1/traces/{trace_id}")
    assert detail.status_code == 200
    assert detail.json()["trace_id"] == trace_id


def test_get_unknown_trace_is_404() -> None:
    client = TestClient(create_app(LiveTraceStore()))

    response = client.get("/v1/traces/does-not-exist")

    assert response.status_code == 404


def test_post_malformed_payload_is_400() -> None:
    client = TestClient(create_app(LiveTraceStore()))

    response = client.post("/v1/traces", json={"hello": "world"})

    assert response.status_code == 400


def test_dashboard_shows_waiting_page_when_store_is_empty() -> None:
    client = TestClient(create_app(LiveTraceStore()))

    response = client.get("/")

    assert response.status_code == 200
    assert "Waiting for traces" in response.text


def test_dashboard_renders_the_posted_trace() -> None:
    client = TestClient(create_app(LiveTraceStore()))
    trace_id = "b" * 32
    client.post("/v1/traces", json=_otlp_payload(trace_id))

    response = client.get("/")

    assert response.status_code == 200
    assert "Agent timeline" in response.text
    assert "chat gpt-4o-mini" in response.text
    assert "Live traces:" in response.text


def test_dashboard_with_unknown_trace_id_is_404() -> None:
    client = TestClient(create_app(LiveTraceStore()))
    client.post("/v1/traces", json=_otlp_payload("c" * 32))

    response = client.get("/?trace_id=does-not-exist")

    assert response.status_code == 404


def test_save_dir_persists_received_traces(tmp_path) -> None:
    client = TestClient(create_app(LiveTraceStore(), save_dir=tmp_path))
    trace_id = "d" * 32

    client.post("/v1/traces", json=_otlp_payload(trace_id))

    saved = tmp_path / f"{trace_id}.json"
    assert saved.exists()
    assert "support-agent" in saved.read_text(encoding="utf-8")


def test_eviction_removes_oldest_trace_from_listing() -> None:
    client = TestClient(create_app(LiveTraceStore(max_traces=1)))

    client.post("/v1/traces", json=_otlp_payload("e" * 32))
    client.post("/v1/traces", json=_otlp_payload("f" * 32))

    listed = client.get("/v1/traces").json()
    assert [item["trace_id"] for item in listed] == ["f" * 32]
    assert client.get(f"/v1/traces/{'e' * 32}").status_code == 404


def test_healthz() -> None:
    client = TestClient(create_app(LiveTraceStore()))

    assert client.get("/healthz").json() == {"status": "ok"}
