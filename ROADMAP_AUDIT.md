# AgenticLens roadmap implementation audit

Audit date: 2026-09-11. Baseline: commit
`11ffabef322ecafcaffb40d7302814bb12a1f44e` plus the current local changes,
including unreleased calibration and the Windows live-target path fix.
Scope: the canonical [product roadmap](agenticlens-roadmap.md), its milestone
deliverables and completion criteria, and listed integrations. The separate
research roadmap is not treated as a product implementation commitment.

**The roadmap is partially implemented. No milestone should be treated as fully
accepted merely because related classes, metadata fields, or examples exist.**

## Correctness follow-up (unreleased)

The audit below records the baseline findings. A subsequent implementation fixes
findings 1, 2, 3, and 5: Draft 2020-12 validation replaces the schema subset,
duplicate/unknown samples are rejected, incomplete cost totals stay unavailable
(including unpriced spans), and task_success takes precedence over execution
status. Historical claims below describe the pre-fix audit snapshot.
See [regression tests](tests/test_evaluation_correctness.py) and the README's
compatibility notes. Evaluator versions, Python timeout enforcement, and HTML
gate-status semantics remain open; the roadmap is not fully complete.

## How to read this audit

- **Implemented (I):** usable code exists for the stated scope; evidence and test
  limits are recorded below. This does not assert publication, merge status,
  production adoption, or independent validation.
- **Partial (P):** a subset, extension point, or narrower related capability exists.
- **Missing (M):** no implementation of the stated capability was found in the
  inspected source, tests, examples, and configuration.
- **Unverified (U):** a completion claim requires evidence not established here.

Related roadmap bullets are grouped where they share implementation and gaps.
Missing entries are repository-scoped findings, not claims about sibling projects.

## Milestone summary

| Milestone | Assessment | Main open work |
| --- | --- | --- |
| v0.2 Trace/comparison | Partial acceptance; core implemented | Overhead benchmark and comprehensive artifact/schema acceptance evidence |
| v0.2.x Evidence/operations | Partial acceptance; core implemented | Universal source-span provenance claim is stronger than enforcement; only AIOS 0.4 draft supported |
| v0.3 Evaluation | Partial | Evaluator identity/version tracking, schema subset limits, async/batch, datasets, built-in judge clients, broader calibration, adapters, webhooks |
| v0.4 Experiments | Partial building blocks | Experiment runner/manifests, repeated per-case trials, multi-variant analysis, pass@k/pass^k, uncertainty, heatmaps, Pareto |
| v0.5 Advanced evaluation | Partial | Built-in semantic/safety/trajectory evaluators, judge provenance/cost, diagnosis validation |
| v0.6 Datasets | Partial building blocks | Immutable snapshots, conversions, splits, curation, approvals, dataset-specific masking |
| v0.7 ModelFit | Missing as a subsystem | Task-aware, measured quality-constrained selection; cost-only suggestions already exist |
| v0.8 Routing | Missing | Runtime selection, failover, shadow/canary execution, escalation, audit |
| v0.9 Optimization | Partial | Outcome tracking, measured quality tradeoffs, broader optimization coverage |
| v1.0 Enterprise | Partial building blocks | Stable contracts, identity/access, registries, retention, audit/compliance, deployment and security acceptance |

## Evidence index

Paths are relative to this repository. Tests substantiate their covered cases,
not every possible behavior of an entire milestone.

| Key | Source | Regression evidence |
| --- | --- | --- |
| TRACE | [trace recorder](src/agenticlens/instrumentation/trace.py), [Run/Span models](src/agenticlens/models/trace.py), [redaction](src/agenticlens/instrumentation/redaction.py) | [test_trace.py](tests/test_trace.py) |
| PROFILE | [profiler](src/agenticlens/profiler/profile.py), [step capture](src/agenticlens/profiler/step.py), [metrics](src/agenticlens/metrics/calculator.py) | [test_profiler.py](tests/test_profiler.py), [test_models.py](tests/test_models.py), [test_providers.py](tests/test_providers.py) |
| DIAG | [trace analysis](src/agenticlens/analysis/trace.py), [next analysis](src/agenticlens/analysis/next_steps.py) | [test_trace.py](tests/test_trace.py), [test_trace_reports.py](tests/test_trace_reports.py) |
| COMP | [comparison runner](src/agenticlens/comparison/runner.py), [models](src/agenticlens/comparison/models.py), [exports](src/agenticlens/comparison/export.py), [Markdown](src/agenticlens/comparison/markdown.py) | [test_comparison.py](tests/test_comparison.py), [test_cli.py](tests/test_cli.py) |
| EVAL | [evaluation runner](src/agenticlens/evaluation/runner.py), [models](src/agenticlens/evaluation/models.py), [callbacks](src/agenticlens/evaluation/evaluators.py), [HTML](src/agenticlens/evaluation/html_report.py) | [test_evaluation.py](tests/test_evaluation.py), [test_cli.py](tests/test_cli.py) |
| CAL | [calibration](src/agenticlens/evaluation/calibration.py) | [test_calibration.py](tests/test_calibration.py) |
| GATE | [gate](src/agenticlens/evaluation/gate.py), [CLI](src/agenticlens/cli/main.py) | [test_evaluation.py](tests/test_evaluation.py) |
| RECS | [recommendation engine](src/agenticlens/recommenders/engine.py), [rules](src/agenticlens/recommenders), [recommendation model](src/agenticlens/models/recommendation.py) | [test_recommenders.py](tests/test_recommenders.py), [test_recommender_rules.py](tests/test_recommender_rules.py), [test_chaos_impact.py](tests/test_chaos_impact.py) |
| SWAP | [model swap](src/agenticlens/recommenders/model_swap.py), [settings](src/agenticlens/config/settings.py) | [test_model_swap.py](tests/test_model_swap.py) |
| OTLP | [OTLP exporter](src/agenticlens/exporters/otlp_trace_exporter.py), TRACE | [test_exporters.py](tests/test_exporters.py), [test_trace.py](tests/test_trace.py); HTTP export is mocked |
| AIOS | [draft validator](src/agenticlens/validation/aios.py) | [test_aios_validation.py](tests/test_aios_validation.py), [test_cli.py](tests/test_cli.py), [local fixtures](tests/fixtures/ai-operations-spec) |
| ARCH | [import-boundary test](tests/test_architecture_imports.py), [CI configuration](.github/workflows/ci.yml) | The import test runs with pytest |
| CLI | [commands](src/agenticlens/cli/main.py), [trace rendering](src/agenticlens/reports/trace.py) | [test_cli.py](tests/test_cli.py), [test_trace_reports.py](tests/test_trace_reports.py) |
| DASH | [dashboard renderer](src/agenticlens/reports/dashboard.py) | [test_dashboard_report.py](tests/test_dashboard_report.py), [test_cli.py](tests/test_cli.py) |
| OTLP-IN | [OTLP ingestion adapter](src/agenticlens/adapters/otlp.py) | [test_adapters_otlp.py](tests/test_adapters_otlp.py), [test_cli.py](tests/test_cli.py) |
| OTLP-LIVE | [live receiver + store](src/agenticlens/api) | [test_api_store.py](tests/test_api_store.py), [test_api_http.py](tests/test_api_http.py) |

## v0.2 Trace and Comparison Foundation

| Roadmap deliverable | Status | Evidence / remaining boundary |
| --- | --- | --- |
| Hierarchical run/span tracing; cyclic-parent detection | I | TRACE tests nested spans, unknown parents, cycles |
| Raw token, latency, cost, retry, tool metrics | I | PROFILE, TRACE, DIAG; costs can be estimated or unavailable |
| Payload redaction | I | TRACE for explicitly captured payloads; not a universal data-loss-prevention guarantee |
| Memory/retry findings; retry attribution and outcome classification | I | DIAG synthetic trace tests |
| Duplicated-context detection | I | DIAG groups reused inputs |
| Repeated-run statistics; baseline/candidate regression detection | I | COMP compares two saved run groups |
| Minimum-sample guidance | I | COMP and CLI; configurable enforcement exists |
| Trace inspection and comparison CLI | I | CLI |
| JSON/CSV/Markdown comparison exports; Markdown trace reports | I | COMP, CLI; formats exist, coverage varies by format |
| Versioned research schemas | I | [schemas](schemas) exist; universal validation is a separate acceptance claim |
| Instrumentation overhead measurement | M | No reproducible overhead benchmark found |
| Local HTML dashboard combining trace, cost, findings, gate, and comparison | I | DASH; `analyze`/`inspect`/`compare --html` and the `dashboard` command render conditionally on whichever artifacts are supplied, offline, no external requests |
| OTLP/OpenTelemetry ingestion (file/batch) into `Run`/`Span`, including third-party GenAI-semconv exports | I | OTLP-IN; `import-otlp` CLI |
| Live OTLP/HTTP receiver with a real-time dashboard | I | OTLP-LIVE; `serve-otlp` CLI, behind the optional `[api]` extra; opt-in only, no authentication, binds to localhost by default, plain-polling refresh (not SSE/websocket) |

Acceptance: saved-run comparisons and privacy defaults have code/tests.
Compatibility is exercised by existing profiler tests, not certified across all
historical releases. The claim that all trace artifacts validate against published
schemas is **U**: model validation and schema presence do not establish exhaustive
artifact conformance. Overhead remains an open gate.

## v0.2.x Evidence Provenance and Operational Intelligence

| Roadmap deliverable | Status | Evidence / remaining boundary |
| --- | --- | --- |
| First-class Evidence on findings/recommendations | I | TRACE defines Evidence; DIAG and RECS populate it |
| Timestamp, confidence, derivation/source information on every finding | P | Fields exist, but optional fields/defaults and generic fallback evidence do not ensure a complete lineage |
| Next-best-analysis guidance | I | DIAG maps findings to suggested follow-ups |
| Import-layer CI enforcement | I | ARCH checks specified package boundaries, not every architectural rule |
| OpenTelemetry trace export | I | OTLP for structured trace() runs; automatic export failure paths tested |
| AIOS validation/conformance CLI | I | AIOS schema and semantic checks for local 0.4 draft artifacts |
| Every recommendation cites source spans | P | RECS can fall back to workflow.recommendation with no span ID; direct rule results also need not pass through engine enrichment |
| Multi-version or native AIOS export | M | Outside this delivered scope: validator rejects versions other than 0.4; no native exporter found |

Acceptance: retain the implemented next-step, import-test, and draft-reporting
capabilities. Narrow the universal provenance and generic "profiled workflows"
wording: structured trace export is demonstrated; legacy profile() is a different
data model. External collector compatibility and unrelated producer validation
are **U** in this local audit.

## v0.3 Evaluation Foundation

| Roadmap deliverable | Status | Evidence / remaining boundary |
| --- | --- | --- |
| TestCase/TestSuite and YAML/JSON loading | I | EVAL; version is a label, not immutable content identity |
| Evaluator/Context/Score/Registry contracts | I | EVAL registry and threshold tests |
| Exact/substring match; required/forbidden tools | I | EVAL |
| Required output fields and tool argument names; turn, latency, cost thresholds | I | EVAL; argument presence is checked, not argument values or complete tool trajectories |
| JSON Schema output validation | P | _validate_json_schema implements types, required/properties/items subset; many keywords are ignored |
| CallableEvaluator, BusinessRuleEvaluator, LLMJudgeEvaluator | I | EVAL; caller supplies trusted execution/model logic through Python |
| Semantic/safety/RAG checks | P | Callback extension points and RAG recommendation heuristics exist; no built-in semantic/safety evaluator suite |
| JSON and standalone HTML reports | I | EVAL; HTML escaping is tested |
| Release gates and evaluate/gate CLI | I | GATE; absolute summary thresholds, not paired per-case regression gates |
| Live Python/HTTP targets | I | EVAL code and documented CLI; Python tests present, HTTP path has no dedicated target regression test in inspected suite |
| Offline LangGraph reference workflow | P | [reference example](examples/reference_workflows/langgraph_supervisor.py); no maintained event adapter or dedicated example integration test found |
| Offline judge agreement report and 95% Wilson interval | I | CAL, unreleased local implementation; strict suite/case matching and trace-linked confusion counts |
| Built-in judge provider clients | M | Provider modules extract usage; they do not perform judge inference |
| Async/batched execution | M | run_live_suite/evaluate_suite use synchronous loops |
| Broader calibration and statistical intervals | P | CAL only covers binary saved-verdict agreement, not probability calibration or threshold optimization |
| Dataset management | P | Version strings/labels/loaders exist; lifecycle management is v0.6 work |
| Automatic framework adapters | M | Example instrumentation is manual |
| Structured agree/partial/disagree verdict, confidence, grounding fields | M | Score has a value and free-form metadata, not that enforced contract |
| Cooldown-protected webhooks | M | No notifier/cooldown implementation found |

Acceptance gaps:
- **P:** scores carry name/type but no required evaluator-version field. Suite
  version is not evaluator version.
- **P:** unavailable costs are represented, but aggregate reports do not preserve
  complete measured/estimated provenance or distinguish partial cost coverage.
- **P:** cases with samples retain trace IDs; a missing sample produces an empty
  trace ID, and trace contents are not embedded in the evaluation report.
- **U:** Python and HTTP same-suite parity needs dedicated HTTP regression evidence.

## v0.4 Experiments and Statistical Comparison

| Roadmap deliverable | Status | Evidence / remaining boundary |
| --- | --- | --- |
| Experiment/variant manifests | P | TRACE has IDs; no manifest validation or experiment orchestration |
| Repeated trials per case | M | COMP summarizes supplied runs; it does not schedule per-case trials |
| Prompt/model/retrieval/memory/retry-policy comparison | P | Generic saved run-group comparison, not controlled variant execution |
| pass@k and pass^k | M | No estimators found |
| Confidence intervals | P | CAL's agreement interval only; no experiment-metric intervals |
| Consistency/stability summaries | P | COMP standard deviation/CV, not per-case consistency |
| Baseline regression analysis | P | COMP group-level thresholds; no paired evaluation-case analysis |
| Test-level score heatmaps | M | No implementation found |
| Pareto analysis | M | No implementation found |
| HTML/CSV experiment reports | P | EVAL HTML and COMP CSV exist for different report models; no experiment report |

Acceptance: three-variant experiments and randomization provenance are **M**.
Sample warnings exist for two-group comparison. Quality is represented largely by
task success, not a combined experimental report of evaluator scores, cost,
latency, and reliability.

## v0.5 Advanced Evaluation and Diagnosis

| Roadmap deliverable | Status | Evidence / remaining boundary |
| --- | --- | --- |
| Model-based judge interface | I | EVAL LLMJudgeEvaluator callback |
| Judge prompt/model versioning | M | No required stored identity/version contract |
| Groundedness/relevance/completeness/citation evaluators | P | Custom callbacks and RECS citation/chunk signals; no built-in suite |
| Tool-trajectory/agent-goal evaluators | P | Tool presence and turn limits; no ordered trajectory or general goal evaluation |
| Handoff/loop evaluators | P | RECS handoff bloat and DIAG retry heuristics; no evaluation suite for these |
| Safety evaluators | P | Callback mechanism only |
| Calibration reports | P | CAL binary reference agreement only |
| Failure taxonomy | P | Trace error fields/retry outcome categories; no full published diagnosis taxonomy |
| Deterministic diagnosis rules | I | DIAG memory/retry/duplicate context and RECS |
| Anomaly detection | P | Threshold heuristics exist, no general statistical anomaly detector |
| Faulty-step/agent attribution | P | DIAG/RECS identify local evidence; general causal attribution unproven |
| Incident timeline reconstruction | P | CLI renders ordered traces, not cross-run incident reconstruction |
| Investigation narratives | P | Rule explanations and follow-up guidance, not a causal investigation engine |
| inspect/compare/trace show/report explain | P | inspect and compare exist; trace show and report explain command trees do not |
| Richer conformance and spec-version selection | P | AIOS detailed reports exist; only 0.4 supported |
| Analysis budget/depth/stagnation guards | M | No automated analyzer guard subsystem |

Acceptance: evaluator_type is serialized, but summary average pools score types
and HTML does not separate deterministic/model-based aggregates. Dedicated judge
cost capture is **M**. CAL shows judge/reference disagreements, not a multi-judge
comparison. Confidence/evidence fields exist, but population-level attribution
accuracy on controlled failures is **U**; synthetic rule tests alone are insufficient.

## v0.6 Test-Suite and Dataset Management

| Roadmap deliverable | Status | Evidence / remaining boundary |
| --- | --- | --- |
| Test-case/suite editors | P | Python models and hand-edited YAML/JSON; no dedicated editing workflow |
| Immutable suite versions | M | TestSuite is mutable; no snapshot/hash store |
| CSV/JSON imports | P | JSON/YAML suite/sample loading; no dataset CSV importer |
| Production trace conversion; user-feedback conversion | M | No conversion pipeline |
| Synthetic variation generation | M | No implementation |
| Tags/domain categories | P | TestCase.tags and metadata exist; no managed categorization |
| Train/validation/test splits | M | No implementation |
| Duplicate detection | P | Duplicate suite IDs rejected; no semantic/content deduplication, sample dictionary overwrites duplicate IDs |
| PII masking | P | TRACE redactor exists; suite labels, outputs, and stored evaluation datasets have no integrated masking lifecycle |
| Approval metadata | P | Generic metadata possible; no validated approval record/workflow |

Acceptance: CLI evaluation/gates can support CI. Conversion, immutable approved
versions, and dataset-wide storage masking remain open.

## v0.7 ModelFit

| Roadmap deliverable | Status | Evidence / remaining boundary |
| --- | --- | --- |
| Task taxonomy | P | TRACE task_type string; no governed taxonomy |
| Constraint configuration | P | SWAP candidate/provider/context filters, not task-quality/safety/deployment constraints |
| Weighted scoring; Pareto frontier | M | No ModelFit ranking engine |
| Cost-per-success ranking | P | COMP reports group cost/success; SWAP does not rank measured task outcomes |
| Recommendation confidence/explanation | P | RECS fields/descriptions exist; no task-level ModelFit calibration |
| Alternative/fallback models | P | SWAP cheaper candidate suggestion; no quality-validated fallback policy |
| Task-level model matrix | M | No implementation |

Acceptance: savings are cost projections, not experimental quality validation.
Task-specific hard constraints, quality risk validation, and experiment-backed
selection remain open. A cost-only ModelSwapRecommender is not ModelFit.

## v0.8 Advisory Runtime Routing

All listed deliverables are **M**: routing SDK; rule/score-based runtime selection;
policy-aware routing; fallback chains; provider failover; confidence thresholds;
human escalation; shadow/canary modes; routing audit log.

No corresponding execution subsystem or tests were found. The provider registry
is usage extraction and the model-swap recommender is advisory analysis.
Explainable runtime decisions, tested failover, measurable shadow operation, and
policy blocking therefore remain open acceptance gates.

## v0.9 Optimization Intelligence

| Roadmap deliverable | Status | Evidence / remaining boundary |
| --- | --- | --- |
| Prompt compression/caching recommendations | P | RECS repeated-prompt/cache suggestions; no measured compression workflow |
| Retrieval/reranking recommendations | P | RECS excess chunks and utility scoring using supplied signals; no reranking experiment |
| Memory retention/summarization recommendations | P | RECS long-history and DIAG memory-share guidance |
| Tool caching/retry recommendations | P | RECS duplicate tools and DIAG retry analysis; no measured retry-policy optimization |
| Redundant steps/unnecessary handoffs | P | Duplicate tool/context and handoff-bloat rules; no general redundancy detector |
| Quality-cost tradeoffs | P | SWAP projected costs and RECS risk fields; no measured quality frontier |
| Projected benefit/confidence/risk | P | RECS fields populated for some rules; not universal or calibrated |
| Accepted/rejected recommendation tracking | M | No persistence/feedback workflow |

Acceptance: source evidence exists for rules but can fall back to generic
workflow evidence. Projected savings and risk fields do not establish observed
benefit. Post-adoption outcome measurement and feedback remain **M**.

## v1.0 Production and Enterprise Readiness

| Roadmap deliverable | Status | Evidence / remaining boundary |
| --- | --- | --- |
| Stable public APIs/schemas | P | Versioned models/schemas exist; stability, compatibility, and migration acceptance not established |
| Organizations/projects; authentication/RBAC | M | No shared-service identity/access model |
| Audit logs | P | Traces/evidence exist; no durable governance audit log |
| Model/prompt registries | M | Pricing/provider lookup is not a model/prompt lifecycle registry |
| Policy-as-code | P | GATE thresholds and suite rules; no general policy runtime |
| Retention/PII controls | P | TRACE capture redaction; no retention/deletion governance |
| Release gates | I | GATE absolute thresholds and CLI exit results |
| Compliance exports | M | General JSON/CSV/Markdown/Jira output is not a compliance evidence contract |
| Private evaluators | I | EVAL trusted application callbacks; not an isolated multi-tenant execution service |
| Kubernetes/Helm options | M | No deployment assets found |

Acceptance: stable compatibility/migration guarantees, audited governance
decisions, and deployment security review are **U/M**, not established by local
tests. Replaying gates over a saved report is implemented; immutable input
provenance is not.

## Integration inventory

| Target | Status | Evidence / boundary |
| --- | --- | --- |
| LangGraph | P | Reference example only; no maintained automatic event adapter |
| OpenAI Agents SDK, CrewAI, AutoGen, Semantic Kernel, LlamaIndex, Haystack | M | No dedicated adapters in source |
| HTTP agents | I | EVAL synchronous target; dedicated HTTP regression coverage missing |
| MCP-hosted agents | M | No native AgenticLens MCP agent target; sibling server integration not audited |
| OpenInference | M | No mapping/export adapter found |
| OpenTelemetry/OTLP | I | OTLP structured trace exporter with mocked transport tests |
| Semantica | M | No exporter or tested Sidecar correlation-ID contract found |
| PROV-O/RDF/JSON-LD | M | Guidance only |
| Agentic Chaos | P | RECS consumes attached chaos evidence; sibling end-to-end workflow not audited |
| Sidecar / Control Tower | U | Coordination intent is not proof of integration in this repository |

## Verification and uncovered acceptance risks

Full local suite: **152 passed** on Windows with workspace-local Python 3.14.0:
`python -m pytest -q --no-cov -p no:cacheprovider`.
No external model, real OTLP collector, production load, package registry, or
multi-organization adoption was verified. Hosted CI and all supported Python
versions were not rerun.

Source review also identified issues worth addressing before stronger enterprise claims:

1. Output schema validation ignores unsupported constraints such as enum/minimum;
   its Python type checks can accept booleans as integers. Use the full validator
   or explicitly reject unsupported schema keywords.
2. evaluate_suite maps samples by ID without rejecting duplicates or extras.
   Duplicate inputs can silently replace evidence.
3. Evaluation cost totals sum known values even when other cases are unpriced.
   A total-cost gate can therefore treat a partial total as complete.
4. Python live targets expose a timeout field but execute synchronously without
   enforcing it. HTTP calls do use the configured timeout.
5. Comparison success uses task_success OR succeeded status: an explicitly false
   task result can count as successful when execution status is succeeded.
6. HTML's READY label depends on failed-case count, not evaluate_gate thresholds.
   It should not be interpreted as a gate decision.
7. Calibration records dataset/suite versions but does not enforce judge
   model/prompt/version or immutable dataset identity.

Synthetic checks reproduced ignored enum constraints, boolean/integer acceptance, duplicate-sample replacement, partial cost totals, failed-task success counting, and missing evaluator-version enforcement. Other findings are from source inspection. No product fixes were made by this audit. All local evidence links resolve.

## Recommended implementation order

1. Close evaluation correctness gaps above and require evaluator provenance.
2. Add versioned immutable dataset snapshots and exact input identity checks.
3. Add async/batched evaluation with explicit failure/timeout behavior and tests.
4. Build per-case repeated trials and baseline/candidate evaluation comparison.
5. Add the remaining experiment metrics, multi-variant reports, and enterprise
   evidence workflows on those foundations.

Keep existing feature sequencing. Do not add a new enterprise roadmap that
duplicates these commitments.
