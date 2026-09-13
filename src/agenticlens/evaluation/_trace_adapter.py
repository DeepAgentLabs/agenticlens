"""Bridge AgenticLens's own `Run`/`Span` trace schema into `agentic_evals`'s
minimal, tool-agnostic `EvalTrace`/`EvalSpan` shape.

`agentic_evals` deliberately doesn't know about AgenticLens's `Run` (see its
README) — this is the one place that direction gets bridged, so anyone
building an `EvaluationSample` from an AgenticLens `Run` (e.g. one just
captured live, or imported from OTLP) doesn't have to hand-roll the
conversion themselves.
"""

from agentic_evals import EvalSpan, EvalTrace

from agenticlens.models.trace import Run


def to_eval_trace(run: Run) -> EvalTrace:
    return EvalTrace(
        trace_id=run.trace_id,
        spans=[
            EvalSpan(tool_name=span.tool_name, attributes=dict(span.attributes))
            for span in run.spans
        ],
        total_latency_ms=run.total_latency_ms,
        estimated_cost_usd=run.estimated_cost_usd,
        metadata=dict(run.metadata),
    )
