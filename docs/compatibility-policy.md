# Candidate public compatibility policy

Applies to AgenticLens 0.13.x. This is a readiness policy, not a stable v1.0
API freeze. Supported Python versions are 3.10–3.14; CI checks each version.

Public surfaces are documented root exports, documented module exports, console
commands and schemas distributed in the wheel. Leading-underscore modules,
internal helpers, undocumented implementation classes and example outputs are
not stable APIs. New enterprise APIs and `1-candidate` markers are explicitly
candidate surfaces. The HTTP receiver's native trace contract is unchanged.

Patch releases fix defects and refresh compatible dependencies without intended
breaking changes to documented behavior. Minor releases may evolve candidate
APIs, with changelog entries, migration examples and regression checks. Native
schema versions remain independent of package versions; readers should tolerate
unknown additive fields. Breaking native schemas require an explicit new schema
version. A package minor does not silently reinterpret an old schema marker.

Deprecations identify the replacement, affected versions and migration in the
changelog before removal where practical; security/correctness fixes may require
an immediate change with an explicit explanation. Pin package versions and keep
original evidence when reproducibility matters. Gate receipts additionally record
the installed Evals version, policy and report digest. Evals remains the owner
of scoring and gates; AIOS remains exploratory draft and is versioned separately.

See [0.12 → 0.13 migration and rollback](production-readiness.md#upgrade-and-rollback)
and [the tested ecosystem matrix](lens-0.13-compatibility.md). Stable commitments
and external acceptance remain gated by the coordinated ecosystem v1.0 policy.
