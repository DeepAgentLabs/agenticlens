# Authenticated evidence verification

Lens authenticates ordered JSON record snapshots without executing their contents.
This Lens-local manifest is not an AIOS execution ledger or an AIOS conformance claim.
Native producer IDs, policy links and payloads are retained unchanged.

```python
import secrets
from agenticlens.integrity import Coverage, seal, verify, replay

key = secrets.token_bytes(32)  # Provision separately; never include in evidence.
records = [{"event_id": "event-1", "kind": "dispatch", "decision_id": "decision-1"}]
manifest = seal(records, key_id="capture-2026-11", key=key,
                coverage=Coverage(stream_id="run-1", description="saved journal", complete=True))
result = verify(records, manifest, trusted_keys={"capture-2026-11": key},
                expected_stream_id="run-1")
assert result.status == "verified"
saved = replay(records, manifest, trusted_keys={"capture-2026-11": key},
               expected_stream_id="run-1")
```

Save records as a JSON array and the manifest with `manifest.model_dump_json()`.
The CLI accepts a separate protected JSON trust store mapping key IDs to hex keys:

```bash
agenticlens evidence verify records.json manifest.json --stream-id run-1 --key-file trusted-keys.json
```

Exit 0 means `verified`; `failed`, `unknown` and `incomplete` exit 1. Results
include authenticated coverage only after authentication and root verification.
Unknown keys do not establish authenticity. Authenticated partial snapshots remain
incomplete; replay requires verified coverage and returns copies in capture order.
Replay invokes no tools, evaluators, callbacks or producer code.

The chain starts with SHA-256 of UTF-8 `lens.evidence-chain/1`. Each next hash
is SHA-256 of the previous raw digest followed by canonical JSON `[index, record]`
(zero-based index). Canonical JSON uses sorted keys, compact separators, ASCII
escaping and rejects NaN/Infinity. Manifest HMAC-SHA256 covers all fields except
`authentication`, using the same canonicalization. Its authenticated count and
root detect modification, reordering, duplication, deletion and tail truncation.

Provision random keys of at least 32 bytes through a trusted channel. Keep the
trust store outside evidence directories with restricted access. Rotate by issuing
a new key ID; retain old trusted keys and manifests for the evidence retention
period. Remove compromised keys: their manifests become unknown. HMAC verifiers
can also forge manifests; use a separate trust service when verifiers must not
have signing authority. This is symmetric authentication, not a public signature.

Retain the expected manifest independently if freshness matters: an attacker can
substitute an older valid snapshot of the same stream. Stream identity comes from
the caller, never from the artifact alone. Whole-snapshot coverage is supported;
range proofs and automatic freshness enforcement are not.

A valid manifest authenticates a snapshot supplied by a key holder. It cannot prove
producer honesty, that every runtime action was captured, or that declared
completeness is true. Replay is recorded evidence inspection, not live reexecution
or automatic reproduction of analysis. AIOS export, causal analysis and a shared
execution/access event schema remain separate work.

## AIOS execution export and downstream integration

`agenticlens.integrity.execution` now exports a native `Run` plus explicitly
supplied `ExecutionRecord` observations to an AIOS `0.4-draft` Run. Both the
spec-owned schema and semantic conformance checks run on export and import.
The packaged schemas are used offline; no remote schemas are fetched.

Spans map to steps, each with a run `contains` relationship and an optional
`parent-of` relationship. Runtime statuses map `succeeded` to `completed`,
`failed` to `failed`, and `running` to `running`. IDs and timestamps are preserved.
Explicit observations map to `io.deepagentlabs.agenticlens.execution.<kind>`
extension events targeted at the recorded run or span. Native actor, policy,
approval, decision and action IDs are preserved, without treating an ALLOW or
BLOCK as actual dispatch. Unknown span references and duplicate event IDs fail.
No proposal, completion or dispatch event is fabricated from span status.

The `io.deepagentlabs.agenticlens.execution` extension retains the complete
native Run, including original metadata, attributes and payloads, plus capture
order and mapping limitations. There are no intended native-field losses; this
makes bundles privileged evidence, subject to the producer's redaction and access
policy. Inputs must be JSON-serializable. Event kind semantics and the lossless
mapping are Lens-owned, not new canonical AIOS meanings. AIOS v0.6 provenance
records describe derived findings and are not an execution-ledger replacement.

`ExecutionBundle` authenticates the whole AIOS artifact as one snapshot record.
The manifest's count is therefore **one artifact**, not the number of events.
All nested records and the lossless extension are covered. On import, Lens also
reconstructs the projection and rejects disagreement with the native evidence,
even when the artifact's MAC is valid. This importer deliberately accepts only
the documented Lens mapping, not arbitrary producers or merged AIOS Runs.

```bash
agenticlens evidence export run.json observations.json bundle.json \
  --key-id capture-2026-11 --key-file trusted-keys.json --complete
agenticlens evidence replay bundle.json \
  --run-id run-1 --key-file trusted-keys.json
```

Omitting `--complete` exports incomplete coverage, which replay refuses. Supply
observations as an array of `ExecutionRecord` objects; native producer attribution
and correlation must come from your host's actual observations. Stop/revoke
acknowledgement events do not establish that all subsequent dispatches were
captured. Missing decision/action IDs remain null; Lens does not infer them.

Use `capture_execution`, `import_execution`, `verify_execution`,
`replay_execution` and `execution_summary` for the corresponding Python APIs.
Run `uv run python examples/evidence/execution_demo.py` for a complete offline
capture-export-import example. Capture order is preserved, not timestamp-sorted;
replay neither calls providers/tools nor reruns arbitrary evaluators.

MCP exposes `lens.execution_verify` with a bundle and an expected `run_id`.
Its trust store is configured on the host through
`DEEP_AGENTIC_CORE_MCP_LENS_TRUST_STORE`; callers cannot supply keys or paths.
Tower accepts `execution_bundle` evidence with an explicit Lens source, run ID
and `0.4-draft` version. Its host injects trusted keys into `EvidenceStore` or
HTTP `create_app`. Both delegate authentication and conformance to Lens.
Verified summaries expose causal IDs; failed, unknown and incomplete summaries
expose no causal claims or native payloads. Neither is an Evals containment score.
Older installed Lens versions degrade to unavailable/unknown until upgraded.
