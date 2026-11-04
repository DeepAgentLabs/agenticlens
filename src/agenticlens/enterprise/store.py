"""Single-node project storage. Audit writes and mutations share SQLite transactions.

The database is a trusted local boundary, not a signed or externally checkpointed ledger.
"""

import sqlite3
from collections.abc import Iterator
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from agenticlens.enterprise.models import Project, RegistryEntry, StoragePolicy, digest
from agenticlens.instrumentation.redaction import redact_sensitive
from agenticlens.models.trace import Run


class EnterpriseStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        with closing(self._connect()) as conn, conn:
            conn.executescript(
                "CREATE TABLE IF NOT EXISTS project_traces ("
                "project TEXT, trace_id TEXT, body TEXT NOT NULL, received TEXT NOT NULL, "
                "PRIMARY KEY(project, trace_id));"
                "CREATE TABLE IF NOT EXISTS registry ("
                "project TEXT, kind TEXT, name TEXT, version TEXT, body TEXT NOT NULL, "
                "PRIMARY KEY(project, kind, name, version));"
                "CREATE TABLE IF NOT EXISTS audit ("
                "sequence INTEGER PRIMARY KEY AUTOINCREMENT, project TEXT NOT NULL, "
                "at TEXT NOT NULL, subject TEXT NOT NULL, action TEXT NOT NULL, "
                "object_digest TEXT NOT NULL);"
            )

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path, timeout=30)

    @staticmethod
    def _audit(
        conn: sqlite3.Connection, project: Project, subject: str, action: str, body: str
    ) -> None:
        conn.execute(
            "INSERT INTO audit(project, at, subject, action, object_digest) VALUES(?,?,?,?,?)",
            (project.key, datetime.now(timezone.utc).isoformat(), subject, action, digest(body)),
        )

    @staticmethod
    def _prune(conn: sqlite3.Connection, project: Project, policy: StoragePolicy) -> int:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=policy.max_age_days)).isoformat()
        old = conn.execute(
            "DELETE FROM project_traces WHERE project=? AND received<?", (project.key, cutoff)
        ).rowcount
        excess = conn.execute(
            "DELETE FROM project_traces WHERE project=? AND trace_id NOT IN "
            "(SELECT trace_id FROM project_traces WHERE project=? "
            "ORDER BY received DESC, trace_id LIMIT ?)",
            (project.key, project.key, policy.max_traces),
        ).rowcount
        return old + excess

    def put_run(self, project: Project, subject: str, run: Run, policy: StoragePolicy) -> None:
        identities = [run.run_id, run.trace_id]
        identities.extend(span.span_id for span in run.spans)
        identities.extend(span.parent_span_id for span in run.spans if span.parent_span_id)
        if any(redact_sensitive(value) != value for value in identities):
            raise ValueError("Trace identities must not contain sensitive strings")
        # Validate after redaction as well: sanitization must not bypass native validation.
        data = run.model_dump(mode="json")
        data["metadata"] = redact_sensitive(data["metadata"])
        for span in data["spans"]:
            for field in ("attributes", "input_data", "output_data"):
                span[field] = redact_sensitive(span[field])
            for field, value in span.items():
                if isinstance(value, str):
                    span[field] = redact_sensitive(value)
        for field, value in data.items():
            if isinstance(value, str):
                data[field] = redact_sensitive(value)
        clean = Run.model_validate(data)
        body = clean.model_dump_json()
        with closing(self._connect()) as conn, conn:
            conn.execute(
                "INSERT INTO project_traces VALUES(?,?,?,?) ON CONFLICT(project,trace_id) "
                "DO UPDATE SET body=excluded.body, received=excluded.received",
                (project.key, clean.trace_id, body, datetime.now(timezone.utc).isoformat()),
            )
            removed = self._prune(conn, project, policy)
            self._audit(conn, project, subject, "trace.put", body)
            if removed:
                self._audit(conn, project, subject, "retention.prune", str(removed))

    def iter_runs(
        self, project: Project, policy: StoragePolicy, *, limit: int = 20, offset: int = 0
    ) -> Iterator[Run]:
        if not 1 <= limit <= 20 or offset < 0:
            raise ValueError("Use a page size from 1 to 20 and a nonnegative offset")
        # Expired records are invisible even if the scheduled purge has not run.
        cutoff = (datetime.now(timezone.utc) - timedelta(days=policy.max_age_days)).isoformat()
        with closing(self._connect()) as conn:
            rows = conn.execute(
                "SELECT body FROM project_traces WHERE project=? AND received>=? "
                "ORDER BY received DESC, trace_id LIMIT ? OFFSET ?",
                (project.key, cutoff, min(limit, max(0, policy.max_traces - offset)), offset),
            )
            for row in rows:
                yield Run.model_validate_json(row[0])

    def runs(
        self, project: Project, policy: StoragePolicy, *, limit: int = 20, offset: int = 0
    ) -> list[Run]:
        return list(self.iter_runs(project, policy, limit=limit, offset=offset))

    def get_run(self, project: Project, trace_id: str, policy: StoragePolicy) -> Run | None:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=policy.max_age_days)).isoformat()
        with closing(self._connect()) as conn:
            row = conn.execute(
                "SELECT body FROM project_traces WHERE project=? AND trace_id=? AND received>=?",
                (project.key, trace_id, cutoff),
            ).fetchone()
        return Run.model_validate_json(row[0]) if row is not None else None

    def prune(self, project: Project, subject: str, policy: StoragePolicy) -> int:
        with closing(self._connect()) as conn, conn:
            removed = self._prune(conn, project, policy)
            self._audit(conn, project, subject, "retention.prune", str(removed))
        return removed

    def register(self, project: Project, subject: str, entry: RegistryEntry) -> None:
        body = entry.model_dump_json()
        with closing(self._connect()) as conn, conn:
            conn.execute("BEGIN IMMEDIATE")
            prior = conn.execute(
                "SELECT body FROM registry WHERE project=? AND kind=? AND name=? AND version=?",
                (project.key, entry.kind, entry.name, entry.version),
            ).fetchone()
            if prior is not None:
                if prior[0] != body:
                    raise ValueError("Registry versions are immutable; choose a new version")
                return
            conn.execute(
                "INSERT INTO registry VALUES(?,?,?,?,?)",
                (project.key, entry.kind, entry.name, entry.version, body),
            )
            self._audit(conn, project, subject, "registry.register", body)

    def registry(self, project: Project) -> list[RegistryEntry]:
        with closing(self._connect()) as conn:
            rows = conn.execute(
                "SELECT body FROM registry WHERE project=? ORDER BY kind,name,version",
                (project.key,),
            ).fetchall()
        return [RegistryEntry.model_validate_json(row[0]) for row in rows]

    def record(self, project: Project, subject: str, action: str, body: str) -> None:
        with closing(self._connect()) as conn, conn:
            self._audit(conn, project, subject, action, body)

    def export_audit(self, project: Project) -> dict[str, Any]:
        with closing(self._connect()) as conn:
            rows = conn.execute(
                "SELECT sequence,at,subject,action,object_digest FROM audit "
                "WHERE project=? ORDER BY sequence",
                (project.key,),
            ).fetchall()
        return {
            "schema_version": "lens.enterprise.audit/1-candidate",
            "project": project.key,
            "integrity": "not_verified",
            "records": [
                dict(
                    zip(("sequence", "at", "subject", "action", "object_digest"), row, strict=True)
                )
                for row in rows
            ],
        }

    def compliance_export(self, project: Project, policy: StoragePolicy) -> dict[str, Any]:
        """Metadata-only inventory, not a compliance certification or native evidence export."""
        cutoff = (datetime.now(timezone.utc) - timedelta(days=policy.max_age_days)).isoformat()
        with closing(self._connect()) as conn:
            # Stream bodies rather than materializing every captured payload together.
            trace_digests = [
                digest(row[0])
                for row in conn.execute(
                    "SELECT body FROM project_traces WHERE project=? AND received>=? "
                    "ORDER BY received DESC, trace_id LIMIT ?",
                    (project.key, cutoff, policy.max_traces),
                )
            ]
        return {
            "schema_version": "lens.enterprise.compliance/1-candidate",
            "project": project.key,
            "policy": policy.model_dump(),
            "trace_digests": trace_digests,
            "registry": [entry.model_dump() for entry in self.registry(project)],
            "audit": self.export_audit(project),
            "certification": "not_assessed",
        }
