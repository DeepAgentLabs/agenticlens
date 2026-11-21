# Configuration

AgenticLens uses separate configuration objects for workflow analysis, tracing, ModelFit, routing, optimization and the enterprise artifact service. Use the configuration for the operation you are running.

## Workflow configuration file

`load_config(path)` loads YAML from an explicit path or `AGENTICLENS_CONFIG`; with neither it returns defaults. A file named `agenticlens.yaml` is not discovered automatically. `[tool.agenticlens]` in `pyproject.toml` is not currently read, and there is no universal CLI `--config` flag.

```yaml
# agenticlens.yaml — illustrative pricing, not a provider quote
pricing_overrides:
  "example:demo-model":
    input_per_1k: 0.001
    output_per_1k: 0.002
live_pricing:
  enabled: false
recommender:
  rag_min_chunk_utility_score: 0.08
  rag_min_low_utility_chunks: 2
  monthly_runs: 1000
```

```bash
export AGENTICLENS_CONFIG=./agenticlens.yaml
```

Pass a loaded config explicitly when constructing a recommendation engine:

```python
from agenticlens.config import load_config
from agenticlens.recommenders import RecommendationEngine

engine = RecommendationEngine(config=load_config("agenticlens.yaml").recommender)
```

The `profile()` context loads the configured workflow settings for cost calculation when it finishes. `analyze` currently constructs a recommendation engine with default thresholds; use the Python engine above to apply custom recommender thresholds. The detailed fields/defaults are declared by `AgenticLensConfig`, `RecommenderConfig`, `LivePricingConfig` and `ModelPricing` in the AI reference.

## Provider pricing

Resolution order is explicit `pricing_overrides`, enabled live pricing, bundled `config/pricing.yaml`, then unknown (`None`). Overrides are keyed by `provider:model` and use USD per **1,000 tokens** (`input_per_1k`, `output_per_1k`). They are not USD per token.

Live pricing uses the community-maintained LiteLLM pricing feed, cached by default at `~/.cache/agenticlens/live_pricing_cache.json`, with a 24-hour TTL and five-second request timeout. Configure `live_pricing.url`, `cache_path`, `ttl_seconds` and `timeout_seconds` to change these. Set `AGENTICLENS_DISABLE_LIVE_PRICING=1` to disable live lookup for offline execution. Cache/fallback prices can age; computed costs are estimates unless actual measured provenance is supplied.

## Structured tracing and environment variables

Structured `trace()` takes OTLP arguments directly; these are separate from workflow YAML configuration:

| Variable | Description | Default |
| --- | --- | --- |
| `AGENTICLENS_OTLP_TRACES_ENDPOINT` | OTLP/HTTP endpoint URL | No export |
| `AGENTICLENS_OTLP_HEADERS` | Comma-separated `Key=Value` pairs | Empty headers |
| `AGENTICLENS_OTLP_TIMEOUT_SECONDS` | Export timeout | `10` seconds |
| `AGENTICLENS_CONFIG` | Workflow-analysis YAML path | Built-in workflow defaults |
| `AGENTICLENS_DISABLE_LIVE_PRICING` | Any nonempty value disables live pricing | Unset |

Explicit nonempty endpoint/header arguments take precedence over environment defaults; an explicit timeout is used when it is not `None`. Supply `redactor=` for application-specific capture sanitization.

```python
from agenticlens import trace

with trace("support", otlp_endpoint="http://localhost:4318/v1/traces",
           otlp_timeout_seconds=5.0) as recording:
    pass
```

## Capability-specific configurations

| Operation | Configuration |
| --- | --- |
| [ModelFit](modelfit.md) | `modelfit recommend/taxonomy --config` loads ModelFit YAML/JSON constraints and weights |
| [Routing](routing.md) | `routing decide --policy` loads `RoutingPolicy` JSON |
| [Optimization](optimization.md) | `optimize analyze --config` loads optimization thresholds in YAML/JSON |
| [Enterprise service](production-readiness.md) | `LENS_CONFIG` names service JSON; `LENS_DATABASE` names the SQLite database |
| [Evaluation and experiments](evaluation-and-release-gates.md) | Suite, sample, dataset and experiment-manifest files have distinct contracts |

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
from typing import Any
from agenticlens import trace
from agenticlens.instrumentation.redaction import redact_sensitive


def my_redactor(value: Any) -> Any:
    sanitized = redact_sensitive(value)
    if isinstance(sanitized, str):
        return sanitized.replace("INTERNAL_CODE", "[REDACTED]")
    if isinstance(sanitized, dict):
        return {key: my_redactor(item) for key, item in sanitized.items()}
    if isinstance(sanitized, list):
        return [my_redactor(item) for item in sanitized]
    return sanitized


with trace("agent", redactor=my_redactor) as recording:
    pass
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
