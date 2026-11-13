# Quickstart

**Observe: What did the agent do, and where did time, tokens, or cost go?**

**Input:** Instrumented workflows, structured traces, or supported imported trace data.  
**Output:** Run artifacts, analysis, comparisons, and evidence-backed recommendations.

## Install

```
python -m pip install agenticlens
```

## Create a local trace

Save this file. Token counts are deliberately synthetic; replace them with actual provider usage in your application.

lens_quickstart.py · complete file

```python
from agenticlens import SpanType, trace

# Synthetic token counts for a local instrumentation example.
with trace("support-demo", environment="development") as recording:
    with recording.span("plan", SpanType.PLANNING) as planner:
        planner.record_tokens(input_tokens=120, output_tokens=30)
    with recording.span("memory", SpanType.MEMORY_READ) as memory:
        memory.record_tokens(input_tokens=80)
recording.save("run.json")
print("Saved run.json; counts are illustrative, not provider measurements.")
```

[Download lens_quickstart.py](examples/lens_quickstart.py)

## Run and inspect

```
python lens_quickstart.py
agenticlens inspect run.json
```

**Expected:** a saved run with planning and memory spans. This proves the instrumentation path, not measured production cost or quality.

## Connect your application

Wrap actual execution boundaries with spans, attach real usage, and preserve run identifiers. For existing OTLP data, follow the supported import contract rather than relabeling arbitrary JSON as a Lens run.

[Tracing and comparison ↗](../trace-and-comparison.md)[CLI reference ↗](../cli-reference.md)
