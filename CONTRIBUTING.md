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
3. Add or update user-facing examples when the feature, CLI, output format, or
   workflow changes.
4. If a roadmap item is completed or its status changes, update `README.md`
   and `agenticlens-roadmap.md` in the same pull request.
5. If the work is release-ready, update `pyproject.toml`,
   `src/agenticlens/__init__.py`, and `CHANGELOG.md` as part of the release.
6. Run:

```bash
ruff check .
ruff format --check .
mypy
pytest
```

7. Keep PRs focused — one concern per pull request.
8. Write clear commit messages describing *why*, not just *what*.

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

Releases are automated via GitHub Actions when a version tag is pushed.

### Release checklist

1. Update the version string in all three locations:
   - `pyproject.toml` → `version = "X.Y.Z"`
   - `src/agenticlens/__init__.py` → `__version__ = "X.Y.Z"`
   - `CHANGELOG.md` → add a `## X.Y.Z - YYYY-MM-DD` section
2. Commit: `git commit -am "release: vX.Y.Z"`
3. Tag: `git tag vX.Y.Z`
4. Push: `git push origin main --tags`

The `release-pypi.yml` workflow triggers on the tag push and publishes to PyPI via Trusted Publishing (OIDC).

## Community and security

- Code of conduct: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- Security policy: [SECURITY.md](SECURITY.md)

## Design principles

- Minimal overhead — profiling should not slow down the agent
- Provider-agnostic — support any LLM backend
- Actionable insights over raw metrics
- Zero required configuration for basic usage
- Optional heavy dependencies must remain optional
