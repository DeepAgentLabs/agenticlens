# v0.6 Portable Conformance Suite

## Status

Exploratory draft, first published in repository release v0.6.1. The current
manifest identifies snapshot v0.8.0 and adds operational-artifact cases; earlier cases and expected outcomes are unchanged. The suite turns the
v0.4 conformance rules, the v0.5 marker routing rule and the v0.6 provenance
rules into fixtures with expected outcomes and rule citations, so any
implementation can check itself without importing a DeepAgentLabs package. It
does not close decision `D-001`, freeze any layer or certify stable
conformance.

## Contents

- [suite.json](suite.json): the manifest. Every path is relative to it.
- `cases/`: one document per case. Each invalid case breaks exactly one rule
  family, so a validator that cites rules can be compared precisely.
- `subjects/`: subject artifacts for the cross-artifact resolution cases,
  including a byte-different copy and a different Run.

The suite needs only a JSON Schema 2020-12 validator with `date-time` and
`uri` format checking, the schemas under `specification/v0.4/schemas/` and
`specification/v0.6/schemas/`, `specification/v0.8/schemas/`, and
[compatibility.json](../../v0.5/compatibility.json). No network access is
needed: register every schema by its `$id` before validating.

## Expected behavior for outcome cases

For each entry in `cases`, a validator reads the document on its own and:

1. Selects the schema set named by the document's `spec_version` from
   `published_schema_sets`, and the schema for its `artifact_type` from that
   set's `artifact_types`. If there is none, the outcome is `unsupported`; it
   MUST NOT fall back to another marker's schema (`AIOS-0.5-V03`).
2. Validates against that schema, with every set named in `depends_on` in the
   registry. Any error gives `schema-invalid`.
3. Otherwise runs the semantic rules of that marker's rule catalog. Any
   violation gives `semantic-invalid`; none gives `valid`.

A validator passes a case when its outcome equals `expected`. A validator that
reports rule identifiers also passes only if, for a `semantic-invalid` or
`unsupported` case, the set of rules it cites equals `rules`. Schema-invalid
cases list only the schema rule (`AIOS-0.4-P01` or `AIOS-0.6-R01` or `AIOS-0.8-R01`) because
schema error reporting differs between validator libraries; the `description`
names any closed-vocabulary or extension rule the schema error enforces.

## Expected behavior for resolution cases

For each entry in `resolution_cases`, a consumer holds the record and the
subject files listed in `subjects` (keyed by subject `id`; an omitted subject
is unavailable) and produces a report shaped like `expected`:

- `subjects.<id>.available`: whether the consumer holds the subject bytes.
- `subjects.<id>.valid`: whether those bytes parse to an artifact that is
  `valid` under the outcome procedure above, or `null` when unavailable.
- `subjects.<id>.identity`: `match` when the held artifact's `id`,
  `artifact_type` and `spec_version` equal the subject entry's `artifact_id`,
  `artifact_type` and `spec_version` (never its record-local `id`),
  `mismatch` otherwise, `null` when unavailable.
- `subjects.<id>.digest`: `verified` or `mismatch` after recomputing the
  digest over the held bytes, `unchecked` when the subject has a digest but no
  bytes are held, `absent` when the subject declares no digest.
- `references`: for each `aios_object` source (keyed by source `id`) and each
  finding target (keyed `<finding id>/targets/<index>`): `resolved`,
  `missing` (the usable subject has no object with that `id`),
  `type_mismatch` (the object exists with another `type`) or `unresolved`
  (the subject is unavailable, invalid or a mismatch, so it cannot be used).

The `rules` list on a resolution case names the consumer rules the case
exercises (`AIOS-0.6-C02`–`C05`).

## What passing means

Passing every case shows that an implementation decides these fixtures the
way the specification's text says. It does not show that the implementation
meets process rules such as extension preservation (`AIOS-0.4-C02`), honest
external-reference reporting (`AIOS-0.4-X02`) or not fetching URIs
(`AIOS-0.6-C07`), and it says nothing about whether any artifact is true,
safe or successful. Claims still follow the draft claim formats in
[v0.4 conformance](../../v0.4/conformance.md) and
[provenance records](../provenance.md), for example:

```text
Aligned with AI Operations Specification v0.4-draft as observed on 2026-11-03; passes the v0.8.0 conformance suite.
```

## Running it in this repository

`uv sync --extra dev` then `make check`. `tests/test_v06_conformance_suite.py`
runs the repository's reference checks (`tests/aios_reference.py`) over every
case and fails if a cataloged schema or semantic rule has no case. Those checks
are test code, not an SDK; implementations are expected to bring their own.

Operational cases use the [0.8-draft rules](../../v0.8/conformance.md). References to native artifacts are citation handles, not resolved or authenticated sources. Process obligations require separate implementation validation.
