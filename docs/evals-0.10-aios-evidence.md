# Evals 0.10.0 evaluation evidence compatibility

[Agentic Evals 0.10.0](https://github.com/DeepAgentLabs/agentic-evals/releases/tag/v0.10.0)
delivers its roadmap v0.10: `to_aios_evidence()` exports an evaluation report
as AI Operations Specification `0.4-draft` `evaluation` evidence, and
`attach_aios_evidence()` merges it into an existing `run` artifact. The CLI
path is `agentic-evals aios export`.

## Validating with Lens

Lens's own AIOS validator accepts the merged Run. The Evals example
(`examples/aios/run-with-evaluations.json`) reports `schema_valid`,
`semantic_valid` and `aligned` as true with no issues:

```bash
agenticlens validate run-with-evaluations.json --spec-root ../ai-operations-spec
```

Each evaluation has an `evaluates` target that resolves in the Run (rule
`AIOS-0.4-P08`). Evals refuses to export without a mapping and refuses to
attach to a target that is not in the Run.

## Ownership

- Lens still owns traces, calibration, experiments, diagnosis and its AIOS
  conformance tooling. Evals derives evidence only from its native report and
  never reads Lens traces.
- To attach Evals evidence to a Run that Lens exported, map each Evals case to
  the Step or occurrence whose output it scored. Use `external: true` for a
  Lens trace that is not in the Run. Evals never infers the mapping.
- Judge usage keys (`judge_*`) ride in each evaluation's attributes as score
  metadata. They are not added to the Run's `measurements`, so judge spend is
  never counted as the run's own cost.
- Unavailable judgments are exported as `unavailable` with no score, and cases
  with no observed output are reported in `unobserved_cases`. Neither reads as
  a pass.

Native report schema 1.0 is unchanged. Lens 0.10.0's full test suite passes
against Evals 0.10.0 (723 tests), and `agentic-evals>=0.7.1,<1` already allows
it. No Lens change or release is needed.
See the [Evals guide](https://github.com/DeepAgentLabs/agentic-evals/blob/v0.10.0/docs/aios-evidence.md).
