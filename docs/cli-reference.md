# CLI Reference

All commands are available via the `agenticlens` console script installed with the package.

```bash
pip install agenticlens
agenticlens --help
```

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

## `calibrate`

Compare LLM judge verdicts against human-labeled references.

```bash
agenticlens calibrate <evaluation.json> <labels.json> [OPTIONS]
```

| Flag | Type | Description |
|------|------|-------------|
| `--evaluator` | `STR` | Evaluator name to calibrate |
| `--save` | `PATH` | Save calibration report as JSON |

**Example:**

```bash
agenticlens calibrate evaluation.json labels.json \
  --evaluator answer_quality \
  --save calibration.json
```
