# Integrations

AgenticLens is framework-neutral and provider-neutral. It instruments any
Python agent or workflow through its explicit API.

---

## LLM providers

### OpenAI

AgenticLens extracts token usage from OpenAI response objects automatically:

```python
from agenticlens import profile, step
import openai

client = openai.OpenAI()

with profile("OpenAI Workflow"):
    with step("Planner", type="planner", provider="openai", model="gpt-4o-mini") as s:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Plan a trip to Rome."}],
        )
        s.record(response)   # captures prompt_tokens, completion_tokens
```

**Supported response types:** `openai.types.chat.ChatCompletion` (and
compatible objects exposing `.usage.prompt_tokens` / `.usage.completion_tokens`)

### Anthropic

```python
import anthropic
from agenticlens import profile, step

client = anthropic.Anthropic()

with profile("Anthropic Workflow"):
    with step("Planner", type="planner", provider="anthropic", model="claude-3-5-haiku-20241022") as s:
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=256,
            messages=[{"role": "user", "content": "Summarize this."}],
        )
        s.record(response)
```

### Any provider

For providers not natively supported, manually set token counts:

```python
with step("LLM", type="llm_call") as s:
    s.record_tokens(input_tokens=120, output_tokens=30)
```

---

## Agent frameworks

### LangGraph

AgenticLens includes a verified offline LangGraph supervisor reference workflow.
See [Multi-agent reference workflows](multi-agent-reference-workflows.md).

Install the optional extra:

```bash
pip install "agenticlens[langgraph]"
# or
uv sync --extra langgraph
```

Run the reference workflow:

```bash
uv run python examples/reference_workflows/langgraph_supervisor.py
uv run agenticlens inspect examples/reference_workflows/artifacts/langgraph-supervisor.json
```

**Note:** Automatic framework event capture is on the roadmap. Current
instrumentation is explicit — wrap spans around LangGraph node calls.

### Any Python agent

AgenticLens works with any Python agent. Wrap the workflow with `profile()`
and each significant step with `step()`:

```python
from agenticlens import profile, step

with profile("My Custom Agent"):
    with step("Plan", type="planner") as s:
        result = my_agent.plan(task)
        s.record(result.llm_response)

    with step("Execute", type="tool_call"):
        my_agent.execute(result.plan)
```

---

## Observability backends

### OTLP/HTTP collectors (Grafana, Jaeger, etc.)

AgenticLens can export structured trace runs to any OTLP/HTTP-compatible
collector:

```python
from agenticlens import SpanType, trace

with trace(
    "support-agent",
    otlp_endpoint="http://localhost:4318/v1/traces",
    otlp_headers={"Authorization": "Bearer my-token"},
) as recording:
    ...
```

Or via environment variables:

```bash
export AGENTICLENS_OTLP_TRACES_ENDPOINT=http://localhost:4318/v1/traces
```

### Importing third-party OTLP traces

AgenticLens can import OTLP/HTTP JSON traces produced by other tools:

```bash
agenticlens import-otlp third-party-trace.json --save run.json
```

Supports OpenTelemetry GenAI semantic conventions (`gen_ai.*` attributes)
and AgenticLens-native attributes. Unrecognized attributes are preserved.

---

## CI / CD

### GitHub Actions

Wire the release gate into your CI pipeline:

```yaml
- name: Run evaluation
  run: agenticlens evaluate suite.yaml samples.json --save evaluation.json

- name: Apply release gate
  run: agenticlens gate evaluation.json --min-pass-rate 0.95 --min-average-score 0.90
```

Exit code `2` fails the step when the gate is not met.

### Regression detection

```yaml
- name: Compare runs
  run: |
    agenticlens compare results/baseline results/candidate \
      --fail-on-regression \
      --regression-threshold 0.05 \
      --min-samples 5 \
      --save comparison.json
```

---

## agentic-chaos

AgenticLens reads `chaos_events` written by
[agentic-chaos](https://github.com/DeepAgentLabs/agentic-chaos).
When a workflow artifact includes `chaos_events`, the `ChaosImpactRecommender`
surfaces unhandled failures and silent degradation findings automatically.

```bash
agenticlens analyze workflow-with-chaos.json
```

No extra installation is needed. See
[Workflow schema spec — chaos events](workflow-schema-spec.md) for the field format.

---

## Export integrations

| Target | Exporter | Details |
|--------|----------|---------|
| JSON pipelines / CI | `JSONExporter` | [Export formats](export-formats.md) |
| Spreadsheets / pandas | `CSVExporter` | [Export formats](export-formats.md) |
| GitHub PRs / issues | `MarkdownExporter` | [Export formats](export-formats.md) |
| Jira | `JiraExporter` | [Export formats](export-formats.md) |
| OTel collectors | `OTLPTraceExporter` | [AIOS validation and OTel export](aios-validation-and-otel.md) |
