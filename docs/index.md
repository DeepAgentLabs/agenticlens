# AgenticLens

## AgenticLens overview

What did the agent do, and where did time, tokens, or cost go?

Instrumented workflows, structured traces, or supported imported trace data. Run artifacts, analysis, comparisons, and evidence-backed recommendations.

**When to start here**

Record a small local trace and inspect run.json.

## Inputs and outputs

| You provide | You receive |
| --- | --- |
| Instrumented workflows, structured traces, or supported imported trace data. | Run artifacts, analysis, comparisons, and evidence-backed recommendations. |

## Execution boundary

Recommendations are advisory. Its richer dataset and experiment workflows do not make every third-party trace schema automatically compatible.

[Start the AgenticLens quickstart →](guide/quickstart.md)

## Capabilities

Use these capabilities to address observe tasks in your application.

| Capability | What it provides |
| --- | --- |
| Workflow profiling | Capture planner, retrieval, tool, memory, and response steps with usage information. |
| Structured tracing | Represent runs and hierarchical spans, including status and errors. |
| Analysis and optimization | Inspect tokens, cost, latency, repeated work, and advisory improvement opportunities. |
| Comparison and experiments | Compare baseline and candidate observations rather than relying on a single anecdotal run. |
| Evaluation workflows | Manage datasets, experiments, calibration and evidence around scoring. |
| OTLP and history | Import/export supported trace data and optionally receive and retain traces locally. |

## Supported scope

Recommendations are advisory. Its richer dataset and experiment workflows do not make every third-party trace schema automatically compatible.

## Core concepts

| Concept | Meaning |
| --- | --- |
| Workflow vs run | A profiling workflow and a structured trace run are distinct artifact shapes. Use the matching analysis command. |
| Spans and hierarchy | Instrument real boundaries and preserve parent/child relationships for attribution. |
| Measured vs estimated | Usage supplied by a provider and costs calculated from pricing are different evidence sources. |
| Baseline vs candidate | Use comparable tasks, cohorts, settings and measurement windows. |
| Recommendations | Projected benefit, confidence, and quality risk are separate; adopted changes require new observations. |

## Recommended workflow

## Capture real work

Instrument execution with `trace()` and spans. Record usage from the response that actually occurred, then save the run. The quickstart's counts are synthetic; replace them before using its output for cost decisions.

## Inspect and compare

```
agenticlens inspect run.json
agenticlens compare baseline/ candidate/
```

Populate both directories with actual repeated runs of comparable tasks. Inspect changes in success, duration, token use, and variability. Keep task mix and measurement conditions aligned.

## Review improvements

Use optimization recommendations as proposals. Review projected benefit alongside confidence and quality risk, record which change you adopt, and collect new runs to measure the outcome.

## Use existing trace data

```
agenticlens import-otlp --help
```

Follow the supported OTLP contract and inspect the resulting spans. An arbitrary vendor export may require an adapter. Verify attributes before comparing costs or assigning failure ownership.

## Next steps

Record a small local trace and inspect run.json.

[Open the developer quickstart →](guide/quickstart.md)
