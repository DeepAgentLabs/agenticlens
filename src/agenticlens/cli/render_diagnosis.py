"""Rich rendering for diagnosis, timeline, score-analysis, and accuracy output."""

from rich.console import Console
from rich.table import Table

from agenticlens.diagnosis import AttributionAccuracyReport, DiagnosisReport, IncidentTimeline
from agenticlens.evaluation import ScoreAnalysis

_SEVERITY_STYLE = {"low": "dim", "medium": "yellow", "high": "red", "critical": "bold red"}


def render_diagnosis(console: Console, report: DiagnosisReport) -> None:
    attribution = report.attribution
    outcome = report.run_status + (
        "" if report.task_success is None else f", task_success={report.task_success}"
    )
    console.print(
        f"[bold]Diagnosis · {report.application_name}[/bold] (run {report.run_id}, {outcome})"
    )
    if report.diagnoses:
        table = Table(title="Diagnoses")
        table.add_column("ID")
        table.add_column("Category")
        table.add_column("Severity")
        table.add_column("Conf.", justify="right")
        table.add_column("Summary")
        for diagnosis in report.diagnoses:
            style = _SEVERITY_STYLE.get(diagnosis.severity, "")
            recovered = " (recovered)" if diagnosis.recovered else ""
            table.add_row(
                diagnosis.diagnosis_id,
                diagnosis.category.value + recovered,
                f"[{style}]{diagnosis.severity}[/{style}]" if style else diagnosis.severity,
                f"{diagnosis.confidence:.2f}",
                diagnosis.summary,
            )
        console.print(table)
    else:
        console.print("[green]No failures diagnosed.[/green]")

    if attribution.status in ("attributed", "recovered"):
        console.print(
            f"Faulty step: [bold]{attribution.faulty_step}[/bold] "
            f"(agent {attribution.faulty_agent or 'n/a'}, "
            f"{attribution.category.value if attribution.category else 'n/a'}, "
            f"confidence {attribution.confidence:.0%}, status {attribution.status})"
        )
    console.print(attribution.explanation)
    summary = report.summary
    if summary.failed_spans or summary.wasted_tokens:
        cost = "unknown" if summary.wasted_cost_usd is None else f"${summary.wasted_cost_usd:.6f}"
        console.print(
            f"Failure cost: {summary.wasted_tokens} tokens, "
            f"{summary.wasted_latency_ms:.0f} ms, {cost} in failed and retry spans"
        )
    if report.anomalies is not None:
        console.print(
            f"Anomalies: {len(report.anomalies.anomalies)} "
            f"(baseline {report.anomalies.baseline_runs} runs, robust z > "
            f"{report.anomalies.threshold:g})"
        )
        for warning in report.anomalies.warnings:
            console.print(f"[yellow]{warning}[/yellow]")
    if report.guardrails.truncated:
        for reason in report.guardrails.stop_reasons:
            console.print(f"[yellow]Guardrail: {reason}[/yellow]")


def render_timeline(console: Console, timeline: IncidentTimeline) -> None:
    table = Table(title=f"Incident timeline · run {timeline.run_id}")
    table.add_column("Offset", justify="right")
    table.add_column("Event")
    table.add_column("Agent")
    table.add_column("Description")
    for event in timeline.events:
        marker = " [bold red]ROOT CAUSE[/bold red]" if event.is_root_cause else ""
        table.add_row(
            f"+{event.offset_ms:.0f} ms",
            event.kind,
            event.agent_name or "",
            event.description + marker,
        )
    console.print(table)
    if timeline.truncated:
        console.print("[yellow]Timeline truncated; routine span starts were dropped.[/yellow]")


def render_score_analysis(console: Console, analysis: ScoreAnalysis) -> None:
    def rate(value: float | None) -> str:
        return "n/a" if value is None else f"{value:.1%}"

    det, model = analysis.deterministic, analysis.model_based
    judge = analysis.judge_cost
    judge_cost = (
        "n/a"
        if judge.total_cost_usd is None
        else f"${judge.total_cost_usd:.6f}" + ("" if judge.complete else " (partial)")
    )
    scores = (
        f"Scores: deterministic {det.passed}/{det.total - det.skipped} passed "
        f"({rate(det.pass_rate)})"
    )
    if model.total:
        scores += (
            f" · model-based {model.passed}/{model.total - model.skipped} passed "
            f"({rate(model.pass_rate)})"
        )
    console.print(scores)
    if model.total:
        console.print(
            f"Judge cost: {judge_cost} ({judge.priced_scores}/{judge.judge_scores} judge scores "
            "priced; separate from agent cost)"
        )
    if analysis.comparable_cases:
        console.print(
            f"Evaluator disagreement: {analysis.disagreement_cases}/{analysis.comparable_cases} "
            f"comparable cases ({rate(analysis.disagreement_rate)})"
        )


def render_accuracy(console: Console, report: AttributionAccuracyReport) -> None:
    table = Table(title=f"Attribution accuracy · {report.total_cases} controlled failures")
    table.add_column("Metric")
    table.add_column("Correct", justify="right")
    table.add_column("Accuracy", justify="right")
    table.add_column(f"{report.confidence_level:.0%} interval", justify="right")
    for label, metric in (
        ("Faulty step (top 1)", report.step),
        ("Faulty step (top 3)", report.top3_step),
        ("Faulty agent", report.agent),
        ("Failure category", report.category),
    ):
        accuracy = "n/a" if metric.accuracy is None else f"{metric.accuracy:.1%}"
        interval = (
            "n/a"
            if metric.interval is None
            else f"{metric.interval[0]:.1%}-{metric.interval[1]:.1%}"
        )
        table.add_row(label, f"{metric.correct}/{metric.total}", accuracy, interval)
    console.print(table)
    console.print(
        f"Mean confidence {report.mean_confidence:.1%}; calibration gap "
        f"{report.calibration_gap:+.1%} (positive = overconfident)"
    )
    for outcome in report.outcomes:
        if not outcome.step_correct:
            console.print(
                f"[yellow]Missed {outcome.case_id}:[/yellow] expected {outcome.expected_span}, "
                f"predicted {outcome.predicted_span_name or 'nothing'}"
            )
    for warning in report.warnings:
        console.print(f"[yellow]{warning}[/yellow]")
