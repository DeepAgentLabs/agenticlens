# AgenticLens Roadmap

See the [implementation audit](ROADMAP_AUDIT.md) for evidence-backed status and
remaining acceptance gaps across every product milestone.

The canonical AgenticLens product roadmap is maintained in
[agenticlens-roadmap.md](agenticlens-roadmap.md).

It also includes a six-month [open-source readiness plan](agenticlens-roadmap.md#open-source-readiness-alongside-feature-delivery) covering reproducibility, interoperability, independent validation, governance, and onboarding.

The separate
[research and development roadmap](AgenticLens_Research_and_Development_Roadmap.md)
documents the supporting research program, experimental metrics, benchmark
design, and publication plan. Research proposals are not product commitments
until they appear in the canonical product roadmap.

## 0.8.0: Test-suite and dataset management

Roadmap milestone v0.6 shipped in 0.8.0: `agenticlens.suites` and
`agenticlens suite` build reviewed regression suites from CSV/JSON imports,
production traces, and user feedback, then approve them into immutable,
hash-verified versions that CI verifies, exports, and evaluates. See the
[guide](docs/suite-management.md) and the
[v0.6 section of the roadmap](agenticlens-roadmap.md#v06--test-suite-and-dataset-management).
The next milestone is v0.7 ModelFit.

## Control Tower 0.6.0 integration

Tower Phase 6 and 6A ship together in 0.6.0 with MCP 0.3.6: evidence-cited
investigation, exact-preview human approval and verified deterministic staging
recovery. Native producer outcomes and package ownership remain unchanged.
See [compatibility, examples and dependency matrix](docs/control-tower-0.6.md).
This is documentation alignment; no package release or dependency bump is needed.

## Evals 0.7.2 report contract

Agentic Evals 0.7.2 publishes native report (`schema_version: "1.0"`) and
gate-decision JSON Schemas, with offline `report_schema()` and
`gate_decision_schema()` accessors. Contract 1.x evolves additively; readers
should tolerate unknown fields. Lens continues to consume the same native report fields through its existing Evals dependency. Trace capture, calibration, score analysis and diagnosis remain Lens-owned.

See the [contract, examples and compatibility policy](https://github.com/DeepAgentLabs/agentic-evals/blob/main/docs/report-contract.md). Existing dependency
ranges remain sufficient; using the new accessors directly requires
`agentic-evals>=0.7.2`. This documentation alignment needs no sibling patch release.

## Chaos 0.7.0 interoperability

Chaos 0.7.0 adds sequential fault cascades, deterministic monotonic breaking-point
search, synthetic response poisoning (including prompt/tool-response instruction
and policy-bypass payloads), and explicit-price retry cost estimates. Native
child event IDs and fault types remain intact; cascade IDs/stages and poisoning
strategy/payload/seed are additive event detail. Existing report readers and
AIOS exports remain compatible.

See the [v0.7 guide and offline synthetic example](https://github.com/DeepAgentLabs/agentic-chaos/blob/v0.7.0/docs/v0.7.md).
The example includes observed synthetic dispatches and a bypassed negative
control. Injection or recovery alone does not prove containment. No new shared
schema, automatic adapter, hosted execution capability or containment guarantee
is introduced.

Lens continues to read chaos_events and diagnose marked spans through existing Chaos span adapters. Suite conversion rules are unchanged. No dependency bump or Lens patch release is needed.

## Control Tower 0.7.0 fleet operations

Tower 0.7.0 adds frozen environment/capability targeting, bulk desired settings,
separate approval, durable per-target results and bounded stop/MCP-revocation
acknowledgement through Python, HTTP and CLI. No fleet atomicity or automatic
rollback/resume is claimed. Timed-out/requested commands need host reconciliation.

Lens retains trace capture, diagnosis and suite management. Enhanced-tracing fleet settings are desired configuration only until a host explicitly applies them; native evidence and health stay independent.

Existing optional dependency ranges remain sufficient. No sibling runtime or
native evidence schema changes are required; this documentation alignment needs
no patch release. See the [operator guide](https://github.com/DeepAgentLabs/agenticops-control-tower/blob/v0.7.0/docs/fleet-operations.md).

See the [local Tower compatibility guide](docs/tower-0.7-fleet-operations.md) for the operator workflow and package boundaries.
