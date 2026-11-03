# Evals 0.11 containment compatibility

Evals 0.11.0 supplies `ContainmentEvaluator` and the six-scenario
`adversarial-containment` pack. It scores actual dispatch/completion and denial
observations separately from task success. Missing evidence, missing policy or
configuration versions, incomplete coverage and bypassed enforcement fail.

Lens 0.12.0 authenticates the exact ordered snapshot. Coverage remains
producer-declared. Chaos 0.10.0 supplies attacks and native scenario assertions;
Sidecar 0.9.2 owns authority, enforcement and effective stop receipts. MCP 0.6.1
pins Evals 0.11.0 and validates scores against the Phase 6 real-adapter harness.
Already-running calls can complete after acknowledgement and remain separately
reported. A BLOCK decision or safe answer alone cannot pass containment.

Use the [Evals guide and passing/failing example](https://github.com/DeepAgentLabs/agentic-evals/blob/main/docs/containment.md):

From an **agentic-evals v0.11.0 checkout**, run:

```bash
uv run --extra integrity python examples/containment/generate.py
uv run --extra integrity agentic-evals evaluate examples/containment/suite.json \
  examples/containment/passing.samples.json \
  --registry examples.containment.registry:registry --out /tmp/containment.json
uv run agentic-evals gate /tmp/containment.json --config examples/containment/gate.json
```

Run those commands from an Evals checkout. Substitute
`post-stop-dispatch.samples.json` or `incomplete.samples.json` to get a failing
gate. The fixture key is public synthetic test material; production trust keys
and expected scope belong to the host, never the evaluated sample.

Native report/gate schema 1.0 is unchanged. Existing optional ranges remain
sufficient except MCP's exact pin, which requires its 0.6.1 patch release.
Lens 0.12.1 also updates report schemas, examples and live-target failure handling.

Lens 0.12.1 requires agentic-evals>=0.11.0,<1. Its integrity verifier remains optional to Evals and supplies verified/failed/unknown/incomplete status. Snapshot authentication does not establish exhaustive capture or runtime enforcement.

Lens 0.12.1 refreshes embedded Evals schemas/examples and preserves native
reports for failed live-target trials. Wrong answers remain completed trials.
The runtime Evals floor becomes 0.11.0; Lens integrity semantics are unchanged.
