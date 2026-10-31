# MCP 0.5.0 hosted access control

[MCP 0.5.0](https://github.com/DeepAgentLabs/mcp-server/releases/tag/v0.5.0) completes MCP Phase 5 with hosted access control. Each hosted key can carry allow and deny tool globs, an expiry and a task scope. The server enforces them at dispatch, outside the model: before each hosted handler runs, it re-authenticates the key and reloads its policy. Revocation, a narrower policy or expiry therefore stops queued calls, retries and calls on existing connections. Calls already running finish. Denied calls return an MCP-local `mcp.access-decision.v1` record, and every hosted call logs `dispatch`/`completion` records that share a `correlation_id`. These records are not AIOS artifacts. `core.access_status` reports a key's effective policy, and operators use `deep-agentic-core-mcp-admin` to narrow or revoke a key by user ID.

## What changes for Lens

- Hosted `lens.*` tools are subject to a key's policy. For example,
  `"allow": ["lens.*"], "deny": ["lens.suite_*"]` permits analysis but not suite
  management.
- Lens analysis, provenance and suite behaviour are unchanged. MCP still
  delegates every judgement to Lens.
- Access evidence is MCP-local. Lens integrity-protected export and verification
  is still open on the Lens roadmap and is not part of this release.

## Compatibility

No Lens API change, dependency bump or release. MCP's hosted pins stay at
`agenticlens==0.11.0`.

See the [MCP hosted access control guide](https://github.com/DeepAgentLabs/mcp-server/blob/v0.5.0/docs/access-control.md).
