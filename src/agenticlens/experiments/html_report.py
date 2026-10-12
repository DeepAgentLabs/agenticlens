"""Standalone HTML report for an experiment: one page, no network requests.

Shows quality, cost, latency, and reliability side by side for every variant,
pass@k / pass^k, baseline deltas with significance and changed factors, a
variant x test-case score heatmap, factor-level averages, warnings, and the
recorded randomization settings.
"""

from html import escape
from pathlib import Path

from agenticlens.experiments.models import (
    ExperimentComparison,
    ExperimentReport,
    ExperimentVariantResult,
)


def _pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.1%}"


def _num(value: float | None, digits: int = 3) -> str:
    return "n/a" if value is None else f"{value:.{digits}f}"


def _usd(value: float | None) -> str:
    return "n/a" if value is None else f"${value:.4f}"


def _interval(variant: ExperimentVariantResult) -> str:
    interval = variant.summary.case_pass_rate_interval
    if interval is None:
        return ""
    return f"<small>{interval.lower:.1%}–{interval.upper:.1%}</small>"


def _variant_rows(report: ExperimentReport) -> str:
    rows = []
    for variant in report.variants:
        summary = variant.summary
        factors = ", ".join(f"{escape(k)}={escape(v)}" for k, v in variant.factors.items())
        badges = "".join(
            [
                '<span class="tag base">baseline</span>'
                if variant.variant_id == report.baseline_variant_id
                else "",
                '<span class="tag pareto">pareto</span>' if variant.pareto_optimal else "",
            ]
        )
        rows.append(
            f"""<tr>
  <td><strong>{escape(variant.variant_name)}</strong> {badges}<br><small>{escape(variant.variant_id)}{" · " + factors if factors else ""}</small></td>
  <td>{_pct(summary.case_pass_rate)} {_interval(variant)}</td>
  <td>{_num(summary.average_score.mean if summary.average_score else None)}</td>
  <td>{_num(summary.average_latency_ms.mean if summary.average_latency_ms else None, 1)} ms</td>
  <td>{_usd(summary.total_cost_usd.mean if summary.total_cost_usd else None)}<br><small>{summary.priced_trials}/{summary.completed_trials} trials priced</small></td>
  <td>{_pct(summary.trial_success_rate)}<br><small>{summary.completed_trials}/{summary.attempted_trials} completed</small></td>
  <td>{_pct(summary.consistency_rate)}<br><small>{len(summary.flaky_case_ids)} flaky</small></td>
</tr>"""
        )
    return "".join(rows)


def _pass_k_rows(report: ExperimentReport) -> str:
    rows = []
    for variant in report.variants:
        cells = "".join(
            f"<td>{_pct(variant.summary.pass_at_k.get(str(k)))}</td>"
            f"<td>{_pct(variant.summary.pass_hat_k.get(str(k)))}</td>"
            for k in report.pass_k
        )
        rows.append(f"<tr><td>{escape(variant.variant_name)}</td>{cells}</tr>")
    return "".join(rows)


def _delta_cell(comparison: ExperimentComparison) -> str:
    delta = comparison.case_pass_rate_delta
    p_value = comparison.case_pass_rate_p_value
    significance = (
        "n/a"
        if comparison.statistically_significant is None
        else "significant"
        if comparison.statistically_significant
        else "not significant"
    )
    p_text = "" if p_value is None else f" (p={p_value:.3f})"
    return f"{'n/a' if delta is None else f'{delta:+.1%}'}<br><small>{significance}{p_text}</small>"


def _comparison_rows(report: ExperimentReport) -> str:
    rows = []
    for comparison in report.comparisons:
        changed = ", ".join(
            f"{escape(name)}: {escape(str(values[0]))} → {escape(str(values[1]))}"
            for name, values in comparison.changed_factors.items()
        )
        cost = comparison.total_cost_usd_delta
        regressions = [
            name
            for name, delta in (
                ("pass rate", comparison.pass_rate_delta),
                ("score", comparison.average_score_delta),
                ("latency", comparison.average_latency_ms_delta),
                ("cost", cost),
            )
            if delta is not None and delta.regressed
        ]
        warnings = "".join(f"<li>{escape(w)}</li>" for w in comparison.warnings)
        rows.append(
            f"""<tr>
  <td><strong>{escape(comparison.candidate_variant_id)}</strong><br><small>{changed or "no factor changes recorded"}</small></td>
  <td>{_delta_cell(comparison)}</td>
  <td>{comparison.average_score_delta.absolute:+.3f}</td>
  <td>{comparison.average_latency_ms_delta.absolute:+.1f} ms</td>
  <td>{"n/a" if cost is None else f"{cost.absolute:+.4f}"}</td>
  <td class="{"bad" if regressions else "good"}">{escape(", ".join(regressions)) or "none"}<br><small>{len(comparison.regressed_case_ids)} case(s) regressed · {len(comparison.improved_case_ids)} improved</small>{f"<ul>{warnings}</ul>" if warnings else ""}</td>
</tr>"""
        )
    return "".join(rows)


def _heat_color(value: float | None) -> str:
    if value is None:
        return "var(--line)"
    # Red (0) -> amber (0.5) -> green (1) in HSL.
    return f"hsl({round(value * 130)} 62% 38%)"


def _heatmap(report: ExperimentReport) -> str:
    case_names: dict[str, str] = {}
    for variant in report.variants:
        for case in variant.cases:
            case_names.setdefault(case.case_id, case.case_name)
    case_ids = report.case_ids or list(case_names)
    header = "".join(
        f'<th title="{escape(case_names.get(case_id, case_id))}">{escape(case_id)}</th>'
        for case_id in case_ids
    )
    rows = []
    for variant in report.variants:
        by_id = {case.case_id: case for case in variant.cases}
        cells = []
        for case_id in case_ids:
            cell = by_id.get(case_id)
            score = cell.mean_score if cell else None
            label = "n/a" if cell is None else f"{cell.passes}/{cell.attempts}"
            flaky = "" if cell is None or cell.consistent else " flaky"
            title = (
                "no data"
                if cell is None
                else f"pass rate {cell.pass_rate:.0%}, mean score {_num(score)}"
            )
            cells.append(
                f'<td class="heat{flaky}" style="background:{_heat_color(score)}" '
                f'title="{escape(title)}">{label}<small>{_num(score, 2)}</small></td>'
            )
        rows.append(f"<tr><th>{escape(variant.variant_name)}</th>{''.join(cells)}</tr>")
    return f'<table class="heatmap"><tr><th></th>{header}</tr>{"".join(rows)}</table>'


def _factor_rows(report: ExperimentReport) -> str:
    return "".join(
        f"<tr><td>{escape(level.factor)}</td><td>{escape(level.value)}</td>"
        f"<td>{escape(', '.join(level.variant_ids))}</td>"
        f"<td>{_pct(level.mean_pass_rate)}</td><td>{_num(level.mean_average_score)}</td>"
        f"<td>{_num(level.mean_latency_ms, 1)} ms</td><td>{_usd(level.mean_cost_usd)}</td>"
        f"<td>{_pct(level.mean_trial_success_rate)}</td></tr>"
        for level in report.factor_levels
    )


def render_experiment_html(report: ExperimentReport) -> str:
    k_header = "".join(f"<th>pass@{k}</th><th>pass^{k}</th>" for k in report.pass_k)
    warnings = "".join(f"<li>{escape(warning)}</li>" for warning in report.warnings)
    randomization = report.randomization
    order = (
        ", ".join(f"{escape(v)}#{t}" for v, t in randomization.execution_order)
        if randomization
        else "not recorded"
    )
    factors_section = (
        f"""<h2>Factor levels</h2>
  <p class="muted">Variants sharing a factor value, averaged. Only factors with at least two values are shown.</p>
  <div class="scroll"><table><tr><th>Factor</th><th>Value</th><th>Variants</th><th>Pass rate</th><th>Score</th><th>Latency</th><th>Cost</th><th>Reliability</th></tr>{_factor_rows(report)}</table></div>"""
        if report.factor_levels
        else ""
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Experiment Report — {escape(report.experiment_name)}</title>
  <style>
    :root {{ --bg:#f7f8fb; --panel:#fff; --text:#16202e; --muted:#5d6b7e; --line:#dfe4ec;
      --good:#18794e; --bad:#c2253c; --accent:#2557d6; }}
    @media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg:#0b1220;
      --panel:#121c2e; --text:#e6edf7; --muted:#9aa9bf; --line:#26354d; --good:#45d39a;
      --bad:#ff7286; --accent:#79a6ff; }} }}
    :root[data-theme="dark"] {{ --bg:#0b1220; --panel:#121c2e; --text:#e6edf7; --muted:#9aa9bf;
      --line:#26354d; --good:#45d39a; --bad:#ff7286; --accent:#79a6ff; }}
    * {{ box-sizing:border-box }}
    body {{ margin:0; background:var(--bg); color:var(--text);
      font:14px/1.5 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif; }}
    main {{ max-width:1180px; margin:auto; padding:32px 16px 64px; }}
    h1 {{ margin:4px 0 }} h2 {{ margin-top:36px }}
    .eyebrow,.muted,small {{ color:var(--muted) }} small {{ display:block; font-size:12px }}
    .scroll {{ overflow-x:auto }}
    table {{ width:100%; border-collapse:collapse; background:var(--panel); border:1px solid var(--line);
      border-radius:10px; overflow:hidden }}
    th,td {{ text-align:left; padding:9px 11px; border-bottom:1px solid var(--line); vertical-align:top }}
    th {{ font-size:12px; text-transform:uppercase; letter-spacing:.04em; color:var(--muted) }}
    .tag {{ font-size:11px; padding:1px 7px; border-radius:99px; border:1px solid var(--line) }}
    .tag.base {{ color:var(--accent) }} .tag.pareto {{ color:var(--good) }}
    .good {{ color:var(--good) }} .bad {{ color:var(--bad) }}
    .heatmap td.heat {{ color:#fff; text-align:center; font-weight:700; min-width:64px }}
    .heatmap td.heat small {{ color:#fffc }} .heatmap td.flaky {{ outline:2px dashed #fff8; outline-offset:-4px }}
    ul {{ margin:6px 0 0; padding-left:18px }}
    .meta {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:10px; margin-top:16px }}
    .meta div {{ background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:10px 12px }}
  </style>
</head>
<body><main>
  <div class="eyebrow">AGENTICLENS · EXPERIMENT REPORT</div>
  <h1>{escape(report.experiment_name)}</h1>
  <div class="muted">Experiment {escape(report.experiment_version)} · suite {escape(report.suite_name)} {escape(report.suite_version)}</div>
  <section class="meta">
    <div><small>Trials per variant</small><strong>{report.trial_count}</strong></div>
    <div><small>Baseline</small><strong>{escape(report.baseline_variant_id)}</strong></div>
    <div><small>Confidence level</small><strong>{report.confidence_level:.0%}</strong></div>
    <div><small>Regression threshold</small><strong>{report.regression_threshold:.0%}</strong></div>
    <div><small>Random seed</small><strong>{"none (fixed order)" if report.random_seed is None else report.random_seed}</strong></div>
    <div><small>Minimum trials</small><strong>{report.minimum_trials}</strong></div>
  </section>
  {f'<h2>Warnings</h2><ul class="bad">{warnings}</ul>' if warnings else ""}
  <h2>Quality, cost, latency, and reliability</h2>
  <div class="scroll"><table><tr><th>Variant</th><th>Case pass rate</th><th>Mean score</th><th>Mean latency</th><th>Mean cost / trial</th><th>Reliability</th><th>Consistency</th></tr>{_variant_rows(report)}</table></div>
  <h2>pass@k and pass^k</h2>
  <p class="muted">pass@k: chance at least one of k attempts passes. pass^k: chance all k attempts pass. Averaged over cases.</p>
  <div class="scroll"><table><tr><th>Variant</th>{k_header}</tr>{_pass_k_rows(report)}</table></div>
  <h2>Against the baseline</h2>
  <div class="scroll"><table><tr><th>Candidate</th><th>Case pass rate Δ</th><th>Score Δ</th><th>Latency Δ</th><th>Cost Δ</th><th>Regressions</th></tr>{_comparison_rows(report)}</table></div>
  <h2>Test-level heatmap</h2>
  <p class="muted">Each cell: passes/attempts and mean score; colour follows mean score. Dashed cells are flaky (mixed outcomes).</p>
  <div class="scroll">{_heatmap(report)}</div>
  {factors_section}
  <h2>Randomization</h2>
  <p class="muted">Execution order: {order}</p>
  <p class="muted">Generated by AgenticLens · {report.created_at.isoformat()}</p>
</main></body></html>"""


def save_experiment_html(report: ExperimentReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_experiment_html(report), encoding="utf-8")
