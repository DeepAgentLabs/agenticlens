"""Investigation-style narratives.

`explain_run()` turns a `DiagnosisReport` into a Markdown write-up: what
happened, the most likely root cause and how sure we are, what else
contributed, what the failure cost, and what to check next.
`explain_recommendations()` does the same for workflow recommendations,
explaining *why* the waste occurred, not only how much could be saved.

Narratives are deterministic templates over recorded evidence. They never
call a model, and every claim they make cites a span or step.
"""

from collections.abc import Sequence

from agenticlens.diagnosis.models import DiagnosisReport
from agenticlens.diagnosis.taxonomy import FailureCategory, describe
from agenticlens.models.recommendation import Recommendation
from agenticlens.models.workflow import Workflow

_ROOT_CAUSES = {
    "prompt_caching": (
        "The same system prompt or prefix is re-sent on every call, so each step pays "
        "for tokens the provider could have cached."
    ),
    "rag_top_k_reduction": (
        "Retrieval returns more chunks than the answer uses, so every downstream model "
        "call carries context it ignores."
    ),
    "rag_chunk_pruning": (
        "Retrieved chunks were included in the prompt but contributed little to the "
        "answer (low measured utility)."
    ),
    "memory_summarization": (
        "Conversation history grows with every turn and is replayed in full instead "
        "of being summarized or truncated."
    ),
    "tool_result_caching": (
        "The same tool was called with the same arguments more than once, repeating "
        "work whose result was already available."
    ),
    "agent_handoff_summarization": (
        "One agent hands its full context to the next, so the receiving agent pays for "
        "history it does not need."
    ),
    "model_swap": ("A step runs on a more expensive model tier than its measured workload needs."),
    "resilience": (
        "An injected fault reached this step and the workflow did not fully absorb it, "
        "so retries or failures added cost."
    ),
}


def _pct(value: float) -> str:
    return f"{value:.0%}"


def explain_run(report: DiagnosisReport) -> str:
    """A Markdown investigation narrative for one diagnosed run."""
    attribution = report.attribution
    lines = [f"# Investigation: {report.application_name}", ""]
    outcome = report.run_status + (
        "" if report.task_success is None else f", task_success={report.task_success}"
    )
    lines += [
        f"- Run `{report.run_id}` (trace `{report.trace_id}`), outcome: {outcome}",
        f"- {report.summary.total_diagnoses} diagnosis(es), "
        f"{report.summary.unrecovered} unrecovered, {report.summary.failed_spans} failed span(s)",
        f"- Taxonomy v{report.taxonomy_version}, engine v{report.engine_version}",
        "",
        "## Verdict",
        "",
    ]
    if attribution.status == "no_failure":
        lines.append("No failures were diagnosed in this run.")
    elif attribution.status == "unattributed":
        lines.append(attribution.explanation)
    else:
        lines.append(
            f"{attribution.explanation} Attribution confidence: {_pct(attribution.confidence)}."
        )

    attributed = attribution.status in ("attributed", "recovered") and any(
        d.origin_span_id == attribution.faulty_span_id for d in report.diagnoses
    )
    if report.diagnoses and not attributed:
        lines += ["", "## Diagnoses", ""]
        for diagnosis in report.diagnoses:
            lines.append(
                f"- **{diagnosis.category.value}**: {diagnosis.summary} "
                f"[confidence {_pct(diagnosis.confidence)}]"
            )
    if report.diagnoses and attributed:
        lead = next(d for d in report.diagnoses if d.origin_span_id == attribution.faulty_span_id)
        info = describe(lead.category)
        lines += [
            "",
            "## Root cause",
            "",
            f"**{lead.title}** ({lead.category.value}, {info.layer} layer, "
            f"severity {lead.severity}, rule `{lead.rule_id}@{lead.rule_version}`)",
            "",
            lead.summary,
        ]
        if lead.span_ids:
            lines += ["", "Supporting spans: " + ", ".join(f"`{s}`" for s in lead.span_ids)]
        others = [d for d in report.diagnoses if d is not lead]
        if others:
            lines += ["", "## Contributing factors", ""]
            for diagnosis in others:
                state = " (recovered)" if diagnosis.recovered else ""
                lines.append(
                    f"- **{diagnosis.category.value}**{state}: {diagnosis.summary} "
                    f"[confidence {_pct(diagnosis.confidence)}]"
                )

    key_events = [
        e
        for e in report.timeline.events
        if e.kind not in ("span_started", "span_completed") or e.is_root_cause
    ]
    if len(key_events) > 2:
        lines += ["", "## What happened", ""]
        for event in key_events[:25]:
            marker = " **(root cause)**" if event.is_root_cause else ""
            lines.append(f"- +{event.offset_ms:.0f} ms — {event.description}{marker}")
        if len(key_events) > 25:
            lines.append(f"- … {len(key_events) - 25} more event(s) in the saved report")

    summary = report.summary
    if summary.failed_spans or summary.wasted_tokens:
        cost = (
            "unknown (some failed or retry spans have no cost)"
            if summary.wasted_cost_usd is None
            else f"${summary.wasted_cost_usd:.6f}"
        )
        lines += [
            "",
            "## Cost of the failure",
            "",
            f"Failed and retry spans used {summary.wasted_tokens} tokens, "
            f"{summary.wasted_latency_ms:.0f} ms, and {cost}.",
        ]

    if report.efficiency_findings:
        lines += ["", "## Efficiency findings", ""]
        for finding in report.efficiency_findings:
            lines.append(f"- **{finding.title}**: {finding.description}")

    if report.anomalies is not None:
        lines += ["", "## Anomalies against baseline", ""]
        if report.anomalies.anomalies:
            for anomaly in report.anomalies.anomalies:
                z = (
                    "n/a (baseline constant)"
                    if anomaly.robust_z is None
                    else (f"{anomaly.robust_z:+.1f}")
                )
                lines.append(
                    f"- `{anomaly.key}` {anomaly.metric}: {anomaly.observed:g} vs median "
                    f"{anomaly.baseline_median:g} (robust z {z}, n={anomaly.baseline_samples})"
                )
        else:
            lines.append(
                f"No anomalies at robust z > {report.anomalies.threshold:g} "
                f"across {report.anomalies.baseline_runs} baseline run(s)."
            )
        lines += [f"- Warning: {w}" for w in report.anomalies.warnings]

    steps = list(
        dict.fromkeys(describe(FailureCategory(d.category)).next_step for d in report.diagnoses)
    )
    if steps:
        lines += ["", "## Next steps", ""]
        lines += [f"{index}. {step}" for index, step in enumerate(steps, start=1)]

    lines += ["", "## Limitations", ""]
    lines += [f"- {item}" for item in report.limitations]
    if report.guardrails.truncated:
        lines += [f"- Analysis cut short: {reason}" for reason in report.guardrails.stop_reasons]
    return "\n".join(lines) + "\n"


def explain_recommendations(workflow: Workflow, recommendations: Sequence[Recommendation]) -> str:
    """A Markdown narrative explaining the root cause behind each recommendation."""
    lines = [f"# Investigation: {workflow.name}", ""]
    if not recommendations:
        lines.append("No optimization recommendations were produced for this workflow.")
        return "\n".join(lines) + "\n"
    total_tokens = workflow.total_tokens
    reducible = sum(r.tokens_saved for r in recommendations)
    share = f" ({reducible / total_tokens:.0%} of {total_tokens})" if total_tokens else ""
    lines += [
        f"{len(recommendations)} finding(s); about {reducible} reducible tokens{share}.",
        "",
    ]
    for index, rec in enumerate(recommendations, start=1):
        where = f"step '{rec.step_name}'" if rec.step_name else "the workflow"
        why = _ROOT_CAUSES.get(
            rec.optimization_type, "The recorded measurements exceed this rule's threshold."
        )
        lines += [f"## {index}. {rec.title}", "", f"**Where:** {where}", "", f"**Why:** {why}"]
        lines += ["", f"**What was measured:** {rec.description}"]
        impact: list[str] = []
        if rec.tokens_saved:
            impact.append(f"{rec.tokens_saved} tokens")
        if rec.estimated_usd_savings is not None:
            impact.append(f"${rec.estimated_usd_savings:.6f} per run")
        if rec.cost_savings is not None:
            impact.append(f"${rec.cost_savings:.6f} per run (model swap)")
        if impact:
            lines += ["", "**Projected impact (estimate):** " + ", ".join(impact)]
        if rec.quality_risk:
            lines += ["", f"**Quality risk:** {rec.quality_risk}"]
        cited = [e for e in rec.evidence if e.span_id or e.details]
        if cited:
            lines += ["", "**Evidence:**"]
            for item in cited[:5]:
                ref = f"`{item.span_id}`" if item.span_id else item.source
                note = f" — {item.reasoning}" if item.reasoning else ""
                lines.append(f"- {ref}{note}")
        lines.append("")
    lines.append(
        "Projected savings are estimates from recorded token counts; measure them again "
        "after adopting a change."
    )
    return "\n".join(lines) + "\n"
