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

from agenticlens.adapters.otlp import parse_otlp_payload
from agenticlens.api.store import LiveTraceStore
from agenticlens.models.trace import Run
from agenticlens.reports.dashboard import render_dashboard_html

_REFRESH_SCRIPT = "<script>setTimeout(() => location.reload(), 4000);</script>"


def create_app(
    store: LiveTraceStore | None = None,
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
            live_store.add(run)
            if save_dir is not None:
                save_dir.mkdir(parents=True, exist_ok=True)
                (save_dir / f"{run.trace_id}.json").write_text(
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

    return app


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
        active = ' style="font-weight:700;text-decoration:underline"' if (
            run.trace_id == selected_trace_id
        ) else ""
        items.append(
            f'<a href="/?trace_id={escape(run.trace_id)}"{active}>'
            f"{escape(run.application_name)} · {escape(run.trace_id[:8])}</a>"
        )
    return (
        '<div style="padding:10px 0;display:flex;gap:14px;flex-wrap:wrap;'
        'font-size:12.5px;border-bottom:1px solid var(--border);margin-bottom:14px">'
        f"<strong>Live traces:</strong> {' · '.join(items)}"
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
