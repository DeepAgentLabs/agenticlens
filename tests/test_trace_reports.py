from datetime import datetime, timedelta, timezone

from rich.console import Console

from agenticlens.analysis import next_best_analyses
from agenticlens.models.trace import Finding, Run, RunStatus, Span, SpanType
from agenticlens.reports import render_trace, render_trace_markdown


def _run_with_findings() -> Run:
    started = datetime.now(timezone.utc)
    return Run(
        application_name="trace-demo",
        started_at=started,
        completed_at=started + timedelta(milliseconds=250),
        status=RunStatus.SUCCEEDED,
        task_success=True,
        spans=[
            Span(
                span_id="memory",
                name="memory lookup",
                span_type=SpanType.MEMORY_READ,
                status=RunStatus.SUCCEEDED,
                input_tokens=80,
            ),
            Span(
                span_id="retry",
                name="retry planner",
                span_type=SpanType.RETRY,
                status=RunStatus.SUCCEEDED,
                input_tokens=30,
            ),
            Span(
                span_id="retry-child",
                parent_span_id="retry",
                name="tool after retry",
                span_type=SpanType.TOOL_CALL,
                status=RunStatus.SUCCEEDED,
                tool_name="lookup",
                input_tokens=5,
                input_reference="context:shared",
            ),
            Span(
                span_id="dup-context",
                name="second lookup",
                span_type=SpanType.MODEL_CALL,
                status=RunStatus.SUCCEEDED,
                input_tokens=2,
                input_reference="context:shared",
            ),
        ],
    )


def test_render_trace_prints_findings_and_next_best_analysis() -> None:
    console = Console(record=True, width=120)
    render_trace(console, _run_with_findings())
    output = console.export_text()

    assert "Run Summary" in output
    assert "Findings" in output
    assert "High memory token share" in output
    assert "High retry overhead" in output
    assert "Next Best Analysis" in output


def test_render_trace_markdown_includes_findings_sections() -> None:
    markdown = render_trace_markdown(_run_with_findings())

    assert "# Trace Report: trace-demo" in markdown
    assert "## Findings" in markdown
    assert "### High memory token share" in markdown
    assert "### High retry overhead" in markdown


def test_render_trace_markdown_escapes_pipe_characters() -> None:
    run = _run_with_findings()
    run.spans[0].name = "memory | lookup"

    markdown = render_trace_markdown(run)

    assert "memory \\| lookup" in markdown


def test_next_best_analyses_returns_guidance_for_single_finding() -> None:
    suggestions = next_best_analyses(
        [
            Finding(
                category="memory",
                title="High memory token share",
                description="Memory spans consume a large share of recorded tokens.",
                severity="medium",
                confidence=1.0,
            )
        ]
    )

    assert suggestions
