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

## 0.6.0 follow-up (2026-10-12)

Release 0.6.0 (with sibling `agentic-evals` 0.7.1) closes the v0.3 acceptance
gaps and delivers the v0.4 deliverables. The v0.3 and v0.4 tables below are
updated in place; other sections still describe the 2026-09-11 snapshot.

| Earlier gap | Resolution | Evidence |
| --- | --- | --- |
| No evaluator version on scores | `Score.evaluator`/`evaluator_version` stamped by agentic-evals; `audit_report` blocks unversioned evaluators | `tests/test_evidence_audit.py`, agentic-evals `tests/test_provenance.py` |
| Cost provenance and coverage | `EvalTrace.cost_source`, per-case `cost_source`, summary `priced_cases`/`cost_sources`; Lens runs default to `estimated` | `tests/test_evidence_audit.py` |
| Missing samples indistinguishable from lost trace IDs | `CaseEvaluation.sample_available`; audit always blocks untraceable failed cases | `tests/test_evidence_audit.py` |
| No HTTP live-target parity evidence | One suite run through Python and HTTP targets with identical reports, sequential and concurrent | `tests/test_live_parity.py`, agentic-evals `tests/test_live_targets.py` |
| Finding 6: HTML READY label implied a gate decision | Label now states case outcome; release decisions stay with `gate` | `tests/test_evidence_audit.py` |
| Finding 7: calibration did not pin the judge | Calibration records the judge version and rejects mixed versions | `tests/test_calibration.py` |

Still open: Python live-target timeouts are not enforced (finding 4); built-in
judge provider clients; async evaluator APIs; framework event adapters;
probability calibration of judge scores.

## 0.7.0 follow-up (2026-10-13)

Release 0.7.0 delivers the v0.5 deliverables and completion criteria. The v0.5
table below is updated in place; other sections still describe earlier
snapshots.

| Earlier gap | Resolution | Evidence |
| --- | --- | --- |
| Judge prompt/model versioning missing | `structured_judge` records judge model, provider, prompt version, prompt SHA-256 | `tests/test_score_analysis.py` |
| Judge cost capture missing | `JudgeVerdict.usage` → `judge_cost_usd`/tokens/latency on scores; `analyze_scores().judge_cost` (estimated from pricing when unreported) | `tests/test_score_analysis.py` |
| Summary pools deterministic and model-based scores | `analyze_scores` reports them separately; CLI and HTML show both | `tests/test_score_analysis.py`, `tests/test_cli_diagnosis.py` |
| No multi-judge disagreement view | Per-case disagreements and pairwise agreement between deterministic checks and each judge | `tests/test_score_analysis.py` |
| No built-in trajectory/goal/handoff/loop/RAG/safety evaluators | Nine trace-aware evaluators registered by name | `tests/test_trace_evaluators.py` |
| No published failure taxonomy | `FailureCategory` taxonomy v1.0 | `tests/test_diagnosis_rules.py` |
| No statistical anomaly detector | Median/MAD robust z against baselines with MeanAD and constant-baseline fallbacks | `tests/test_diagnosis_engine.py` |
| Attribution accuracy on controlled failures unverified | `evaluate_attribution`; 40-case corpus, 40/40 (Wilson 91.2–100%) | `tests/test_attribution_accuracy.py`, `examples/diagnosis/attribution-accuracy.json` |
| No incident timeline, narratives, trace show / explain | `build_timeline`, `explain_run`, `explain_recommendations`; `trace show/timeline`, `explain`, `diagnose` | `tests/test_diagnosis_engine.py`, `tests/test_cli_diagnosis.py` |
| No analyzer guard subsystem | `AnalysisBudget`/`AnalysisGuard`: spans, depth, diagnoses, time, iterations, cost, stagnation | `tests/test_diagnosis_engine.py` |
| Conformance not rule-cited | AIOS rule IDs, per-rule results, summary, `--json`, `--list-versions`, AIOS-0.5-V03 routing | `tests/test_aios_conformance_rules.py` |

Still open: the controlled-failure corpus is synthetic (independent corpora are
needed); attribution shares are not calibrated probabilities; lexical
evaluators do not judge meaning; only AIOS v0.4-draft is supported; Python
live-target timeouts remain unenforced.

## 0.8.0 follow-up (2026-10-17)

Release 0.8.0 delivers the v0.6 deliverables and completion criteria. The v0.6
table below is updated in place; other sections still describe earlier
snapshots.

| Earlier gap | Resolution | Evidence |
| --- | --- | --- |
| No dedicated editing workflow | `agenticlens.suites` editors and `suite add-case/remove-case/tag/review/filter/diff/summary` | `tests/test_suites_editing.py`, `tests/test_cli_suites.py` |
| TestSuite mutable; no snapshot/hash store | `SuiteStore`: write-once versions, canonical-JSON SHA-256 re-verified on every read, conflicting re-approval refused | `tests/test_suites_store.py` |
| No dataset CSV importer | CSV (unknown columns rejected), JSON, JSON Lines, YAML imports | `tests/test_suites_importers.py` |
| No trace/feedback conversion pipeline | `cases_from_runs`, `cases_from_feedback`; skipped inputs reported with reasons | `tests/test_suites_conversion.py` |
| No synthetic variations or splits | Deterministic variations; stable, lineage-aware hash splits | `tests/test_suites_quality.py` |
| No content deduplication | Exact, near (Jaccard), and conflicting-label duplicate groups | `tests/test_suites_quality.py` |
| No integrated masking lifecycle | Masking on by default for imports/conversions; approval refuses unmasked PII; value-free reports | `tests/test_suites_pii.py` |
| No validated approval record | `ApprovalRecord` with recorded checks; per-case review status | `tests/test_suites_store.py` |
| CI regression run unproven | CI `regression-suite` job: verify → export → evaluate → gate on `examples/suites/store` | `.github/workflows/ci.yml`, `tests/test_examples_suites.py` |

Still open: PII detection is pattern/key based; variations are not paraphrases;
deduplication is lexical and pairwise; approvals are not authenticated; the
store is local files rather than a shared registry.

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
| v0.3 Evaluation | Implemented (0.6.0) | Follow-ons only: built-in judge clients, async evaluator APIs, framework adapters, probability calibration, Python target timeouts |
| v0.4 Experiments | Implemented (0.6.0) | Multiple-comparison correction; correlated-attempt-aware intervals; parallel trials |
| v0.5 Advanced evaluation | Implemented (0.7.0) | Independent controlled-failure corpora; semantic (non-lexical) evaluators; judge provider clients |
| v0.6 Datasets | Implemented (0.8.0) | Semantic deduplication and paraphrases; authenticated approvals and a shared registry (v1.0) |
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
| OTLP-LIVE | [live receiver + store](src/agenticlens/api) (`LiveTraceStore` and `PersistentTraceStore`, `GET /history`) | [test_api_store.py](tests/test_api_store.py), [test_api_http.py](tests/test_api_http.py) |

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
| OTLP/OpenTelemetry ingestion (file/batch) into `Run`/`Span`, including third-party GenAI-semconv exports | I | OTLP-IN; `import-otlp` CLI; fidelity is bounded by the OTel GenAI spec itself — cost and 7 of 11 `SpanType` values (retrieval, planning, final_response, etc.) have no standardized attribute and are only recovered when the source also emits `agenticlens.*` attributes (see README's ingestion fidelity table) |
| Live OTLP/HTTP receiver with a real-time dashboard | I | OTLP-LIVE; `serve-otlp` CLI, behind the optional `[api]` extra; opt-in only, no authentication, binds to localhost by default, plain-polling refresh (not SSE/websocket) |
| Persistent local trace history and cross-trace aggregate view | I | OTLP-LIVE; `serve-otlp --db` (stdlib `sqlite3`, no new dependency), `GET /history`, and the offline `agenticlens history` CLI command; unbounded by default, no alerting (explicitly out of scope for local visibility) |

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
| JSON Schema output validation | I | Full Draft 2020-12 validation since 0.5.0; external references are not fetched |
| CallableEvaluator, BusinessRuleEvaluator, LLMJudgeEvaluator | I | EVAL; caller supplies trusted execution/model logic through Python |
| Semantic/safety/RAG checks | P | Callback extension points and RAG recommendation heuristics exist; no built-in semantic/safety evaluator suite |
| JSON and standalone HTML reports | I | EVAL; HTML escaping is tested |
| Release gates and evaluate/gate CLI | I | GATE; absolute summary thresholds, not paired per-case regression gates |
| Live Python/HTTP targets | I | Same-suite Python/HTTP parity tests (`tests/test_live_parity.py`); `--max-workers` concurrency with stable case order |
| Offline LangGraph reference workflow | P | [reference example](examples/reference_workflows/langgraph_supervisor.py); no maintained event adapter or dedicated example integration test found |
| Offline judge agreement report and 95% Wilson interval | I | CAL, unreleased local implementation; strict suite/case matching and trace-linked confusion counts |
| Built-in judge provider clients | M | Provider modules extract usage; they do not perform judge inference |
| Async/batched execution | P | Thread-pool concurrency for live targets (`max_workers`); no async evaluator API |
| Broader calibration and statistical intervals | P | Verdict agreement plus threshold tuning (`tune_judge_threshold`, balanced accuracy); no probability calibration |
| Dataset management | I | `agenticlens dataset summary/split/export-samples`; lifecycle management (immutability, approvals) is v0.6 work |
| Automatic framework adapters | M | Example instrumentation is manual |
| Structured agree/partial/disagree verdict, confidence, grounding fields | I | `JudgeVerdict` + `structured_judge`; self-judging skipped or flagged (`tests/test_judging.py`) |
| Cooldown-protected webhooks | I | `notify_gate_breach`, `gate --notify-webhook`; generic/Slack/Teams; per-threshold and per-category cooldowns (`tests/test_gate_notifications.py`) |

Acceptance (0.6.0):
- **I:** every score identifies its evaluator and version; `audit_report` and
  `evaluate --strict-evidence` block unversioned evaluators.
- **I:** reports preserve measured/estimated cost provenance and cost coverage
  (`priced_cases`, `cost_sources`); incomplete totals remain unavailable.
- **I:** failed cases retain trace IDs; missing samples are flagged with
  `sample_available=False`, and the audit blocks any untraceable failure.
  Trace contents are referenced by ID, not embedded.
- **I:** Python/HTTP same-suite parity has dedicated regression tests.

## v0.4 Experiments and Statistical Comparison

| Roadmap deliverable | Status | Evidence / remaining boundary |
| --- | --- | --- |
Evidence key EXP: `src/agenticlens/experiments/`, `tests/test_experiments.py`,
`tests/test_experiments_v04.py`, `tests/test_experiment_stats.py`,
`tests/test_cli_evaluation_experiments.py`, and the reproducible example in
`examples/experiments/` (`tests/test_examples_evaluation_experiments.py`).

| Roadmap deliverable | Status | Evidence / remaining boundary |
| --- | --- | --- |
| Experiment/variant manifests | I | EXP; validated manifests with ≥ 3 variants, factors, `pass_k`, `minimum_trials`; published JSON Schemas |
| Repeated trials per case | I | EXP; per-case attempts/passes across trials; live (Python/HTTP) or recorded replay |
| Prompt/model/retrieval/memory/retry-policy comparison | I | EXP; variant `factors`, `changed_factors` per comparison, factor-level summaries |
| pass@k and pass^k | I | EXP; unbiased pass@k and pass^k per case and per variant |
| Confidence intervals | I | EXP; Wilson intervals for case pass rate, normal intervals for per-trial metrics |
| Consistency/stability summaries | I | EXP; per-case consistency, flaky-case lists, CV per metric |
| Baseline regression analysis | I | EXP; deltas, two-proportion p-values, regressed/improved case lists |
| Test-level score heatmaps | I | EXP; variant x case heatmap in the HTML report, case-matrix CSV |
| Pareto analysis | I | EXP; frontier over reliability, pass rate, score, latency, cost |
| HTML/CSV experiment reports | I | EXP; `--html`, `--csv`, `--cases-csv`, `experiment report` re-render |

Acceptance (0.6.0): three-variant experiments **I**; trial counts, seed, and
execution order recorded **I**; minimum-sample warnings in reports and
comparisons **I**; quality, cost, latency, and reliability shown together **I**.
Boundary: intervals and p-values treat case attempts as independent, and there
is no multiple-comparison correction.

## v0.5 Advanced Evaluation and Diagnosis

Updated for 0.7.0 (2026-10-13).

| Roadmap deliverable | Status | Evidence / remaining boundary |
| --- | --- | --- |
| Model-based judge interface | I | EVAL `LLMJudgeEvaluator`, `structured_judge` |
| Judge prompt/model versioning | I | Judge model, provider, prompt version and SHA-256 on every judge score |
| Groundedness/relevance/completeness/citation evaluators | I | Trace-aware evaluators; groundedness/relevance/completeness are lexical heuristics |
| Tool-trajectory/agent-goal evaluators | I | `tool_trajectory` (exact/in-order/any-order), `agent_goal` |
| Handoff/loop evaluators | I | `handoff`, `loop` evaluators; `handoff_loop`/`tool_loop` diagnosis rules |
| Safety evaluators | I | `safety`: PII and forbidden terms in output and tool arguments (pattern-based) |
| Calibration reports | I | CAL agreement, Wilson intervals, threshold tuning (0.5.0/0.6.0) |
| Failure taxonomy | I | `FailureCategory` taxonomy v1.0 |
| Deterministic diagnosis rules | I | `agenticlens.diagnosis.rules` (9 versioned rules) |
| Anomaly detection | I | Robust z against baseline runs |
| Faulty-step/agent attribution | I | `attribute()`; accuracy measured on controlled failures |
| Incident timeline reconstruction | I | `build_timeline`, `trace timeline` |
| Investigation narratives | I | `explain_run`, `explain_recommendations`, `explain` |
| inspect/compare/trace show/report explain | I | `trace show`, `trace timeline`, `explain` (in place of `report explain`) |
| Richer conformance and spec-version selection | I | Rule-cited per-rule results, `--json`, `--list-versions`; only 0.4 supported |
| Analysis budget/depth/stagnation guards | I | `AnalysisBudget`, `AnalysisGuard` |

Acceptance: deterministic and model-based scores are separated in
`analyze_scores`, CLI, and HTML; judge cost is recorded per score and per
evaluator; disagreement is listed per case with pairwise agreement; every
diagnosis carries confidence, supporting spans, and span-level evidence;
attribution accuracy on controlled failures is measured (40/40 on a synthetic
corpus written alongside the rules, so independent corpora remain **U**).

## v0.6 Test-Suite and Dataset Management

| Roadmap deliverable | Status | Evidence / remaining boundary |
| --- | --- | --- |
Updated for 0.8.0 (2026-10-17).

| Roadmap deliverable | Status | Evidence / remaining boundary |
| --- | --- | --- |
| Test-case/suite editors | I | `agenticlens.suites` editors and `suite` CLI; no interactive UI |
| Immutable suite versions | I | `SuiteStore` write-once versions with re-verified SHA-256 |
| CSV/JSON imports | I | CSV, JSON, JSON Lines, YAML (`import_cases`, `suite import`) |
| Production trace conversion; user-feedback conversion | I | `cases_from_runs`, `cases_from_feedback`; failed runs and uncorrected negative feedback skipped with reasons |
| Synthetic variation generation | I | Six deterministic surface perturbations; not paraphrases |
| Tags/domain categories | I | `tags`, `metadata.domain`; filtering and summaries |
| Train/validation/test splits | I | `assign_splits`: stable hash of lineage; ratios approximate |
| Duplicate detection | I | Exact, near (lexical Jaccard), and conflicting-label groups; pairwise |
| PII masking | I | `PIIMasker` (patterns + sensitive keys; redact/hash) on by default before storage; pattern-based limits |
| Approval metadata | I | `ApprovalRecord` (approver, time, notes, checks), per-case review status; approver not authenticated |

Acceptance: all four completion criteria are met in 0.8.0 (see the
[roadmap](agenticlens-roadmap.md#v06--test-suite-and-dataset-management)).

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
