# TokenLens

An open-source profiler for AI agents that analyzes token usage, cost, latency, and optimization opportunities across LLM workflows.

> **Status:** early scaffold. Core data models, provider abstraction, and the explicit `profile()`/`step()` instrumentation API are in place. The recommendation engine's heuristic rules are not yet implemented — see [TokenLens_Spec.md](TokenLens_Spec.md).

## Install (development)

```bash
uv sync --extra dev
```

## Usage

```python
from tokenlens import profile, step

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

See [TokenLens_Spec.md](TokenLens_Spec.md) for the full project specification and [ROADMAP.md](ROADMAP.md) for what's planned beyond the MVP.
