# AgenticLens

An open-source profiler for AI agents that analyzes token usage, cost, latency, and optimization opportunities across LLM workflows.



## Install (development)

```bash
uv sync --extra dev
```

## Usage

```python
from agenticlens import profile, step

with profile("Customer Support"):
    with step("Planner", type="planner") as s:
        response = planner_llm.invoke(prompt)
        s.record(response)
```

## Development

```bash
uv run pytest          # tests
uv run ruff check .    # lint
uv run ruff format .   # format
uv run mypy            # type check
```

See [AgenticLens_Spec.md](AgenticLens_Spec.md) for the full project specification and [ROADMAP.md](ROADMAP.md) for what's planned beyond the MVP.
