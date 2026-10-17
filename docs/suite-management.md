# Test-Suite and Dataset Management

AgenticLens 0.8.0 adds `agenticlens.suites` and the `agenticlens suite`
command group (roadmap milestone v0.6). Use them to build regression suites
from hand-written cases, production traces, and user feedback. You can then
review, mask, de-duplicate, vary, and split the cases, and approve the suite
as an immutable version that CI can verify and run.

Suites stay plain agentic-evals `TestSuite` files the whole way through, so a
draft or an exported version runs with `agenticlens evaluate`,
`evaluate-live`, and `experiment run` unchanged.

## Lifecycle

```text
CSV / JSON ──► import ─┐
production traces ─────┼─► draft suite ─► mask ─► dedupe ─► vary ─► split ─► review
user feedback ─────────┘        ▲                                              │
                                └──────── edit (add, remove, tag) ◄────────────┘
                                                                               │
                                     approve (checks) ─► store/<name>/<version>.json
                                                                               │
                                  CI: verify ─► export ─► evaluate ─► gate ◄───┘
```

| Stage | CLI | Python |
| --- | --- | --- |
| Import CSV/JSON/JSONL/YAML | `suite import` | `import_cases`, `import_suite` |
| Convert traces | `suite from-traces` | `case_from_run`, `cases_from_runs` |
| Convert feedback | `suite from-feedback` | `case_from_feedback`, `cases_from_feedback` |
| Edit cases | `suite add-case`, `remove-case`, `tag` | `add_case`, `update_case`, `remove_cases`, `tag_cases` |
| Review | `suite review` | `review_cases` |
| Mask PII | `suite mask [--check]` | `PIIMasker`, `mask_suite`, `scan_suite` |
| Duplicates | `suite dedupe [--drop]` | `find_duplicates`, `drop_duplicates` |
| Synthetic variations | `suite vary` | `generate_variations`, `vary_case` |
| Splits | `suite split` | `assign_splits` |
| Filter / summarize / diff | `suite filter`, `summary`, `diff` | `filter_suite`, `summarize_suite`, `diff_suites` |
| Approve and store | `suite approve` | `SuiteStore.approve` |
| CI | `suite verify`, `suite export`, `suite versions` | `SuiteStore.verify`, `load_suite`, `versions` |

Editing commands rewrite the suite file in place unless `--save` names
another file. YAML is written for `.yaml`/`.yml` paths and JSON otherwise.

## Case metadata

AgenticLens records management state in each case's `metadata`:

| Key | Meaning |
| --- | --- |
| `source` | Lineage: `kind` (`imported`, `trace`, `feedback`, `synthetic`; absent means authored), plus `file`/`row`, `trace_id`/`run_id`, `feedback_id`, or `parent_case_id`/`variation`/`seed` |
| `review_status` | `needs_review`, `accepted`, or `rejected`. A case without a status counts as accepted (authored by a person) |
| `reviewed_by`, `review_notes` | Who reviewed the case and why |
| `domain` | Domain category, e.g. `billing` |
| `split` | `train`, `validation`, or `test` |

Tags stay in the case's `tags` list.

## Importing cases

```bash
agenticlens suite import cases.csv --name support-regression --version 1.0.0 \
  --save suite.yaml
```

CSV columns map onto `TestCase` fields. List columns (`expected_contains`,
`required_tools`, `forbidden_tools`, `required_tool_order`, `tags`) are
`|`-separated. `input` is parsed as JSON when it is a JSON object or array.
`domain`, `split`, and any `metadata.<key>` column go to case metadata.
Unknown columns are rejected, so a misspelled expectation fails the import
instead of being dropped silently. JSON imports accept a list, `{"cases": [...]}`,
or JSON Lines. Add `--into suite.yaml` to append to an existing suite.

PII is masked by default before anything is written (`--no-mask` to opt out).

## From production traces

```bash
agenticlens suite from-traces traces/ --name prod-regression --version 1.0.0 --save suite.yaml
```

A successful run becomes a case that expects what the run did:

- `required_tools` and `required_tool_order` from its successful tool calls
- `max_latency_ms` and `max_cost_usd` set to the observed values times
  `--latency-margin` / `--cost-margin` (default 1.5)
- `expected_output` only with `--include-output`, because exact model output
  rarely repeats

The input comes from `metadata.input` or the first span with `input_data`, and
the domain from `task_type`. Each converted case is marked `needs_review`, and
cases that can't be converted are reported with a reason:

- **Failed runs** show what went wrong, not what right looks like. Turn them
  into cases with corrected feedback instead.
- **Runs without a recorded input** have nothing to replay.

Record the request when tracing, either as run metadata
(`trace("support", input=question)`) or on a span
(`span.record_io(input_data=question)`), so there is an input to replay. The
tracer's redactor still applies.

## From user feedback

```json
{"feedback": [
  {"feedback_id": "fb-101", "input": "Where is my parcel?", "output": "It ships in 2 business days.", "rating": "positive"},
  {"feedback_id": "fb-102", "input": "Can I pay by invoice?", "output": "No.", "rating": "negative",
   "corrected_output": "Let me connect you with a specialist."}
]}
```

```bash
agenticlens suite from-feedback feedback.json --into suite.yaml --save suite.yaml --traces traces/
```

If feedback has a correction, the case expects the correction. Positive
feedback (`rating: positive`, or a `score` of 0.5 or more) expects the
confirmed output. Negative feedback without a correction is skipped, because it
says what's wrong but not what's right. When a record has no `input`, the input
comes from the run named by `run_id` or `trace_id` in `--traces`. The rejected
output is kept in `metadata.rejected_output` for reviewers. The schema is
[`schemas/suites/feedback-batch.schema.json`](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/suites/feedback-batch.schema.json).

## PII masking

```bash
agenticlens suite mask suite.yaml                      # mask in place
agenticlens suite mask suite.yaml --check              # scan only; exit 7 if PII found
agenticlens suite mask suite.yaml --strategy hash --salt "$SALT" --report mask.json
```

What gets masked:

- **Patterns in text:** emails, phone numbers, Luhn-valid card numbers, US
  SSNs, IPv4 addresses, bearer tokens, and API keys.
- **Values under sensitive keys** (`password`, `token`, `email`, `phone`,
  `ssn`, `address`, `date_of_birth`, ...), matched as whole words of the key.
  `customer_email` is masked; `input_tokens` is not.
- **Fields covered:** a case's input, expected output, expected substrings,
  expected tool arguments, and metadata. Case lineage is never masked.

`redact` writes `[EMAIL]`. `hash` writes `[EMAIL:3f2a9c1e]`, a salted SHA-256
prefix, so equal values stay equal and you can still spot duplicates. Reports
list the case, the field path, and the PII type, never the value.

Pattern matching is a safeguard, not a guarantee. It doesn't detect names,
street addresses in free text, or locale-specific identifiers. A version
string such as `1.2.3.4` is masked as an IP address. Masking an expected
output also changes what the agent has to produce, so review those cases.

## Duplicates, variations, and splits

```bash
agenticlens suite dedupe suite.yaml --threshold 0.85 --report dupes.json --drop
agenticlens suite vary suite.yaml --per-case 2 --kind typo --kind prefix --seed 7
agenticlens suite split suite.yaml --train 0.7 --validation 0.15 --test 0.15 --seed 7
```

**Duplicates.** Exact duplicates share a normalised input (case,
punctuation, and whitespace ignored). Near duplicates reach the Jaccard
threshold over word unigrams and bigrams. A group is *conflicting* when
cases with the same normalised input expect different results, which usually
means a labelling error. Near duplicates with distinct inputs never conflict. `--drop` keeps the first case of each group. Synthetic
variants of the same original are not compared to each other unless you pass
`--include-variants`. Comparison is pairwise, so it is sized for suites of
thousands of cases.

**Variations.** `lowercase`, `uppercase`, `whitespace`, `punctuation`,
`typo`, and `prefix` change every string in the input, skipping masked
values. They test robustness to how a request is typed, not what it means.
They are not paraphrases and make no model calls. Each variant:

- keeps its parent's expectations
- inherits its parent's split
- is marked `needs_review`
- records `parent_case_id`, `variation`, and `seed`

`--per-case` caps variants per original, so re-running adds nothing new.

**Splits.** A case is placed by hashing its lineage with the seed. A case
keeps its split when other cases are added or removed, so a later version
can't move test cases into training. A variant always lands with its
original. The trade-off is that split sizes only approximate the ratios, and
the CLI warns when a split is empty.

## Review and approval

```bash
agenticlens suite review suite.yaml --status accepted --reviewer qa-lead --case trace-run-1
agenticlens suite review suite.yaml --status rejected --reviewer qa-lead --case fb-7 --notes "policy changed"
agenticlens suite approve suite.yaml --store suites/ --approver qa-lead --notes "Q4 regression set"
```

`approve` runs three checks, records them, and refuses (exit 6) when any
fails:

| Check | Fails when | Override |
| --- | --- | --- |
| `review` | any case is `rejected` (remove it), or `needs_review` | `--allow-unreviewed` (needs_review only) |
| `pii` | the scan finds unmasked PII | `--allow-pii` |
| `conflicting_duplicates` | cases share an input but expect different results | none; fix the labels |

The approved version is written once to `<store>/<name>/<version>.json` as a
`SuiteVersion`. It holds the suite exactly as approved, its SHA-256 over
canonical JSON, the case count, the approver, the time, the notes, the
checks, and an optional `--parent-version`. The schema is
[`schemas/suites/suite-version.schema.json`](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/suites/suite-version.schema.json).

Approved versions are immutable:

- Approving the same name and version again is a no-op if the content is
  identical, and is refused if it differs. Bump the version instead.
- Every read re-hashes both the suite (`content_sha256`) and the whole
  envelope (`record_sha256`, covering the approver, time, notes, checks, case
  count, and parent version). A hand-edited, moved, or corrupted version fails
  `verify`, `export`, and `load_suite`.
- Suite names and versions must be plain path segments (letters, digits,
  `.`, `_`, `-`).

Use `suite diff support@1.0.0 suite.yaml --store suites/` to review what a
new draft changes before approving it.

## Running approved suites in CI

```yaml
- run: uv run agenticlens suite verify --store suites
- run: uv run agenticlens suite export support-regression@1.0.0 --store suites --save build/suite.json --split test
- run: uv run agenticlens evaluate build/suite.json build/samples.json --save build/evaluation.json --strict-evidence
- run: uv run agenticlens gate build/evaluation.json
```

`verify` exits 6 when any stored version is missing or changed. `export`
writes a plain suite, optionally filtered by `--tag`, `--domain`, or
`--split`. It stamps `metadata.agenticlens_suite_version` with the name,
version, hash, approver, and approval time, so the evaluation report traces
back to the approved version. For live agents, use `evaluate-live` in place
of `evaluate`. This repository's CI runs exactly these steps against
`examples/suites/store`.

## Example

[`examples/suite_management_demo.py`](https://github.com/DeepAgentLabs/agenticlens/blob/main/examples/suite_management_demo.py)
runs the whole lifecycle offline. Its inputs are a CSV with PII and a
duplicate row, three production traces (one failed), and four feedback
records (two unconvertible). It produces 15 approved cases in
`examples/suites/store/support-regression/1.0.0.json` and evaluates them
against a deterministic stub agent. `tests/test_examples_suites.py` checks
that the store and artifacts reproduce byte for byte, apart from the
evaluation report's `created_at`.

```bash
uv run python examples/suite_management_demo.py
```

## Relationship to evaluation datasets

`agenticlens dataset ...` (since 0.5.0) manages labelled *outputs and traces*
for judge calibration. `agenticlens suite ...` manages the *test cases*
(inputs and expectations) those outputs are scored against. Both are
versioned. Only approved suite versions are immutable and hash-verified.
