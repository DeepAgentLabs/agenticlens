import pytest

from agenticlens.api.store import LiveTraceStore
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
