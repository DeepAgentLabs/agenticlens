"""Stores of recently received traces, used by the live OTLP receiver
(`agenticlens.api.http`) so the live dashboard and history view have
something to render. Deliberately has no dependency on FastAPI so this
module stays importable and testable without the optional `api` extra
installed.

Two implementations share the same shape (`TraceStore`):

- `LiveTraceStore` — bounded, in-memory, gone on restart. The default.
- `PersistentTraceStore` — backed by a stdlib `sqlite3` file, survives a
  restart. Opt in via `serve-otlp --db`.
"""

import sqlite3
import threading
from collections import OrderedDict
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

from agenticlens.models.trace import Run

_DEFAULT_MAX_TRACES = 200


class TraceStore(Protocol):
    """Shared contract both stores satisfy; `api/http.py` codes against this."""

    def add(self, run: Run) -> None: ...
    def list_recent(self, limit: int | None = None) -> list[Run]: ...
    def get(self, trace_id: str) -> Run | None: ...
    def __len__(self) -> int: ...


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


class PersistentTraceStore:
    """SQLite-backed store of `Run`s keyed by trace id — survives a restart.

    Each method opens its own short-lived connection rather than holding one
    open across calls, so it's safe to use from uvicorn's threadpool without
    any per-thread connection affinity; a lock still guards the
    upsert-then-evict sequence in `add`.
    """

    def __init__(self, db_path: Path, max_traces: int | None = None) -> None:
        if max_traces is not None and max_traces < 1:
            raise ValueError("max_traces must be at least 1 when given")
        self._db_path = db_path
        self._max_traces = max_traces
        self._lock = threading.Lock()
        with closing(self._connect()) as conn, conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute(
                "CREATE TABLE IF NOT EXISTS traces ("
                "trace_id TEXT PRIMARY KEY, "
                "run_json TEXT NOT NULL, "
                "received_at TEXT NOT NULL)"
            )

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self._db_path))

    def add(self, run: Run) -> None:
        with self._lock, closing(self._connect()) as conn, conn:
            conn.execute(
                "INSERT INTO traces (trace_id, run_json, received_at) VALUES (?, ?, ?) "
                "ON CONFLICT(trace_id) DO UPDATE SET run_json=excluded.run_json, "
                "received_at=excluded.received_at",
                (run.trace_id, run.model_dump_json(), datetime.now(timezone.utc).isoformat()),
            )
            if self._max_traces is not None:
                conn.execute(
                    "DELETE FROM traces WHERE trace_id NOT IN ("
                    "SELECT trace_id FROM traces ORDER BY received_at DESC, rowid DESC LIMIT ?)",
                    (self._max_traces,),
                )

    def list_recent(self, limit: int | None = None) -> list[Run]:
        query = "SELECT run_json FROM traces ORDER BY received_at DESC, rowid DESC"
        params: tuple[int, ...] = ()
        if limit is not None:
            query += " LIMIT ?"
            params = (limit,)
        with closing(self._connect()) as conn:
            rows = conn.execute(query, params).fetchall()
        return [Run.model_validate_json(row[0]) for row in rows]

    def get(self, trace_id: str) -> Run | None:
        with closing(self._connect()) as conn:
            row = conn.execute(
                "SELECT run_json FROM traces WHERE trace_id = ?", (trace_id,)
            ).fetchone()
        return Run.model_validate_json(row[0]) if row is not None else None

    def __len__(self) -> int:
        with closing(self._connect()) as conn:
            (count,) = conn.execute("SELECT COUNT(*) FROM traces").fetchone()
        return int(count)
