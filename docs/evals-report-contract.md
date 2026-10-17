# Evals native contract compatibility

Agentic Evals 0.7.2 publishes native report (`schema_version: "1.0"`) and
gate-decision JSON Schemas, with offline `report_schema()` and
`gate_decision_schema()` accessors. Contract 1.x evolves additively; readers
should tolerate unknown fields. Lens continues to consume the same native report fields through its existing Evals dependency. Trace capture, calibration, score analysis and diagnosis remain Lens-owned.

See the [contract, examples and compatibility policy](https://github.com/DeepAgentLabs/agentic-evals/blob/main/docs/report-contract.md). Existing dependency
ranges remain sufficient; using the new accessors directly requires
`agentic-evals>=0.7.2`. This documentation alignment needs no sibling patch release.

These schemas validate native Evals output; they do not establish AIOS
conformance. See [AIOS validation and OpenTelemetry](aios-validation-and-otel.md)
for the separate specification validation surface.
