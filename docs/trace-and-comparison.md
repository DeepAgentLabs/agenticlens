# Trace and Comparison

AgenticLens provides an experimental, framework-neutral trace format for research and
repeated-run evaluation. This API is additive; the existing `profile()` and `step()` API
continues to work.

## Capture a trace

```python
from agenticlens import SpanType, trace

with trace("support-agent", environment="test") as recording:
    with recording.span("planner", SpanType.PLANNING) as planner:
        planner.record_tokens(input_tokens=120, output_tokens=30)

    with recording.span("memory", SpanType.MEMORY_READ) as memory:
        memory.record_tokens(input_tokens=80)

recording.save("run.json")
```

Input and output values are not captured by default. Explicit values recorded with
`record_io()` pass through the default secret, bearer-token, and email redactor. Supply a
custom `redactor=` function to meet application-specific privacy requirements.

## Inspect a run

```bash
agenticlens inspect run.json
```

The report includes a span tree, raw token and latency distributions, retry and tool-call
counts, deterministic findings, and next-best-analysis guidance when findings suggest
an obvious follow-up. Findings cite the exact spans and measurements that triggered
them.

Save a Markdown trace report:

```bash
agenticlens inspect run.json --save trace-report.md
```

## Compare repeated runs

Place baseline and candidate JSON traces in separate directories:

```bash
agenticlens compare results/baseline results/candidate \
  --regression-threshold 0.05 \
  --save comparison.json
```

Use `--format csv` for tabular export and `--fail-on-regression` in CI. Comparisons report
success rate, mean/median/P95 values, standard deviation, coefficient of variation,
cost per successful task, and relative regressions.

Use `--format md` for a review-friendly Markdown summary and `--min-samples` when a
comparison should fail under CI if either cohort is too small:

```bash
agenticlens compare results/baseline results/candidate \
  --format md \
  --save comparison.md \
  --min-samples 5
```

The comparison is descriptive. It does not claim statistical significance or causal
attribution, particularly for small or uncontrolled samples.

## Schemas

Versioned JSON schemas are maintained in the repository `schemas/` directory and bundled
under `agenticlens/schemas` in wheel distributions:

- `trace.schema.json`
- `finding.schema.json`
- `report.schema.json`
