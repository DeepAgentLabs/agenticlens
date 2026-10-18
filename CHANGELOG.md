# Changelog

All notable changes to this project will be documented here.

This project follows [Semantic Versioning](https://semver.org/).

## Unreleased

## 0.9.0 - 2026-10-18

Delivers roadmap milestone v0.7 (ModelFit).

### Added — model recommendations (`agenticlens.modelfit`)

- Experiment evidence: `load_experiment_evidence` reads an experiment report
  (`agenticlens experiment run --save`) and records its file name and
  SHA-256; `collect_candidates` turns every variant into a candidate with one
  attempt per case per trial. Failed trials count as failed attempts with no
  cost. Model names come from the `model` factor (`model_factor`); provider,
  deployment, and capabilities from the config's `candidates` catalog, the
  manifest's variant metadata, or `provider`/`deployment` factors.
- Task taxonomy: `TaskCategory` selects cases by tag, `metadata.domain`, or
  case ID; `derive_categories` creates one category per tag when none are
  configured; the `all` category covers every case; `resolve_taxonomy`
  reports uncategorized cases and categories that match nothing.
- Hard constraints: `ModelConstraints` (`min_pass_rate`,
  `min_pass_rate_lower_bound`, `max_cost_per_case_usd`,
  `max_cost_per_success_usd`, `max_mean_latency_ms`, `max_p95_latency_ms`,
  `min_consistency`, `min_safety_pass_rate`, `allowed_providers`,
  `blocked_providers`, `allowed_deployments`, `required_capabilities`) with
  config defaults and per-category overrides (`null` removes a default,
  including for list constraints). `check_constraints` fails closed: a limit
  the evidence cannot verify is a violation, including a block-list against
  an unknown provider and a latency limit over partial latency evidence.
- Scoring: `ScoringWeights` (quality, cost, latency, reliability; per-category
  weights allowed) over feasible candidates, normalised to the cheapest and
  fastest; per-category `pareto_frontier` (pass rate, cost per success,
  latency) and `cost_per_success_ranking`.
- Recommendations: `recommend_models` returns a `ModelFitReport` with one
  `CategoryResult` per category. Each `Recommendation` has a status
  (`recommended`, `no_feasible_model`, `no_evidence`), a confidence level
  with reasons, an explanation citing measured values and every rejection,
  ranked alternatives, a fallback on a different provider when one is
  feasible, a `SavingsEstimate` against the reference variant (per case, per
  success, and per month from `monthly_volume`, with attempts, case IDs, and
  source indexes; unavailable when cost is incomplete or the two candidates
  were measured on different cases), and `QualityRisk`s
  (quality regression with significance, regressed, flaky, and safety-failed
  cases, low evidence, unavailable cost, failed trials, no fallback).
- Task-level model matrix: `ModelFitReport.matrix` (one row per category and
  candidate, with its role), `render_matrix_csv`, and `render_markdown`.
- Config and report I/O: `load_modelfit_config` (YAML or JSON),
  `load_modelfit_report`, `save_modelfit_report`.

### Added — CLI

- `agenticlens modelfit recommend REPORT... [--config] [--manifest] [--save]
  [--markdown] [--csv] [--json] [--fail-on-unfit] [--fail-on-low-confidence]`.
  Exit 8 when a category has no feasible model (`--fail-on-unfit`) or a
  recommendation is low confidence (`--fail-on-low-confidence`).
- `agenticlens modelfit matrix MODELFIT_REPORT [--csv] [--markdown]` and
  `agenticlens modelfit taxonomy REPORT... [--config] [--json]`.

### Added — schemas, example, docs, CI

- `schemas/modelfit/modelfit-config.schema.json` and
  `schemas/modelfit/modelfit-report.schema.json` (`schema_version: "1.0"`).
- `examples/modelfit_demo.py`: a recorded four-model experiment (two
  providers, cloud and on-prem) on a ten-case support suite, with committed
  artifacts reproduced by `tests/test_examples_modelfit.py`.
- [ModelFit guide](docs/modelfit.md); README, roadmap, audit, and AGENTS
  updates.
- CI `modelfit` job: replays the experiment and runs
  `modelfit recommend --fail-on-unfit`.

### Ecosystem

- No AIOS object or existing Lens artifact changes. Agentic Sidecar 0.8.4
  widens its optional `agenticlens` extra from `<0.9` to `<1`; MCP 0.3.11
  pins hosted images to 0.9.0 and adds a read-only `lens.modelfit_recommend`
  tool; Control Tower, Chaos, and Evals already admit 0.9.0.

## 0.8.0 - 2026-10-17

Delivers roadmap milestone v0.6 (Test-Suite and Dataset Management).

### Added — suite management (`agenticlens.suites`)

- Imports from CSV (`|`-separated list columns, JSON `input`, `domain`,
  `split`, `metadata.<key>`; unknown columns rejected), JSON, JSON Lines, and
  YAML: `import_csv`, `import_json`, `import_cases`, `import_suite`.
- Production trace conversion: `case_from_run` / `cases_from_runs` turn
  successful runs into cases expecting their tool trajectory
  (`required_tools`, `required_tool_order`) and latency/cost within a margin;
  `include_output` also expects the recorded output. Failed runs, runs
  without a recorded input, and runs with nothing to expect are skipped with
  a reason.
- User-feedback conversion: `FeedbackRecord`, `load_feedback`,
  `case_from_feedback` / `cases_from_feedback`. Corrections and confirmed
  outputs become expected outputs. A missing input is filled from the
  referenced run. Uncorrected negative feedback is skipped with a reason.
- Suite editors: `add_case`, `update_case`, `remove_cases`, `tag_cases`
  (tags and domain categories), `review_cases`, `merge_suites`,
  `filter_suite`, `summarize_suite`, `diff_suites`, `load_suite_file`,
  `save_suite_file`. Case lineage (`source`), `review_status`,
  `reviewed_by`, `review_notes`, `domain`, and `split` live in case metadata,
  so suites stay plain agentic-evals `TestSuite`s.
- Synthetic variations: `generate_variations` / `vary_case` (lowercase,
  uppercase, whitespace, punctuation, typo, prefix). They are deterministic
  per seed, keep expectations and split, skip masked values, are marked
  `needs_review`, and are capped per original.
- Duplicate detection: `find_duplicates` / `drop_duplicates` group exact and
  near (word unigram+bigram Jaccard) duplicates and flag conflicting groups
  (same input, different expectations).
- PII masking: `PIIMasker`, `mask_suite`, `scan_suite`. Covers emails,
  phones, Luhn-valid cards, US SSNs, IPv4, bearer tokens and API keys, and
  whole-word sensitive keys, with a `redact` or salted `hash` strategy.
  Reports carry the location and type, never the value.
- Splits: `assign_splits` places cases by a stable hash of their lineage, so
  cases keep their split as a suite grows and variants follow their original.
- Approval and immutable versions: `SuiteStore.approve` checks review status,
  unmasked PII, and conflicting duplicates. It then writes
  `<store>/<name>/<version>.json` once, with the SHA-256 of the canonical
  suite JSON and an `ApprovalRecord` (approver, time, notes, checks,
  `parent_version`). Identical re-approval is idempotent; different content
  is refused. Every read re-hashes the suite and the whole envelope
  (`record_sha256`) (`get`, `load_suite`, `versions`, `latest`, `verify`). `load_suite` stamps
  `metadata.agenticlens_suite_version` provenance.

### Added — CLI

- `agenticlens suite` command group: `import`, `from-traces`,
  `from-feedback`, `add-case`, `remove-case`, `tag`, `review`, `mask`
  (`--check` exits 7), `dedupe`, `vary`, `split`, `filter`, `summary`,
  `approve` (exit 6 when refused), `versions`, `verify` (exit 6 when a
  version is missing or altered), `export`, and `diff`. Imports and
  conversions mask PII by default (`--no-mask`).

### Added — schemas, examples, docs, CI

- JSON Schemas in `schemas/suites/`: suite version, feedback batch,
  duplicate report, masking report.
- `examples/suite_management_demo.py` builds `support-regression@1.0.0` (15
  cases) from a CSV, production traces, and feedback. It masks,
  de-duplicates, varies, splits, reviews, approves, exports, evaluates, and
  gates the suite, and commits the store and artifacts in `examples/suites/`
  (reproduced by `tests/test_examples_suites.py`).
- CI `regression-suite` job: `suite verify` → `suite export` → `evaluate
  --strict-evidence` → `gate` on the committed store.
- `docs/suite-management.md`. README, roadmap (v0.6 delivered), audit
  follow-up, and AGENTS.md updated.

### Compatibility

- Additive only: no existing API, schema, or CLI behaviour changes. Requires
  `agentic-evals>=0.7.1,<1` as before.

## 0.7.1 - 2026-10-17

### Added

- Native `sidecar.correlation/1` decision readback with exact trace identity,
  idempotency and atomic validation; governance outcomes preserve span/run health.
- Diagnosis schema 1.1 adds `supervision_decision` incident timeline events.

## 0.7.0 - 2026-10-13

Delivers roadmap milestone v0.5 (Advanced Evaluation and Diagnosis).

### Added — diagnosis (`agenticlens.diagnosis`)

- Versioned failure taxonomy (`FailureCategory`, `TAXONOMY_VERSION = "1.0"`):
  14 categories, each with a layer, default severity, attribution weight, and
  next step.
- Deterministic, versioned diagnosis rules: origin failures with propagation
  to failed ancestors and recovery detection (`failed_span`), injected faults
  on spans that did not fail (`injected_fault`), exhausted retries, tool
  loops, handoff loops, stagnation, empty retrieval, cost/token/latency
  budgets, and an incomplete-task fallback. Every diagnosis has a confidence,
  supporting span IDs, span-level evidence, and its `rule_id@version`.
- Faulty-step and faulty-agent attribution: ranked candidates with blame
  shares, per-agent shares, a confidence, and a status (`attributed`,
  `recovered`, `unattributed`, `no_failure`). Recovered failures and later
  consequences are discounted.
- Attribution accuracy on controlled failures: `evaluate_attribution()`,
  `controlled_failure_from_run()` (agentic-chaos `chaos.injected` markers or
  `metadata["expected_faulty_span_id"]`), `load_controlled_failures()`; top-1 /
  top-3 step, agent, and category accuracy with Wilson intervals and a
  calibration gap.
- Incident timelines with the root cause marked, robust (median/MAD) anomaly
  detection against baseline runs, and `explain_run()` /
  `explain_recommendations()` investigation narratives.
- Analysis guardrails: `AnalysisBudget` and `AnalysisGuard` (span, depth,
  diagnosis, time, iteration, and cost limits; stagnation detection).
- `diagnose_run()` assembles a reproducible `DiagnosisReport` (schema
  `1.0`, no wall-clock fields).
- CLI: `diagnose` (`--baseline`, budgets, `--max-spans`, `--max-depth`,
  `--markdown`, `--fail-on-unrecovered` exits 4), `explain`, `trace show
  [--span]`, `trace timeline`, `attribution-accuracy` (`--min-step-accuracy`
  exits 5).

### Added — evaluation

- Trace-aware evaluators registered by name: `tool_trajectory`,
  `agent_goal`, `handoff`, `loop`, `groundedness`, `relevance`,
  `completeness`, `citation`, `safety`. `default_registry()` combines them
  with agentic-evals' built-in scorers; `evaluate` and `evaluate-live` now
  use it, so suites can reference evaluators by name.
- `analyze_scores()` / `ScoreAnalysis`: deterministic and model-based scores
  reported separately, judge cost totals kept apart from agent cost (estimated
  from tokens and pricing when the judge reports none), per-case evaluator
  disagreement, and pairwise agreement. `evaluate --score-analysis PATH`; the
  HTML report gains a "Score analysis" section when judges are present.
- `structured_judge(..., judge_provider=, prompt_version=, prompt_template=)`
  records the judge provider, prompt version, prompt SHA-256, measured
  latency, and the usage the judge reports through `JudgeVerdict.usage`
  (`JudgeUsage`).

### Added — conformance

- Every AIOS issue carries the `rule_id` it violates; reports list a pass /
  fail / not-checked result for each applicable rule in the spec's
  `conformance-rules.json` and a `summary` (status, counts by code and rule).
- `conformance --json` prints the structured report; `--list-versions` lists
  supported AIOS versions. `--version` accepts `0.4`, `0.4-draft`, or `v0.4`;
  an artifact declaring a different `spec_version` is rejected (AIOS-0.5-V03).

### Added — schemas, examples, docs

- `schemas/diagnosis/diagnosis-report.schema.json`,
  `schemas/diagnosis/attribution-accuracy-report.schema.json`,
  `schemas/evaluation/score-analysis.schema.json`.
- `examples/diagnosis_demo.py`, `examples/diagnosis/` (40 controlled-failure
  traces, their builder, and the accuracy report: 40/40 on this synthetic
  corpus), `examples/advanced_evaluation_demo.py`; all reproduced in CI.
- `docs/diagnosis.md`; evaluation and AIOS docs updated.

### Changed

- `to_eval_trace()` / the trace adapter add namespaced span attributes
  (`agenticlens.span_type`, `agenticlens.name`, `agenticlens.agent_name`,
  `agenticlens.status`, `agenticlens.span_id`, `agenticlens.parent_span_id`,
  `agenticlens.input_fingerprint`, `agenticlens.retrieved`) and trace
  metadata (`agenticlens.run_status`, `agenticlens.task_success`). Additive;
  existing keys are never overwritten.
- `ValidationIssue` gains `rule_id`; `ConformanceReport` gains
  `declared_spec_version`, `rules_catalog`, `rules`, and `summary`
  (additive).
- `python -m agenticlens.cli.main` registers every command before running
  (the `__main__` guard moved to the end of the module).

### Fixed (review)

- Handoff round trips (diagnosis rule and `handoff` evaluator) count
  alternating A→B→A sequences in order, so grouped handoffs are not loops.
- `tool_args`-only inputs are fingerprinted canonically, so equal argument
  dicts in a different key order count as the same call.
- Efficiency findings in a diagnosis report respect the analysis budget.
- Narratives for unattributed runs list diagnoses without a root-cause section.
- Judge scores skipped before any call (self-judging) are reported as
  `skipped_scores` and left out of judge cost coverage.

## 0.6.1 - 2026-10-13

Closes the v0.2.x completion gate "every recommendation has resolvable
source-span provenance".

### Changed

- `ModelSwapRecommender` recommendations now identify their step
  (`step_id`, `step_name`, `step_type`), use `optimization_type="model_swap"`
  instead of the generic default, and record `current_model`,
  `suggested_model`, `current_cost`, and `suggested_cost` in `metadata`.
  Previously they named no step, so the engine could only attach unresolved
  `workflow.recommendation` evidence.
- `ChaosImpactRecommender` recommendations now carry the resolved `step_id`
  and `step_type` (by event `step_id`, then by step name only when that name is
  unique in the workflow). Events are grouped by step identity, so same-named
  steps get separate findings. When the step is
  not part of the workflow, the producer's `step_id` is kept. Evidence is one
  `workflow.chaos_event` entry per source event, with the event ID, fault
  type, outcome, timestamp, and message.

### Added

- `tests/test_recommendation_provenance.py`: every default recommender's
  output must resolve to a workflow step and carry evidence with that step's
  span ID.

## 0.6.0 - 2026-10-12

Completes roadmap milestones v0.3 (Evaluation Foundation) and v0.4
(Experiments and Statistical Comparison). Requires `agentic-evals>=0.7.1`.

### Added — evaluation evidence (v0.3)

- Every score names its evaluator and version (`Score.evaluator`,
  `Score.evaluator_version`, stamped by agentic-evals 0.7.1). AgenticLens
  run costs carry `cost_source` (`estimated` unless the run's metadata says
  `measured`), and reports count priced cases per provenance.
- `audit_report()` evidence audit: unversioned evaluators, failed cases with
  no sample or trace ID, incomplete cost, and unspecified cost provenance.
  `agenticlens evaluate --audit PATH` saves it; `--strict-evidence` exits with
  code 3 on blocking issues.
- Structured judge verdicts: `JudgeVerdict` (agree / partially agree /
  disagree, confidence, unsupported claims, missed evidence, rationale) and
  `structured_judge()`, which records the judge and evaluated models and skips
  (or, with `allow_self_judging=True`, flags) a judge grading its own model.
- Judge pass-threshold tuning: `tune_judge_threshold()` and
  `agenticlens calibrate --tune-threshold PATH` (balanced accuracy, or
  agreement for one-class labels).
- Cooldown-protected gate alerts: `notify_gate_breach()` and
  `agenticlens gate --notify-webhook URL --notify-format generic|slack|teams
  --cooldown-minutes N --notify-state PATH` (also `AGENTICLENS_GATE_WEBHOOK`).
  Per-threshold and per-category cooldowns in Python; alert failures never
  change the gate's exit code.
- Concurrent live evaluation: `run_live_suite(..., max_workers=N)` and
  `evaluate-live --max-workers N`; `evaluate-live --html`.
- Python/HTTP same-suite parity regression tests.

### Added — experiments (v0.4)

- Variant `factors` (model, prompt, retrieval, memory, retry_policy, or any
  name), `changed_factors` per comparison, and factor-level summaries.
- `recorded` variant targets that replay saved per-trial samples, so an
  experiment reproduces exactly from committed files.
- Per-case repeated-trial results with unbiased pass@k and pass^k,
  consistency, and flaky-case lists; variant-level pass@k / pass^k.
- Wilson intervals on case pass rates; two-proportion significance tests,
  regressed/improved case lists, and minimum-sample and multi-factor warnings
  on each comparison.
- Recorded randomization (seed and exact execution order), confidence level,
  regression threshold, and `pass_k` on every report.
- Standalone HTML experiment report with a variant x test-case heatmap;
  variant summary and case-matrix CSV exports.
- `agenticlens experiment run --html/--csv/--cases-csv` and
  `agenticlens experiment report SAVED.json` to re-render saved results.
- JSON Schemas for experiment manifests and reports in `schemas/experiments/`.
- Examples: `examples/experiments/` (reproducible four-variant experiment
  with saved reports), `examples/structured_judge_demo.py`,
  `examples/gate_alert_demo.py`; `examples/experiment_runner_demo.py` now
  records factors and writes HTML/CSV.

### Changed

- Experiment manifest and report `schema_version` is `1.1` (additive).
- `calibrate_judge` records the judge's evaluator version and rejects reports
  whose judge scores mix versions; unversioned scores produce a warning.
- The evaluation HTML report labels case outcomes ("CASE RESULT · 2 CASES
  FAILED") instead of "RELEASE STATUS · READY/REVIEW", which implied a gate
  decision. It also shows `evaluator@version`, cost provenance, and missing
  samples.
- Experiment console output splits pass@k / pass^k into its own table.
- Experiment `pass_rate_delta` (and its regression flag) uses case-level pass
  rates, which count crashed trials as failed attempts, matching the case
  pass-rate delta shown in reports.
- Gate-alert cooldown state is keyed per suite (`<suite>::<threshold>`), and
  alert text lists only the breaches being alerted on. Existing unscoped
  state entries are ignored, so each threshold may alert once after upgrade.
- CSV exports prefix formula-like text cells (`=`, `+`, `-`, `@`) with `'`.

### Fixed

- Trace payloads in `EvalTrace` shape that omit `total_latency_ms` were
  treated as AgenticLens `Run` payloads, dropping their trace-level cost.
- `Run`-shaped trace payloads with `Z`-suffixed UTC timestamps failed to
  parse on Python 3.10.

## 0.5.0 - 2026-09-13

### Fixed

- Enforce Draft 2020-12 structured-output constraints and reject invalid schema
  configurations, remote reference resolution, and non-JSON NaN/Infinity.
- Reject duplicate/unknown evaluation samples rather than silently replacing
  evidence or ignoring inputs.
- Keep incomplete span/case/run cost aggregates unavailable and reject incomplete
  report cost gates; explicit zero costs remain valid.
- Respect explicit task outcomes in comparison success metrics.
- Export and re-import a failed run's `error_type` via OTLP instead of
  silently dropping it (the exporter never wrote it as a resource
  attribute, so even a native AgenticLens round-trip lost it).

### Added

- Offline judge calibration API and CLI with versioned human labels, exact case matching, agreement confidence intervals, confusion counts, and trace-linked verdict evidence.
- Standalone HTML dashboard renderer (`agenticlens.reports.render_dashboard_html`/
  `save_dashboard_html`) combining an agent timeline, cost-by-workflow-area
  breakdown, waste findings, a release gate, and a baseline-vs-candidate
  comparison from whichever artifacts are supplied. Wired into `analyze`,
  `inspect`, and `compare` via a new `--html` option, plus a new `dashboard`
  command that composes several already-saved artifacts into one page. No
  external fonts or network requests; renders fully offline.
- OTLP/OpenTelemetry ingestion adapter (`agenticlens.adapters.otlp`, new
  `import-otlp` CLI command) converting OTLP/HTTP JSON trace exports —
  including third-party exports that follow the OpenTelemetry GenAI
  semantic conventions (`gen_ai.*`, with legacy attribute names supported)
  and exports AgenticLens never produced itself — into AgenticLens run
  files. Field mapping prefers AgenticLens's own attributes, falls back to
  GenAI semconv, and never fabricates a value; unrecognized attributes are
  preserved rather than discarded. Zero new dependencies.
- Live OTLP/HTTP receiver and real-time dashboard (`agenticlens.api`, new
  `serve-otlp` CLI command), behind a new optional `agenticlens[api]` extra
  (FastAPI + uvicorn — **a dependency-surface change**, opt-in only, the
  base package still requires neither). Reuses the OTLP adapter's
  conversion and the dashboard renderer's rendering directly. Bounded
  in-memory trace store (default cap 200, FIFO eviction); binds to
  `127.0.0.1` by default and ships with no authentication — documented as
  a stated limitation, not a silent gap. Live refresh is plain polling, not
  websockets/SSE.
- Persistent local trace history: `PersistentTraceStore`
  (`agenticlens.api.store`), a stdlib-`sqlite3`-backed drop-in for the
  in-memory trace store — zero new dependency. `serve-otlp --db PATH` uses
  it instead of memory-only storage, so traces survive a restart. A new
  cross-trace `render_history_html` view (`GET /history` on the receiver,
  and a new offline `agenticlens history` CLI command against a `--db`
  file or a directory of run JSON) shows aggregate tokens/cost/error-rate/
  p95-latency across recent traces instead of one trace at a time; cost
  aggregates note "N of M traces priced" rather than fabricating a total.

### Fixed (evaluation module wiring)

- `agenticlens.evaluation` failed to import `load_dataset`, `save_dataset`,
  `split_dataset`, `summarize_dataset`, `dataset_from_samples`, and
  `dataset_to_samples` from `agenticlens.evaluation.datasets`, breaking every
  CLI command (the whole `agenticlens.cli.main` module failed at import time)
  and the `dataset export-samples` command specifically.

## 0.4.0 - 2026-08-08

### Added

- Markdown trace and comparison reports, including CLI support via
  `agenticlens inspect --save` and `agenticlens compare --format md`.
- Minimum-sample guidance for repeated-run comparison, plus `--min-samples`
  enforcement in the CLI for CI-friendly under-sampling checks.
- First-class `Evidence` objects on findings and recommendations, with
  provenance carried through analysis and reporting.
- Duplicate-context detection, retry attribution, retry outcome
  classification, and next-best-analysis suggestions for structured traces.
- AIOS draft validation and conformance commands in the CLI, including
  `agenticlens validate` and `agenticlens conformance` backed by local
  `ai-operations-spec` draft schemas and semantic checks.
- OTLP/HTTP JSON trace export for structured runs, including optional
  export-on-trace-completion support for configured endpoints.
- Additional deterministic evaluation checks for JSON Schema validation,
  required output fields, required tool arguments, and turn-count thresholds.
- `BusinessRuleEvaluator` and trusted live evaluation targets for Python and
  HTTP workflows via `evaluate-live`.
- Architecture import-layer enforcement tests and a runnable live-evaluation
  example covering structured-output checks.

### Changed

- The finding schema now reflects evidence as structured arrays rather than an
  untyped object, matching shipped runtime artifacts.
- Trace analysis no longer mutates the input run while computing retry
  attribution.
- AIOS schema resolution now uses the non-deprecated `referencing` registry
  path instead of `jsonschema.RefResolver`.
- Documentation, examples, and roadmap details now match the shipped trace,
  comparison, and evaluation feature surface.

## 0.3.0 - 2026-08-05

### Added

- Structured run-and-span tracing with payload redaction, trace inspection, raw metric
  distributions, and versioned trace, finding, and report JSON Schemas.
- A unified evaluation framework for deterministic, semantic, safety, RAG, LLM-as-a-Judge,
  tool-behavior, latency, and cost scoring, with JSON and standalone HTML reports.
- Configurable release gates that enforce evaluation pass rate, score, failed-case,
  latency, and cost thresholds with CI-friendly exit codes.
- Repeated-run baseline/candidate comparison with regression detection and JSON or CSV
  export.
- Agent-aware reporting and multi-agent diagnostics, including handoff-bloat findings
  and reference LangGraph workflows.
- Live model pricing with on-disk caching and bundled fallback data.
- A model-swap simulator that recommends compatible lower-cost models and reports
  estimated dollar savings.
- An interactive product website, expanded architecture and research roadmaps, and
  contributor automation through Make targets and documented CI workflows.

### Changed

- The CLI now includes `inspect`, `compare`, `evaluate`, and `gate` workflows and
  presents agent summaries and token-optimization results in analysis output.
- Recommendation findings now carry richer evidence, confidence, quality-risk, and
  cost-savings information.
- Python 3.14 is now included in the supported and tested version matrix.
- Bundled pricing data is now a fallback behind user overrides and live pricing.

## 0.2.0 - 2026-07-13

### Added

- `chaos_events` schema extension (v1.1) to `Workflow`/`workflow.json`, documented
  in `docs/workflow-schema-spec.md`, so fault-injection tools such as
  [agentic-chaos](https://github.com/DeepAgentLabs/agentic-chaos) can report through
  AgenticLens's existing analysis engine.
- `ChaosImpactRecommender`, registered by default, surfaces resilience findings
  (unhandled failures, silent output degradation) from `chaos_events`.

### Changed

- The recommendation engine's budget-impact pass no longer overwrites the
  severity of recommendations with zero token savings, so non-savings-based
  recommenders like `ChaosImpactRecommender` can set their own severity.

## 0.1.2 - 2026-07-07

### Added

- Budget-impact ranking for recommendations, including dollar-per-run and monthly
  savings projections.
- Recommendation confidence and quality-risk fields for heuristic advice.
- Low-utility RAG chunk recommendation to flag retrieved context that appears
  unlikely to influence the final answer.
- Expanded open-source README with quickstart, CLI usage, cost calculation,
  examples, development workflow, and roadmap.

### Changed

- CLI analysis output now leads with a budget optimization summary.
- Recommendation severity is now based on estimated token and dollar impact.

## 0.1.1 - 2026-07-05

Initial release.

### Added

- Core data models for profiling sessions, steps, and token usage
- Provider abstraction layer with pricing support
- Explicit `profile()` / `step()` instrumentation API
- CLI interface via Typer with `report` and `export` commands
- Rich terminal output for profiling reports
- Recommendation engine framework (rules pending implementation)
- JSON and YAML export support
- pytest-based test suite with coverage reporting
- CI workflow with linting, type checking, and multi-version testing
