# Chaos 0.11 ChaosHub compatibility

Lens 0.13.0 continues reading native Chaos reports and caller-created span markers. Instrument target spans explicitly; recipe names do not establish ground truth for quality or containment. Existing optional ranges admit Chaos 0.11; no Lens release is needed.

Chaos 0.11.0 adds six offline framework-neutral starter recipes, explicit
commit-pinned GitHub registry exchange and opt-in installed fault plugins.
Downloads and catalog listing never execute recipe targets. JSON recipes are
also valid YAML and need no YAML extra. `hub push` stages a contribution in a
caller-owned registry checkout for an ordinary reviewed pull request.

## Offline operator example

Run from an agentic-chaos checkout with its instrumented offline target:

```bash
agentic-chaos hub search rag
agentic-chaos hub pull rag-context-poisoning recipe.json
agentic-chaos chaos run examples/chaoshub_app.py --experiment rag-context-poisoning --save hub-report.json
```

The example deliberately emits a synthetic wrong answer. Availability can pass
while resilience stays inconclusive without quality probes or a fidelity judge.
Review target, probe and workflow paths before running downloaded recipes.
Remote access needs an explicit repository and full commit SHA; plugin loading
executes trusted installed code only when explicitly requested. The native
Chaos report and AIOS export formats are unchanged.

See the [ChaosHub guide](https://github.com/DeepAgentLabs/agentic-chaos/blob/main/docs/v0.11.md)
and [offline app](https://github.com/DeepAgentLabs/agentic-chaos/blob/main/examples/chaoshub_app.py).
Coordinated ecosystem v1.0 acceptance remains open.
