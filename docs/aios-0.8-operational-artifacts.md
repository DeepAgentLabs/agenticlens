# AIOS 0.8.0 operational-artifact compatibility

AIOS repository v0.8.0 adds exploratory verification_signal, audit_event and
investigation_report companion artifacts under **0.8-draft**, with incident
context and operator summaries. Earlier Run/Workflow remain 0.4-draft and
provenance remains 0.6-draft. Independent review and coordinated v1.0 gates
remain open.

## Structured judges and diagnosis evidence

JudgeVerdict.verdict/confidence/unsupported_claims/evidence_missed inform verification_signal. Map partially_agree to partially_supports, retain the native verdict, source identity and explicit evidence references. Safety remains not_checked unless separately assessed. Native diagnosis findings can be cited by investigation_report; a suspicion is not an observed cause. Existing Lens conformance support is unchanged; this change does not add 0.8-draft validation or exporters.

## Optional adoption

The [AIOS 0.8.0 compatibility matrix](https://github.com/DeepAgentLabs/ai-operations-spec/blob/v0.8.0/docs/v0.8.0-ecosystem.md)
and [schemas, examples and rules](https://github.com/DeepAgentLabs/ai-operations-spec/tree/v0.8.0/specification/v0.8)
define the projection contract. The examples are synthetic projections of
inspected sibling shapes, not output from shipped sibling adapters.

A future adapter needs schema and semantic checks, source/native identity,
explicit unavailable/unknown states, redaction and unknown-extension
preservation. Register schemas by full $id, route by the document's own marker
and reject unsupported marker/type pairs. Source/citation presence does not
authenticate a producer or verify its conclusion; reference URIs are not
instructions to fetch or execute anything.

## Dependencies and release

This is documentation alignment only. Existing runtime and native contracts
are unchanged. No AIOS Python runtime dependency, optional dependency floor
increase or package patch release is needed. New artifact adoption requires an
explicit implementation and release in the owning package. Roll back optional
companion emission without relabeling it as an older artifact family.
