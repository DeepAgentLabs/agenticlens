# Configure capture and export

Reference examples below show API composition and configuration fragments. Start with the complete quickstart before adapting these to your application.

## Environment variables

All OTLP settings can also be set via environment variables:

| Variable | Description | Default |
| --- | --- | --- |
| `AGENTICLENS_OTLP_TRACES_ENDPOINT` | OTLP/HTTP endpoint URL | — |
| `AGENTICLENS_OTLP_HEADERS` | Comma-separated `Key=Value` pairs | — |
| `AGENTICLENS_OTLP_TIMEOUT_SECONDS` | Request timeout | `10` |

Environment variables take precedence over `agenticlens.yaml` settings.

Example:

```
export AGENTICLENS_OTLP_TRACES_ENDPOINT=http://localhost:4318/v1/traces
export AGENTICLENS_OTLP_HEADERS='Authorization=Bearer my-token'
```

## Redaction

The `trace()` API redacts secrets, bearer tokens, and email addresses from

captured I/O by default. To supply a custom redactor:

```
def my_redactor(value: str) -> str:
    # Return the sanitized string
    return value.replace("SECRET", "[REDACTED]")

with trace("agent", redactor=my_redactor) as recording:
    ...
```

## `serve-otlp` configuration

The live OTLP receiver accepts configuration as CLI flags:

```
agenticlens serve-otlp \
  --host 127.0.0.1 \
  --port 4318 \
  --db traces.db \
  --max-traces 200
```

| Flag | Default | Description |
| --- | --- | --- |
| `--host` | `127.0.0.1` | Bind address |
| `--port` | `4318` | Port |
| `--db` | in-memory | SQLite path for persistent storage |
| `--max-traces` | `200` | In-memory trace cap (FIFO eviction) |

**Security note:** The receiver ships with no authentication. Run it only on

localhost or in a trusted network.
