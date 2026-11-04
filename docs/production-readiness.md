# Production readiness candidate — 0.13

Lens 0.13.0 adds an opt-in single-node project artifact service. It is separate
from `serve-otlp`, which remains a local, unauthenticated developer dashboard.
Do not expose the developer receiver to an untrusted network.

## Scope and compatibility

`agenticlens.enterprise` exports `Project`, `Credential`, `StoragePolicy`,
`RegistryEntry`, `EnterpriseStore`, and `digest`. The optional `[api]` extra
adds `enterprise.http.create_enterprise_app` and the Uvicorn factory
`enterprise.server:create_app`. Existing native Run/Span, evaluation, diagnosis,
routing, optimization, execution-evidence and AIOS draft shapes are unchanged.
The new audit, compliance and gate markers end in `1-candidate`; they are
Lens-local artifacts, not AIOS schemas or Sidecar runtime policy decisions.

The organization/project key is an immutable namespace configured by the host;
there is no organization signup, identity federation, membership editor or
fleet control plane. Each configured credential binds one subject, role and
project. Readers list project traces and registry metadata; writers additionally
store traces, register versions and request release receipts; admins additionally
prune traces and export audit/compliance metadata. Every data route checks both
organization and project. Only `/healthz` is anonymous. OpenAPI and interactive documentation routes are disabled.

## Configure and run

Install `pip install 'agenticlens[api]==0.13.0'`. Generate random bearer tokens
with `secrets.token_urlsafe(32)` and keep them in a secret manager. Store only
SHA-256 hex digests in an operator-owned JSON file:

```json
{
  "credentials": [{
    "subject": "ci-support",
    "token_sha256": "<SHA-256 hex digest of a random token>",
    "project": {"organization": "demo", "name": "support"},
    "role": "writer"
  }],
  "storage_policy": {"max_age_days": 30, "max_traces": 1000, "redact": true},
  "gate_policy": {"min_pass_rate": 1.0, "max_failed_cases": 0}
}
```

```bash
LENS_CONFIG=/secure/config.json LENS_DATABASE=/data/lens.db \
  uvicorn agenticlens.enterprise.server:create_app --factory \
  --host 127.0.0.1 --port 8000 --workers 1 --no-access-log
```

Missing/invalid credentials fail startup. Restart after token removal or rotation;
configuration is copied at startup. Use unique random tokens, TLS at the proxy,
request concurrency/rate limits, and restrictive filesystem permissions. Never
put tokens or sensitive request bodies in proxy logs. The service caps each
artifact request at 2 MiB, including chunked requests. It accepts native Run JSON,
not OTLP, at `POST /v1/organizations/demo/projects/support/traces`. Each POST
replaces that project's trace ID; this endpoint does not merge OTLP batches.

Trace lists return summaries in pages of at most 20 (`limit`/`offset`); use
`GET trace?trace_id=<id>` for one complete native trace. Sensitive run/span/trace
identities are rejected with 422 before storage, rather than redacted into colliding keys.

Registry, audit and compliance reads also accept `limit` (default 20, maximum
100) and `offset`. Audit pages report `has_more`; compliance export bounds each
collection independently and marks `consistent_snapshot: false`. These are live
pages, not a point-in-time database snapshot; concurrent writes can change page
membership. Use an operator-managed stopped-service database backup for an exact
full inventory. SDK metadata reads default to at most 100 records too.

Other project routes: `GET traces`, `GET trace`, `GET/POST registry`, `POST gate`,
`POST retention/prune`, `GET audit`, and `GET compliance`. Send
`Authorization: Bearer <token>` on every request. Registries accept only kind
(`model` or `prompt`), name, version and content SHA-256. Re-registering identical
metadata is idempotent; replacing a version returns 409. Prompt bodies, provider
keys and executable evaluator references are never stored in this registry.

## Policy, gates and private evaluators

The host's `gate_policy` is Evals `GateConfig` policy-as-code. Callers submit
native Evals `EvaluationReport` JSON to `POST gate`; callers cannot override the
server policy. Returned receipts record the exact policy, native gate decision,
canonical report SHA-256 and installed Lens/Evals versions. Save the original
report and receipt, pin both package versions, then call
`enterprise.gates.release_receipt(report, policy)` offline to reproduce the
receipt. No external tools or target callables run. A gate evaluates the submitted
report; it does not authenticate the producer or establish capture completeness.
Use the separate execution-evidence verifier when authenticity is required.

Private evaluators continue to use `EvaluatorRegistry`/`CallableEvaluator` in a
trusted local Python process (see [evaluation guide](evaluation-and-release-gates.md)).
The service accepts their saved native report, never an import path or code.
Standalone scoring and gate computation remain Evals-owned; this service only
composes them. Runtime interception remains Sidecar-owned.

## Retention, PII and audit limits

Common secret fields in metadata, attributes and captured input/output, bearer
strings and email addresses are redacted before trace persistence; native token
counters are preserved. This is pattern-based sanitization, not comprehensive
PII discovery. Use upstream domain-specific redaction, avoid PII in IDs/names,
and authorize recipients. Sanitized traces differ from original evidence; do
not attach an original snapshot's integrity claim to a sanitized copy.

Trace writes prune expired/excess project records transactionally. Reads hide
expired records even before a purge. Schedule an admin `POST retention/prune`
for inactive projects. The policy uses receiver time, not producer timestamps.
Registry metadata and audit records have separate operator-managed archival;
they are not removed by trace retention. Deletion does not erase SQLite free
pages, backups, snapshots or previously exported copies. Use encrypted storage,
a backup expiry policy and secure media disposal for stronger deletion needs.

Mutations and audit inserts share a transaction: if auditing fails the mutation
rolls back. Authenticated authorization denials and successful reads/exports are
also audited; unknown credentials are rejected without creating an attributed
audit record. Subjects are host-managed identifiers; do not use personal data.
Audit rows contain time, sequence, actor, action and object digest, never raw
trace/prompt/token bodies. Compliance export is metadata only and explicitly
`not_assessed`; audit integrity is `not_verified`. Local DB administrators can
rewrite rows. This is neither a signed ledger nor compliance certification.

## Deployment recipes and security acceptance

`deploy/Dockerfile` builds a non-root image. The candidate Helm chart in
`deploy/helm/agenticlens` requires an existing config Secret and an operator-built
image (pin its digest). It runs one replica with Recreate updates, a PVC,
read-only root filesystem, no service-account token, dropped capabilities,
resource limits, probes, ClusterIP and a restrictive network policy. Label
approved same-namespace client/proxy pods `lens-client=<release-name>`.

```bash
docker build -f deploy/Dockerfile -t lens:0.13.0 .
helm lint deploy/helm/agenticlens --set image=example/lens@sha256:<digest> --set configSecret=lens-config
helm template lens deploy/helm/agenticlens --set image=example/lens@sha256:<digest> --set configSecret=lens-config
```

These are candidate deployment recipes, not a claim of cluster certification.
Local automated review covers cross-project reads/writes, role bypass,
invalid/oversized bodies, secret redaction, immutable registry races, persistence,
retention isolation, gate reproducibility and audit rollback (`test_enterprise.py`).
SQLite is a trusted single-node boundary; use one worker and a local block-backed
volume. Horizontal scaling, shared/network filesystems, OIDC/SSO, distributed
audit, legal holds and high availability are outside this release. Cluster
admission, TLS termination, image scanning, encrypted backups, restore drills,
network-policy enforcement and independent security review must pass in the
operator's environment before production approval. These external acceptance
gates and the coordinated ecosystem v1.0 remain open.

## Upgrade and rollback

Back up the SQLite database and config while the service is stopped. Install
0.13.0 with the existing native artifacts unchanged. The new service uses new
`project_traces`, `registry`, and `audit` tables in its own database; it does not
migrate or open the old receiver database. Existing receiver deployments continue
unchanged. To move selected traces, submit reviewed native Run JSON under the
intended project credential; this redacts and re-timestamps the stored copy.
Rollback stops the new service and restores the previous deployment/config;
retain its separate database for export/inspection. Do not downgrade and reuse
a future database without its documented migration path.

Run the offline storage example: `uv run python examples/enterprise_demo.py`.
See [ecosystem matrix](lens-0.13-compatibility.md).
