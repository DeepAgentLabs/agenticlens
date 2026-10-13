from html import escape
from pathlib import Path

from agentic_evals import CaseEvaluation, EvaluationReport, Score

from agenticlens.evaluation.score_analysis import KindSummary, ScoreAnalysis, analyze_scores


def _evaluator_label(score: Score) -> str:
    if not score.evaluator:
        return ""
    version = score.evaluator_version or "unversioned"
    return f' <span class="evaluator">{escape(score.evaluator)}@{escape(version)}</span>'


def _score_class(score: Score) -> str:
    return "skip" if score.skipped else "pass" if score.passed else "fail"


def _case_cost(case: CaseEvaluation) -> str:
    if case.cost_usd is None:
        return "Unavailable"
    source = f" ({escape(case.cost_source)})" if case.cost_source else ""
    return f"${case.cost_usd:.6f}{source}"


def _trace_label(case: CaseEvaluation) -> str:
    if not case.sample_available:
        return "no sample supplied"
    return f"trace {escape(case.trace_id or 'missing')}"


def _kind_row(label: str, kind: KindSummary) -> str:
    rate = "n/a" if kind.pass_rate is None else f"{kind.pass_rate:.1%}"
    average = "n/a" if kind.average_score is None else f"{kind.average_score:.3f}"
    return (
        f"<tr><td>{label}</td><td>{kind.passed}/{kind.total - kind.skipped}</td>"
        f"<td>{rate}</td><td>{average}</td><td>{kind.skipped}</td></tr>"
    )


def _analysis_section(analysis: ScoreAnalysis) -> str:
    """Deterministic vs model-based results, judge cost, and disagreement."""
    if analysis.model_based.total == 0 and not analysis.disagreements:
        return ""
    judge = analysis.judge_cost
    judge_cost = (
        "Unavailable"
        if judge.total_cost_usd is None
        else f"${judge.total_cost_usd:.6f}" + ("" if judge.complete else " (partial)")
    )
    disagreement_rate = (
        "n/a" if analysis.disagreement_rate is None else f"{analysis.disagreement_rate:.1%}"
    )
    items = "".join(
        f"<li><strong>{escape(d.case_id)}</strong>: passed by {escape(', '.join(d.passing))}; "
        f"failed by {escape(', '.join(d.failing))}</li>"
        for d in analysis.disagreements[:50]
    )
    return f"""
  <h2>Score analysis</h2>
  <article class="case">
    <table><tr><th>Scores</th><th>Passed</th><th>Pass rate</th><th>Average</th><th>Skipped</th></tr>
    {_kind_row("Deterministic", analysis.deterministic)}
    {_kind_row("Model-based", analysis.model_based)}</table>
    <p class="metrics">Judge cost: {judge_cost} · {judge.priced_scores}/{judge.judge_scores} judge scores priced · kept separate from agent cost</p>
    <p class="metrics">Evaluator disagreement: {analysis.disagreement_cases}/{analysis.comparable_cases} comparable cases ({disagreement_rate})</p>
    {f"<ul>{items}</ul>" if items else ""}
  </article>"""


def render_html_report(report: EvaluationReport) -> str:
    summary = report.summary
    cost = "Unavailable" if summary.total_cost_usd is None else f"${summary.total_cost_usd:.6f}"
    sources = ", ".join(f"{escape(k)} {v}" for k, v in summary.cost_sources.items())
    coverage = f"{summary.priced_cases}/{summary.total_cases} priced" + (
        f" · {sources}" if sources else ""
    )
    rows = []
    for case in report.cases:
        score_items = "".join(
            f'<li class="{_score_class(score)}">'
            f"<strong>{escape(score.name)}</strong>{_evaluator_label(score)}: "
            f"{escape(score.explanation)}</li>"
            for score in case.scores
        )
        rows.append(
            f"""
            <article class="case">
              <div class="case-heading">
                <div><span class="badge {"pass-bg" if case.passed else "fail-bg"}">
                  {"PASS" if case.passed else "FAIL"}
                </span><h3>{escape(case.case_name)}</h3></div>
                <div class="metrics">{case.latency_ms:.1f} ms · {_case_cost(case)}</div>
              </div>
              <p class="case-id">{escape(case.case_id)} · {_trace_label(case)}</p>
              <pre>{escape(case.output or "No output supplied.")}</pre>
              <ul>{score_items}</ul>
            </article>
            """
        )
    # Case outcome only: a release decision needs `evaluate_gate` thresholds.
    status = (
        "ALL CASES PASSED"
        if summary.failed_cases == 0
        else f"{summary.failed_cases} CASE{'S' if summary.failed_cases != 1 else ''} FAILED"
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>AgenticLens Evaluation — {escape(report.suite_name)}</title>
  <style>
    :root {{ color-scheme: dark; --bg:#07111f; --panel:#101d2e; --text:#eaf2ff;
      --muted:#91a4bd; --line:#24364e; --green:#3ddc97; --red:#ff6b7a; --blue:#62a8ff; }}
    * {{ box-sizing:border-box }} body {{ margin:0; background:linear-gradient(135deg,#07111f,#0c1730);
      color:var(--text); font:15px/1.5 Inter,ui-sans-serif,system-ui,sans-serif; }}
    main {{ max-width:1100px; margin:auto; padding:48px 24px 72px; }}
    header {{ display:flex; justify-content:space-between; gap:24px; align-items:end; }}
    h1 {{ font-size:36px; margin:6px 0 }} h3 {{ display:inline; margin-left:12px }}
    .eyebrow,.case-id,.metrics {{ color:var(--muted) }} .release {{ color:var(--blue); font-weight:800 }}
    .cards {{ display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin:30px 0; }}
    .card,.case {{ background:rgba(16,29,46,.92); border:1px solid var(--line);
      border-radius:14px; padding:20px; box-shadow:0 12px 36px #0004; }}
    .card span {{ color:var(--muted); display:block }} .card strong {{ font-size:27px }}
    .case {{ margin:14px 0 }} .case-heading {{ display:flex; justify-content:space-between; gap:12px }}
    .badge {{ border-radius:99px; padding:5px 9px; font-size:11px; font-weight:900 }}
    .pass-bg {{ background:#153f34; color:var(--green) }} .fail-bg {{ background:#4b202b; color:var(--red) }}
    .pass {{ color:var(--green) }} .fail {{ color:var(--red) }} .skip {{ color:var(--muted) }}
    .evaluator {{ color:var(--muted); font-size:12px }} .card small {{ color:var(--muted) }}
    pre {{ white-space:pre-wrap; background:#07111f; border-radius:9px; padding:13px; color:#cfe0f6 }}
    li {{ margin:7px 0 }} footer {{ color:var(--muted); margin-top:30px }}
    table {{ border-collapse:collapse; width:100% }} th,td {{ text-align:left; padding:6px 10px; border-bottom:1px solid var(--line) }}
    @media(max-width:760px) {{ .cards {{ grid-template-columns:1fr 1fr }} header {{ display:block }} }}
  </style>
</head>
<body><main>
  <header><div><div class="eyebrow">AGENTICLENS · EVALUATION REPORT</div>
    <h1>{escape(report.suite_name)}</h1><div>{escape(report.suite_version)}</div></div>
    <div class="release" title="Case outcomes only; run agenticlens gate for a release decision">CASE RESULT · {status}</div></header>
  <section class="cards">
    <div class="card"><span>Pass rate</span><strong>{summary.pass_rate:.1%}</strong></div>
    <div class="card"><span>Average score</span><strong>{summary.average_score:.3f}</strong></div>
    <div class="card"><span>Average latency</span><strong>{summary.average_latency_ms:.1f} ms</strong></div>
    <div class="card"><span>Total cost</span><strong>{cost}</strong><small>{coverage}</small></div>
  </section>
  {_analysis_section(analyze_scores(report))}
  <h2>Test cases</h2>{"".join(rows)}
  <footer>Generated by AgenticLens · {report.created_at.isoformat()}</footer>
</main></body></html>"""


def save_html_report(report: EvaluationReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_html_report(report), encoding="utf-8")
