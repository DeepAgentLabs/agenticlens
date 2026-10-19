# MCP 0.4.0 unified workflows

[MCP 0.4.0](https://github.com/DeepAgentLabs/mcp-server/releases/tag/v0.4.0) completes Phase 4 with its unified workflows: `core.compare_runs`, a fail-closed `core.release_check`, `core.incident_summary` and `core.export_report`. MCP judges nothing itself; it composes Lens comparisons, the Evals release gate and Chaos run reports. Malformed or failed-call evidence always blocks readiness, and so does missing evidence of a required kind; all three kinds are required by default and `required_evidence` narrows that.

## What MCP reads

- `core.compare_runs` and `lens.compare_runs` share one path and store the Lens
  comparison in the MCP session.
- `core.release_check` re-validates a supplied comparison with
  `agenticlens.comparison.models.ComparisonReport`; anything that does not
  validate, or a failed call (`ok: false`), is an `invalid` gate.
- Evaluation reports go through `agenticlens.evaluation.evaluate_gate` with a
  `GateConfig`, as `lens.slo_summary` does.

## What blocks a release

Lens-related conditions:

- Any entry in `regressions`.
- A comparison that does not validate as a `ComparisonReport`, or a failed call.
- An evaluation report that fails the Evals gate or is not a valid Evals report.

The release check also blocks on chaos crashes or timeouts, malformed chaos
reports, and any kind listed in `required_evidence` (all three by default) that
is missing. Lens-specific notes:

- `sample_size_guidance` is surfaced in the gate's `observed` values but does not
  block on its own. Compare at least five runs per cohort for stable results.

## Compatibility

No Lens API change, dependency bump or release. MCP keeps its existing optional
Lens import; without Lens the comparison and evaluation gates report `invalid`.

See the [MCP unified workflows guide](https://github.com/DeepAgentLabs/mcp-server/blob/v0.4.0/docs/unified-workflows.md).
