# AgenticLens

What did the agent do, and where did time, tokens, or cost go?

## What it does

Run artifacts, analysis, comparisons, and evidence-backed recommendations, grouped by area below. Each area links to its detailed guide; for runnable commands, see the [developer guide](developer-guide.md).

### 1. Tracing and instrumentation

- **Structured traces**
    - `trace()` context manager and `recording.span()` API with parent/child spans
    - Span types: model call, planning, retrieval, memory read/write, tool call,
      validation, retry, delegation, final response, custom
    - Per-span details: agent, model, provider, start/end time, latency, status,
      errors, tokens, cost and attributes
- **Workflow profiling**
    - `profile()` and `step()` for step-level workflow capture
    - Retrieval, memory, retry and handoff metadata on steps
- **Privacy**
    - Input/output capture is opt-in (`record_io()`)
    - Default redaction of common secrets, bearer tokens and emails; custom `redactor=`
- **Providers and frameworks**
    - Automatic usage extraction from OpenAI and Anthropic responses
    - Other providers supply token counts explicitly
    - LangGraph and framework-neutral multi-agent workflows (`[langgraph]` / `[multi-agent]` extras)
- **OpenTelemetry (OTLP)**
    - Export traces to a collector (`otlp_endpoint=` or OTLP environment variables)
    - Import OTLP files (`import-otlp`)
    - Local OTLP receiver (`serve-otlp`)

Guides: [Trace and comparison](trace-and-comparison.md) ·
[Integrations](integrations.md) · [AIOS validation and OTel](aios-validation-and-otel.md)

### 2. Metrics

- **Token usage**
    - Input (prompt) and output (completion) tokens for each LLM call or span
    - Total tokens per span and per run
    - Tokens by span type, such as model calls versus retrieval versus planning
    - Captured automatically from OpenAI and Anthropic responses, recorded by hand
      with `record_tokens()`, or imported from OTLP traces
- **Cost**
    - Token count × model price, from the built-in pricing table or live pricing
    - Pricing overrides in configuration (USD per 1,000 tokens)
    - Cost per step and per run
    - Cost per success (in ModelFit and comparisons) and judge cost (in evaluation)
    - Unknown prices stay unknown; they are never counted as zero
- **Latency and performance**
    - Latency per span, per step and by span type
    - Tokens per second and measured time to first token
    - Mean, median and P95 latency across repeated runs
- **Reliability counts**
    - Retry count and tool-call count
    - Tokens, latency and cost attributed to retries (shown in diagnosis)

Guides: [Metrics and trace analysis API](api-reference.md#metrics-and-trace-analysis-api) ·
[Features](features.md) · [Configuration](configuration.md)

### 3. Profiling and analysis

- **Reports**
    - `report` and `analyze` for profiled workflows (with optional HTML)
    - `inspect` for structured runs: span tree, token and latency distributions,
      retry and tool-call counts, deterministic findings
- **Trace views**
    - `trace show` for a run or a single span
    - `trace timeline` for incident timelines
- **Guidance**
    - Next-best-analysis suggestions when findings point to an obvious follow-up
    - Every finding cites the spans and measurements behind it

Guides: [Trace and comparison](trace-and-comparison.md) ·
[Metrics and trace analysis API](api-reference.md#metrics-and-trace-analysis-api)

### 4. Recommendations (finding waste)

- **Prompt and context**
    - Repeated system prompts
    - Long conversation history
- **Retrieval**
    - Excessive retrieved chunks
    - Low-utility RAG chunks (citations, reranker or similarity scores, lexical fallback)
- **Tools and agents**
    - Duplicate tool calls
    - Handoff bloat between agents
- **Models and faults**
    - Model swap suggestions
    - Impact of injected faults from Chaos evidence
- **Provenance**
    - Every recommendation names the step it is about and carries evidence

Guides: [Features](features.md) · [RAG chunk utility](rag-chunk-utility.md)

### 5. Evaluation

- **Scoring**
    - Evaluate recorded outputs against YAML/JSON suites (`evaluate`)
    - Live targets: trusted Python callables and HTTP endpoints (`evaluate-live`)
    - Trace-aware checks: tool trajectories, agent goals, handoffs, loops,
      groundedness, relevance, completeness, citations, safety
- **Judges**
    - Structured judge verdicts with confidence, unsupported claims and missed evidence
    - Judge latency, usage and cost recorded; self-judging skipped by default
    - Deterministic scores kept separate from model-based scores, with evaluator disagreement
- **Calibration**
    - Compare evaluators against human labels (`calibrate`)
    - Threshold tuning
- **Release gates**
    - Quality, latency and cost thresholds (`gate`)
    - Evidence audits of evaluator versions, trace evidence and cost coverage
    - Optional webhook alerts (generic, Slack, Teams)
- **Reports**
    - JSON and HTML evaluation reports

Guides: [Evaluation and release gates](evaluation-and-release-gates.md) ·
[Evals judge reliability](evals-0.9-judge-reliability.md)

### 6. Experiments and comparison

- **Run comparison**
    - Baseline versus candidate runs (`compare`)
    - Success, latency, variability, tokens, cost per success and regressions
- **Experiments**
    - Repeated trials across model, prompt, retrieval, memory and retry variants (`experiment run`)
    - Re-render saved results without rerunning (`experiment report`)
- **Statistics**
    - pass@k and pass^k
    - Confidence intervals and significance tests
    - Consistency and factor summaries
- **Output**
    - Variant × test-case heatmaps, HTML, CSV and Markdown reports

Guides: [Trace and comparison](trace-and-comparison.md) · [Experiments](experiments.md)

### 7. Diagnosis (root cause)

- **Failure analysis**
    - Versioned failure taxonomy and deterministic diagnosis rules (`diagnose`)
    - Origin versus propagated failures, and recovery
    - Explicit rules for budgets, tool and handoff loops, empty retrieval and injected faults
- **Attribution**
    - Faulty step and faulty agent
    - Accuracy measured on controlled failures (`attribution-accuracy`)
- **Investigation**
    - Incident timelines
    - Anomaly detection against healthy baseline runs
    - Investigation narratives (`explain`)
- **Guardrails**
    - Analysis budgets on spans, depth and time; incomplete analysis is reported

Guides: [Diagnosis and failure attribution](diagnosis.md)

### 8. Test suites and datasets

- **Building suites**
    - Import from CSV or JSON (`suite import`)
    - Convert production traces and user feedback into cases
- **Curating**
    - Edit cases, tags and domains
    - Stable train/test splits and synthetic variations
    - Duplicate detection and PII masking
- **Review and release**
    - Review and approval metadata
    - Immutable, hash-verified suite versions that CI can verify and export
- **Datasets**
    - Summarize, split and export saved samples (`dataset`)

Guides: [Test-suite and dataset management](suite-management.md)

### 9. ModelFit (choosing a model)

- **Inputs**
    - Task taxonomy built from experiment evidence
    - Hard constraints on quality, cost, latency, safety, provider and deployment
- **Ranking**
    - Weighted scoring and per-category Pareto frontiers
    - Cost per success
- **Output**
    - Confidence and explanations
    - Alternatives and provider-diverse fallbacks
    - Projected savings with separate quality risks
    - Task-by-model matrix (`modelfit matrix`)

Guides: [ModelFit recommendations](modelfit.md)

### 10. Runtime routing

- **Decisions**
    - Select eligible models from a ModelFit report (`routing decide`)
    - Modes: advisory, enforce, shadow and canary
- **Execution (Python SDK)**
    - Host-owned callbacks with bounded failover
    - Local audit journals and outcome summaries (`routing summary`)

Guides: [Advisory runtime routing](routing.md)

### 11. Optimization

- **Opportunities**
    - Prompt caching and compression
    - Retrieval pruning and reranking
    - Memory summarization
    - Tools, retries, redundant steps and handoffs
    - Model quality/cost trade-offs
- **Trade-offs**
    - Evidence, projected benefit, confidence and quality risk kept separate
- **Adoption**
    - Record decisions against a report hash (`optimize decide`, `optimize status`)
    - Compare before/after traces with the original projection (`optimize outcome`)

Guides: [Optimization intelligence](optimization.md)

### 12. Integrity and validation

- **Execution evidence**
    - Export evidence bundles sealed with an operator-held key (`evidence export`)
    - Verify records and manifests (`evidence verify`)
    - Replay verified execution records offline (`evidence replay`)
- **AIOS contracts**
    - Schema validation of draft artifacts (`validate`)
    - Rule-cited conformance summaries (`conformance`)
    - Operational companion artifacts and provenance resolution

Guides: [Execution evidence verification](evidence-verification.md) ·
[AIOS validation and OTel](aios-validation-and-otel.md)

### 13. Exports, reports and history

- **Exports**
    - JSON, CSV, Markdown and Jira payloads
    - OTLP trace export
- **Reports**
    - HTML dashboard (`dashboard`)
    - Markdown trace reports (`inspect --save`)
- **History**
    - Persistent local trace history (`history`)

Guides: [Export formats](export-formats.md) · [Features](features.md)

### 14. Enterprise artifact service

- **Isolation and access**
    - Organization and project isolation
    - Hashed bearer credentials with reader, writer and admin roles
- **Storage**
    - SQLite storage with redaction and retention policies
    - Retention pruning
- **Governance**
    - Immutable model and prompt registry metadata
    - Policy-bound release gate receipts
    - Audit log and compliance metadata
- **HTTP API**
    - Trace ingest and query, registry, gate, retention, audit and compliance routes

Guides: [Production readiness](production-readiness.md)

### 15. Ecosystem interoperability

- **Sidecar**: attach supervision decisions to matching runs and spans
- **Chaos**: analyze injected-fault evidence (Lens does not inject faults)
- **Control Tower**: consumes attributed Lens evidence
- **MCP**: the separate MCP package exposes Lens workflows as tools

Guides: [Sidecar integration](sidecar-integration.md) ·
[Lens 0.13 ecosystem matrix](lens-0.13-compatibility.md)

## What you need

Instrumented workflows, structured traces, or supported imported trace data.

## Start here

Record a small local trace and inspect `run.json`: [follow the quickstart](developer-guide.md#quickstart).

## Limits

- Recommendations are heuristic and advisory; savings are projections.
- Instrument real execution boundaries; arbitrary frameworks are not intercepted automatically.
- Streaming token capture is not provided.
- Dataset and experiment workflows don't make every third-party trace schema compatible automatically.

See [Limitations](limitations.md).

## Documentation

- [Developer Guide (simple)](developer-guide.md): short task workflows and a capability index
- [API Reference (detailed)](api-reference.md): exact Python functions, parameters and return values
- [AI Readable Documentation](ai-reference-index.md): the full reference as one file for AI tools, with source declarations and schemas
