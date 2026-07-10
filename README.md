# AgenticLens

AgenticLens is an open-source Python profiler for LLM applications and agentic
workflows. It helps developers understand where tokens, latency, and cost are
spent, then turns that profile into actionable budget optimization
recommendations.

Think of it as a lightweight, local `cProfile` for AI workflows: no hosted
dashboard, no required backend, no account, and no data egress just to inspect a
run.

## Why AgenticLens?

LLM applications rarely spend money in one place. Cost often leaks across
planners, retrievers, memory, tool calls, repeated system prompts, and final
response steps.

Most observability tools can show token usage. AgenticLens focuses on the next
question:

> What should I change to reduce the bill?

AgenticLens currently detects patterns such as:

- repeated system prompts that may be cached or deduplicated
- excessive retrieved chunks in RAG workflows
- low-utility retrieved chunks that appear unlikely to affect the final answer
- long conversation history that should be summarized or truncated
- duplicate tool calls that should be cached
- projected token, dollar-per-run, and monthly savings

## Status

AgenticLens is early-stage software. The core profiling, cost calculation,
export, CLI, and rule-based recommendation engine are implemented, but the API
may still evolve before a stable 1.0 release.

## Installation

For local development from this repository:

```bash
git clone https://github.com/agenticlens/agenticlens.git
cd agenticlens
uv sync --extra dev
```

If you do not use `uv`, install in editable mode with development extras:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

## Quickstart

Instrument your workflow with explicit `profile()` and `step()` blocks:

```python
from agenticlens import profile, step

with profile("Customer Support Agent"):
    with step(
        "Planner",
        type="planner",
        provider="openai",
        model="gpt-4o-mini",
        prompt=planner_prompt,
    ) as s:
        response = planner_llm.invoke(planner_prompt)
        s.record(response)

    with step(
        "Retriever",
        type="retriever",
        chunk_count=12,
        avg_tokens_per_chunk=80,
    ):
        chunks = retriever.search(user_question)

    with step(
        "Final Answer",
        type="final_response",
        provider="openai",
        model="gpt-4o-mini",
        final_answer="Refunds are processed to the original payment method.",
    ) as s:
        response = answer_llm.invoke(final_prompt)
        s.record(response)
```

Then profile and analyze a script:

```bash
uv run agenticlens profile examples/recommendations_demo.py --save workflow.json
uv run agenticlens analyze workflow.json
```

Example output:

```text
Budget Optimization Run cost: $0.0068; reducible: ~$0.0024/run (35%), ~$2.38/month.

Optimization Suggestions
  * Long conversation history
  * Excessive retrieved chunks
  * Repeated system prompt
  * Low-utility retrieved chunks
  * Duplicate tool call

Estimated Savings: 35%
```

## Core Concepts

### Workflow

A workflow is one complete execution of an LLM application, such as answering a
customer support question or running a multi-agent task.

```python
with profile("Refund Support"):
    ...
```

### Step

A step is a meaningful unit inside that workflow: planner, retriever, memory,
tool call, LLM call, or final response.

```python
with step("Retrieve Policy Chunks", type="retriever", chunk_count=10):
    ...
```

### Recommendation

A recommendation is a rule-based optimization suggestion. Recommendations carry
token savings, estimated percentage savings, dollar impact when pricing is
known, confidence when relevant, and quality-risk notes for heuristics such as
RAG chunk utility.

## Features

| Area | Capability |
| --- | --- |
| Profiling | Explicit `profile()` and `step()` context managers |
| Metrics | Prompt tokens, completion tokens, total tokens, latency, TPS, cost |
| Providers | OpenAI and Anthropic response usage extraction |
| Costing | Local pricing table plus user pricing overrides |
| Recommendations | Repeated prompts, excessive chunks, low-utility chunks, long history, duplicate tool calls |
| Budget impact | Dollar-per-run and monthly savings projections |
| CLI | `profile`, `report`, and `analyze` commands |
| Export | JSON, CSV, Markdown, and Jira workflow export |
| Tooling | pytest, Ruff, mypy, GitHub Actions |

## Cost Calculation

AgenticLens does not pull live prices from the internet. It uses a local pricing
table in `src/agenticlens/config/pricing.yaml` and this formula:

```text
input_cost = (prompt_tokens / 1000) * input_price_per_1k
output_cost = (completion_tokens / 1000) * output_price_per_1k
total_cost = input_cost + output_cost
```

Pricing resolution order:

1. User-supplied pricing override
2. Bundled `pricing.yaml`
3. Unknown model -> cost is reported as `None`, not `$0.00`

This keeps reporting honest when model pricing is missing or stale.

## RAG Chunk Utility

The RAG utility rule identifies retrieved chunks that are unlikely to influence
the final answer. It supports multiple signal types (in priority order):

| Signal Type | Supported Fields | Source |
| --- | --- | --- |
| Citation | `cited`, `used`, `referenced` (boolean) | Your app logic |
| Reranker | `reranker_score`, `rerank_score`, `cross_encoder_score` (0–1) | Cross-encoder models |
| Embedding | `embedding_similarity`, `cosine_similarity`, `semantic_score` (0–1) | Vector search |
| Generic | `utility_score`, `relevance_score` (0–1) | Custom scoring |
| Fallback | Word-overlap against final answer | Automatic |

Example chunk metadata:

```python
{"text": "...", "reranker_score": 0.92}
{"text": "...", "cosine_similarity": 0.85}
{"text": "...", "cited": True}
{"text": "...", "utility_score": 0.12}
```

When rich signals (reranker, embedding, citation) are available, confidence is
higher and quality risk is lower. If no explicit signals are present, it falls
back to lightweight word-overlap against the final answer.

For a complete guide, see [docs/rag-chunk-utility.md](docs/rag-chunk-utility.md).

## Examples

Run the recommendation demo:

```bash
uv run agenticlens profile examples/recommendations_demo.py --save workflow.json
uv run agenticlens analyze workflow.json
```

Other examples:

- `examples/basic_usage.py`
- `examples/rag_customer_support_demo.py`
- `examples/multiagent_support_demo.py`
- `examples/export_demo.py` — export to Markdown and Jira
- `examples/rag_scoring_demo.py` — RAG chunk utility with reranker/embedding/citation signals

Some examples call real provider APIs and require provider API keys.

## Exporting Reports

### Markdown

```python
from agenticlens.exporters import MarkdownExporter

MarkdownExporter().export(workflow, "report.md")
```

### With Recommendations

All exporters accept an optional `recommendations` parameter (Jira currently ignores it):

```python
from agenticlens.exporters import MarkdownExporter, JSONExporter, CSVExporter
from agenticlens.recommenders import RecommendationEngine

engine = RecommendationEngine()
recs = engine.run(workflow)

MarkdownExporter().export(workflow, "report.md", recommendations=recs)
JSONExporter().export(workflow, "report.json", recommendations=recs)
CSVExporter().export(workflow, "steps.csv", recommendations=recs)
# CSV also writes steps_recommendations.csv alongside
```

### Jira Integration

Post profiling results directly as a comment on a Jira issue:

```python
from agenticlens.exporters import JiraExporter

JiraExporter(
    base_url="https://yourteam.atlassian.net",
    user_email="you@example.com",
    api_token="your-api-token",
    issue_key="PROJ-123",
).export(workflow)
```

Set credentials via environment variables for safety — see
`examples/export_demo.py` for a complete example.

For sample output previews of all formats, see [docs/export-formats.md](docs/export-formats.md).

## CLI Reference

Profile a Python script:

```bash
uv run agenticlens profile app.py
```

Save a workflow report:

```bash
uv run agenticlens profile app.py --save workflow.json
```

Display a saved workflow:

```bash
uv run agenticlens report workflow.json
```

Analyze a saved workflow:

```bash
uv run agenticlens analyze workflow.json
```

## Development

Install development dependencies:

```bash
uv sync --extra dev
```

Run the test suite:

```bash
uv run pytest
```

Run linting, formatting, and type checks:

```bash
uv run ruff check .
uv run ruff format .
uv run mypy
```

Useful targeted checks while working:

```bash
uv run ruff check src tests
uv run ruff format --check src tests
```

## Project Structure

```text
src/agenticlens/
  profiler/       workflow and step profiling
  metrics/        cost and performance calculation
  providers/      provider response usage extraction
  recommenders/   rule-based optimization suggestions
  exporters/      JSON, CSV, Markdown, and Jira exports
  cli/            Typer CLI and Rich rendering
  config/         pricing and settings
  models/         Pydantic data models
```

## Roadmap

Near-term priorities:

- richer RAG utility scoring with citation, reranker, and embedding signals
- model-tier mismatch detection
- prompt caching opportunity detection
- integrations for LangChain, LangGraph, LiteLLM, and OpenAI Agents SDK
- OpenTelemetry and OpenInference trace import
- optional prompt compression handoff

See [ROADMAP.md](ROADMAP.md) and [AgenticLens_Spec.md](AgenticLens_Spec.md) for
more detail.

## Contributing

Contributions are welcome. Good first areas include:

- provider integrations
- recommender rules
- example workflows
- docs and tutorials
- export formats
- test coverage

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

## Security

Please report vulnerabilities privately. See [SECURITY.md](SECURITY.md).

## Code of Conduct

This project follows [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## License

AgenticLens is released under the MIT License. See [LICENSE](LICENSE).
