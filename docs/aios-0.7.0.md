# AIOS repository v0.7.0 compatibility

AIOS v0.7.0 adds non-normative migration guidance, an OpenTelemetry companion
profile pinned to upstream semantic conventions 1.37.0, tested retry examples,
and a strict MkDocs publishing pipeline. Run/Workflow remain `0.4-draft`;
provenance remains `0.6-draft`. Independent-review gates remain open.

Existing trace exports and conformance checks keep their current meaning. Lens already supports [OTLP/HTTP export](aios-validation-and-otel.md);
this release does not change it or claim that it implements the new companion profile.

No runtime dependency floor changes or package patch release are required.
This is documentation alignment; it does not add an automatic exporter or
migration adapter. The paired telemetry example is illustrative, not OTLP JSON.

For an offline example, clone AIOS at tag `v0.7.0`, run `uv sync --extra dev`,
then `uv run pytest tests/test_otel_binding.py tests/test_v06_conformance_suite.py`.
Use `make docs` to build its browsable documentation. These are specification
repository checks, not commands supplied by this package.

See the [migration guide](https://github.com/DeepAgentLabs/ai-operations-spec/blob/v0.7.0/specification/v0.6/migration-guide.md),
[OTel profile](https://github.com/DeepAgentLabs/ai-operations-spec/blob/v0.7.0/specification/v0.6/otel-binding.md)
and [dependency matrix](https://github.com/DeepAgentLabs/ai-operations-spec/blob/v0.7.0/docs/v0.7.0-ecosystem.md).

Repository v0.7.0 supersedes the same-day v0.6.2 publication; the historical
tag remains available. Artifact markers and independent-review gates do not change.
