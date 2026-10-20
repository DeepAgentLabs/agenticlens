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

## 0.10.0: Advisory Runtime Routing

Roadmap v0.8 ships with the routing SDK, rules/scores, fail-closed constraints,
bounded provider failover, confidence and host escalation handoffs, explicit
shadow/canary modes and a local routing journal. See [the guide](docs/routing.md)
and [offline acceptance example](examples/routing_demo.py). MCP 0.3.12 pins
Lens 0.10.0 and exposes read-only routing decisions. Existing Evals, Chaos and
Sidecar dependency ranges remain sufficient; Tower and AIOS need no runtime change.
Next is v0.9 Optimization Intelligence.

## 0.9.0: ModelFit

Roadmap milestone v0.7 shipped in 0.9.0: `agenticlens.modelfit` and
`agenticlens modelfit` recommend a model per task category from recorded
experiment reports, under hard quality, cost, latency, safety, provider, and
deployment constraints that fail closed. Each recommendation carries a
confidence level with reasons, an explanation, alternatives, a
provider-diverse fallback, savings against a reference variant tied to the
experiment report's SHA-256, and quality risks; every category also has a
Pareto frontier, a cost-per-success ranking, and a row in the task-level
model matrix. See the [guide](docs/modelfit.md) and the
[v0.7 section of the roadmap](agenticlens-roadmap.md#v07--modelfit).
The next milestone is v0.9 Optimization Intelligence.

Sibling impact: Agentic Sidecar 0.8.4 widens its optional `agenticlens` extra
from `<0.9` to `<1`, and MCP 0.3.11 pins hosted images to Lens 0.9.0 and adds
a read-only `lens.modelfit_recommend` tool. Control Tower, Chaos, Evals, and
the specification need no change; see the
[ecosystem compatibility notes](agenticlens-roadmap.md#090-ecosystem-compatibility).

## 0.8.0: Test-suite and dataset management

Roadmap milestone v0.6 shipped in 0.8.0: `agenticlens.suites` and
`agenticlens suite` build reviewed regression suites from CSV/JSON imports,
production traces, and user feedback, then approve them into immutable,
hash-verified versions that CI verifies, exports, and evaluates. See the
[guide](docs/suite-management.md) and the
[v0.6 section of the roadmap](agenticlens-roadmap.md#v06--test-suite-and-dataset-management).

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

## Chaos 0.8.0 interoperability

Chaos 0.8.0 adds:

- multi-stage chaos workflows: steps, steady-state health checks, parallel
  branches, approval gates that can be resumed, and reusable templates
- declarative YAML/JSON/TOML experiments, with validation that never executes
  targets and cron schedule previews
- `Scope` explosion-radius control (steps, providers and exclusions) on every
  built-in fault and `cascade()`; custom faults get it by calling
  `BaseFault.__init__`, setting `scope` or overriding `in_scope()`
- a topology fuzzer that weights fault placement by fan-out

Native event IDs and fault types are unchanged. Workflow provenance
(`detail.workflow`) and an optional `ChaosReport.workflow` summary are
additive. A workflow's steps merge into one native report for contracts and
AIOS export.

See the [v0.8 guide](https://github.com/DeepAgentLabs/agentic-chaos/blob/v0.8.0/docs/v0.8.md)
and the [offline examples](https://github.com/DeepAgentLabs/agentic-chaos/tree/v0.8.0/examples/workflows).
Workflow statuses, health checks and fuzz outcomes are resilience evidence.
They are not scores, release gates or proof of containment. No new shared
schema, automatic adapter or hosted execution capability is introduced.

Lens reads workflow reports and merged reports as `Workflow` JSON and analyzes their `chaos_events` as before. `detail.workflow` is producer-specific event detail under schema v1.1. Suite conversion rules are unchanged. Chaos's optional `agenticlens>=0.7.0` extra is unchanged, so no dependency bump or Lens patch release is needed.

## Sidecar 0.9.0 interoperability

Task-authority/delegation and reader-safe summaries are available in Sidecar.
See [compatibility and ownership boundaries](docs/sidecar-0.9.md). Existing
native decisions/correlation stay compatible; no new normative schema is claimed.

## AIOS v0.6 examples and extension guidance

See [AIOS v0.6 compatibility](docs/aios-v0.6.md) for canonical examples,
namespace rules and native contract boundaries. AIOS artifacts remain
`0.4-draft`; no runtime dependency bump or package release is required.
