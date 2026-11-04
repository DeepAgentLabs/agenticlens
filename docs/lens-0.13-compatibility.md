# Lens 0.13 ecosystem compatibility

The production-readiness candidate adds optional project artifact storage. It
changes no existing native report, Run/Span or integrity-verification semantics.
No automatic adapter turns the new audit/compliance artifacts into native
Sidecar, Tower, MCP or AIOS evidence.

| Consumer | Dependency / tested boundary | Impact |
| --- | --- | --- |
| agentic-evals 0.12.0 | Lens integrity extra `>=0.12.0,<1`; Lens requires Evals `>=0.11.0,<1` | Existing native reports, gates and optional verifier stay compatible; no floor increase |
| agentic-chaos 0.10.0 | Lens analysis extra `>=0.7.0`; containment extra `>=0.12.0,<1` | Chaos reports/containment remain producer-owned; no range change |
| agentic-sidecar 0.10.0 | Lens extra `>=0.7.1,<1` | Existing decisions/correlation remain native; new service policy controls stored artifacts only |
| Control Tower 0.9.1 | Lens extra `>=0.12,<1` | Native evidence reader and health semantics unchanged; no project/audit ingestion implied |
| MCP 0.6.4 | Hosted recipes pair Lens 0.13.0, Evals 0.12.0, Sidecar 0.10.0 and Chaos 0.10.0 | Patch refreshes the Lens pin; no new enterprise routes exposed as MCP tools |
| AIOS repository 0.7.0 | No Lens runtime dependency | Native exports retain `0.4-draft`; enterprise artifacts are Lens-local candidates |
| Organization profile | Documentation only | Readiness scope and open security/stability gates recorded |

Only MCP needs a package patch because its hosted image pins change. The other
siblings' existing ranges already admit Lens 0.13; their compatibility docs and
examples are updated without unnecessary package releases. Existing installed
optional extras can update Lens normally. Hosting a new enterprise service is an
explicit operator action, never an automatic effect of a sibling upgrade.

## Offline operator example

```python
from agenticlens.enterprise import Project
from agenticlens.models.trace import Run

project = Project(organization="demo", name="support")
run = Run(application_name="support", trace_id="recorded-trace")
assert project.key == "demo/support"
assert run.schema_version == "1.0"  # Existing native trace contract
```

Run `uv run python examples/enterprise_demo.py` for isolated storage, redaction,
registry and metadata export. Run `make check` for Lens acceptance; sibling CI
retains each package's existing producer-specific checks. Package compatibility
is not evidence completeness, runtime containment or a deployment health verdict.
