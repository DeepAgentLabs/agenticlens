# CLI Reference

All commands are available via the `agenticlens` console script installed with the package.

```bash
pip install agenticlens
agenticlens --help
```

---

## Command inventory

Every registered command is listed below, including nested groups. Run `agenticlens COMMAND --help` (for example, `agenticlens suite approve --help`) for its complete options. The robust AI reference also includes source declarations for all CLI functions, with the exact argument and option definitions.

| Command (after `agenticlens`) | Purpose |
| --- | --- |
| `analyze` | Run the recommendation engine against a saved workflow. |
| `attribution-accuracy` | Measure faulty-step attribution accuracy on controlled failures. |
| `calibrate` | Compare saved judge verdicts with human reference labels. |
| `compare` | Compare repeated baseline and candidate traces. |
| `conformance` | Run schema and semantic AIOS draft checks and report rule-cited draft alignment. |
| `dashboard` | Combine a workflow, run, evaluation report, and/or comparison into one HTML dashboard. |
| `dataset export-samples` | Export evaluation samples from a versioned dataset artifact. |
| `dataset split` | Assign deterministic train, validation, and test splits to a dataset. |
| `dataset summary` | Summarize dataset size, split assignment, and available human labels. |
| `diagnose` | Diagnose failures, attribute the faulty step and agent, and rebuild the timeline. |
| `evaluate` | Score agent outputs, tool use, latency, and cost against a test suite. |
| `evaluate-live` | Run one trusted live Python or HTTP target against an evaluation suite. |
| `evidence export` | Export native Run + explicit records to an authenticated AIOS execution bundle. |
| `evidence replay` | Verify/import saved AIOS evidence, then print capture-order records offline. |
| `evidence verify` | Read a JSON array and manifest. Exit 0 only for verified coverage. |
| `experiment report` | Re-render a saved experiment report without re-running any variant. |
| `experiment run` | Run repeated trials for three or more variants against one suite. |
| `explain` | Explain a run's failures, or a workflow's recommendations, as an investigation. |
| `gate` | Apply release thresholds and return exit code 2 when the gate fails. |
| `history` | Render a cross-trace history view from a --db file or a run-JSON directory. |
| `import-otlp` | Convert OTLP/HTTP JSON trace exports into AgenticLens run files. |
| `inspect` | Inspect a validated run trace, span tree, and raw metric distributions. |
| `modelfit matrix` | Show the task-level model matrix of a saved ModelFit report. |
| `modelfit recommend` | Recommend a model for every task category under hard constraints. |
| `modelfit taxonomy` | Show which cases each task category covers, before recommending. |
| `optimize analyze` | Rank opportunities by projected cost saving, with evidence, confidence, and risks. |
| `optimize decide` | Record a decision. Adopting requires a prior accept; reverting requires adoption. |
| `optimize outcome` | Compare projected and observed savings; the projection is never adjusted. |
| `optimize status` | Show the latest decision status of every opportunity in a report. |
| `profile` | Run a script that uses `agenticlens.profile()` / `agenticlens.step()` and report it. |
| `report` | Display a saved workflow report. |
| `routing decide` | Select and explain without invoking models, in every policy mode. |
| `routing summary` | Summarize measured serving/shadow outcomes; unknown costs stay unknown. |
| `serve-otlp` | Run a live OTLP/HTTP receiver with a real-time dashboard. Requires `agenticlens[api]`. |
| `suite add-case` | Add an authored case (at least one expectation is required). |
| `suite approve` | Check and store a suite as an immutable approved version (exit 6 when refused). |
| `suite dedupe` | Find exact, near, and conflicting duplicate cases. |
| `suite diff` | Show cases added, removed, and changed between two suites. |
| `suite export` | Export a verified approved version (optionally filtered) for evaluation in CI. |
| `suite filter` | Write the subset of cases matching tags, domains, and splits. |
| `suite from-feedback` | Convert user feedback (ratings and corrections) into draft cases for review. |
| `suite from-traces` | Convert successful production traces into draft cases for review. |
| `suite import` | Import test cases from CSV or JSON into a new or existing suite. |
| `suite mask` | Mask emails, phones, cards, SSNs, IPs, secrets, and sensitive fields. |
| `suite remove-case` | Remove cases by ID. |
| `suite review` | Record a review decision on cases. |
| `suite split` | Assign stable train/validation/test splits (variants follow their original). |
| `suite summary` | Count cases by split, domain, tag, source, and review status. |
| `suite tag` | Add or remove tags and set domain categories. |
| `suite vary` | Add deterministic synthetic input variations (marked needs_review). |
| `suite verify` | Re-hash stored versions; exit 6 when any is missing or was changed. |
| `suite versions` | List approved suite versions. |
| `trace show` | Show a trace's span tree and metrics, or one span in full. |
| `trace timeline` | Reconstruct the incident timeline, marking the attributed root cause. |
| `validate` | Validate an AIOS artifact against the draft JSON Schema. |

---

## `profile`

Run and profile a Python workflow script.

```bash
agenticlens profile <script> [OPTIONS]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--save` | `PATH` | — | Save the resulting `workflow.json` to this path |
| `--config` | `PATH` | — | Path to `agenticlens.yaml` config |

**Example:**

```bash
agenticlens profile examples/recommendations_demo.py --save workflow.json
```

---

## `analyze`

Analyze a saved workflow artifact for token use, cost, and optimization findings.

```bash
agenticlens analyze <workflow.json> [OPTIONS]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--html` | `PATH` | — | Also save a standalone HTML dashboard |
| `--save` | `PATH` | — | Save analysis findings as JSON |
| `--config` | `PATH` | — | Path to `agenticlens.yaml` config |

**Example:**

```bash
agenticlens analyze workflow.json --html dashboard.html
```

---

## `inspect`

Inspect a structured trace run artifact.

```bash
agenticlens inspect <run.json> [OPTIONS]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--save` | `PATH` | — | Save a Markdown trace report |
| `--html` | `PATH` | — | Save a standalone HTML dashboard |

**Example:**

```bash
agenticlens inspect run.json --save trace-report.md
agenticlens inspect run.json --html dashboard.html
```

---

## `compare`

Compare a baseline and candidate set of repeated run artifacts.

```bash
agenticlens compare <baseline-dir> <candidate-dir> [OPTIONS]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--regression-threshold` | `FLOAT` | `0.05` | Relative change above which a metric is a regression |
| `--fail-on-regression` | flag | off | Exit non-zero if any regression is detected |
| `--min-samples` | `INT` | — | Fail if either cohort has fewer than N samples |
| `--format` | `json\|csv\|md` | `json` | Output format |
| `--save` | `PATH` | — | Save the comparison report |
| `--html` | `PATH` | — | Save a standalone HTML dashboard |

**Example:**

```bash
agenticlens compare results/baseline results/candidate \
  --regression-threshold 0.05 \
  --fail-on-regression \
  --min-samples 5 \
  --format md \
  --save comparison.md
```

---

## `evaluate`

Run an evaluation suite against saved samples.

```bash
agenticlens evaluate <suite.yaml> <samples.json> [OPTIONS]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--save` | `PATH` | — | Save evaluation report as JSON |
| `--html` | `PATH` | — | Save a standalone HTML dashboard |

**Example:**

```bash
agenticlens evaluate suite.yaml samples.json \
  --save evaluation.json \
  --html evaluation.html
```

---

## `evaluate-live`

Run an evaluation suite against a trusted live target.

```bash
agenticlens evaluate-live <suite.yaml> [OPTIONS]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--target-kind` | `python\|http` | — | Target type |
| `--target` | `STR` | — | `path:callable` (python) or URL (http) |
| `--save` | `PATH` | — | Save evaluation report as JSON |

**Examples:**

```bash
# Python callable
agenticlens evaluate-live suite.yaml \
  --target-kind python \
  --target examples/live_evaluation_demo.py:run_case \
  --save evaluation-live.json

# HTTP endpoint
agenticlens evaluate-live suite.yaml \
  --target-kind http \
  --target http://localhost:8000/evaluate \
  --save evaluation-live.json
```

---

## `gate`

Apply a release gate to a saved evaluation report.

```bash
agenticlens gate <evaluation.json> [OPTIONS]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--min-pass-rate` | `FLOAT` | — | Minimum fraction of cases that must pass |
| `--min-average-score` | `FLOAT` | — | Minimum average evaluator score |
| `--max-failed-cases` | `INT` | — | Maximum number of failed cases allowed |
| `--max-average-latency-ms` | `FLOAT` | — | Maximum acceptable average latency |
| `--max-total-cost-usd` | `FLOAT` | — | Maximum acceptable total evaluation cost |

**Exit codes:** `0` = passed, `2` = gate failed, `1` = invalid input

**Example:**

```bash
agenticlens gate evaluation.json \
  --min-pass-rate 0.95 \
  --min-average-score 0.98 \
  --max-failed-cases 1 \
  --max-average-latency-ms 1500 \
  --max-total-cost-usd 0.25
```

---

## `validate`

Validate an artifact against an AIOS draft JSON Schema.

```bash
agenticlens validate <artifact.json> [OPTIONS]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--version` | `STR` | — | AIOS spec version (e.g. `0.4`) |
| `--save` | `PATH` | — | Save validation report as JSON |

**Example:**

```bash
agenticlens validate workflow.json --version 0.4
```

---

## `conformance`

Run full AIOS schema and semantic conformance checks.

```bash
agenticlens conformance <run.json> [OPTIONS]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--version` | `STR` | — | AIOS spec version |
| `--spec-root` | `PATH` | auto-detected | Path to the `ai-operations-spec` repo |
| `--save` | `PATH` | — | Save conformance report as JSON |

**Example:**

```bash
agenticlens conformance run.json --version 0.4 --save conformance-report.json
```

---

## `dashboard`

Render a combined offline HTML dashboard from saved artifacts.

```bash
agenticlens dashboard [OPTIONS]
```

| Flag | Type | Description |
|------|------|-------------|
| `--run` | `PATH` | Path to a `run.json` trace artifact |
| `--evaluation` | `PATH` | Path to an `evaluation.json` report |
| `--comparison` | `PATH` | Path to a `comparison.json` report |
| `--save` | `PATH` | Output path for the HTML dashboard |

**Example:**

```bash
agenticlens dashboard \
  --run run.json \
  --evaluation evaluation.json \
  --comparison comparison.json \
  --save dashboard.html
```

---

## `serve-otlp`

Start the live OTLP/HTTP receiver and real-time dashboard.
Requires `agenticlens[api]`.

```bash
agenticlens serve-otlp [OPTIONS]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--host` | `STR` | `127.0.0.1` | Bind address |
| `--port` | `INT` | `4318` | Port |
| `--db` | `PATH` | in-memory | SQLite path for persistent trace storage |
| `--max-traces` | `INT` | `200` | In-memory trace cap (FIFO eviction) |

**Example:**

```bash
agenticlens serve-otlp --port 4318 --db traces.db
```

---

## `history`

View cross-trace aggregate history from a SQLite DB or directory of run JSON files.

```bash
agenticlens history [OPTIONS]
```

| Flag | Type | Description |
|------|------|-------------|
| `--db` | `PATH` | SQLite database path |
| `<dir>` | `PATH` | Directory of `run.json` files |

**Example:**

```bash
agenticlens history --db traces.db
agenticlens history results/
```

---

## `import-otlp`

Convert an OTLP/HTTP JSON trace export to an AgenticLens `run.json`.

```bash
agenticlens import-otlp <otlp.json> [OPTIONS]
```

| Flag | Type | Description |
|------|------|-------------|
| `--save` | `PATH` | Output path for the converted `run.json` |

**Example:**

```bash
agenticlens import-otlp third-party-trace.json --save run.json
```

---

## `dataset`

Subcommand group for managing versioned evaluation datasets.

### `dataset summary`

```bash
agenticlens dataset summary <dataset.json>
```

### `dataset split`

```bash
agenticlens dataset split <dataset.json> [OPTIONS]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--save` | `PATH` | — | Save the split dataset |
| `--train-ratio` | `FLOAT` | `0.7` | Fraction for the train split |
| `--validation-ratio` | `FLOAT` | `0.15` | Fraction for the validation split |
| `--test-ratio` | `FLOAT` | `0.15` | Fraction for the test split |
| `--seed` | `INT` | — | Random seed for reproducibility |

**Example:**

```bash
agenticlens dataset split dataset.json \
  --save dataset-split.json \
  --train-ratio 0.7 \
  --validation-ratio 0.15 \
  --test-ratio 0.15 \
  --seed 7
```

### `dataset export-samples`

```bash
agenticlens dataset export-samples <dataset.json> [OPTIONS]
```

| Flag | Type | Description |
|------|------|-------------|
| `--split` | `train\|validation\|test` | Split to export |
| `--save` | `PATH` | Output `samples.json` path |

**Example:**

```bash
agenticlens dataset export-samples dataset-split.json \
  --split test \
  --save samples-test.json
```

---

## `optimize`

Evidence-backed optimization recommendations from trace files or directories.
See [Optimization intelligence](optimization.md).

```bash
agenticlens optimize analyze <traces>... [--config FILE] [--baseline-variant ID] \
  [--ledger FILE] [--save FILE] [--markdown FILE]
agenticlens optimize decide <report.json> <opportunity-id> --status STATUS --by NAME \
  --ledger FILE [--reason TEXT] [--change REF]
agenticlens optimize status <report.json> --ledger FILE
agenticlens optimize outcome <report.json> <opportunity-id> --before PATH --after PATH \
  [--ledger FILE] [--min-runs N] [--save FILE] [--markdown FILE] [--fail-on-regression]
```

| Command | Purpose |
|---------|---------|
| `analyze` | Rank opportunities by projected cost saving, with evidence, confidence, and risks |
| `decide` | Append `accepted`, `rejected`, `adopted`, or `reverted` to the ledger |
| `status` | Latest decision status per opportunity, with counts |
| `outcome` | Projected vs observed per-run tokens, cost, latency, and success after adoption |

**Exit codes:** `0` = success, `1` = invalid input or refused transition,
`9` = `outcome --fail-on-regression` and quality regressed.

---

## `calibrate`

Compare LLM judge verdicts against human-labeled references.

```bash
agenticlens calibrate <evaluation.json> <labels.json> [OPTIONS]
```

| Flag | Type | Description |
|------|------|-------------|
| `--evaluator` | `STR` | Evaluator name to calibrate |
| `--save` | `PATH` | Save calibration report as JSON |
| `--tune-threshold` | `PATH` | Sweep pass thresholds and save the threshold-tuning report |

**Example:**

```bash
agenticlens calibrate evaluation.json labels.json \
  --evaluator answer_quality \
  --save calibration.json
```

---

## `report`

Display a saved profiling workflow (not a structured Run):

```bash
agenticlens report workflow.json
```

## `diagnose`, `explain`, `trace`, and `attribution-accuracy`

```bash
agenticlens diagnose run.json [--baseline PATH] [--save FILE] [--markdown FILE] \
  [--max-cost-usd USD] [--max-tokens N] [--max-latency-ms MS] \
  [--loop-threshold N] [--max-spans N] [--max-depth N] [--fail-on-unrecovered]
agenticlens explain artifact.json [--save FILE]
agenticlens trace show run.json [--span SPAN_ID]
agenticlens trace timeline run.json [--save FILE]
agenticlens attribution-accuracy controlled-failures/ [--save FILE] [--min-step-accuracy RATE]
```

`--baseline` is repeatable. `explain` accepts a Run, Workflow or DiagnosisReport.
`diagnose --fail-on-unrecovered` exits 4 on unrecovered failures; attribution accuracy exits 5 when the configured minimum is not met. Invalid inputs exit 1. See [diagnosis rules, budgets, timelines and attribution](diagnosis.md).

## `experiment`

```bash
agenticlens experiment run manifest.yaml suite.yaml --save experiment.json
agenticlens experiment report experiment.json --html experiment.html --csv variants.csv
```

Repeated trials support recorded, trusted Python and HTTP targets. Output flags include `--html`, `--csv` and `--cases-csv`; `run` also supports confidence/regression/sample controls. See [manifest, statistics and full workflow](experiments.md).

## `suite`

The inventory above lists every suite operation. Start with `suite import` or trace/feedback conversion, then edit, mask, deduplicate, vary, split, filter and review. Approval stores an immutable version for later verification/export; `versions` lists stored history and `diff` compares two suites. Commands have different positional arguments: use each subcommand's help rather than assuming every one accepts a suite path. See [suite commands, inputs and approval checks](suite-management.md).

## `modelfit`

```bash
agenticlens modelfit taxonomy experiment.json [--config FILE] [--json]
agenticlens modelfit recommend experiment.json [--config FILE] [--manifest FILE] \
  [--save FILE] [--markdown FILE] [--csv FILE] [--json] \
  [--fail-on-unfit] [--fail-on-low-confidence]
agenticlens modelfit matrix modelfit.json [--csv FILE] [--markdown FILE]
```

`recommend` and `taxonomy` accept multiple experiment files; `--manifest` is repeatable. CI checks exit 8 for an unfit category or low confidence when the corresponding flag is set. See [ModelFit constraints, scoring, taxonomy and confidence](modelfit.md).

## `routing`

```bash
agenticlens routing decide modelfit.json --category CATEGORY --request-id OPAQUE_ID \
  [--policy FILE] [--save FILE] [--audit FILE]
agenticlens routing summary result.json [MORE_RESULTS...] [--save FILE]
```

`decide` never invokes providers; exit 5 means blocked/escalated and exit 1 means invalid input. `summary` reads SDK `RoutingResult` files. See [runtime policies, callbacks and audit](routing.md).

## `evidence`

```bash
agenticlens evidence verify records.json manifest.json --stream-id EXPECTED_STREAM \
  --key-file trusted-keys.json
agenticlens evidence export run.json observations.json bundle.json --key-id KEY_ID \
  --key-file trusted-keys.json [--complete]
agenticlens evidence replay bundle.json --run-id EXPECTED_RUN --key-file trusted-keys.json
```

Trust keys come from an operator-owned JSON map of key IDs to hex keys. Verification exits 0 only for verified coverage; replay refuses untrusted or incomplete bundles. Capture completeness must be explicitly justified by the producer. See [evidence authentication, execution mapping and replay](evidence-verification.md).
