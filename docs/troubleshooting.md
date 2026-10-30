# Troubleshooting

---

## Installation

### `pip install agenticlens` fails

Ensure you are on Python 3.10 or later:

```bash
python --version
```

If the version is below 3.10, install a newer Python or use [pyenv](https://github.com/pyenv/pyenv).

### Dependency conflict with `pydantic`

AgenticLens requires Pydantic v2 (`pydantic>=2.0,<3`). If you have a project
that pins Pydantic v1, install AgenticLens in a separate virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install agenticlens
```

---

## Token capture

### `s.record(response)` captures zero tokens

The provider response object must expose `.usage.prompt_tokens` and
`.usage.completion_tokens`. Objects without this structure are silently
skipped. Use `s.record_tokens()` to set counts manually:

```python
with step("Planner", type="planner") as s:
    response = my_llm.call(prompt)
    # Fallback if response format is unsupported
    s.record_tokens(input_tokens=150, output_tokens=45)
```

### Cost shows `$0.0000`

This happens when:

1. No provider name was passed to `step()` — add `provider="openai"` (or your provider)
2. The model name is unrecognized — check `config/pricing_data.json` or set a custom pricing file
3. Token count is zero — see above

---

## CLI

### `agenticlens: command not found`

The console script is installed into your virtual environment's `bin/` (or `Scripts/` on Windows).
Activate the environment first:

```bash
source .venv/bin/activate
agenticlens --version
```

Or use `uv run`:

```bash
uv run agenticlens --version
```

### `agenticlens analyze` produces no recommendations

Recommendations are evidence-driven. If the workflow has no retriever steps
with `retrieved_chunks`, no duplicate tool calls, and no `chaos_events`, the
engine will produce no findings. Add metadata to your steps to enable the
relevant recommenders.

### `agenticlens gate` exits with code 1 (invalid input)

Exit code `1` means the report file is invalid or the configuration is malformed.
Check that the evaluation report was saved correctly:

```bash
agenticlens evaluate suite.yaml samples.json --save evaluation.json
cat evaluation.json | python -m json.tool   # verify JSON is valid
```

---

## Evaluation

### Suite YAML raises `evaluator not found`

Evaluators must be registered in application code before calling `evaluate_suite`.
Suite YAML files cannot import Python modules. Register the evaluator first:

```python
registry = EvaluatorRegistry()
registry.register(LLMJudgeEvaluator("quality_judge", my_judge_fn))
report = evaluate_suite(suite, samples, registry=registry)
```

### `evaluate-live` with a Python target fails

Ensure the callable path uses the format `module_path.py:function_name` and
that the function returns the expected sample structure. The target is executed
in the same Python process — all imports must be available.

### Case ID mismatch in `calibrate`

The reference label file and evaluation report must have identical suite
`name` and `version`, and all case IDs in the label file must exactly match
case IDs in the report. A mismatch raises an error rather than silently
comparing misaligned evidence.

---

## OTLP / tracing

### OTLP export silently does nothing

1. Verify the endpoint is reachable: `curl http://localhost:4318/v1/traces`
2. Check that `AGENTICLENS_OTLP_TRACES_ENDPOINT` is set or `otlp_endpoint=` is passed to `trace()`
3. Increase `otlp_timeout_seconds` if the collector is slow to respond

### `serve-otlp` raises `address already in use`

Another process is using port 4318. Use a different port:

```bash
agenticlens serve-otlp --port 4319
```

---

## AIOS conformance

### `conformance` raises `spec-root not found`

The `conformance` command looks for the sibling `ai-operations-spec` repository.
Pass `--spec-root` explicitly:

```bash
agenticlens conformance run.json --version 0.4 --spec-root ../ai-operations-spec
```

---

## Docs build

### `mkdocs build --strict` fails

1. Every page listed in `nav` must have a corresponding file in `docs/`
2. Run `uv sync --extra docs` before building
3. Check for broken links in markdown files

```bash
uv sync --extra docs
uv run mkdocs build --strict --site-dir site/docs
```

### `mkdocs serve` shows broken images

Some image paths use MkDocs-specific syntax (e.g. `{ width="420" }`).
These render correctly with `mkdocs serve` but not under `file://`.
Use a local HTTP server instead:

```bash
python -m http.server 8000
```

---

## Getting help

- [GitHub Issues](https://github.com/DeepAgentLabs/agenticlens/issues)
- [CONTRIBUTING.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/CONTRIBUTING.md)
- [CHANGELOG.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/CHANGELOG.md)
