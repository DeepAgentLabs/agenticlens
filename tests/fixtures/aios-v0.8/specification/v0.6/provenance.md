# v0.6 Draft Provenance Records

## Status and scope

Exploratory draft, dependent on v0.1–v0.5. This document defines the first
v0.6.x concept: a **provenance record**, a companion artifact that states where
a derived finding came from. It is published in repository release v0.6.1 and
does not freeze any layer or close decision `D-001`.

A provenance record declares `spec_version: "0.6-draft"` and
`artifact_type: "provenance"` and validates against
[schemas/provenance.schema.json](schemas/provenance.schema.json). Run and
Workflow artifacts are unchanged and still declare `0.4-draft`; the `0.6-draft`
schema set names only the provenance record. The machine-readable mirror of
this document is [provenance-rules.json](provenance-rules.json).

## Why a companion artifact

v0.4 Run artifacts are closed schemas. Under [v0.5 versioning](../v0.5/versioning.md),
adding a provenance field to them would be a Breaking change, and the
specification's own `aiops` namespace cannot be used as an extension name.
A separate record keeps every existing `0.4-draft` artifact valid and lets a
consumer that does not know `0.6-draft` reject the record as an unknown
marker, as `AIOS-0.5-V03` already requires, rather than misreading it.

A provenance record never adds objects to, or changes the meaning of, the
artifacts it describes. In-run `evidence` objects and `evidence-for`
relationships (v0.4) remain the way a Run carries its own evaluations,
safety signals and reliability events. A provenance record sits outside the
Run and can draw on several artifacts and on material that is not an AIOS
artifact at all.

## Concepts

### Subject

An AIOS artifact the record describes, named by its own `id`, `artifact_type`
and declared `spec_version`, optionally with a `uri` where it was retrieved and
a `digest` of its exact bytes. A record names at least one subject. A subject
is described, not embedded.

### Source reference

One piece of material a finding was derived from. Its `kind` is one of:

| `kind` | Meaning | Required fields |
|---|---|---|
| `aios_object` | One object inside a subject artifact | `subject`, `object` |
| `artifact` | A whole subject artifact | `subject` |
| `document` | A document outside AIOS, such as a policy or runbook | `uri` or `description` |
| `dataset` | A dataset or evaluation suite | `uri` or `description` |
| `log` | A log, trace or telemetry export that is not an AIOS artifact | `uri` or `description` |
| `tool_output` | Output captured from a tool or command | `uri` or `description` |
| `human_input` | A statement, label or review supplied by a person | `uri` or `description` |

`object` uses the v0.4 reference shape: an object `id` and its
closed-vocabulary `type`. Because the object is inside the subject, `external`
is absent or `false`; the schema rejects `external: true`. Finding `targets`
use the same shape. `captured_at` records when the material was observed.

### Derived finding

A statement produced by a named `method` (`rule`, `model`, `human`,
`statistical` or `heuristic`) with a `status` of `open`, `confirmed`,
`disputed` or `retracted`. It MAY carry a `severity` and a `confidence`
between 0 and 1, and `targets` naming the subject objects it is about. A
finding's `category` is producer-defined text with no shared meaning.

### Evidence lineage

Directed edges between sources and findings, read from `source` to `target`:

| `type` | Source endpoint | Target endpoint | Meaning |
|---|---|---|---|
| `derived-from` | finding | source or finding | The finding was produced from the target |
| `supports` | source or finding | finding | The source endpoint is evidence for the finding |
| `contradicts` | source or finding | finding | The source endpoint is evidence against the finding |
| `supersedes` | finding | finding | The source finding replaces the target finding |

Lineage records how a finding was reached. It does not make the finding true.

## Producer requirements

A producer claiming draft alignment for a provenance record MUST:

1. Emit a record that validates against the provenance record schema.
2. Preserve unique identities across subjects, sources, findings, and lineage edges within the record.
3. Resolve every source subject and every finding target subject to a subject declared in the record.
4. Resolve every lineage endpoint to a source or finding in the record with an endpoint kind the lineage type permits.
5. Give every finding at least one derived-from edge.
6. Keep every lineage edge free of self-reference, and derived-from and supersedes lineage free of cycles.
7. Not record a source captured_at later than the record created_at.

## Consumer requirements

A consumer claiming draft alignment for provenance records MUST perform
schema and semantic validation of the record before treating it as aligned.

When a consumer has the subject artifact, it MUST validate that artifact
against the schema its own `spec_version` names before resolving references
into it. It MUST NOT report an `aios_object` source or finding target as
resolved unless the subject contains an object with that `id` and declared
`type`; an unavailable subject leaves its references unresolved, not invalid.
A held artifact whose own `id`, `artifact_type` or `spec_version` differs from
the subject entry's `artifact_id`, `artifact_type` or `spec_version` MUST NOT
be used to resolve that entry; the subject entry's `id` is local to the record.

A consumer MUST NOT report a digest as verified unless it recomputed the digest
over the subject bytes it actually holds. A re-emitted artifact that preserves
JSON values can still change bytes, so a digest mismatch shows different
bytes, not different meaning.

A consumer MUST NOT treat a finding's status, severity, confidence or lineage as
evidence that the finding is true. It MUST NOT fetch a `uri` or execute content
merely because a record contains it. It MUST preserve unknown `attributes` and
namespaced `extensions` entries in the record.

## Digests

`digest.algorithm` is one of `sha-256`, `sha-384` or `sha-512`, and
`digest.value` is the lowercase hexadecimal digest of the subject artifact's
exact bytes as published or retrieved. AIOS defines no JSON canonicalization
for digests in this draft.

## Claim format

A claim SHOULD include the draft marker and observation date, for example:

```text
Aligned with AI Operations Specification 0.6-draft provenance records as observed on 2026-10-31.
```

An implementation MUST describe its support for provenance records as aligned
with the 0.6-draft, not stably conformant. Provenance alignment says nothing
about whether the subject artifacts are themselves aligned.

## Privacy

Sources and findings can quote personal data, credentials or proprietary
content. Producers SHOULD reference such material by `uri` or digest rather
than copying it into `description` or `statement`, and SHOULD document any
redaction they apply. Records in this repository use synthetic values.

## Examples

- [Support finding](examples/provenance/support-finding.provenance.json):
  two findings about the [advanced support Run](examples/advanced-support-run.json),
  derived from an in-run evaluation, a retrieval, an external document and a
  human review, with a verifiable `sha-256` digest of the subject.
- The [portable conformance suite](conformance-suite/README.md) holds valid
  and invalid records with the rule each invalid one breaks.
