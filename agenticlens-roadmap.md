# AgenticLens Product Roadmap

## Correctness follow-up

The four verified audit gaps were fixed in `0.5.0`: structured-output validation
uses Draft 2020-12; duplicate/unknown samples are rejected; incomplete
span/case/run costs remain unavailable; explicit task outcomes override
execution status. Regression evidence:
[correctness tests](tests/test_evaluation_correctness.py). `0.6.0` closes
evaluator-version enforcement (every score names its evaluator and version)
and HTML gate-status semantics (the HTML label now states case outcomes only).
`0.7.0` makes the evaluation trace adapter carry span semantics (type, agent,
status, retrieved context) additively, and keeps judge cost out of agent cost.
Python live-target timeouts remain open.

## Implementation Audit

The [2026-09-11 implementation audit](ROADMAP_AUDIT.md) maps this roadmap to
source and tests. Core v0.2/v0.2.x capabilities exist, but milestone acceptance
still has open evidence and provenance gates. The audit's
[0.6.0 follow-up](ROADMAP_AUDIT.md#060-follow-up-2026-10-12) records v0.3
acceptance and v0.4 delivery evidence, and the
[0.7.0 follow-up](ROADMAP_AUDIT.md#070-follow-up-2026-10-13) records v0.5
delivery evidence, and the
[0.8.0 follow-up](ROADMAP_AUDIT.md#080-follow-up-2026-10-17) records v0.6
delivery evidence, and the
[0.9.0 follow-up](ROADMAP_AUDIT.md#090-follow-up-2026-10-18) records v0.7
delivery evidence, and the
[0.11.0 follow-up](ROADMAP_AUDIT.md#0110-follow-up-2026-10-31) records v0.9
delivery evidence. Later milestones contain partial
building blocks; planned scope is not a claim of completion.

## Release Status

Shipped PyPI releases: `0.1.1` → `0.1.2` → `0.2.0` → `0.3.0` → `0.4.0` →
`0.5.0` → `0.6.0` → `0.6.1` → `0.7.0` → `0.7.1` → `0.8.0` → `0.9.0` →
`0.10.0` → `0.11.0` (current, 2026-10-31) — see [CHANGELOG.md](CHANGELOG.md). The version labels
below are this roadmap's release-plan sequence, not PyPI tags — shipped
`0.4.0` already covers most of planned `v0.2` and `v0.3`, and pulled pieces
forward from `v0.5` and `v1.0`.

- **v0.2** ✅ Delivered in `0.3.0` — Trace and Comparison Foundation
  (hierarchical tracing, cyclic-parent detection, retry attribution,
  regression detection, baseline/candidate comparison, and Markdown reports)
- **v0.2.x** ✅ Delivered in `0.4.0` — Evidence Provenance & Operational
  Intelligence (`Evidence` objects, next-best-analysis guidance,
  import-layer enforcement, OpenTelemetry trace export, and AIOS draft
  validation/conformance CLI are delivered)
- **v0.3** ✅ Delivered in `0.6.0` — Evaluation Foundation (evaluator
  framework, deterministic checks, custom/LLM-judge evaluators with recorded
  versions, structured judge verdicts, release gates with cooldown-protected
  alerts, live targets with Python/HTTP parity, datasets, judge calibration and
  threshold tuning, evidence audits)
- **v0.4** ✅ Delivered in `0.6.0` — Experiments and Statistical Comparison
  (manifests with factors, live or recorded repeated trials, pass@k/pass^k,
  confidence intervals, significance tests, consistency, heatmaps, Pareto, and
  HTML/CSV reports)
- **v0.5** ✅ Delivered in `0.7.0` — Advanced Evaluation and Diagnosis (failure
  taxonomy, deterministic diagnosis rules, faulty-step/agent attribution
  measured on controlled failures, incident timelines, anomaly detection,
  investigation narratives, analysis guardrails, trace-aware evaluators, judge
  cost and prompt versioning, deterministic vs model-based scores with
  evaluator disagreement, rule-cited AIOS conformance summaries)
- **v0.6** ✅ Delivered in `0.8.0` — Test-Suite and Dataset Management
  (CSV/JSON imports, production-trace and user-feedback conversion into
  reviewable cases, suite editors, tags and domain categories, stable
  lineage-aware splits, synthetic variations, duplicate and conflicting-label
  detection, PII masking before storage, review and approval metadata, and
  immutable hash-verified suite versions that CI verifies, exports, and
  evaluates)
- **v0.7** ✅ Delivered in `0.9.0` — ModelFit (task taxonomy, hard
  quality/cost/latency/safety/provider/deployment constraints that fail
  closed, weighted scoring, per-category Pareto frontier and cost-per-success
  ranking, recommendation confidence and explanations, alternatives and
  provider-diverse fallbacks, savings tied to experiment evidence, quality
  risks, and a task-level model matrix)
- **v0.8** ✅ Delivered in `0.10.0` — Advisory Runtime Routing (routing SDK,
  rule/score selection, fail-closed policy constraints, bounded fallback and
  provider failover, confidence thresholds, host escalation handoffs,
  shadow/canary modes, and a local routing journal)
- **v0.9** ✅ Delivered in `0.11.0` — Optimization Intelligence (prompt caching
  and compression, retrieval pruning and reranking, memory summarization, tool
  caching and retry policy, redundant-step and unnecessary-handoff detection,
  quality-cost trade-offs, projected benefit with separate confidence and
  quality risk, accepted/rejected/adopted tracking, and post-adoption outcome
  evaluation)
- **v1.0** 🚧 Planned — Production and Enterprise Readiness (release gates
  partially pulled forward into `v0.3`)

## Purpose

This roadmap defines the planned evolution of AgenticLens from a local workflow
profiler into an open-source runtime intelligence and evaluation framework for
agentic AI systems.

The roadmap is directional. Release scope may change as implementation evidence,
compatibility requirements, and contributor feedback develop. Features are
considered complete only when they are implemented, documented, tested, and
available through a stable Python or CLI interface.

## Product Direction

AgenticLens provides local-first tools to observe, evaluate, compare, optimize,
and govern AI workflows.

The platform is intended to answer:

- What happened during an agent run?
- Where were tokens, latency, and cost consumed?
- Did the agent complete the intended task?
- Which model, prompt, retrieval strategy, or workflow performed best?
- Did a candidate configuration introduce a regression?
- Which execution steps added cost without improving outcomes?
- Is a workflow operating within defined reliability and policy limits?

The primary operating principle is:

> Instrument once, evaluate continuously, and optimize from recorded evidence.

## Product Principles

### Package-first

Core capabilities must remain usable through Python and the CLI without a
hosted service.

### Local-first

Tracing, evaluation, comparison, and reporting must work with local artifacts by
default.

### Framework-neutral

Core models must not depend on one provider, agent framework, orchestration
library, or telemetry backend.

### Evidence-backed

Findings and recommendations must identify the measurements, thresholds, and
trace evidence on which they are based.

### Advisory-first

Early release and control features should report and recommend before they
enforce or modify production behavior.

### Compatible evolution

Schemas and public APIs must use explicit versioning. Additive changes are
preferred where practical.

### Honest measurement

Measured, estimated, projected, and inferred values must be distinguishable in
reports and APIs.

## Cross-Project Dependencies

AgenticLens is intentionally package-first, but several roadmap items need
cross-project coordination before they should be marked complete.

- `ai-operations-spec`
  Provides the normative artifact model and conformance rules for AIOS-aligned
  validation, schema references, and interoperability claims.
- `agentic-sidecar`
  Coordinate with: both projects independently export to Semantica
  (AgenticLens: trace/evidence; Sidecar: decision/governance) and must
  agree on a shared correlation-ID contract linking a trace to the
  decision(s) made against it before either export is considered
  non-experimental. See the Provenance and Governance Export Guidance
  section below and `agentic-sidecar`'s `ROADMAP.md` v0.6 deliverables for
  the other half of this.
- `agentic-chaos`
  Produces resilience/fault evidence that AgenticLens may analyze, summarize,
  or validate as part of cross-tool workflows. Since `0.7.0`, spans marked
  with agentic-chaos's `chaos.injected` / `chaos.fault_type` /
  `chaos.event_id` attributes are diagnosed as injected faults and serve as
  ground truth for attribution accuracy (`agentic-chaos` 0.5.3 adds
  `span_attributes()` to write them). Chaos 0.6.0 reports add a call log
  (`calls`, `calls_dropped`) and `unhandled_error`. `Workflow` loads them
  unchanged and ignores the new fields, and `chaos_events` are analysed as
  before. Chaos's pytest contracts read the same report Lens analyzes. Validated
  in agentic-chaos's sibling-integration CI; no Lens change is needed.
- `deep-agentic-core-mcp`
  Exposes AgenticLens capabilities through MCP and is a useful sibling check
  for CLI/API behavior that is expected to be consumable by hosts and tools.
- `agenticops-control-tower`
  Coordinate with: once Control Tower ships real inventory and control-plane
  surfaces, AgenticLens findings, evaluation summaries, and readiness posture
  should be centrally visible there without turning AgenticLens into a hosted
  dashboard product.

For roadmap items with ecosystem impact, contributors should distinguish:

- `Depends on`: a sibling repo or spec milestone that must exist first.
- `Coordinate with`: sibling repos that should be updated or verified together.
- `Validate in`: the sibling repos or fixtures that should be checked before
  the roadmap item is marked done.

## Definition of Done

A roadmap item is done only when all applicable work is complete:

- implementation is merged and usable through the intended Python API, CLI, or
  artifact surface
- tests or regression fixtures cover the behavior
- user-facing examples and docs are added or updated
- `README.md` and this roadmap are updated when the feature changes user
  expectations or milestone status
- schema/version compatibility is handled explicitly for any public contract
  change
- sibling-project dependencies and coordination checks are recorded for
  ecosystem-facing work
- release metadata (`pyproject.toml`, `src/agenticlens/__init__.py`,
  `CHANGELOG.md`) is updated when the work is part of a release-ready change
  set

## Open-Source Readiness Alongside Feature Delivery

Continue the existing feature sequence: finish remaining v0.3 evaluation work,
then build v0.4 experiments and statistical comparison. This plan accompanies
those milestones without changing shipped feature status.

These are AgenticLens delivery goals informed by AAIF guidance, not a claim of
AAIF acceptance. Track implementation, independent validation, and foundation
admission separately; pending external review does not erase a shipped feature.

### Delivery evidence for each upcoming milestone

- Publish a runnable example with sanitized inputs, expected outputs, package
  versions, and commands that work from a clean installation.
- Link regression tests and passing release checks; document limitations,
  failure behavior, and public API/schema compatibility impact.
- For model-based evaluation, record model/judge configuration, dataset version,
  trial counts, and uncertainty. Distinguish replay of saved results from live
  model calls whose outputs may vary.
- For interoperability, record producer, consumer, artifact version, mapping
  losses, and validation results. Keep normative AIOS rules in
  `ai-operations-spec` and label draft alignment explicitly.
- Update release and security support documentation when supported behavior or
  versions change. Include privacy/redaction checks where captured data or
  outbound integrations change.

### First six months of readiness work

Windows start when maintainers adopt this plan and are planning targets, not
promised release dates. All items remain open until linked evidence is recorded
here or in a linked public tracking issue.

| Window | Feature alignment | Deliverable and acceptance evidence |
| --- | --- | --- |
| Months 1-2 | Remaining v0.3 work | Reproducible calibration and versioned-dataset examples with disagreement, uncertainty, and limitations (delivered: `examples/dataset_and_calibration_demo.py`, `examples/structured_judge_demo.py`); measure instrumentation overhead still open under v0.2. |
| Months 1-2 | Project maintenance | Review licensing and dependency notices; publish maintainer-reviewed governance covering decisions, maintainer admission/removal, disputes, and governance changes; document maintainer responsibilities and verify onboarding and private security reporting. |
| Months 3-4 | v0.4 experiments | Repeatable comparison of at least three variants with saved inputs/results, trial settings, uncertainty, and minimum-sample warnings, matching milestone completion criteria (delivered: `examples/experiments/`, reproduced by `tests/test_examples_evaluation_experiments.py`). |
| Months 3-4 | Artifact interoperability | One producer-to-validation-to-consumer workflow using a documented AIOS draft snapshot; add supported mappings/export behavior if needed, record unsupported fields, and check valid/invalid fixtures against spec-owned rules. Existing validation tooling alone does not prove a native AIOS exporter. |
| Months 5-6 | Independent validation | Seek artifact or workflow reviews from two unaffiliated external teams; record versions, reproduction steps, findings, and resulting issues with permission. Sibling repositories count as integration evidence, not independent adoption. |
| Months 5-6 | Community and adoption | Publish a readiness review covering external usage evidence, contributor/maintainer participation, release cadence, unresolved gaps, and the next six-month priorities. Record missing evidence explicitly. |

### Readiness tracking

- [ ] Governance and maintainer responsibilities published and reviewed.
- [ ] Licensing, dependency notices, onboarding, and security reporting reviewed.
- [ ] Milestone examples reproduce from a clean installation. (v0.4's
      recorded experiment, v0.5's diagnosis, controlled-failure, and
      advanced evaluation examples, and v0.6's suite-management example
      reproduce their saved artifacts in CI; other milestones remain open.)
- [ ] Instrumentation overhead measured with a documented workload/environment.
- [ ] Artifact interoperability demonstrated with versioned fixtures.
- [ ] Independent feedback from two unaffiliated teams recorded and triaged.
- [ ] External usage and contributor participation documented without equating
      downloads, stars, or sibling integrations with production adoption.
- [ ] Six-month readiness review published with evidence links and open gaps.

### AAIF context

AAIF's [submission guidance](https://aaif.io/submit-a-project) emphasizes
implementation quality, community, governance, security, and a 6-12 month roadmap.
Its [September 1, 2026 Sandbox announcement](https://aaif.io/blog/aaif-sandbox-phase)
describes entry for working implementations with early interest or a credible
thesis and an active maintainer. Growth progression includes production use by
two unaffiliated organizations, contributions from two or more organizations
over six months, and a TC-sponsor-approved growth plan.

The [published lifecycle policy](https://github.com/aaif/project-proposals/blob/main/governance/project-lifecycle-policy.md)
reviewed on September 10, 2026 still describes the older Growth/Impact entry
model. Recheck current policy and intake guidance before preparing an application.
Our external review targets do not establish those production-use or contributor
requirements. Formal submission, a charter, and asset contribution are separate
maintainer decisions.

## Current Capabilities

The following capabilities are implemented in the current development line.

### Workflow profiling

- explicit `profile()` and `step()` instrumentation
- OpenAI and Anthropic usage extraction
- prompt, completion, and total-token metrics
- latency, time-to-first-token, and throughput metrics
- per-step, per-agent, and workflow summaries
- JSON, CSV, Markdown, and Jira-oriented exports

### Cost intelligence

- user-defined pricing overrides
- cached live pricing from the LiteLLM community feed
- bundled offline pricing fallback
- stale-cache fallback when pricing refresh fails
- explicit unknown-pricing behavior
- workflow and step cost calculation
- model-swap cost recommendations
- projected per-run and monthly savings

### Optimization analysis

- repeated prompt detection
- excessive retrieval detection
- RAG chunk-utility analysis
- long-history detection
- duplicate tool-call detection
- multi-agent handoff analysis, including handoff-bloat findings
- agent-aware summaries in CLI analysis output
- model-tier cost comparison
- agentic-chaos impact findings

### Research trace foundation

- framework-neutral `Run` and nested `Span` models
- planning, model, memory, retrieval, tool, validation, retry, delegation, and
  final-response span types
- token, latency, cost, status, and error capture
- parent-child trace validation
- opt-in payload capture with recursive redaction
- JSON trace persistence
- trace inspection through the CLI

### Diagnostics and comparison

- memory-share analysis
- retry token, latency, and cost analysis
- deterministic findings with span-level evidence
- repeated-run baseline and candidate groups
- mean, median, P95, standard deviation, and coefficient of variation
- success-rate and cost-per-successful-task reporting
- configurable regression detection
- JSON and CSV comparison reports
- CI-compatible regression exit status

### Evaluation and release gates

- versioned YAML and JSON test suites (`TestSuite`, `TestCase`)
- a unified, provider-neutral evaluator contract (`Evaluator`, `EvaluationContext`,
  `Score`, `EvaluatorRegistry`)
- built-in deterministic checks: exact match, required-substring match, required
  and forbidden tool calls, latency threshold, cost threshold
- custom evaluators via `CallableEvaluator`, and model-based judges via
  `LLMJudgeEvaluator`, sharing one normalized score contract
- evaluation against recorded samples and traces, plus synchronous live Python
  and HTTP targets; dedicated HTTP parity regression coverage remains open
- JSON and standalone HTML evaluation reports
- configurable release gates on pass rate, average score, failed-case count,
  average latency, and total cost, with CI-friendly exit codes
- `evaluate`, `evaluate-live`, and `gate` CLI commands
- versioned evaluation dataset workflows via `agenticlens dataset ...`
- judge calibration reports and pass-threshold tuning via `calibrate`
- evaluator name and version on every score, measured/estimated cost
  provenance, and evidence audits via `evaluate --audit/--strict-evidence`
- structured judge verdicts (`JudgeVerdict`, `structured_judge`) with a
  self-confirmation guard
- cooldown-protected webhook alerts on `gate` failures (generic, Slack, Teams)
- concurrent live evaluation (`--max-workers`)
- trace-aware evaluators: tool trajectory, agent goal, handoff, loop,
  groundedness, relevance, completeness, citation, and safety (output and
  tool arguments)
- judge provider, prompt version/hash, latency, tokens, and cost on judge
  scores; deterministic vs model-based score analysis with evaluator
  disagreement (`evaluate --score-analysis`)

### Experiments

- experiment manifests with variant factors (model, prompt, retrieval, memory,
  retry policy), live Python/HTTP or recorded-replay targets, and seeded
  execution order
- per-case repeated trials with pass@k, pass^k, consistency, and flaky cases
- Wilson and normal-approximation confidence intervals, two-proportion
  significance tests, regressed/improved case lists, and minimum-sample warnings
- factor-level summaries and a Pareto frontier
- HTML report with a variant x test-case heatmap; variant and case-matrix CSV
  exports; `experiment report` re-renders saved results
- a deterministic, offline LangGraph reference workflow demonstrating tracing,
  evaluation, and release-gate output together

### Diagnosis and failure attribution

- versioned failure taxonomy (14 categories with layer, severity, attribution
  weight, and next step)
- deterministic, versioned diagnosis rules: origin failures with propagation
  and recovery, injected faults, exhausted retries, tool and handoff loops,
  stagnation, empty retrieval, budgets, and an incomplete-task fallback
- faulty-step and faulty-agent attribution with ranked candidates, per-agent
  blame shares, and confidence
- attribution accuracy on controlled failures (agentic-chaos markers or
  recorded ground truth) with Wilson intervals and a calibration gap
- incident timeline reconstruction with the root cause marked
- robust (median/MAD) anomaly detection against baseline runs
- analysis guardrails: span, depth, diagnosis, time, iteration, and cost caps
  with stagnation detection
- investigation narratives for runs and for workflow recommendations
- `diagnose`, `explain`, `trace show`, `trace timeline`, and
  `attribution-accuracy` CLI commands

### Test-suite and dataset management

- suite imports from CSV (unknown columns rejected), JSON, JSON Lines, and YAML
- production-trace conversion: successful runs become cases expecting their
  tool trajectory and latency/cost within a margin; failed runs are skipped
  with a reason
- user-feedback conversion: corrected or confirmed outputs become expected
  outputs; uncorrected negative feedback is skipped with a reason
- suite editors (add, update, remove, tag, domain, review, merge, filter, diff)
- case lineage, review status, domain, and split recorded in case metadata
- deterministic synthetic input variations that keep their parent's split
- exact, near, and conflicting duplicate detection
- PII masking (`redact` or salted `hash`) before storage, with value-free reports
- stable, lineage-aware train/validation/test splits
- approval checks (review, PII, conflicting duplicates) and an immutable,
  hash-verified suite store with `verify`, `export`, `versions`, and `diff`

### Model selection (ModelFit)

- task taxonomy: categories select cases by tag, `metadata.domain`, or case
  ID, or are derived from case tags; an `all` category covers every case
- hard constraints per category (with default inheritance and explicit
  removal): pass rate and its Wilson lower bound, cost per case and per
  success, mean and p95 latency, consistency, suite-wide safety pass rate,
  provider allow/block lists, deployment allow-list, required capabilities;
  unverifiable limits are violations
- weighted scoring of feasible candidates (quality, cost, latency,
  reliability), Pareto frontier, and cost-per-success ranking per category
- recommendation confidence with stated reasons, explanations citing measured
  values, alternatives, and provider-diverse fallbacks
- savings against a reference variant on the same cases, with attempts, case
  IDs, and the experiment report's SHA-256; quality regressions, regressed,
  flaky, and safety-failed cases, thin evidence, and failed trials reported
  as separate risks
- task-level model matrix (JSON, CSV, Markdown) and `agenticlens modelfit`
  `recommend`, `matrix`, and `taxonomy` commands

### Optimization intelligence

- trace-level rules over many runs: prompt caching (recorded prefix hashes,
  provider cache hits skipped) and compression, retrieval top-k pruning that
  never cuts a used chunk and reranking upper bounds, memory summarization and
  retention, tool-result caching that skips side-effecting tools, non-retryable
  error types, redundant steps, and handoffs that add no work
- quality-cost trade-offs between experiment variants: Wilson intervals, Pareto
  status, success and cost deltas, and significance against a baseline
- every opportunity cites run and span evidence and the thresholds used, and
  keeps projected benefit (with its basis; cost unavailable when incomplete),
  graded confidence with reasons, and quality risks separate
- an append-only decision ledger bound to the report hash, with enforced
  accepted/rejected/adopted/reverted transitions
- post-adoption outcome evaluation reporting projected and observed per-run
  tokens, cost, latency, and success side by side, with a rule re-check
- `agenticlens optimize analyze|decide|status|outcome` (exit 9 with
  `--fail-on-regression`)

### Artifact contracts

- versioned trace schema
- versioned finding schema
- versioned comparison-report schema
- experiment manifest/report, diagnosis report, attribution-accuracy report,
  and score-analysis schemas
- suite-version, feedback-batch, duplicate-report, and masking-report schemas
- ModelFit config and report schemas
- schema inclusion in wheel distributions

## Capability Architecture

```text
Application and agent runtimes
            |
            v
Instrumentation
├── workflow profiler
└── structured trace API
            |
            v
Local artifacts and schemas
            |
     +------+------+----------------+
     |             |                |
     v             v                v
Diagnostics    Evaluation      Comparison
     |             |                |
     +-------------+----------------+
                   |
                   v
          Recommendations and gates
                   |
          +--------+---------+
          |                  |
          v                  v
        CLI/API        Optional dashboard
```

## Release Plan

## v0.2 — Trace and Comparison Foundation

### Objective

Establish reproducible execution traces, cost intelligence, deterministic
diagnostics, and baseline comparison.

### Delivered

- hierarchical run and span tracing
- raw token, latency, cost, retry, and tool metrics
- payload redaction
- memory and retry findings
- cyclic parent detection
- retry attribution and retry outcome classification
- duplicated-context detection
- repeated-run statistics
- baseline-versus-candidate regression detection
- minimum-sample guidance in comparison reports
- trace inspection and comparison CLI commands
- JSON, CSV, and Markdown comparison exports
- Markdown trace reports
- versioned research schemas

### Remaining work

- measure instrumentation overhead

### Completion criteria

- all trace artifacts validate against published schemas
- existing profiler APIs remain compatible
- comparison results reproduce from saved traces
- privacy defaults and redaction behavior are documented
- [ ] performance overhead is measured

## v0.2.x — Evidence Provenance & Operational Intelligence

### Objective

Make every finding and recommendation traceable to its source evidence, and add
intelligent guidance for what analysis to run next.

### Delivered

- first-class `Evidence` object on findings and recommendations (source
  step/span, timestamp, confidence, derived reasoning chain)
- "next best analysis" recommendations — suggest what the user should inspect
  next based on workflow shape and current findings
- import-layer enforcement in CI — prevent architectural drift as the package
  grows (e.g., `exporters/` must not import from `cli/`)
- OpenTelemetry trace export — let agenticlens traces flow into
  Grafana/Jaeger/OTel-native systems via OTLP/HTTP JSON export
- AIOS draft validation and conformance tooling in the CLI — commands such as
  `agenticlens validate workflow.json` and
  `agenticlens conformance --version 0.4 workflow.json`, with normative rules,
  fixtures, and expected behavior defined by `ai-operations-spec`, and
  draft-alignment reporting that distinguishes AIOS-defined pass/fail rules
  from AgenticLens-specific presentation

### Completion criteria

- [x] every recommendation has resolvable source-span provenance — closed in
      `0.6.1`: all default recommenders (including model swap and chaos
      impact) now set `step_id`/`step_type`, and chaos-impact evidence cites
      each source `chaos_events` entry. The engine's generic
      `workflow.recommendation` evidence remains only as an explicitly labeled
      fallback for third-party recommenders that do not name a step.
- [x] next-step suggestions are generated from current findings
- [x] structured trace() runs emit OTLP spans when configured
- [x] CI rejects forbidden cross-module imports
- [x] conformance reports clearly distinguish AIOS-defined pass/fail rules from
      AgenticLens-specific presentation and CLI behavior

## v0.3 — Evaluation Foundation

### Objective

Evaluate task outcomes and execution requirements using versioned, reusable test
suites.

### Delivered

- `TestCase` and `TestSuite` models with versioned YAML/JSON loading
- `Evaluator`, `EvaluationContext`, `Score`, and `EvaluatorRegistry` interfaces
- built-in deterministic checks: exact match, required-substring match,
  required/forbidden tools, JSON Schema Draft 2020-12 validation, required fields,
  required tool arguments, turn-count threshold, latency threshold, and cost
  threshold
- `CallableEvaluator` for application-supplied rules (including semantic,
  safety, or RAG logic), `BusinessRuleEvaluator`, and `LLMJudgeEvaluator`
  for application-supplied judge calls; these are extension points, not a
  built-in semantic/safety/RAG evaluator suite
- JSON and standalone HTML evaluation reports (HTML in place of the
  originally planned Markdown report)
- configurable release gates (pass rate, average score, failed cases,
  latency, cost) with CI-friendly exit codes, via the `evaluate` and `gate`
  CLI commands
- live Python and HTTP evaluation targets via `evaluate-live`
- versioned evaluation datasets, deterministic dataset splitting, sample export,
  and dataset summary CLI workflows via `agenticlens dataset ...`
- judge calibration reports with a Wilson-interval agreement rate and
  confusion counts via `calibrate`
- a deterministic, offline LangGraph reference workflow demonstrating the
  full trace-to-evaluation-to-gate path

- offline judge/reference verdict agreement via the Python API and calibrate
  CLI, with versioned labels, exact case matching, 95% Wilson agreement
  intervals, confusion counts, and trace-linked cases (`0.5.0`)

### Delivered in `0.6.0`

- `Score.evaluator` and `Score.evaluator_version` on every score (from
  `agentic-evals` 0.7.1); built-in checks are attributed to
  `agentic_evals.builtin` at its version; calibration records the judge
  version and rejects mixed-version runs
- measured/estimated cost provenance per case, priced-case coverage per
  report, and `sample_available` for missing samples
- `audit_report()` and `evaluate --audit/--strict-evidence`
- Python/HTTP same-suite parity regression tests, and concurrent live
  evaluation via `max_workers`
- structured judge verdicts: `JudgeVerdict` (agree / partially agree /
  disagree, confidence, unsupported claims, missed evidence) via
  `structured_judge()`, which skips or flags a judge grading its own model
- judge pass-threshold tuning (`tune_judge_threshold`, `calibrate --tune-threshold`)
- cooldown-protected webhook notifications on `gate` breaches
  (`notify_gate_breach`, `gate --notify-webhook`), generic/Slack/Teams payloads,
  per-threshold and per-category cooldowns
- the HTML report labels case outcomes, not a release decision

This pulled forward parts of the semantic, safety, RAG, and LLM-judge scoring
originally planned for [v0.5](#v05--advanced-evaluation-and-diagnosis), and
part of the release-gate concept originally planned for
[v1.0](#v10--production-and-enterprise-readiness), via the shared evaluator
contract rather than as separate subsystems.

### Follow-on work

The `v0.3` evaluation foundation is complete. Remaining follow-on
enhancements for later milestones:

- built-in provider clients for LLM-as-a-Judge calls (applications currently
  supply the model call themselves)
- async evaluator APIs (live targets already run concurrently on threads)
- probability calibration of judge scores beyond verdict agreement and
  threshold tuning
- dataset lifecycle management (immutable snapshots, approvals) under v0.6
- automatic framework event adapters beyond the LangGraph reference demo
- enforced timeouts for Python live targets

### Completion criteria

- [x] every score identifies its evaluator and version (`Score.evaluator`,
      `Score.evaluator_version`; unversioned evaluators fail
      `evaluate --strict-evidence`)
- [x] reports preserve measured/estimated provenance and cost completeness
      (`cost_source`, `priced_cases`, `cost_sources`; incomplete totals stay
      unavailable)
- [x] failed cases retain sufficient trace-level evidence (trace IDs on every
      sampled case; missing samples flagged with `sample_available=False`;
      the evidence audit blocks untraceable failures)
- [x] verify Python/HTTP same-suite parity with dedicated regression tests
      (`tests/test_live_parity.py`)

## v0.4 — Experiments and Statistical Comparison

### Objective

Compare models and agent configurations against the same test suite with
repeated trials.

### Planned deliverables

- experiment and variant manifests
- repeated trials per test case
- prompt, model, retrieval, memory, and retry-policy comparison
- pass@k and pass^k
- confidence intervals
- consistency and stability summaries
- baseline regression analysis
- test-level score heatmaps
- Pareto analysis
- HTML and CSV reports

### Completion criteria

- [x] at least three variants can be compared in one experiment
- [x] trial counts and randomization settings are recorded (seed and exact
      execution order in `ExperimentReport.randomization`)
- [x] regression reports include minimum-sample warnings (report-level and
      per-comparison, driven by `minimum_trials`)
- [x] quality, cost, latency, and reliability are shown together (console,
      HTML, and CSV)

### Delivered in `0.6.0`

- experiment and variant manifests with `factors`, `pass_k`,
  `minimum_trials`, and `max_workers`; live Python/HTTP or `recorded` replay
  targets; JSON Schemas in `schemas/experiments/`
- per-case repeated trials with unbiased pass@k and pass^k, consistency, and
  flaky-case lists
- prompt, model, retrieval, memory, and retry-policy comparison through
  `changed_factors` and factor-level summaries
- Wilson intervals for case pass rates and normal intervals for per-trial
  metrics; two-proportion significance tests against the baseline
- baseline regression analysis with regressed and improved case lists
- test-level score heatmaps and Pareto analysis
- HTML and CSV reports (`experiment run --html/--csv/--cases-csv`,
  `experiment report`)
- a reproducible four-variant example in `examples/experiments/`

Known limits: intervals and p-values treat case attempts as independent; no
multiple-comparison correction; live trials run sequentially.

## v0.5 — Advanced Evaluation and Diagnosis

### Objective

Evaluate semantic quality and execution trajectories, then attribute failures to
recorded evidence.

### Planned deliverables

- LLM-as-a-Judge interface
- judge prompt and model versioning
- groundedness, relevance, completeness, and citation evaluators
- tool-trajectory and agent-goal evaluators
- handoff and loop evaluators
- safety evaluators
- evaluator calibration reports
- failure taxonomy
- deterministic diagnosis rules
- anomaly detection
- faulty-step and faulty-agent attribution
- incident timeline reconstruction
- investigation-style narratives on top of recommendations — root-cause
  explanations of waste, retries, handoff bloat, or tool inefficiency
- richer CLI subcommands for inspection (`inspect`, `compare`, `trace show`,
  `report explain`)
- richer conformance commands and reporting (`conformance`, spec-version
  selection, structured pass/fail summaries)
- analysis guardrails (budget limits, recursion-depth caps, stagnation
  detection for automated analyzers)

### Delivered in `0.7.0`

- LLM-as-a-Judge interface: `structured_judge()` / `LLMJudgeEvaluator`
  (application-supplied model call) now record judge provider, prompt
  version, prompt SHA-256, measured latency, and reported usage and cost
  (`JudgeVerdict.usage`)
- trace-aware evaluators in `agenticlens.evaluation` registered by name for
  `evaluate`/`evaluate-live`: `tool_trajectory`, `agent_goal`, `handoff`,
  `loop`, `groundedness`, `relevance`, `completeness`, `citation`, `safety`
  (groundedness, relevance, and completeness are lexical heuristics)
- evaluator calibration reports (delivered in `0.5.0`/`0.6.0`)
- `agenticlens.diagnosis`: failure taxonomy v1.0, deterministic diagnosis
  rules, robust anomaly detection against baselines, faulty-step and
  faulty-agent attribution, incident timelines, investigation narratives
  (`explain_run`, `explain_recommendations`), and `AnalysisBudget` /
  `AnalysisGuard` guardrails
- CLI: `diagnose`, `explain` (shipped instead of `report explain`, because
  `report` is an existing command), `trace show [--span]`, `trace timeline`,
  `attribution-accuracy`; `evaluate --score-analysis`
- conformance: AIOS rule IDs on every issue, per-rule pass / fail /
  not-checked results from the spec's `conformance-rules.json`, a structured
  summary, `--json`, `--list-versions`, and declared-version routing
  (AIOS-0.5-V03)
- JSON Schemas: `schemas/diagnosis/` and
  `schemas/evaluation/score-analysis.schema.json`
- examples: `examples/diagnosis_demo.py`, `examples/diagnosis/` (40
  controlled failures, builder, accuracy report),
  `examples/advanced_evaluation_demo.py`; all reproduced in CI

### Completion criteria

- [x] deterministic and model-based scores are reported separately
      (`analyze_scores`, CLI, HTML report)
- [x] judge cost is recorded (per score and per evaluator, kept separate from
      agent cost; estimated from tokens and pricing when not reported)
- [x] evaluator disagreement is visible (per-case disagreements and pairwise
      agreement rates)
- [x] diagnoses include confidence and supporting spans (every diagnosis has
      a confidence, span IDs, and span-level evidence)
- [x] attribution accuracy is evaluated on controlled failures
      (`evaluate_attribution`, `attribution-accuracy`; 40/40 on the bundled
      synthetic corpus, 95% Wilson interval 91.2%–100%)

Known limits: the controlled-failure corpus is synthetic and written alongside
the rules, so it is not independent evidence; attribution shares are
rule-weighted blame, not calibrated probabilities; lexical evaluators do not
judge meaning; anomaly detection applies no multiple-comparison correction.

### Follow-on work

- independent controlled-failure corpora (agentic-chaos runs, external teams)
- built-in judge provider clients and judge-score probability calibration
- semantic (embedding or judge-based) groundedness as an optional evaluator

## v0.6 — Test-Suite and Dataset Management

### Objective

Support the creation, review, versioning, and reuse of evaluation datasets.

### Planned deliverables

- test-case and suite editors
- immutable suite versions
- CSV and JSON imports
- production trace conversion
- user-feedback conversion
- synthetic variation generation
- tags and domain categories
- train, validation, and test splits
- duplicate detection
- PII masking
- approval metadata

### Delivered in `0.8.0`

- test-case and suite editors: `agenticlens.suites` (`add_case`,
  `update_case`, `remove_cases`, `tag_cases`, `review_cases`, `merge_suites`,
  `filter_suite`, `diff_suites`) and `agenticlens suite add-case`,
  `remove-case`, `tag`, `review`, `filter`, `diff`, `summary`
- immutable suite versions: `SuiteStore.approve()` / `suite approve` writes
  `<store>/<name>/<version>.json` once (exclusive create) with the SHA-256 of
  the suite's canonical JSON; identical re-approval is idempotent, different
  content is refused, and every read re-hashes (`suite verify`, exit 6)
- CSV and JSON imports: `import_csv`, `import_json` (JSON, JSON Lines, YAML),
  `suite import`
- production trace conversion: `case_from_run`, `cases_from_runs`,
  `suite from-traces`
- user-feedback conversion: `FeedbackRecord`, `cases_from_feedback`,
  `suite from-feedback` (missing inputs filled from the referenced run)
- synthetic variation generation: `generate_variations`, `suite vary`
  (lowercase, uppercase, whitespace, punctuation, typo, prefix)
- tags and domain categories: case `tags` and `metadata.domain`, with
  filtering and summaries
- train, validation, and test splits: `assign_splits`, `suite split`
- duplicate detection: `find_duplicates`, `drop_duplicates`, `suite dedupe`
- PII masking: `PIIMasker`, `mask_suite`, `scan_suite`, `suite mask [--check]`
  (exit 7)
- approval metadata: `ApprovalRecord` (approver, time, notes, recorded
  checks) and per-case `review_status` / `reviewed_by` / `review_notes`
- JSON Schemas: `schemas/suites/`
- example: `examples/suite_management_demo.py` with its committed store and
  artifacts, reproduced by `tests/test_examples_suites.py`; CI's
  `regression-suite` job verifies, exports, evaluates, and gates it

### Completion criteria

- [x] traces can be converted into reviewable test cases (converted cases are
      `needs_review` and record trace and run IDs; skipped runs are reported
      with a reason)
- [x] approved suite versions are immutable (write-once store, content hash
      re-verified on every read, conflicting re-approval refused)
- [x] regression suites can run in CI (`suite verify` → `suite export` →
      `evaluate`/`evaluate-live` → `gate`, exercised by this repository's CI)
- [x] sensitive fields can be masked before storage (masking is on by default
      for every import and conversion, and approval refuses unmasked PII)

Known limits: PII detection is pattern- and key-based and misses names, free-text
street addresses, and locale-specific identifiers; synthetic variations are
surface perturbations, not paraphrases; duplicate detection is lexical and
pairwise; approval records an approver name but does not authenticate it; the
store is local files, not a multi-user registry.

### Follow-on work

- semantic (embedding or judge-based) duplicate detection and paraphrase
  variations as optional extensions
- an interactive review surface (the CLI and Python API are the editors today)
- signed approvals and a shared registry, tracked under v1.0 audit logs and
  model and prompt registries

## v0.7 — ModelFit

### Objective

Recommend models for defined task categories under quality, cost, latency,
safety, provider, and deployment constraints.

### Planned deliverables

- task taxonomy
- constraint configuration
- weighted scoring
- Pareto frontier
- cost-per-success ranking
- recommendation confidence
- recommendation explanation
- alternative and fallback models
- task-level model matrix

### Delivered in `0.9.0`

- task taxonomy: `TaskCategory` (tags, domains, case IDs), derived per-tag
  categories, the `all` category, and `agenticlens modelfit taxonomy`
- constraint configuration: `ModelConstraints` defaults with per-category
  overrides (`ModelConstraints.merged`), loaded from YAML or JSON with
  `load_modelfit_config`
- weighted scoring: `ScoringWeights` (quality, cost, latency, reliability),
  with per-category weights
- Pareto frontier: `pareto_frontier` over pass rate, cost per success, and
  latency, per category
- cost-per-success ranking: `cost_per_success_ranking`, per category
- recommendation confidence: `high`/`medium`/`low` with reasons (evidence
  volume, close and non-significant runner-up, interval below the minimum,
  incomplete cost, a high-severity quality or safety trade-off)
- recommendation explanation: per-category lines citing measured pass rates,
  intervals, costs, latency, scores, and every rejection reason
- alternative and fallback models: ranked alternatives and a fallback on a
  different provider when one is feasible
- task-level model matrix: `ModelFitReport.matrix`, `render_matrix_csv`,
  `render_markdown`, `agenticlens modelfit matrix`
- `recommend_models` / `agenticlens modelfit recommend` (exit 8 with
  `--fail-on-unfit` or `--fail-on-low-confidence`)
- JSON Schemas: `schemas/modelfit/`
- example: `examples/modelfit_demo.py` with a recorded four-model experiment
  and committed artifacts, reproduced by `tests/test_examples_modelfit.py`;
  CI's `modelfit` job replays the experiment and requires a feasible model
  for every category

### Completion criteria

- [x] recommendations are generated by task category (one `CategoryResult`
      per taxonomy category, plus `all`)
- [x] hard constraints are enforced (infeasible candidates are never
      recommended; unverifiable limits are violations; a category without a
      feasible candidate reports `no_feasible_model`)
- [x] savings estimates are tied to experiment evidence (same cases as the
      reference, attempts and case IDs recorded, source report SHA-256, and
      `available: false` when cost evidence is incomplete)
- [x] quality risks and alternatives are reported (regressions with
      significance, regressed, flaky, and safety-failed cases, thin evidence,
      failed trials, alternatives, fallbacks)

Known limits: recommendations are only as representative as the suite and
trials; costs are the experiment's recorded costs; monthly savings assume the
production mix matches the category's cases; provider, deployment, and
capability facts are declared, not verified; intervals and significance tests
treat case attempts as independent; ModelFit recommends and does not route.

### Follow-on work

- price-sheet re-costing of recorded token usage, so savings track price
  changes without re-running the experiment
- confidence from bootstrap resampling across cases rather than pooled
  attempts
- feeding recommendations and fallbacks into v0.8 advisory runtime routing

## v0.8 — Advisory Runtime Routing

Implemented in package **0.10.0**. See [routing guide](docs/routing.md),
[offline example](examples/routing_demo.py), `tests/test_routing.py` and
`tests/test_examples_routing.py`. Python provides bounded callback execution;
CLI/MCP only select and explain. Human escalation hands off to the host;
local journals are not enterprise governance logs. Shadow metrics measure
explicitly executed callback pairs. Completion criteria below are covered by
the offline acceptance tests; real-provider production validation is separate.

### Objective

Use evaluation evidence to recommend or select models at runtime with complete
decision records.

### Planned deliverables

- routing SDK
- rule-based and score-based routing
- policy-aware routing
- fallback chains
- provider failover
- confidence thresholds
- human escalation
- shadow and canary modes
- routing audit log

### Completion criteria

- routing decisions are explainable
- fallback behavior is tested
- shadow-mode performance is measurable
- policy violations can be blocked when enforcement is enabled

## v0.9 — Optimization Intelligence

### Objective

Generate evidence-backed recommendations across prompts, retrieval, memory,
tools, models, and multi-agent workflows.

### Planned deliverables

- prompt compression and caching recommendations
- retrieval and reranking recommendations
- memory retention and summarization recommendations
- tool caching and retry recommendations
- redundant-step and unnecessary-handoff detection
- quality-cost trade-off analysis
- projected benefit, confidence, and risk
- accepted and rejected recommendation tracking

### Delivered in `0.11.0`

- prompt compression and caching: `PromptCompressionRule` (input-heavy model
  calls; reduction is a configured target, so confidence is capped at medium)
  and `PromptCachingRule` (repeated `prompt.prefix_sha256` prefixes without a
  provider cache hit, priced with the cached-read ratio)
- retrieval and reranking: `RetrievalRule` lowers top-k only to the deepest
  chunk any observed answer used, and reports reranking as a perfect-reranker
  upper bound
- memory retention and summarization: `MemoryRule` (memory-read share and
  token budget, with growth detection that adds a retention window)
- tool caching and retry: `ToolCachingRule` (identical successful calls;
  side-effecting and non-idempotent tools are never cached) and
  `RetryPolicyRule` (error types no observed retry recovered)
- redundant-step and unnecessary-handoff detection: `RedundantStepRule` (same
  input and output in one run) and `UnnecessaryHandoffRule` (receiver did no
  work or echoed its input)
- quality-cost trade-off analysis: `analyze_tradeoffs` and
  `QualityCostTradeoffRule` over measured variant runs
- projected benefit, confidence, and risk: `ProjectedBenefit` with a stated
  basis, graded confidence with reasons, and separate `QualityRisk`s
- accepted and rejected recommendation tracking: `RecommendationLedger` and
  `agenticlens optimize decide/status`
- outcome evaluation: `evaluate_outcome` and `agenticlens optimize outcome`
- JSON Schemas: `schemas/optimization/`
- example: `examples/optimization_demo.py` with recorded before/after traces
  and committed artifacts, reproduced by `tests/test_examples_optimization.py`;
  CI's `optimization` job records an adoption and runs
  `optimize outcome --fail-on-regression`

### Completion criteria

- [x] recommendations cite measured evidence (run IDs, span IDs, measurements,
      and thresholds on every opportunity; spans without a signal are skipped)
- [x] expected benefit and quality risk are separated (`benefit` and `risks`
      are distinct fields and never netted)
- [x] projected and observed outcomes are reported independently (the
      projection is copied unchanged beside observed per-run deltas)
- [x] recommendation outcomes can be evaluated after adoption (ledger status,
      rule re-check, realized ratio, and `quality_regressed` with exit 9)

Known limits: projections assume future traffic resembles the analysed traces;
compression and reranking benefits are assumptions until measured;
prompt-caching cost is pro-rated by token share; outcome evaluation compares
two traffic windows, not a controlled experiment; recommendations are advisory.

### Follow-on work

- price-sheet re-costing of projected and observed savings
- outcome evaluation over routing canary cohorts instead of time windows
- measured compression and reranking reductions from experiment variants

## v1.0 — Production and Enterprise Readiness

### Objective

Provide stable contracts, policy controls, audit evidence, and supported
deployment options.

### Planned deliverables

- stable public APIs and schemas
- organizations and projects
- authentication and role-based access controls
- audit logs
- model and prompt registries
- policy-as-code
- retention and PII controls
- release gates
- compliance exports
- private evaluator support
- Kubernetes and Helm deployment options

### Completion criteria

- public compatibility policy is published
- upgrade and migration paths are documented
- governance decisions produce audit evidence
- release gates are reproducible
- supported deployment modes pass security review

## Ecosystem Integrations

Integrations will be introduced after the trace and evaluation contracts are
stable enough to map framework behavior consistently.

A deterministic LangGraph example demonstrates tracing, evaluation, and
release-gate output together (see [v0.3](#v03--evaluation-foundation)), but
this is a reference demo, not a first-class, maintained integration package.

Planned targets include:

- LangGraph
- OpenAI Agents SDK
- CrewAI
- AutoGen
- Semantic Kernel
- LlamaIndex
- Haystack
- HTTP agents
- MCP-hosted agents
- OpenInference
- OpenTelemetry and OTLP
- Semantica, as a provenance- and audit-oriented export surface

Integration packages must document coverage and any framework behavior that
cannot be represented in the core schema.

### Provenance and Governance Export Guidance

AgenticLens owns trace/evidence export — what ran, what it cost, why it
behaved that way. It does not own decision governance: `agentic-sidecar`
owns the decision/governance side of that same Semantica export (allow,
block, escalate, and why), so the two exports must agree on a shared
compatibility shape — a common ID/correlation convention linking a trace to
the decision(s) made against it — rather than each project inventing its
own. This is tracked as a real coordination item, not just prose intent:
see the `agentic-sidecar` entry under [Cross-Project
Dependencies](#cross-project-dependencies) near the top of this document,
and `agentic-sidecar`'s own `ROADMAP.md` (Cross-Project Dependencies and
v0.6 deliverables), where the correlation-ID contract is defined,
versioned, and tested before either project's Semantica export is
considered non-experimental.

- do not turn AgenticLens into a knowledge-graph or policy-engine runtime
- do add provenance-aware evidence fields and lineage-friendly export shapes
- do consider optional PROV-O, RDF, or JSON-LD export targets once the trace
  and evaluation schemas are stable enough, with Semantica as one such
  target
- do keep any external audit or governance integration optional and
  artifact-oriented rather than a runtime dependency

## Success Measures

### Developer experience

- time required to instrument a representative workflow
- percentage of runs that produce valid artifacts
- reproducibility of local and CI reports
- compatibility across supported Python versions

### Evaluation quality

- evaluator agreement and calibration
- regression-detection precision and recall
- repeated-run stability
- trace coverage for failed cases

### Operational value

- cost per successful task
- reduction in avoidable tokens and retries
- improvement in P95 latency
- reduction in undiagnosed failures
- time required to identify the responsible step

## Early Non-Goals

The following are not near-term core objectives:

- autonomous production prompt rewriting
- automatic production model replacement
- live traffic shifting
- a general-purpose infrastructure monitoring platform
- a full SOC or SIEM replacement
- a full deployment orchestrator
- a universal score intended to summarize every agent quality dimension
- a hosted multi-tenant service as a requirement for core functionality

## Documentation Policy

Public documentation must:

- describe implemented and planned capabilities separately
- use stable product terminology
- avoid unsupported performance or quality claims
- identify experimental APIs
- state limitations and required operator judgment
- include runnable examples where practical
- remain consistent with the current code and schemas

The supporting research plan is maintained in
`AgenticLens_Research_and_Development_Roadmap.md`. Research metrics described
there remain experimental until implemented and validated.

## Verifiable execution evidence (planned, v1.0 readiness)

Added 2026-10-11. Existing traces/source references provide traceability, not a
tamper-evident execution ledger. Extend production readiness; correlation depends
on Sidecar v0.7–v0.8 lifecycle work.

- [ ] Correlate proposed, allowed, denied, dispatched and completed actions with
      run/span/decision IDs, actor, policy version, approvals and actual outcomes.
      Preserve producer attribution; missing evidence must not imply success.
- [ ] Capture and export execution evidence in versioned AI Operations Specification
      format, using spec-owned schemas and semantic checks. Declare the supported
      draft/version, mappings, unsupported fields and any capture losses; validation
      tooling alone does not establish a native exporter.
- [ ] Let users import saved AIOS evidence and replay its event timeline, inspect
      causal policy/action links, and reproduce analysis and evaluation offline.
      Preserve original evidence and record analyzer/evaluator/configuration versions.
- [ ] Provide valid/invalid capture-export-import fixtures and an end-to-end replay
      example. Offline evidence replay must not invoke original tools or repeat
      external side effects. Live reruns are separate, explicitly authorized work;
      recorded traces alone cannot guarantee identical model/provider behavior.
- [ ] Implement integrity-protected export/verification using a documented hash
      chain with authenticated external checkpoints or signed manifests. Define
      trusted keys, rotation, retention and verification coverage.
- [ ] Detect modification, reordering, duplication and missing records within
      declared coverage; detect truncation relative to trusted checkpoints.
      Editable local chains or ordinary checksums do not establish authenticity.
- [ ] Publish tampering fixtures. Explain that record integrity does not establish
      completeness or truth of an untrusted producer's reported execution.
- [ ] Expose verification/coverage status and causal policy/action links to Tower
      and MCP; keep failed, unknown and incomplete verification visibly distinct.

## Sidecar 0.8 compatibility

Lens 0.7.1 reads `sidecar.correlation/1` through
`agenticlens.integrations.sidecar.attach_decisions(run, records)`. Records must
match the exact run, trace and existing span IDs. Duplicate decisions are
idempotent; conflicting identities and mixed invalid batches are rejected.
All seven outcomes appear as `supervision_decision` timeline events in diagnosis
schema 1.1. BLOCK/ESCALATE do not mark spans, runs or deployments unhealthy.
Decision evidence is not proof of tool execution; the Sidecar journal carries
actual dispatch/completion and must be verified separately. Reasons may contain
sensitive information: callers must authorize recipients. Shared/Exclusive
context privacy and delegated authority remain Sidecar 0.9 validation work.
No Sidecar runtime dependency is added.

See [integration details](docs/sidecar-integration.md).

## Tower 0.6.0 integration

Native Lens run evidence supports Tower's approved staging recovery, shipped
with its combined Phase 6/6A and MCP 0.3.6. Lens retains analysis ownership. See
[compatibility and examples](docs/control-tower-0.6.md).

## Evals 0.8.0 CLI interoperability

Evals 0.8.0 runs Lens 0.8.0 approved suite exports directly with `agentic-evals evaluate` or `live`, then applies release policy with `gate`. Lens retains dataset curation, approval, lineage and diagnosis. The existing `agentic-evals>=0.7.1,<1` dependency admits 0.8.0; no floor increase is needed.

See [CLI usage and compatibility](docs/evals-0.8-cli.md).

## Chaos 0.7.0 interoperability

Chaos 0.7.0 adds sequential fault cascades, deterministic monotonic breaking-point
search, synthetic response poisoning (including prompt/tool-response instruction
and policy-bypass payloads), and explicit-price retry cost estimates. Native
child event IDs and fault types remain intact; cascade IDs/stages and poisoning
strategy/payload/seed are additive event detail. Existing report readers and
AIOS exports remain compatible.

See the [v0.7 guide and offline synthetic example](https://github.com/DeepAgentLabs/agentic-chaos/blob/v0.7.0/docs/v0.7.md).
The example includes observed synthetic dispatches and a bypassed negative
control. Injection or recovery alone does not prove containment. No new shared
schema, automatic adapter, hosted execution capability or containment guarantee
is introduced.

Lens continues to read chaos_events and diagnose marked spans through existing Chaos span adapters. Suite conversion rules are unchanged. No dependency bump or Lens patch release is needed.

## Control Tower 0.7.0 fleet operations

Tower 0.7.0 adds frozen environment/capability targeting, bulk desired settings,
separate approval, durable per-target results and bounded stop/MCP-revocation
acknowledgement through Python, HTTP and CLI. No fleet atomicity or automatic
rollback/resume is claimed. Timed-out/requested commands need host reconciliation.

Lens retains trace capture, diagnosis and suite management. Enhanced-tracing fleet settings are desired configuration only until a host explicitly applies them; native evidence and health stay independent.

Existing optional dependency ranges remain sufficient. No sibling runtime or
native evidence schema changes are required; this documentation alignment needs
no patch release. See the [operator guide](https://github.com/DeepAgentLabs/agenticops-control-tower/blob/v0.7.0/docs/fleet-operations.md).

## 0.9.0 ecosystem compatibility

ModelFit is Lens-owned analysis over Lens experiment reports. It adds no
cross-package object, event meaning, or AIOS schema, and changes no existing
trace, finding, experiment, diagnosis, or suite contract.

- `agentic-sidecar`: its optional `agenticlens` extra capped Lens below 0.9.
  Sidecar 0.8.4 widens the range to `>=0.7.1,<1` and moves its locked
  ecosystem check to Lens 0.9.x. Sidecar correlation (`attach_decisions`) is
  unchanged.
- `agenticops-control-tower`: the optional `agenticlens>=0.7,<1` extra already
  admits 0.9.0. A ModelFit report is local analysis, not fleet health or
  native evidence posture; Tower does not read it.
- `agentic-chaos`: `agenticlens>=0.7.0` admits 0.9.0; chaos span adapters and
  `chaos_events` analysis are unchanged.
- `agentic-evals`: Lens keeps `agentic-evals>=0.7.1,<1`; ModelFit reads the
  native evaluation reports embedded in experiment trials and computes no
  release gate.
- `deep-agentic-core-mcp`: MCP 0.3.11 pins its hosted images to
  `agenticlens==0.9.0` and adds a read-only `lens.modelfit_recommend` tool
  over supplied experiment reports; existing Lens-backed tools are
  unchanged.
- `ai-operations-spec`: no spec change; ModelFit schemas are Lens-local.

## Chaos 0.8.0 interoperability

Chaos 0.8.0 adds:

- multi-stage chaos workflows: steps, steady-state health checks, parallel
  branches, approval gates that can be resumed, and reusable templates
- declarative YAML/JSON/TOML experiments, with validation that never executes
  targets and cron schedule previews
- `Scope` explosion-radius control (steps, providers and exclusions) on every
  built-in fault and `cascade()`; custom faults get it by calling
  `BaseFault.__init__`, setting `scope` or overriding `in_scope()`
- a topology fuzzer that weights fault placement by fan-out

Native event IDs and fault types are unchanged. Workflow provenance
(`detail.workflow`) and an optional `ChaosReport.workflow` summary are
additive. A workflow's steps merge into one native report for contracts and
AIOS export.

See the [v0.8 guide](https://github.com/DeepAgentLabs/agentic-chaos/blob/v0.8.0/docs/v0.8.md)
and the [offline examples](https://github.com/DeepAgentLabs/agentic-chaos/tree/v0.8.0/examples/workflows).
Workflow statuses, health checks and fuzz outcomes are resilience evidence.
They are not scores, release gates or proof of containment. No new shared
schema, automatic adapter or hosted execution capability is introduced.

Lens reads workflow reports and merged reports as `Workflow` JSON and analyzes their `chaos_events` as before. `detail.workflow` is producer-specific event detail under schema v1.1. Suite conversion rules are unchanged. Chaos's optional `agenticlens>=0.7.0` extra is unchanged, so no dependency bump or Lens patch release is needed.

## Evals 0.9.0 judge reliability compatibility

Evals 0.9.0 records the same `judge_*` usage keys that `structured_judge()`
writes and `analyze_scores()` reads. Its own rubric and judge evaluators now
produce them too, and it totals them in `summary.judge`. A judge that raises
now yields an unavailable score that never passes instead of aborting the
suite. `samples=N` adds `judge_agreement`. Lens 0.10.0's tests pass unchanged,
and `agentic-evals>=0.7.1,<1` already covers 0.9.0. No Lens release is needed.
See [the compatibility note](docs/evals-0.9-judge-reliability.md).

## Evals 0.10.0 evaluation evidence compatibility

Evals 0.10.0 exports its reports as AIOS `0.4-draft` `evaluation` evidence and
merges it into an existing Run. `agenticlens validate` reports the merged
example as aligned. Mapping Evals cases to Lens-exported steps stays explicit;
judge usage stays in evaluation attributes, never in the Run's cost. Lens
0.10.0's tests pass unchanged, and `agentic-evals>=0.7.1,<1` covers 0.10.0. No
Lens release is needed.
See [the compatibility note](docs/evals-0.10-aios-evidence.md).

## MCP 0.4.0 unified release checks

MCP 0.4.0's `core.release_check` consumes the Lens `ComparisonReport` and the Evals
gate re-exported by `agenticlens.evaluation`. Lens needs no runtime change or release.
A comparison field rename would be a breaking change for MCP's validation.
See [the compatibility guide](docs/mcp-0.4-unified-workflows.md)
and the [MCP guide](https://github.com/DeepAgentLabs/mcp-server/blob/v0.4.0/docs/unified-workflows.md).

## AIOS v0.6 compatibility

See [canonical example and extension guidance](docs/aios-v0.6.md). The AIOS
v0.6 layer is exploratory; export schemas remain v0.4 and dependency floors
are unchanged. Lens-local suite, ModelFit and routing contracts remain native.

## Chaos 0.9.0 interoperability

Chaos 0.9.0 adds:

- resilience probes: `HttpProbe`, `ResponseQualityProbe`, `LatencyProbe` and
  `FunctionProbe` check steady state before chaos, while faults are active and
  after recovery. By default no fault is injected when a pre-chaos probe
  fails; `require_steady_state=False` runs the chaos anyway and leaves the
  score inconclusive
- a 0-100 resilience score built from recovery, probe, latency,
  retry-efficiency and cost evidence, with per-fault verdicts. Components a
  run cannot show (for example latency without a baseline) are left out and
  the remaining weights renormalized. The score is inconclusive (`null`) after
  a failed pre-chaos probe, for dry runs, when no fault fired, or when no
  component can be computed
- a local run-history store for score trends, with `max_runs` and
  `max_age_days` retention, and a `--min-score` CI gate
- probes and scoring on chaos workflows, experiment files and the pytest marker

Native event IDs and fault types are unchanged. `ChaosReport.probes`,
`ChaosReport.resilience` and the matching `WorkflowReport` fields are optional
and additive. When a score was computed, AIOS exports add a derived
`resilience_score` measurement; inconclusive runs export none. Probe results
and the score breakdown stay in the `io.deepagentlabs.agentic-chaos`
producer extension.

See the [v0.9 guide](https://github.com/DeepAgentLabs/agentic-chaos/blob/v0.9.0/docs/v0.9.md)
and the [offline demo](https://github.com/DeepAgentLabs/agentic-chaos/blob/v0.9.0/examples/chaos_resilience_demo.py).
The resilience score summarizes the evidence of one chaos run. It is not an
Evals score, a release-gate decision, a deployment health signal or proof of
containment. No new shared schema, automatic adapter or hosted execution
capability is introduced.

Lens reads scored reports as `Workflow` JSON and analyzes their `chaos_events` as before. The chaos-impact recommender does not consume `probes` or `resilience`, so Lens cost, latency and diagnosis findings do not change. Suite conversion rules are unchanged. Chaos's optional `agenticlens>=0.7.0` extra is unchanged, so no dependency bump or Lens patch release is needed.

## AIOS v0.6.1 compatibility

See [provenance and conformance suite guidance](docs/aios-0.6.1.md). Exports and
`agenticlens conformance` stay on `0.4-draft`; running the portable suite and a
provenance exporter for Lens findings are candidates, not shipped. Dependency
floors are unchanged.

## MCP 0.5.0 hosted access control

[MCP 0.5.0](https://github.com/DeepAgentLabs/mcp-server/releases/tag/v0.5.0) completes MCP Phase 5 with hosted access control. Each hosted key can carry allow and deny tool globs, an expiry and a task scope. The server enforces them at dispatch, outside the model: before each hosted handler runs, it re-authenticates the key and reloads its policy. Revocation, a narrower policy or expiry therefore stops queued calls, retries and calls on existing connections. Calls already running finish. Denied calls return an MCP-local `mcp.access-decision.v1` record, and every hosted call logs `dispatch`/`completion` records that share a `correlation_id`. These records are not AIOS artifacts. `core.access_status` reports a key's effective policy, and operators use `deep-agentic-core-mcp-admin` to narrow or revoke a key by user ID.
See [the compatibility guide](docs/mcp-0.5-access-control.md).
