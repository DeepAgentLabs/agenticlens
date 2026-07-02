# Contributing

Thanks for helping make `agenticlens` better for everyone building AI agent systems.

## Local setup

```bash
git clone https://github.com/agenticlens/agenticlens.git
cd agenticlens
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
```

Or with `uv`:

```bash
uv sync --extra dev
```

## Development workflow

1. Create a focused branch from `main`.
2. Add or update tests with every behavior change.
3. Run:

```bash
ruff check .
ruff format --check .
mypy
pytest
```

4. Keep PRs focused — one concern per pull request.
5. Write clear commit messages describing *why*, not just *what*.

## Good contributions

- New LLM provider integrations (pricing data, token counting)
- Recommendation engine heuristic rules
- Additional exporters (JSON, CSV, OpenTelemetry, etc.)
- CLI improvements and new report formats
- Documentation, tutorials, and usage examples
- Bug fixes with regression tests
- Performance improvements with benchmarks

## Adding a provider

A good provider integration should include:

1. A pricing module with current model costs
2. Token counting support (or delegation to the provider's tokenizer)
3. Tests covering token estimation and cost calculation
4. Documentation in the provider's docstring

## Adding a recommendation rule

Recommendation rules should:

1. Be opt-in and clearly documented
2. Have well-defined thresholds and rationale
3. Include tests with realistic profiling scenarios
4. Provide actionable suggestions in their output

## Releases

Releases are automated via GitHub Actions when a version tag is pushed. See the release workflow for details.

## Community and security

- Code of conduct: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- Security policy: [SECURITY.md](SECURITY.md)

## Design principles

- Minimal overhead — profiling should not slow down the agent
- Provider-agnostic — support any LLM backend
- Actionable insights over raw metrics
- Zero required configuration for basic usage
- Optional heavy dependencies must remain optional
