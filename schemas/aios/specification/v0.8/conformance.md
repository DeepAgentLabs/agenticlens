# Operational artifact conformance

Exploratory draft. Requirements apply within `0.8-draft`; earlier review gates
and the coordinated ecosystem release remain prerequisites for stability.

## Validation procedure

Route using [compatibility.json](../v0.5/compatibility.json). An unsupported
marker/type pair has outcome `unsupported` with `AIOS-0.5-V03`. Otherwise run
JSON Schema 2020-12 with date-time/URI format validation, then the semantic
rules below. Schema failures cite `AIOS-0.8-R01`; semantic failures cite every
applicable rule, deduplicated and sorted. No network request is needed.

## Rules

### AIOS-0.8-R01

An operational artifact MUST validate against the schema selected by its declared marker and artifact type.

### AIOS-0.8-R02

Evidence, finding and timeline entry identities MUST be unique across those collections within an artifact.

### AIOS-0.8-R03

Every investigation summary, finding, timeline and recovery citation MUST name an evidence entry declared in that report.

### AIOS-0.8-R04

An audit occurred_at, incident detected_at or timeline occurred_at MUST NOT be later than the enclosing artifact created_at.

### AIOS-0.8-R05

A verification signal with grounded or partial grounding MUST contain at least one evidence reference.

### AIOS-0.8-R06

Observed or contradictory investigation claims and verified recovery MUST cite at least one declared evidence entry.

### AIOS-0.8-R07

An audit event MUST NOT name its own identity in causal_event_ids.

### AIOS-0.8-P01

A projection MUST preserve the source producer, native identity, native format and outcome meaning without inventing absent observations.

### AIOS-0.8-S01

Producers MUST NOT copy credentials, credential hashes, raw tool arguments or privileged context into operational artifacts, including free text, attributes and extensions.

### AIOS-0.8-C01

A consumer MUST perform both schema and semantic validation before describing an operational artifact as draft-aligned.

### AIOS-0.8-C02

A consumer MUST NOT fetch a reference URI or execute its content merely because it appears in an artifact.

### AIOS-0.8-C03

A consumer MUST preserve unknown attributes and namespaced extensions when forwarding an artifact.

### AIOS-0.8-C04

A consumer MUST NOT treat citation presence, a native outcome, confidence or schema validity as proof of factual truth, authorization, safety, containment or successful recovery.

### AIOS-0.8-D01

An implementation MUST NOT describe this exploratory draft as stable AIOS conformance.

## Identity and evidence boundaries

The artifact id, producer identity, subject reference id, affected-target ids
and actor ids have distinct scopes. R02 applies to the evidence collection and,
for investigations, the finding and timeline collections together. Report
citations address only the report-local evidence collection. A reference's id
is a local citation handle; artifact_id identifies the source artifact and
object_id optionally narrows it. format identifies the source contract or AIOS
marker; producer identifies its origin. Native formats are not AIOS markers.

R03 checks declared citation handles, not the existence or content of remote
artifacts. Resolution, digest verification and authentication require separately
held source evidence and an implementation-specific verifier. This family makes
no cross-artifact resolution or journal-completeness claim. The existing
0.6-draft provenance family remains available for evidence lineage and digests.

Causal audit ids may refer to externally held events and need not resolve from
one event. R07 forbids self-reference; this family does not claim global causal
cycle detection from a single event. Times denote timezone-aware instants;
comparison uses instants rather than lexicographic timestamp order. Future
planned actions belong in native plans, not the observed incident timeline.

Process requirements cannot be established by JSON validation. In particular,
strict wrappers reject undeclared fields but cannot detect secrets in arbitrary
strings or prove that an actor was authenticated. Projection code remains
responsible for redaction and truthful mappings.

Every operational envelope includes a required source reference identifying the
native record being projected. This is distinct from a verification subject or
audit target. Retain the original native record under that identity; the
projected artifact id identifies the companion, not its native source.
