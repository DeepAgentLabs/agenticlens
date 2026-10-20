# Configuration

AgenticLens works with zero configuration. Every setting below is optional
and has a sensible default.

---

## Configuration file

Create `agenticlens.yaml` (or `.agenticlens.yaml`) in the project root or
pass `--config <path>` to any CLI command.

```yaml
# agenticlens.yaml

recommender:
  # RAG chunk utility threshold — chunks below this score are flagged
  rag_min_chunk_utility_score: 0.08    # default: 0.08
  # Minimum number of low-utility chunks before a finding is emitted
  rag_min_low_utility_chunks: 2        # default: 2

pricing:
  # Path to a custom provider pricing JSON file
  # Overrides the bundled fallback; live pricing is still used when available
  custom_pricing_file: null            # default: null

tracing:
  # OTLP/HTTP endpoint for automatic trace export on completion
  otlp_endpoint: null                  # default: null
  # Additional headers sent with every OTLP request
  otlp_headers: {}                     # default: {}
  # Request timeout in seconds
  otlp_timeout_seconds: 10             # default: 10
```

---

## Environment variables

All OTLP settings can also be set via environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `AGENTICLENS_OTLP_TRACES_ENDPOINT` | OTLP/HTTP endpoint URL | — |
| `AGENTICLENS_OTLP_HEADERS` | Comma-separated `Key=Value` pairs | — |
| `AGENTICLENS_OTLP_TIMEOUT_SECONDS` | Request timeout | `10` |

Environment variables take precedence over `agenticlens.yaml` settings.

Example:

```bash
export AGENTICLENS_OTLP_TRACES_ENDPOINT=http://localhost:4318/v1/traces
export AGENTICLENS_OTLP_HEADERS='Authorization=Bearer my-token'
```

---

## Provider pricing

AgenticLens resolves pricing in this order:

1. **Custom pricing file** — set `pricing.custom_pricing_file` in config
2. **Live pricing** — fetched from provider APIs and cached on disk
3. **Bundled fallback** — shipped with the package; never stale at install time

Pricing data is stored in `config/pricing_data.json`.

### Custom pricing file format

```json
{
  "openai": {
    "gpt-4o-mini": {
      "input": 0.00000015,
      "output": 0.0000006
    }
  },
  "anthropic": {
    "claude-3-5-haiku-20241022": {
      "input": 0.0000008,
      "output": 0.000004
    }
  }
}
```

Values are cost per token in USD.

---

## Release gate thresholds

Gate thresholds are passed directly as CLI flags — no configuration file needed.
See [CLI reference — gate](cli-reference.md#gate) for the complete flag reference.

---

## Evaluation suite files

Evaluation suites are YAML or JSON files that define test cases, evaluators,
and per-evaluator thresholds. See [Evaluation and release gates](evaluation-and-release-gates.md).

---

## Redaction

The `trace()` API redacts secrets, bearer tokens, and email addresses from
captured I/O by default. To supply a custom redactor:

```python
def my_redactor(value: str) -> str:
    # Return the sanitized string
    return value.replace("SECRET", "[REDACTED]")

with trace("agent", redactor=my_redactor) as recording:
    ...
```

---

## `serve-otlp` configuration

The live OTLP receiver accepts configuration as CLI flags:

```bash
agenticlens serve-otlp \
  --host 127.0.0.1 \
  --port 4318 \
  --db traces.db \
  --max-traces 200
```

| Flag | Default | Description |
|------|---------|-------------|
| `--host` | `127.0.0.1` | Bind address |
| `--port` | `4318` | Port |
| `--db` | in-memory | SQLite path for persistent storage |
| `--max-traces` | `200` | In-memory trace cap (FIFO eviction) |

**Security note:** The receiver ships with no authentication. Run it only on
localhost or in a trusted network.
