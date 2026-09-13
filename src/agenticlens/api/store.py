"""A bounded, thread-safe in-memory store of recently received traces.

Used by the live OTLP receiver (`agenticlens.api.http`) to hold the most
recent runs so the live dashboard has something to render. Deliberately has
no dependency on FastAPI so it stays importable and testable without the
optional `api` extra installed.
"""

import threading
from collections import OrderedDict

from agenticlens.models.trace import Run

_DEFAULT_MAX_TRACES = 200


class LiveTraceStore:
    """FIFO-bounded store of `Run`s keyed by trace id, newest last."""

    def __init__(self, max_traces: int = _DEFAULT_MAX_TRACES) -> None:
        if max_traces < 1:
            raise ValueError("max_traces must be at least 1")
        self._max_traces = max_traces
        self._runs: OrderedDict[str, Run] = OrderedDict()
        self._lock = threading.Lock()

    def add(self, run: Run) -> None:
        with self._lock:
            self._runs.pop(run.trace_id, None)  # re-insert moves it to "most recent"
            self._runs[run.trace_id] = run
            while len(self._runs) > self._max_traces:
                self._runs.popitem(last=False)

    def list_recent(self, limit: int | None = None) -> list[Run]:
        with self._lock:
            runs = list(reversed(self._runs.values()))
        return runs if limit is None else runs[:limit]

    def get(self, trace_id: str) -> Run | None:
        with self._lock:
            return self._runs.get(trace_id)

    def __len__(self) -> int:
        with self._lock:
            return len(self._runs)
