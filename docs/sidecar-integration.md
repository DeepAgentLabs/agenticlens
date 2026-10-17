# Correlated Sidecar decisions

## Sidecar 0.8 compatibility

Lens 0.7.1 reads `sidecar.correlation/1` through
`agenticlens.integrations.sidecar.attach_decisions(run, records)`. Records must
match the exact run, trace and existing span IDs. Duplicate decisions are
idempotent; conflicting identities and mixed invalid batches are rejected.
All seven outcomes appear as `supervision_decision` timeline events in diagnosis
schema 1.1. BLOCK/ESCALATE do not mark spans, runs or deployments unhealthy.
Decision evidence is not proof of tool execution; the Sidecar journal carries
actual dispatch/completion and must be verified separately. Reasons may contain
sensitive information: callers must authorize recipients. Shared/Exclusive
context privacy and delegated authority remain Sidecar 0.9 validation work.
No Sidecar runtime dependency is added.
