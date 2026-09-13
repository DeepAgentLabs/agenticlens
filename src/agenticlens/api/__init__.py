"""Optional live OTLP receiver + dashboard, behind the `agenticlens[api]` extra.

Nothing in this package is imported by `agenticlens.cli.main` at module load
time — the CLI imports `agenticlens.api.http` lazily, inside the `serve-otlp`
command body, so importing the base package never requires FastAPI/uvicorn.
"""

from agenticlens.api.store import LiveTraceStore

__all__ = ["LiveTraceStore"]
