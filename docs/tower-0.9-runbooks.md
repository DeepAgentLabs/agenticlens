# Control Tower 0.9.0 runbooks compatibility

Control Tower 0.9.0 adds versioned runbooks and recovery workflows. Installed
runbook versions are immutable and declare prerequisites, named string parameters
(each constrained by a pattern, length and optional allowed list) and ordered steps with per-step timeouts, retry limits and optional rollback actions.
Recommendations come only from installed versions. A writer previews an exact
digest, a separate human approves it, and Tower claims each step before
dispatching it to a host-installed connector. Clean failures retry within the step
limit and then run declared rollback actions for completed steps; partial,
timed-out or unknown outcomes stop for reconciliation without replay. A runbook
resolves only after a connector probe, a fresh successful Lens run and a passing
Evals gate for the same run. The supported runtime is a deterministic staging
fixture; production runtime connectors are not included.

Tower owns runbooks, approvals and incident coordination. Lens owns analysis; Evals
owns scoring; Sidecar owns runtime enforcement; Chaos owns resilience testing;
MCP owns tool exposure. AIOS remains the draft shared-semantics authority.

Resolving a runbook requires a fresh successful native Lens run whose run ID differs from the detection run, with no failed Lens run recorded for that run ID. Tower does not compute diagnosis, trace integrity or routing decisions.

MCP 0.5.1 adds local `tower.runbook*` tools over the new routes; approval stays
human-only. No sibling dependency bump, new mandatory import or native artifact
change is needed here. This compatibility update is documentation only and needs
no patch release.

## Example operator workflow

```bash
agenticops-control-tower --token reader-token runbooks recommend INCIDENT_ID
agenticops-control-tower --token writer-token runbooks preview INCIDENT_ID preview.json
agenticops-control-tower --token approver-token runbooks approval EXECUTION_ID approval.json
agenticops-control-tower --token writer-token runbooks execute EXECUTION_ID execute.json
agenticops-control-tower --token writer-token runbooks verify EXECUTION_ID verify.json
```

Use Tower's [runbook guide](https://github.com/DeepAgentLabs/agenticops-control-tower/blob/v0.9.0/docs/runbooks.md) for definitions, step outcomes,
authorization, request bodies and limits, and its
[standalone walkthrough](https://github.com/DeepAgentLabs/agenticops-control-tower/blob/v0.9.0/examples/runbook_recovery.py) for recovery,
compensation and escalation without optional siblings.
