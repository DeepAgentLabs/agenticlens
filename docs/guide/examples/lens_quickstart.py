from agenticlens import SpanType, trace

# Synthetic token counts for a local instrumentation example.
with trace("support-demo", environment="development") as recording:
    with recording.span("plan", SpanType.PLANNING) as planner:
        planner.record_tokens(input_tokens=120, output_tokens=30)
    with recording.span("memory", SpanType.MEMORY_READ) as memory:
        memory.record_tokens(input_tokens=80)
recording.save("run.json")
print("Saved run.json; counts are illustrative, not provider measurements.")
