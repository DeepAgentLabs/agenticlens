import pytest

from agenticlens.api.store import LiveTraceStore, PersistentTraceStore
from agenticlens.models.trace import Run


def _run(trace_id: str, application_name: str = "demo") -> Run:
    return Run(trace_id=trace_id, application_name=application_name, spans=[])


def test_add_and_get_round_trips() -> None:
    store = LiveTraceStore()
    store.add(_run("a"))

    assert store.get("a") is not None
    assert store.get("a").trace_id == "a"
    assert store.get("missing") is None


def test_list_recent_is_newest_first() -> None:
    store = LiveTraceStore()
    store.add(_run("a"))
    store.add(_run("b"))
    store.add(_run("c"))

    assert [run.trace_id for run in store.list_recent()] == ["c", "b", "a"]


def test_list_recent_respects_limit() -> None:
    store = LiveTraceStore()
    store.add(_run("a"))
    store.add(_run("b"))

    assert [run.trace_id for run in store.list_recent(limit=1)] == ["b"]


def test_re_adding_a_trace_moves_it_to_most_recent() -> None:
    store = LiveTraceStore()
    store.add(_run("a"))
    store.add(_run("b"))
    store.add(_run("a"))

    assert [run.trace_id for run in store.list_recent()] == ["a", "b"]
    assert len(store) == 2


def test_evicts_oldest_past_max_traces() -> None:
    store = LiveTraceStore(max_traces=2)
    store.add(_run("a"))
    store.add(_run("b"))
    store.add(_run("c"))

    assert len(store) == 2
    assert store.get("a") is None
    assert [run.trace_id for run in store.list_recent()] == ["c", "b"]


def test_rejects_non_positive_max_traces() -> None:
    with pytest.raises(ValueError):
        LiveTraceStore(max_traces=0)


def test_persistent_store_add_and_get_round_trips(tmp_path) -> None:
    store = PersistentTraceStore(tmp_path / "traces.db")
    store.add(_run("a"))

    assert store.get("a") is not None
    assert store.get("a").trace_id == "a"
    assert store.get("missing") is None


def test_persistent_store_list_recent_is_newest_first(tmp_path) -> None:
    store = PersistentTraceStore(tmp_path / "traces.db")
    store.add(_run("a"))
    store.add(_run("b"))
    store.add(_run("c"))

    assert [run.trace_id for run in store.list_recent()] == ["c", "b", "a"]


def test_persistent_store_re_adding_a_trace_moves_it_to_most_recent(tmp_path) -> None:
    store = PersistentTraceStore(tmp_path / "traces.db")
    store.add(_run("a"))
    store.add(_run("b"))
    store.add(_run("a"))

    assert [run.trace_id for run in store.list_recent()] == ["a", "b"]
    assert len(store) == 2


def test_persistent_store_evicts_oldest_past_max_traces(tmp_path) -> None:
    store = PersistentTraceStore(tmp_path / "traces.db", max_traces=2)
    store.add(_run("a"))
    store.add(_run("b"))
    store.add(_run("c"))

    assert len(store) == 2
    assert store.get("a") is None
    assert [run.trace_id for run in store.list_recent()] == ["c", "b"]


def test_persistent_store_is_unbounded_by_default(tmp_path) -> None:
    store = PersistentTraceStore(tmp_path / "traces.db")
    for i in range(250):
        store.add(_run(f"trace-{i}"))

    assert len(store) == 250


def test_persistent_store_rejects_non_positive_max_traces(tmp_path) -> None:
    with pytest.raises(ValueError):
        PersistentTraceStore(tmp_path / "traces.db", max_traces=0)


def test_persistent_store_survives_reopening(tmp_path) -> None:
    db_path = tmp_path / "traces.db"
    first = PersistentTraceStore(db_path)
    first.add(_run("a", application_name="support-bot"))

    reopened = PersistentTraceStore(db_path)

    assert len(reopened) == 1
    reopened_run = reopened.get("a")
    assert reopened_run is not None
    assert reopened_run.application_name == "support-bot"
