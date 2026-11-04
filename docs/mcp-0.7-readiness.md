# MCP 0.7 integration readiness — Lens 0.13.0

Lens owns analysis and authenticated execution snapshot verification. MCP does not reinterpret snapshot authentication as exhaustive observation or production readiness. Project artifact-service credentials and MCP/Tower credentials remain distinct.

MCP 0.7.0 completes its local integration-readiness milestone: read-only
`core.compatibility`, packaged candidate matrix, standalone installed-wheel MCP
protocol acceptance and released sibling matrix validation. It reports
`baseline_match`, `different_version` or `not_installed` for local distribution
metadata. Those observations do not certify imported workspace sources, adapter
readiness, a remote service version or hosted deployment health. Use `core.verify`
for adapter probes and Tower discovery for the configured remote contract.

The acceptance baseline is MCP 0.7.0, MCP Python SDK 2.0.0, Lens 0.13.0,
Chaos 0.11.0, Evals 0.12.0, Sidecar 0.10.1, Tower 0.10.0 and AIOS repository
0.7.0. Optional package boundaries and native schemas are unchanged. Explicit
workspace checkouts may override installed producer sources.

This companion update changes documentation only; it requires no dependency
floor change, runtime patch or sibling package release. Publishing MCP does not
deploy AWS. Coordinated ecosystem v1.0, independent AIOS review and operator
security/deployment acceptance remain open gates.

See [MCP support, acceptance commands, upgrades and rollback](https://github.com/DeepAgentLabs/mcp-server/blob/fcdf635d522acc8103173d2f7ef56539222d04b5/docs/release-readiness.md)
and [the executable diagnostic example](https://github.com/DeepAgentLabs/mcp-server/blob/fcdf635d522acc8103173d2f7ef56539222d04b5/examples/compatibility_check.py):

```bash
# Run from an MCP 0.7 checkout:
uv run python examples/compatibility_check.py
```
