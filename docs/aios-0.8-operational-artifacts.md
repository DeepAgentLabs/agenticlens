# AIOS operational-artifact compatibility

AIOS repository v0.8.1 distributes the v0.8.0 schema snapshot under MIT.
Run/Workflow remain **0.4-draft**, provenance **0.6-draft**, and operational
companions **0.8-draft**. Independent acceptance and coordinated v1.0 gates remain open.

## Structured judges and diagnosis evidence

AgenticLens 0.14.0 ships marker-routed schema and semantic validation for 0.4-draft Run/Workflow, 0.6-draft provenance and 0.8-draft operational companions, plus held-byte provenance resolution. `export_verification_signal` projects native judge Scores with explicit source, subject and evidence. Unavailable judgments retain null verdict/confidence, and safety stays not_checked. Native findings remain evidence, not proof of execution or recovery.

## Adoption and validation

See [coordinated readiness and examples](coordinated-v1-readiness.md) for the
public API and migration path. The [canonical schemas and rules](https://github.com/DeepAgentLabs/ai-operations-spec/tree/v0.8.1/specification/v0.8)
define the projection contract. Source and citation presence do not authenticate
a producer or verify its conclusion. Reference URIs are not instructions to
fetch or execute anything. Use Lens or MCP for optional schema and semantic
checks; source/native identity and unavailable/unknown states remain explicit.

## Dependencies and rollback

The implementation is released in the owning package's minor version, with no
AIOS Python runtime dependency. Native contracts retain their own versions.
Disable optional companion emission or pin the preceding package version to
roll back; do not relabel a companion as an older artifact family.
