"""Live OTLP/HTTP receiver and real-time dashboard.

Behind the optional ``agenticlens[api]`` extra. Reuses the exact same
conversion (`agenticlens.adapters.otlp.parse_otlp_payload`) and rendering
(`agenticlens.reports.dashboard.render_dashboard_html`) already used by the
batch `import-otlp` command and the file-based `dashboard` command — this
module is wiring, not new conversion/render logic.
"""

from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from agenticlens.adapters.otlp import parse_otlp_payload, safe_trace_filename
from agenticlens.api.store import LiveTraceStore, TraceStore
from agenticlens.models.trace import Run, RunStatus
from agenticlens.reports.dashboard import render_dashboard_html, render_history_html

_REFRESH_SCRIPT = "<script>setTimeout(() => location.reload(), 4000);</script>"


def create_app(
    store: TraceStore | None = None,
    *,
    save_dir: Path | None = None,
) -> FastAPI:
    app = FastAPI(title="AgenticLens Live OTLP Receiver")
    live_store = store if store is not None else LiveTraceStore()

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/v1/traces")
    def receive_traces(payload: dict[str, Any]) -> dict[str, Any]:
        try:
            runs = parse_otlp_payload(payload)
        except (ValueError, KeyError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        for run in runs:
            existing = live_store.get(run.trace_id)
            if existing is not None:
                run = _merge_runs(existing, run)
            live_store.add(run)
            if save_dir is not None:
                save_dir.mkdir(parents=True, exist_ok=True)
                (save_dir / f"{safe_trace_filename(run.trace_id)}.json").write_text(
                    run.model_dump_json(indent=2), encoding="utf-8"
                )
        return {}

    @app.get("/v1/traces")
    def list_traces() -> list[dict[str, Any]]:
        return [_summary(run) for run in live_store.list_recent()]

    @app.get("/v1/traces/{trace_id}")
    def get_trace(trace_id: str) -> Run:
        run = live_store.get(trace_id)
        if run is None:
            raise HTTPException(status_code=404, detail=f"Unknown trace id: {trace_id}")
        return run

    @app.get("/", response_class=HTMLResponse)
    def dashboard(trace_id: str | None = None) -> str:
        recent = live_store.list_recent(limit=20)
        if not recent:
            return _waiting_page()

        selected = live_store.get(trace_id) if trace_id else recent[0]
        if selected is None:
            raise HTTPException(status_code=404, detail=f"Unknown trace id: {trace_id}")

        nav_html = _nav_strip(recent, selected.trace_id)
        return render_dashboard_html(
            run=selected,
            title=f"Live · {selected.application_name}",
            extra_header_html=nav_html + _REFRESH_SCRIPT,
        )

    @app.get("/history", response_class=HTMLResponse)
    def history() -> str:
        return render_history_html(
            live_store.list_recent(),
            title="Trace history",
            trace_link_base="/?trace_id=",
        )

    return app


def _merge_runs(existing: Run, incoming: Run) -> Run:
    """Combine a later OTLP batch's spans into an already-stored trace.

    A single trace can arrive across multiple POSTs (batching exporters,
    long-lived agent traces spanning minutes) — treating a repeat trace_id
    as a merge rather than a wholesale replace is what keeps earlier spans
    from silently disappearing. Span ids that appear in both batches take
    the incoming version (e.g. a span whose end/status was only known once
    it completed in a later batch). Note: a parent/child link that spans
    two different batches was already flattened to no-parent at build time
    (each batch only knows its own span ids) — this merge doesn't attempt
    to re-stitch that; it only stops spans from being lost.
    """
    merged_spans = {span.span_id: span for span in existing.spans}
    merged_spans.update({span.span_id: span for span in incoming.spans})
    completed_candidates = [
        c for c in (existing.completed_at, incoming.completed_at) if c is not None
    ]
    status = (
        RunStatus.FAILED
        if RunStatus.FAILED in (existing.status, incoming.status)
        else incoming.status
    )
    return existing.model_copy(
        update={
            "spans": list(merged_spans.values()),
            "started_at": min(existing.started_at, incoming.started_at),
            "completed_at": max(completed_candidates) if completed_candidates else None,
            "status": status,
        }
    )


def _summary(run: Run) -> dict[str, Any]:
    cost = run.estimated_cost_usd
    return {
        "trace_id": run.trace_id,
        "application_name": run.application_name,
        "span_count": len(run.spans),
        "total_tokens": run.total_tokens,
        "estimated_cost_usd": cost,
        "status": run.status.value,
    }


def _nav_strip(recent: list[Run], selected_trace_id: str) -> str:
    items = []
    for run in recent:
        active = (
            ' style="font-weight:700;text-decoration:underline"'
            if (run.trace_id == selected_trace_id)
            else ""
        )
        items.append(
            f'<a href="/?trace_id={escape(run.trace_id)}"{active}>'
            f"{escape(run.application_name)} · {escape(run.trace_id[:8])}</a>"
        )
    return (
        '<div style="padding:10px 0;display:flex;gap:14px;flex-wrap:wrap;'
        'font-size:12.5px;border-bottom:1px solid var(--border);margin-bottom:14px">'
        f"<strong>Live traces:</strong> {' · '.join(items)}"
        ' · <a href="/history">History</a>'
        "</div>"
    )


def _waiting_page() -> str:
    now = escape(datetime.now(timezone.utc).isoformat(timespec="seconds"))
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AgenticLens · Waiting for traces</title>
{_REFRESH_SCRIPT}
</head>
<body style="font-family:system-ui,sans-serif;background:#f4f7f5;color:#0e1815;
  display:flex;align-items:center;justify-content:center;height:100vh;margin:0">
<div style="text-align:center">
  <h1 style="font-size:18px">Waiting for traces&hellip;</h1>
  <p>Point an OTel Collector's <code>otlphttp</code> exporter at
  <code>/v1/traces</code> on this server. This page refreshes automatically.</p>
  <p style="color:#8a9995;font-size:12px">Checked at {now}</p>
</div>
</body>
</html>"""
