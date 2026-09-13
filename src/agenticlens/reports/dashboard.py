"""Render AgenticLens artifacts (trace, workflow, evaluation, comparison) as one
standalone HTML dashboard.

This module only renders already-computed data — it does not run the
recommendation engine, the evaluation gate, or the comparison runner itself.
Callers (typically the CLI) build those models first and pass them in.
"""

from datetime import datetime
from html import escape
from pathlib import Path

from agenticlens.comparison.models import ComparisonReport, MetricDelta
from agenticlens.comparison.stats import percentile
from agenticlens.evaluation.gate import GateDecision
from agenticlens.evaluation.models import EvaluationReport
from agenticlens.models.enums import Severity, StepType
from agenticlens.models.recommendation import Recommendation
from agenticlens.models.step import Step
from agenticlens.models.trace import Run, RunStatus, Span, SpanType
from agenticlens.models.workflow import Workflow

# ---------------------------------------------------------------------------
# Fixed categorical + status color slots.
#
# Slots are hardcoded (not derived from what appears in any one report) so a
# given step/span type always renders in the same color across reports. Only
# the 8 most-informative SpanType members get a dedicated slot; the rest
# (VALIDATION, RETRY, CUSTOM) share one muted "Other" swatch rather than
# generating a 9th hue.
# ---------------------------------------------------------------------------

_OTHER_SLOT = "other"

_STEP_TYPE_SLOTS: dict[StepType, int] = {
    StepType.PLANNER: 1,
    StepType.RETRIEVER: 2,
    StepType.TOOL_CALL: 3,
    StepType.LLM_CALL: 4,
    StepType.MEMORY: 5,
    StepType.FINAL_RESPONSE: 6,
}

_SPAN_TYPE_SLOTS: dict[SpanType, int] = {
    SpanType.MODEL_CALL: 1,
    SpanType.TOOL_CALL: 2,
    SpanType.RETRIEVAL: 3,
    SpanType.PLANNING: 4,
    SpanType.FINAL_RESPONSE: 5,
    SpanType.MEMORY_READ: 6,
    SpanType.MEMORY_WRITE: 7,
    SpanType.DELEGATION: 8,
}

_SEVERITY_CHIP: dict[Severity, tuple[str, str]] = {
    Severity.CRITICAL: ("critical", "Critical"),
    Severity.WARNING: ("warning", "Warning"),
    Severity.INFO: ("info", "Info"),
}


def _swatch(slot: int | str) -> str:
    return f"var(--cat-{slot})"


def _label(value: StepType | SpanType) -> str:
    return str(value.value).replace("_", " ").capitalize()


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------


def _fmt_usd(value: float | None) -> str:
    if value is None:
        return "—"
    if abs(value) < 1:
        return f"${value:.4f}"
    return f"${value:,.2f}"


def _fmt_int(value: float | int | None) -> str:
    if value is None:
        return "—"
    return f"{value:,.0f}"


def _fmt_ms(value: float | None) -> str:
    if value is None:
        return "—"
    if value < 1000:
        return f"{value:.0f}ms"
    return f"{value / 1000:.2f}s"


# ---------------------------------------------------------------------------
# Stat strip
# ---------------------------------------------------------------------------


def _stat_tile(label: str, value: str, sub: str | None = None, *, accent: bool = False) -> str:
    accent_style = ' style="color:var(--accent-strong)"' if accent else ""
    sub_html = f'<div class="stat-sub">{escape(sub)}</div>' if sub else ""
    return (
        '<div class="stat">'
        f'<div class="stat-label">{escape(label)}</div>'
        f'<div class="stat-value mono"{accent_style}>{value}</div>'
        f"{sub_html}"
        "</div>"
    )


def _render_stats(
    workflow: Workflow | None,
    run: Run | None,
    recommendations: list[Recommendation] | None,
) -> str:
    tiles: list[str] = []

    if run is not None:
        cost, tokens, latency_ms = run.estimated_cost_usd, run.total_tokens, run.total_latency_ms
    elif workflow is not None:
        cost, tokens, latency_ms = (
            workflow.total_cost,
            workflow.total_tokens,
            workflow.latency * 1000,
        )
    else:
        cost, tokens, latency_ms = None, None, None

    if cost is not None:
        tiles.append(_stat_tile("Total cost", _fmt_usd(cost)))
    if tokens is not None:
        tiles.append(_stat_tile("Total tokens", _fmt_int(tokens)))
    if latency_ms is not None:
        tiles.append(_stat_tile("Latency", _fmt_ms(latency_ms)))

    if recommendations:
        tokens_saved = sum(r.tokens_saved for r in recommendations)
        usd_saved = sum(r.estimated_usd_savings or 0.0 for r in recommendations)
        if tokens_saved:
            tiles.append(
                _stat_tile(
                    "Reducible tokens", _fmt_int(tokens_saved), f"{len(recommendations)} finding(s)"
                )
            )
        if usd_saved:
            tiles.append(_stat_tile("Projected savings", _fmt_usd(usd_saved), accent=True))

    if not tiles:
        return ""
    return f'<section class="stat-strip">{"".join(tiles)}</section>'


# ---------------------------------------------------------------------------
# Agent timeline (from a Run)
# ---------------------------------------------------------------------------


def _timeline_scale_ms(run: Run) -> float:
    total = run.total_latency_ms
    if total > 0:
        return total
    max_end = 0.0
    for span in run.spans:
        offset = (span.started_at - run.started_at).total_seconds() * 1000
        max_end = max(max_end, offset + span.latency_ms)
    return max_end


def _axis_row(total_ms: float) -> str:
    if total_ms <= 0:
        return ""
    marks = "".join(
        f'<span style="left:{pct:.2f}%">{_fmt_ms(total_ms * pct / 100)}</span>'
        for pct in (0.0, 50.0, 100.0)
    )
    return (
        f'<div class="tl-axis"><div></div><div class="tl-axis-track">{marks}</div><div></div></div>'
    )


def _timeline_legend(run: Run) -> str:
    present = {span.span_type for span in run.spans}
    items: list[str] = []
    for span_type, slot in _SPAN_TYPE_SLOTS.items():
        if span_type in present:
            items.append(_legend_item(slot, _label(span_type)))
    if present - set(_SPAN_TYPE_SLOTS):
        items.append(_legend_item(_OTHER_SLOT, "Other"))
    return f'<div class="legend">{"".join(items)}</div>' if items else ""


def _legend_item(slot: int | str, label: str) -> str:
    return f'<span class="legend-item"><span class="sw" style="background:{_swatch(slot)}"></span>{escape(label)}</span>'


def _span_row(span: Span, run_start: datetime, total_ms: float) -> str:
    offset_ms = max(0.0, (span.started_at - run_start).total_seconds() * 1000)
    duration_ms = max(span.latency_ms, 0.0)
    if total_ms > 0:
        left_pct = min(100.0, (offset_ms / total_ms) * 100)
        width_pct = max(0.6, min(100.0 - left_pct, (duration_ms / total_ms) * 100))
    else:
        left_pct, width_pct = 0.0, 100.0

    slot = _SPAN_TYPE_SLOTS.get(span.span_type, _OTHER_SLOT)
    agent = f"{escape(span.agent_name)} · " if span.agent_name else ""
    figs_parts = [f"{span.total_tokens:,} tok" if span.total_tokens else _label(span.span_type)]
    if span.estimated_cost_usd is not None:
        figs_parts.append(f'<span class="mono">{_fmt_usd(span.estimated_cost_usd)}</span>')
    figs_parts.append(f'<span class="mono">{_fmt_ms(duration_ms)}</span>')

    return (
        '<div class="tl-row">'
        '<div class="tl-id">'
        f'<span class="sw" style="background:{_swatch(slot)}"></span>'
        f'<div><div class="tl-name">{escape(span.name)}</div>'
        f'<div class="tl-agent">{agent}{escape(span.span_type.value)}</div></div>'
        "</div>"
        '<div class="tl-track">'
        f'<div class="tl-bar" style="left:{left_pct:.2f}%;width:{width_pct:.2f}%;'
        f'background:{_swatch(slot)}"></div>'
        "</div>"
        f'<div class="tl-figs">{"".join(figs_parts)}</div>'
        "</div>"
    )


def _render_timeline(run: Run) -> str:
    if not run.spans:
        return ""
    spans = sorted(run.spans, key=lambda s: s.started_at)
    total_ms = _timeline_scale_ms(run)
    rows = "".join(_span_row(s, run.started_at, total_ms) for s in spans)
    return (
        '<div class="panel">'
        '<div class="panel-head"><h2 class="panel-title">Agent timeline</h2>'
        f'<span class="panel-note">{len(spans)} span(s) · {_fmt_ms(total_ms)}</span></div>'
        f"{_timeline_legend(run)}"
        f'<div role="table" aria-label="Trace spans on a shared timeline">{rows}</div>'
        f"{_axis_row(total_ms)}"
        "</div>"
    )


# ---------------------------------------------------------------------------
# Cost / token breakdown (from a Run's spans or a Workflow's steps)
# ---------------------------------------------------------------------------

_CostRow = tuple[str, int | str, float | None, int]


def _group_run_by_span_type(run: Run) -> list[_CostRow]:
    groups: dict[SpanType, list[Span]] = {}
    for span in run.spans:
        groups.setdefault(span.span_type, []).append(span)

    rows: list[_CostRow] = []
    for span_type, slot in _SPAN_TYPE_SLOTS.items():
        spans = groups.get(span_type)
        if not spans:
            continue
        costs = [s.estimated_cost_usd for s in spans if s.estimated_cost_usd is not None]
        cost = sum(costs) if costs else None
        tokens = sum(s.total_tokens for s in spans)
        rows.append((_label(span_type), slot, cost, tokens))

    other_spans = [s for st, ss in groups.items() if st not in _SPAN_TYPE_SLOTS for s in ss]
    if other_spans:
        costs = [s.estimated_cost_usd for s in other_spans if s.estimated_cost_usd is not None]
        cost = sum(costs) if costs else None
        tokens = sum(s.total_tokens for s in other_spans)
        rows.append(("Other", _OTHER_SLOT, cost, tokens))
    return rows


def _group_workflow_by_step_type(workflow: Workflow) -> list[_CostRow]:
    groups: dict[StepType, list[Step]] = {}
    for step in workflow.steps:
        groups.setdefault(step.type, []).append(step)

    rows: list[_CostRow] = []
    for step_type, slot in _STEP_TYPE_SLOTS.items():
        steps = groups.get(step_type)
        if not steps:
            continue
        costs = [s.metrics.cost for s in steps if s.metrics.cost is not None]
        cost = sum(costs) if costs else None
        tokens = sum(s.metrics.total_tokens for s in steps)
        rows.append((_label(step_type), slot, cost, tokens))
    return rows


def _render_cost_breakdown(rows: list[_CostRow]) -> str:
    if not rows:
        return ""
    use_cost = any(cost is not None for _, _, cost, _ in rows)
    values = [(cost if use_cost else float(tokens)) for _, _, cost, tokens in rows]
    numeric_values = [v for v in values if v is not None]
    max_value = max(numeric_values) if numeric_values else 0.0

    body: list[str] = []
    for label, slot, cost, tokens in rows:
        raw_value = cost if use_cost else float(tokens)
        width_pct = (
            0.0 if not max_value else max(2.0, min(100.0, (raw_value or 0.0) / max_value * 100))
        )
        display = _fmt_usd(cost) if use_cost else f"{tokens:,} tok"
        body.append(
            '<div class="cost-row">'
            f'<div class="cost-name"><span class="sw" style="background:{_swatch(slot)}"></span>'
            f"{escape(label)}</div>"
            '<div class="cost-track">'
            f'<div class="cost-fill" style="width:{width_pct:.1f}%;background:{_swatch(slot)}"></div>'
            "</div>"
            f'<div class="cost-val mono">{display}</div>'
            "</div>"
        )

    axis = ""
    if max_value:
        half = max_value / 2
        fmt = _fmt_usd if use_cost else (lambda v: f"{v:,.0f}")
        axis = (
            '<div class="cost-axis"><div></div><div class="cost-axis-track">'
            f'<span style="left:0%">{fmt(0.0)}</span>'
            f'<span style="left:50%">{fmt(half)}</span>'
            f'<span style="left:100%">{fmt(max_value)}</span>'
            "</div><div></div></div>"
        )

    note = (
        ""
        if use_cost
        else '<p class="panel-note-line">No priced spans in this run — showing token counts.</p>'
    )
    return (
        '<div class="panel">'
        '<div class="panel-head"><h2 class="panel-title">Cost by workflow area</h2></div>'
        f"{note}"
        f'<div role="table" aria-label="Cost per workflow area">{"".join(body)}</div>'
        f"{axis}"
        "</div>"
    )


# ---------------------------------------------------------------------------
# Waste findings (from RecommendationEngine output)
# ---------------------------------------------------------------------------


def _finding_card(rec: Recommendation) -> str:
    css_class, label = _SEVERITY_CHIP.get(rec.severity, _SEVERITY_CHIP[Severity.INFO])
    meta_bits: list[str] = []
    if rec.tokens_saved:
        meta_bits.append(f"−{rec.tokens_saved:,} tok/run")
    if rec.estimated_usd_savings:
        meta_bits.append(f"−{_fmt_usd(rec.estimated_usd_savings)}/run")
    if rec.cost_savings:
        meta_bits.append(f"−{_fmt_usd(rec.cost_savings)}/run")
    if rec.estimated_monthly_savings:
        meta_bits.append(f"≈ {_fmt_usd(rec.estimated_monthly_savings)}/mo")
    meta = " · ".join(meta_bits) or "No savings estimate"
    context = f"<span>{escape(rec.step_name)}</span>" if rec.step_name else "<span></span>"
    return (
        '<div class="finding">'
        f'<div class="f-head"><span class="f-chip c-{css_class}"><span class="dot"></span>{label}</span></div>'
        f'<div class="f-title">{escape(rec.title)}</div>'
        f'<p class="f-body">{escape(rec.description)}</p>'
        f'<div class="f-meta">{context}<span class="f-save">{escape(meta)}</span></div>'
        "</div>"
    )


def _render_findings(recommendations: list[Recommendation] | None) -> str:
    if not recommendations:
        return ""
    cards = "".join(_finding_card(r) for r in recommendations)
    return (
        '<div class="panel">'
        '<div class="panel-head"><h2 class="panel-title">Waste findings</h2>'
        f'<span class="panel-note">{len(recommendations)} flagged</span></div>'
        f"{cards}"
        "</div>"
    )


# ---------------------------------------------------------------------------
# Release gate (from an EvaluationReport, optionally with a GateDecision)
# ---------------------------------------------------------------------------


def _render_gate(evaluation: EvaluationReport | None, gate: GateDecision | None) -> str:
    if evaluation is None:
        return ""
    summary = evaluation.summary
    rows: list[tuple[str, str]] = [
        (
            "Cases passed",
            f"{summary.passed_cases:,} / {summary.total_cases:,} ({summary.pass_rate:.1%})",
        ),
        ("Average score", f"{summary.average_score:.3f}"),
        ("Average latency", _fmt_ms(summary.average_latency_ms)),
    ]
    if summary.total_cost_usd is not None:
        rows.append(("Total cost", _fmt_usd(summary.total_cost_usd)))
    row_html = "".join(
        '<div class="gate-row">'
        f'<span class="gate-label">{escape(label)}</span>'
        f'<span class="gate-value mono">{escape(value)}</span>'
        "</div>"
        for label, value in rows
    )

    if gate is not None:
        verdict_class = "pill-good" if gate.passed else "pill-crit"
        verdict_text = "PASS" if gate.passed else "FAIL"
        reasons_html = ""
        if gate.reasons:
            items = "".join(f"<li>{escape(reason)}</li>" for reason in gate.reasons)
            reasons_html = f'<ul class="gate-reasons">{items}</ul>'
        footer = (
            '<div class="gate-verdict"><span class="label">Verdict</span>'
            f'<span class="pill {verdict_class}"><span class="dot"></span>{verdict_text}</span></div>'
            f"{reasons_html}"
        )
    else:
        footer = '<p class="panel-note-line">No release gate configured for this evaluation.</p>'

    return (
        '<div class="panel">'
        '<div class="panel-head"><h2 class="panel-title">Release gate</h2>'
        f'<span class="panel-note">{escape(evaluation.suite_name)}</span></div>'
        f"{row_html}"
        f"{footer}"
        "</div>"
    )


# ---------------------------------------------------------------------------
# Baseline vs. candidate comparison
# ---------------------------------------------------------------------------


def _cmp_card(metric: str, old_fmt: str, new_fmt: str, delta: MetricDelta) -> str:
    css_class, label = ("critical", "Regression") if delta.regressed else ("good", "No regression")
    rel = f" ({delta.relative:+.1%})" if delta.relative is not None else ""
    return (
        '<div class="cmp-cell">'
        f'<div class="cmp-metric">{escape(metric)}</div>'
        '<div class="cmp-vals">'
        f'<span class="cmp-old mono">{old_fmt}</span><span class="cmp-new mono">{new_fmt}</span>'
        "</div>"
        f'<span class="cmp-delta c-{css_class}"><span class="dot"></span>{escape(label)}{escape(rel)}</span>'
        "</div>"
    )


def _render_comparison(comparison: ComparisonReport | None) -> str:
    if comparison is None:
        return ""
    baseline, candidate = comparison.baseline, comparison.candidate
    cards = [
        _cmp_card(
            "Success rate",
            f"{baseline.success_rate:.1%}",
            f"{candidate.success_rate:.1%}",
            comparison.success_rate_delta,
        ),
        _cmp_card(
            "Mean tokens",
            f"{baseline.tokens.mean:,.0f}",
            f"{candidate.tokens.mean:,.0f}",
            comparison.mean_tokens_delta,
        ),
        _cmp_card(
            "Mean latency",
            _fmt_ms(baseline.latency_ms.mean),
            _fmt_ms(candidate.latency_ms.mean),
            comparison.mean_latency_ms_delta,
        ),
    ]
    if (
        comparison.mean_cost_usd_delta is not None
        and baseline.cost_usd is not None
        and candidate.cost_usd is not None
    ):
        cards.append(
            _cmp_card(
                "Mean cost",
                _fmt_usd(baseline.cost_usd.mean),
                _fmt_usd(candidate.cost_usd.mean),
                comparison.mean_cost_usd_delta,
            )
        )

    note_bits: list[str] = []
    if comparison.regressions:
        note_bits.append("Regressions: " + ", ".join(escape(r) for r in comparison.regressions))
    if comparison.sample_size_guidance:
        note_bits.append(escape(comparison.sample_size_guidance))
    note = (
        f'<div class="compare-foot"><div class="compare-note">{" — ".join(note_bits)}</div></div>'
        if note_bits
        else ""
    )
    return (
        '<div class="panel">'
        '<div class="panel-head"><h2 class="panel-title">Baseline vs. candidate</h2>'
        f'<span class="panel-note">{baseline.run_count} vs {candidate.run_count} runs · '
        f"threshold {comparison.regression_threshold:.0%}</span></div>"
        f'<div class="compare-grid">{"".join(cards)}</div>'
        f"{note}"
        "</div>"
    )


# ---------------------------------------------------------------------------
# Document assembly
# ---------------------------------------------------------------------------

_CSS = """
  :root{
    --bg:#f4f7f5; --surface:#ffffff; --surface-2:#eef3f0;
    --border:rgba(13,26,23,0.11); --border-strong:rgba(13,26,23,0.18);
    --ink:#0e1815; --ink-2:#4c5c58; --muted:#8a9995;
    --accent:#0e8b8a; --accent-strong:#086564; --accent-soft:#e0f2f0;
    --shadow:0 1px 2px rgba(13,26,23,0.04), 0 8px 24px -12px rgba(13,26,23,0.16);
    --good:#0ca30c; --warning:#fab219; --critical:#d03b3b;
    --cat-1:#2a78d6; --cat-2:#eb6834; --cat-3:#1baf7a; --cat-4:#eda100;
    --cat-5:#e87ba4; --cat-6:#008300; --cat-7:#4a3aa7; --cat-8:#e34948;
    --cat-other:#8a9995;
  }
  @media (prefers-color-scheme: dark){
    :root:not([data-theme="light"]){
      --bg:#0c1211; --surface:#131b19; --surface-2:#182220;
      --border:rgba(233,242,238,0.10); --border-strong:rgba(233,242,238,0.18);
      --ink:#eef3f0; --ink-2:#aebdb8; --muted:#6d8280;
      --accent:#43c7c4; --accent-strong:#7fdcd9; --accent-soft:rgba(67,199,196,0.14);
      --shadow:0 1px 2px rgba(0,0,0,0.3), 0 12px 30px -14px rgba(0,0,0,0.6);
      --cat-1:#3987e5; --cat-2:#d95926; --cat-3:#199e70; --cat-4:#c98500;
      --cat-5:#d55181; --cat-6:#008300; --cat-7:#9085e9; --cat-8:#e66767;
      --cat-other:#6d8280;
    }
  }
  :root[data-theme="dark"]{
    --bg:#0c1211; --surface:#131b19; --surface-2:#182220;
    --border:rgba(233,242,238,0.10); --border-strong:rgba(233,242,238,0.18);
    --ink:#eef3f0; --ink-2:#aebdb8; --muted:#6d8280;
    --accent:#43c7c4; --accent-strong:#7fdcd9; --accent-soft:rgba(67,199,196,0.14);
    --shadow:0 1px 2px rgba(0,0,0,0.3), 0 12px 30px -14px rgba(0,0,0,0.6);
    --cat-1:#3987e5; --cat-2:#d95926; --cat-3:#199e70; --cat-4:#c98500;
    --cat-5:#d55181; --cat-6:#008300; --cat-7:#9085e9; --cat-8:#e66767;
    --cat-other:#6d8280;
  }
  *{box-sizing:border-box}
  body{background:var(--bg);color:var(--ink);
    font-family:system-ui,-apple-system,"Segoe UI",sans-serif;-webkit-font-smoothing:antialiased;margin:0}
  h1,h2{font-family:inherit;margin:0}
  .mono{font-family:ui-monospace,"SFMono-Regular","SF Mono",Consolas,"Liberation Mono",monospace;
    font-variant-numeric:tabular-nums}
  .shell{max-width:1180px;margin:0 auto;padding:28px 24px 60px}
  .topbar{display:flex;align-items:center;justify-content:space-between;gap:16px;
    padding-bottom:18px;border-bottom:1px solid var(--border);margin-bottom:16px;flex-wrap:wrap}
  .brand{display:flex;align-items:center;gap:10px}
  .brand-name{font-size:19px;font-weight:700;letter-spacing:-0.01em}
  .brand-tag{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:0.08em;margin-top:1px}
  .run-meta{display:flex;align-items:center;gap:18px;flex-wrap:wrap}
  .run-meta dl{display:flex;align-items:baseline;gap:6px;margin:0}
  .run-meta dt{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:0.06em}
  .run-meta dd{margin:0;font-size:13px;color:var(--ink-2)}
  .pill{display:inline-flex;align-items:center;gap:6px;padding:5px 12px 5px 9px;border-radius:100px;
    font-size:12.5px;font-weight:600;white-space:nowrap;border:1px solid var(--border-strong);
    background:var(--surface-2);color:var(--ink)}
  .pill .dot{width:7px;height:7px;border-radius:50%;flex:none}
  .pill-good .dot{background:var(--good)}
  .pill-warn .dot{background:var(--warning)}
  .pill-crit .dot{background:var(--critical)}
  .stat-strip{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:1px;
    background:var(--border);border:1px solid var(--border);border-radius:12px;overflow:hidden;margin-bottom:24px}
  .stat{background:var(--surface);padding:16px 18px}
  .stat-label{font-size:11.5px;color:var(--muted);text-transform:uppercase;letter-spacing:0.06em;margin-bottom:8px}
  .stat-value{font-size:25px;font-weight:600;letter-spacing:-0.01em}
  .stat-sub{font-size:12px;color:var(--ink-2);margin-top:4px}
  .grid-main{display:grid;grid-template-columns:1.62fr 1fr;gap:18px;align-items:start}
  .col-main,.col-side{display:flex;flex-direction:column;gap:18px}
  .panel{background:var(--surface);border:1px solid var(--border);border-radius:12px;
    box-shadow:var(--shadow);padding:20px 22px 22px}
  .panel-head{display:flex;align-items:baseline;justify-content:space-between;gap:12px;margin-bottom:16px}
  .panel-title{font-size:15px;font-weight:700}
  .panel-note{font-size:12px;color:var(--muted)}
  .panel-note-line{font-size:12.5px;color:var(--ink-2);margin:4px 0 0}
  .legend{display:flex;gap:14px;flex-wrap:wrap;margin-bottom:14px}
  .legend-item{display:flex;align-items:center;gap:6px;font-size:12px;color:var(--ink-2)}
  .sw{width:9px;height:9px;border-radius:3px;flex:none}
  .tl-row{display:grid;grid-template-columns:190px 1fr 168px;gap:12px;align-items:center;padding:9px 0}
  .tl-row+.tl-row{border-top:1px solid var(--border)}
  .tl-id{display:flex;align-items:center;gap:8px;min-width:0}
  .tl-name{font-size:13px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .tl-agent{font-size:11px;color:var(--muted)}
  .tl-track{position:relative;height:20px;background:var(--surface-2);border-radius:5px}
  .tl-bar{position:absolute;top:2px;bottom:2px;border-radius:4px;min-width:6px}
  .tl-figs{display:flex;justify-content:flex-end;gap:10px;font-size:11.5px;color:var(--ink-2);white-space:nowrap}
  .tl-figs .mono{color:var(--ink)}
  .tl-axis{display:grid;grid-template-columns:190px 1fr 168px;gap:12px;margin-top:6px}
  .tl-axis-track{position:relative;height:14px}
  .tl-axis-track span{position:absolute;top:0;font-size:10.5px;color:var(--muted);transform:translateX(-50%)}
  .tl-axis-track span:first-child{transform:none}
  .cost-row{display:grid;grid-template-columns:118px 1fr 92px;gap:12px;align-items:center;padding:7px 0}
  .cost-name{display:flex;align-items:center;gap:7px;font-size:12.5px;color:var(--ink-2)}
  .cost-track{position:relative;height:14px;background:var(--surface-2);border-radius:4px}
  .cost-fill{position:absolute;top:0;bottom:0;left:0;border-radius:4px}
  .cost-val{font-size:12.5px;text-align:right}
  .cost-axis{display:grid;grid-template-columns:118px 1fr 92px;gap:12px;margin-top:4px}
  .cost-axis-track{position:relative;height:14px}
  .cost-axis-track span{position:absolute;top:0;font-size:10.5px;color:var(--muted);transform:translateX(-50%)}
  .cost-axis-track span:first-child{transform:none}
  .finding{padding:13px 0}
  .finding+.finding{border-top:1px solid var(--border)}
  .f-head{display:flex;align-items:center;gap:8px;margin-bottom:5px}
  .f-chip{display:inline-flex;align-items:center;gap:6px;font-size:11px;font-weight:700;
    text-transform:uppercase;letter-spacing:0.04em}
  .f-chip .dot{width:7px;height:7px;border-radius:50%}
  .f-chip.c-critical .dot{background:var(--critical)}
  .f-chip.c-warning .dot{background:var(--warning)}
  .f-chip.c-info .dot{background:var(--accent)}
  .f-title{font-size:13.5px;font-weight:700}
  .f-body{font-size:12.5px;color:var(--ink-2);line-height:1.5;margin:0 0 8px}
  .f-meta{display:flex;justify-content:space-between;align-items:center;font-size:11.5px;
    color:var(--muted);gap:10px}
  .f-save{font-weight:700;color:var(--ink)}
  .gate-row{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:8px 0;font-size:13px}
  .gate-row+.gate-row{border-top:1px solid var(--border)}
  .gate-label{color:var(--ink-2)}
  .gate-value{font-size:13px;font-weight:600}
  .gate-verdict{display:flex;align-items:center;justify-content:space-between;gap:10px;
    margin-top:12px;padding-top:14px;border-top:1px solid var(--border-strong)}
  .gate-verdict .label{font-size:13px;font-weight:700}
  .gate-reasons{margin:10px 0 0;padding-left:18px;font-size:12.5px;color:var(--ink-2)}
  .compare-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:14px}
  .cmp-cell{background:var(--surface-2);border-radius:10px;padding:14px 16px}
  .cmp-metric{font-size:11.5px;color:var(--muted);text-transform:uppercase;letter-spacing:0.05em;margin-bottom:8px}
  .cmp-vals{display:flex;align-items:baseline;gap:8px;margin-bottom:6px}
  .cmp-old{font-size:13px;color:var(--muted);text-decoration:line-through}
  .cmp-new{font-size:19px;font-weight:600}
  .cmp-delta{display:inline-flex;align-items:center;gap:5px;font-size:11.5px;font-weight:700}
  .cmp-delta .dot{width:6px;height:6px;border-radius:50%}
  .cmp-delta.c-good .dot{background:var(--good)}
  .cmp-delta.c-critical .dot{background:var(--critical)}
  .compare-foot{margin-top:16px;padding-top:14px;border-top:1px solid var(--border)}
  .compare-note{font-size:12.5px;color:var(--ink-2)}
  footer{margin-top:30px;padding-top:18px;border-top:1px solid var(--border);
    font-size:12px;color:var(--muted);display:flex;justify-content:space-between;gap:14px;flex-wrap:wrap}
  @media (max-width:920px){
    .grid-main{grid-template-columns:1fr}
    .stat-strip{grid-template-columns:repeat(2,1fr)}
  }
  @media (max-width:640px){
    .tl-row{grid-template-columns:130px 1fr;grid-template-areas:"id id" "track figs";row-gap:6px}
    .tl-id{grid-area:id}.tl-track{grid-area:track}.tl-figs{grid-area:figs;justify-content:flex-start}
    .tl-axis{display:none}
    .cost-row{grid-template-columns:100px 1fr;grid-template-areas:"name name" "track val";row-gap:5px}
    .cost-name{grid-area:name}.cost-track{grid-area:track}.cost-val{grid-area:val;text-align:left}
    .cost-axis{display:none}
  }
"""


def _heading_and_meta(
    workflow: Workflow | None,
    run: Run | None,
    evaluation: EvaluationReport | None,
    title: str | None,
) -> tuple[str, list[tuple[str, str]]]:
    if title:
        heading = title
    elif run is not None:
        heading = run.application_name
    elif workflow is not None:
        heading = workflow.name
    elif evaluation is not None:
        heading = evaluation.suite_name
    else:
        heading = "AgenticLens dashboard"

    meta: list[tuple[str, str]] = []
    if run is not None:
        meta.append(("Run", run.run_id))
        meta.append(("Status", run.status.value))
    if workflow is not None:
        meta.append(("Workflow ID", workflow.id))
    if evaluation is not None:
        meta.append(("Suite version", evaluation.suite_version))
    return heading, meta


def render_dashboard_html(
    *,
    workflow: Workflow | None = None,
    recommendations: list[Recommendation] | None = None,
    run: Run | None = None,
    evaluation: EvaluationReport | None = None,
    gate: GateDecision | None = None,
    comparison: ComparisonReport | None = None,
    title: str | None = None,
    extra_header_html: str | None = None,
) -> str:
    """Render a standalone HTML dashboard from whichever artifacts are given.

    At least one of ``workflow``, ``run``, ``evaluation``, or ``comparison``
    is required. ``recommendations`` and ``gate`` are display-only companions
    to ``workflow`` and ``evaluation`` respectively and are ignored if their
    companion is absent from the output (they still render standalone
    sections where that makes sense).

    ``extra_header_html`` is an optional pre-built, already-escaped HTML
    fragment rendered directly under the top bar — e.g. a "recent traces"
    nav strip for a live view. It is inserted verbatim: the caller is
    responsible for escaping anything user-controlled in it, the same as
    every other string this function treats as trusted markup.
    """
    if workflow is None and run is None and evaluation is None and comparison is None:
        raise ValueError(
            "render_dashboard_html requires at least one of workflow, run, "
            "evaluation, or comparison."
        )

    heading, meta = _heading_and_meta(workflow, run, evaluation, title)
    meta_html = "".join(
        f'<dl><dt>{escape(k)}</dt><dd class="mono">{escape(v)}</dd></dl>' for k, v in meta
    )

    cost_rows: list[_CostRow] = []
    if run is not None:
        cost_rows = _group_run_by_span_type(run)
    elif workflow is not None:
        cost_rows = _group_workflow_by_step_type(workflow)

    main_html = "".join(
        [
            _render_timeline(run) if run is not None else "",
            _render_cost_breakdown(cost_rows),
        ]
    )
    side_html = "".join(
        [
            _render_findings(recommendations),
            _render_gate(evaluation, gate),
        ]
    )

    if main_html and side_html:
        content = (
            '<section class="grid-main">'
            f'<div class="col-main">{main_html}</div>'
            f'<div class="col-side">{side_html}</div>'
            "</section>"
        )
    elif main_html or side_html:
        content = f'<div class="col-main">{main_html or side_html}</div>'
    else:
        content = ""

    stats_html = _render_stats(workflow, run, recommendations)
    comparison_html = _render_comparison(comparison)
    body_html = f"{stats_html}{content}{comparison_html}"

    return _page(heading, meta_html, extra_header_html, body_html)


def _page(
    heading: str,
    meta_html: str,
    extra_header_html: str | None,
    body_html: str,
    *,
    tagline: str = "AgenticLens dashboard",
) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AgenticLens · {escape(heading)}</title>
<style>{_CSS}</style>
</head>
<body>
<div class="shell">
  <header class="topbar">
    <div class="brand">
      <svg width="28" height="28" viewBox="0 0 30 30" fill="none" aria-hidden="true">
        <circle cx="15" cy="15" r="13" style="stroke:var(--accent);stroke-width:2"/>
        <circle cx="15" cy="15" r="7.5" style="stroke:var(--accent);stroke-width:2"/>
        <circle cx="15" cy="15" r="2.4" style="fill:var(--accent)"/>
      </svg>
      <div>
        <div class="brand-name">{escape(heading)}</div>
        <div class="brand-tag">{escape(tagline)}</div>
      </div>
    </div>
    <div class="run-meta">{meta_html}</div>
  </header>
  {extra_header_html or ""}
  {body_html}
  <footer>
    <span>Rendered locally by AgenticLens — no hosted backend, no data egress.</span>
  </footer>
</div>
</body>
</html>"""


def render_history_html(
    runs: list[Run],
    *,
    title: str | None = None,
    trace_link_base: str | None = None,
) -> str:
    """Render a cross-trace history view: aggregate stats + a row per trace.

    Unlike `render_dashboard_html`, an empty ``runs`` list is a valid input
    (renders a placeholder) rather than a `ValueError` — a fresh trace store
    legitimately has nothing in it yet.

    ``trace_link_base`` is prefixed to each trace id to build that row's
    link (e.g. ``"/?trace_id="`` for the live receiver); omit it to render
    plain text, for offline/standalone history pages with nowhere to link.
    """
    heading = title or "Trace history"
    if not runs:
        body_html = (
            '<div class="panel"><p class="panel-note-line">No traces recorded yet.</p></div>'
        )
        return _page(heading, "", None, body_html, tagline="AgenticLens history")

    meta_html = f'<dl><dt>Traces</dt><dd class="mono">{len(runs)}</dd></dl>'
    body_html = _render_history_stats(runs) + _render_history_rows(runs, trace_link_base)
    return _page(heading, meta_html, None, body_html, tagline="AgenticLens history")


def _render_history_stats(runs: list[Run]) -> str:
    total_tokens = sum(run.total_tokens for run in runs)
    priced = [run.estimated_cost_usd for run in runs if run.estimated_cost_usd is not None]
    cost_sub = None if len(priced) == len(runs) else f"{len(priced)} of {len(runs)} traces priced"
    failed = sum(1 for run in runs if run.status is RunStatus.FAILED)
    error_rate = failed / len(runs)
    latencies = [run.total_latency_ms for run in runs if run.completed_at is not None]
    p95_latency = percentile(latencies, 0.95) if latencies else None

    tiles = [
        _stat_tile("Total traces", _fmt_int(len(runs))),
        _stat_tile("Total tokens", _fmt_int(total_tokens)),
        _stat_tile(
            "Total cost", _fmt_usd(sum(priced)) if priced else "—", sub=cost_sub, accent=True
        ),
        _stat_tile("Error rate", f"{error_rate * 100:.1f}%"),
        _stat_tile("P95 latency", _fmt_ms(p95_latency)),
    ]
    return f'<section class="stat-strip">{"".join(tiles)}</section>'


def _history_row(run: Run, trace_link_base: str | None) -> str:
    short_id = run.trace_id[:12]
    label = f'{escape(run.application_name)} · <span class="mono">{escape(short_id)}</span>'
    identity = (
        f'<a href="{escape(trace_link_base)}{escape(run.trace_id)}">{label}</a>'
        if trace_link_base
        else label
    )
    cost = _fmt_usd(run.estimated_cost_usd) if run.estimated_cost_usd is not None else "—"
    started = run.started_at.isoformat(timespec="seconds")

    return (
        '<div class="tl-row">'
        f'<div class="tl-id"><div><div class="tl-name">{identity}</div>'
        f'<div class="tl-agent">{escape(run.status.value)} · {started}</div></div></div>'
        f'<div class="tl-figs">{len(run.spans)} span(s) · {run.total_tokens:,} tok · {cost}'
        f' · <span class="mono">{_fmt_ms(run.total_latency_ms)}</span></div>'
        "</div>"
    )


def _render_history_rows(runs: list[Run], trace_link_base: str | None) -> str:
    rows = "".join(_history_row(run, trace_link_base) for run in runs)
    return (
        '<div class="panel">'
        '<div class="panel-head"><h2 class="panel-title">Recent traces</h2>'
        f'<span class="panel-note">{len(runs)} trace(s)</span></div>'
        f'<div role="table" aria-label="Recent traces">{rows}</div>'
        "</div>"
    )


def save_dashboard_html(
    path: Path,
    *,
    workflow: Workflow | None = None,
    recommendations: list[Recommendation] | None = None,
    run: Run | None = None,
    evaluation: EvaluationReport | None = None,
    gate: GateDecision | None = None,
    comparison: ComparisonReport | None = None,
    title: str | None = None,
) -> None:
    """Render the dashboard and write it to ``path``, creating parent dirs as needed."""
    html_text = render_dashboard_html(
        workflow=workflow,
        recommendations=recommendations,
        run=run,
        evaluation=evaluation,
        gate=gate,
        comparison=comparison,
        title=title,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html_text, encoding="utf-8")
