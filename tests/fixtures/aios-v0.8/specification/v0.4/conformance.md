# v0.4 Draft Conformance

Because v0.4 is pre-release, implementations MUST describe themselves as **aligned with the v0.4 draft**, not stably conformant.

## Producer requirements

A producer claiming draft alignment MUST:

1. Emit an artifact that validates against the schema selected by `artifact_type`.
2. Preserve globally unique object identities within a Run artifact.
3. Preserve unique relationship and event identities.
4. Ensure an end timestamp does not precede its start timestamp.
5. Resolve every non-external relationship endpoint to an object in the artifact with the declared type.
6. Contain every Step in its Run exactly once.
7. Connect every runtime occurrence to exactly one Step using `observed-in`.
8. Give every Evaluation at least one `evaluates` target.
9. Support `workflow_id` with a matching `run-of` relationship.
10. Ensure event targets resolve with the declared object type.
11. Reject self-relationships and cycles in structural, causal, and ordering graphs.
12. When representing retries, preserve distinct occurrence identities for each
    attempt and link each retry attempt to the prior attempt with an explicit
    recoverability edge such as `follows` or `caused`.

An external reference MUST set `external: true`. External resolution is the consumer's responsibility and MUST NOT be reported as verified unless it was resolved.

## Consumer requirements

A consumer claiming draft alignment MUST perform schema and semantic validation before treating an artifact as aligned. It MUST preserve unknown namespaced extensions and MUST NOT interpret structural validity as factual accuracy.

## Unknown-value behavior (decision `D-004`)

Closed vocabularies — `object_type`, reference `type`, relationship `type`, `occurrence`/`evidence` `type`, and the canonical `event_name` catalog — are fixed by this draft's schemas. A value outside a closed vocabulary is a schema violation, not an unknown value to tolerate: producers MUST NOT invent new members of a closed enum, and consumers MUST reject an artifact that contains one rather than guessing its meaning.

Forward-compatible growth belongs in the two open extension points instead:

1. Freeform `attributes` objects, which MAY carry any producer-defined keys.
2. Namespaced `extensions` objects, which MUST use a reverse-domain name outside the `aiops` namespace.

Consumers MUST preserve unrecognized `attributes` keys and namespaced `extensions` entries rather than discarding them, and MUST NOT treat their presence as a validation failure.

## Claim format

A claim SHOULD include the draft marker and observation date, for example:

```text
Aligned with AI Operations Specification v0.4-draft as observed on 2026-07-21.
```

No compatibility across different draft snapshots is promised.
