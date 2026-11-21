# AI Reference capability index

This index opens the generated [AI Reference (robust)](https://deepagentlabs.io/agenticlens/docs/llms-full.md). **Full reference** links identify the included topic sections in that file; **Source** links identify the maintained documentation. For a short task-oriented introduction, use the [Developer Guide (simple)](developer-guide.md#capability-index).

## Capability index

| Capability | Included scope | Detailed reference |
| --- | --- | --- |
| Workflow profiling | Profile steps, extract provider usage, and analyze cost and token consumption. | <a href="#api-reference">Full reference</a> · [Source](api-reference.md) |
| Structured tracing and privacy | Record hierarchical runs, spans, agents, errors, tokens and redacted I/O. | <a href="#tracing-and-comparison">Full reference</a> · [Source](trace-and-comparison.md) |
| Run comparison | Compare repeated baseline/candidate runs and detect descriptive regressions. | <a href="#tracing-and-comparison">Full reference</a> · [Source](trace-and-comparison.md) |
| Diagnosis and attribution | Find failure categories, faulty steps and agents, timelines, anomalies and investigation narratives. | <a href="#failure-diagnosis-and-attribution">Full reference</a> · [Source](diagnosis.md) |
| Analysis guardrails and attribution accuracy | Bound analysis work and measure attribution on controlled failures. | <a href="#failure-diagnosis-and-attribution">Full reference</a> · [Source](diagnosis.md) |
| Evaluation and live targets | Score recorded outputs or trusted Python/HTTP targets using Evals and Lens evaluators. | <a href="#evaluation-and-release-gates">Full reference</a> · [Source](evaluation-and-release-gates.md) |
| Advanced evaluation and judge reliability | Use structured verdicts, trace-aware checks, score disagreement, judge cost and threshold calibration. | <a href="#evaluation-and-release-gates">Full reference</a> · [Source](evaluation-and-release-gates.md) |
| Release gates and evidence audits | Check quality thresholds, evaluator provenance, cost coverage and optional gate alerts. | <a href="#evaluation-and-release-gates">Full reference</a> · [Source](evaluation-and-release-gates.md) |
| Datasets and suite management | Import, convert, edit, mask, deduplicate, vary, split, review, approve and verify cases. | <a href="#suite-management">Full reference</a> · [Source](suite-management.md) |
| Experiments and statistics | Run repeated model/prompt/retrieval/memory/retry variants with uncertainty and factor summaries. | <a href="#experiments-and-statistics">Full reference</a> · [Source](experiments.md) |
| ModelFit | Rank models per task with hard constraints, weighted scoring, Pareto analysis, fallbacks and model matrices. | <a href="#modelfit-recommendations">Full reference</a> · [Source](modelfit.md) |
| Runtime routing | Select eligible models; use SDK callbacks for failover, shadow or canary execution and outcome journals. | <a href="#advisory-runtime-routing">Full reference</a> · [Source](routing.md) |
| Optimization and adoption outcomes | Find prompt, retrieval, memory, tool, retry, handoff and model trade-offs; track decisions and realized savings. | <a href="#optimization-intelligence">Full reference</a> · [Source](optimization.md) |
| RAG chunk utility | Identify low-utility chunks using citations, reranker/similarity scores or lexical fallback. | <a href="#rag-chunk-utility">Full reference</a> · [Source](rag-chunk-utility.md) |
| Dashboards, OTLP and history | Render HTML reports, import/export OTLP and receive or retain traces locally. | <a href="#cli-reference">Full reference</a> · [Source](cli-reference.md) |
| Exports and AIOS contracts | Export JSON/CSV/Markdown/Jira, validate draft artifacts and resolve provenance from held bytes. | <a href="#coordinated-readiness">Full reference</a> · [Source](coordinated-v1-readiness.md) |
| Execution evidence verification and replay | Authenticate explicitly scoped snapshots and replay verified execution records offline. | <a href="#execution-evidence-verification">Full reference</a> · [Source](evidence-verification.md) |
| Enterprise artifact operations | Isolate project artifacts with credentials/roles, storage policy, registries, gate receipts, retention and audit. | <a href="#enterprise-artifact-operations">Full reference</a> · [Source](production-readiness.md) |
| Provider and multi-agent integrations | Extract OpenAI/Anthropic usage and instrument framework-neutral or LangGraph multi-agent workflows. | <a href="#provider-and-framework-integrations">Full reference</a> · [Source](integrations.md) |
| Sidecar, Chaos, Tower and MCP interoperability | Consume correlated native evidence while preserving producer identity, authority and health semantics. | <a href="#sidecar-correlation">Full reference</a> · [Source](sidecar-integration.md) |
| Configuration and limitations | Configure pricing, thresholds, capture and deployment; preserve unknowns and draft/candidate boundaries. | <a href="#configuration">Full reference</a> · [Source](configuration.md) |

## How to use this reference

1. Choose a capability above and read its detailed workflow, prerequisites and limitations.
2. Consult **Source declarations: src/agenticlens/...** for declared callable signatures, CLI arguments/options, exported names and model fields. These are extracted statically, without importing or executing the package. Undocumented helpers remain internal; extraction does not make them stable public APIs. Re-exported Evals types remain owned by the installed `agentic-evals` dependency.
3. Consult **Data contract: schemas/...** for bundled schema IDs, required fields, enum values and constraints. AIOS draft versions and Lens-local candidate versions remain independent of package versions. Vendored AIOS schemas retain their upstream ownership; adjacent source metadata and license identify their provenance.
4. Use the final historical compatibility/release sections only for their stated package versions. Prefer the current source declarations, package metadata and coordinated readiness notes for the included checkout.
5. Verify `ai-docs-manifest.json` before ingestion. It records every selected document, declaration source, schema and downloadable example with normalized source hashes, plus the generated reference checksum.

## Maintaining coverage

`docs/ai-docs.json` selects the full topic guides, historical integration notes, package declaration sources and bundled schemas. After changing a selected source, regenerate the pack with the shared documentation generator from the sibling `deepagentlabs.github.io` checkout:

```bash
python3 ../deepagentlabs.github.io/scripts/build_ai_docs.py --sources .. --project agenticlens
python3 ../deepagentlabs.github.io/scripts/build_ai_docs.py --sources .. --project agenticlens --check
```

Run from the AgenticLens repository root with Python 3.11 or newer (the generator uses `tomllib`). The documentation deployment uses the shared theme; the generated pack remains a raw Markdown download. Keep both capability indexes and the CLI inventory aligned when adding a user-facing capability.
