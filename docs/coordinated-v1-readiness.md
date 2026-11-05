# Coordinated v1.0 engineering readiness

Lens 0.14.0 implements offline validation of Run/Workflow (0.4-draft),
provenance (0.6-draft), and operational companions (0.8-draft). The full 66-case
portable suite and 5 held-byte provenance-resolution cases run without importing
AIOS test code. Schemas and catalogs are bundled with source commit/checksums.

`validate_aios_artifact(path)` routes by the document's declared marker.
An explicit `spec_version=` is an assertion, never a fallback. CLI `validate`
and `conformance` default to the declared marker; `--version` asserts a version.
Schema-only validation sets semantic_checked/aligned false; use conformance
for schema plus semantic alignment. Unsupported marker/type pairs are rejected.
`resolve_provenance(record, held_subject_bytes)` uses only caller-held bytes and
reports availability, identity, digest and reference states separately. A
resolved reference is not an authenticated source or verified conclusion.

`agenticlens.exporters.verification.export_verification_signal` projects native
Evals judge scores with Lens structured verdict metadata. It requires a source
id, attributed subject, evidence references, recording time and method version.
Unavailable/skipped judges have no verdict or confidence. Deterministic scores
are rejected. Native free text/metadata are withheld; grounding detail preserves
item counts as redacted entries and safety remains not_checked. Run
`python examples/operational_artifacts.py` for an offline example.

Migration: existing Run/Workflow calls continue to work. Add explicit version
assertions if callers need to constrain accepted markers. Code that used
schema-only aligned as semantic proof must inspect schema_valid instead or run
conformance. No native trace/report/storage contract changes. Rollback by
pinning 0.13.0 and disabling optional companion exports; retain original native
artifacts and do not relabel new companions as older artifacts.

These acceptances remain open as follow-up work under the
[1.0.0 milestone policy](https://github.com/DeepAgentLabs/.github/blob/main/profile/RELEASE_POLICY.md).

## Coordinated 1.0.0 milestone

Version 1.0.0 marks the coordinated DeepAgentLabs milestone on 2026-11-05.
Development and roadmap delivery continue after this release. Existing draft
and candidate schema markers retain their maturity; package versions do not
certify AIOS conformance or production deployment readiness. Independent review,
independent implementations, security/deployment acceptance, live-provider
validation and the stable contract freeze remain tracked follow-up work.
See the [ecosystem release policy](https://github.com/DeepAgentLabs/.github/blob/main/profile/RELEASE_POLICY.md).
