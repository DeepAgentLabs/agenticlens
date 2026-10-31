# Roadmap

This page lists planned capabilities for AgenticLens. None of these features
are implemented today. For implemented capabilities, see [Features](features.md).

For the detailed research and development roadmap, see
[AgenticLens Research and Development Roadmap](https://github.com/DeepAgentLabs/agenticlens/blob/main/AgenticLens_Research_and_Development_Roadmap.md)
and the [Product Roadmap](https://github.com/DeepAgentLabs/agenticlens/blob/main/agenticlens-roadmap.md)
on GitHub.

---

## Instrumentation

| Capability | Status |
|------------|--------|
| Automatic framework adapters (LangGraph, LangChain, CrewAI, AutoGen) | Planned |
| Streaming response token capture | Planned |
| OpenTelemetry SDK integration (instrument and export in one step) | Planned |
| Async span recording | Planned |

---

## Evaluation

| Capability | Status |
|------------|--------|
| Batched and asynchronous evaluation | Planned |
| Built-in provider client for LLM-as-a-Judge | Planned |
| Multi-metric evaluation leaderboards | Planned |
| Automatic test case generation from traces | Planned |
| Regression test suites tied to trace baselines | Planned |

---

## Analysis and recommendations

| Capability | Status |
|------------|--------|
| Statistical significance reporting in comparison | Planned |
| Causal attribution analysis | Planned |
| Agent topology visualization | Planned |
| Drift detection across rolling windows | Planned |
| Lineage and provenance fields (Workflow Spec v1.x) | Planned |
| Evaluation and audit evidence fields (Workflow Spec v1.x) | Planned |
| Price-sheet re-costing of optimization savings | Planned |
| Optimization outcome evaluation with controlled rollouts (canary cohorts) | Planned |

---

## Dashboard and reporting

| Capability | Status |
|------------|--------|
| Interactive web dashboard (standalone, no backend) | Planned |
| Shareable report links | Planned |
| Team annotation and review workflow | Planned |

---

## Workflow Specification

| Version | Field | Primary producer | Status |
|---------|-------|------------------|--------|
| v1.2 | `agent_topology` | `agentic-chaos` | Planned |
| v1.3 | Drift-report fields | `agentic-chaos` | Planned |
| v1.x | Lineage and provenance fields | `agenticlens` | Planned |
| v1.x | Evaluation and audit evidence | `agenticlens` | Planned |

---

## Integrations

| Integration | Status |
|-------------|--------|
| `agentic-evals` standalone release-gate boundary | Planned |
| `agenticops-control-tower` attribution surface | Planned |
| `agentic-sidecar` decision and escalation events | Planned |
| `deep-agentic-core-mcp` MCP-native analysis tools | Planned |
| Prometheus / Grafana metrics export | Planned |
| Slack / PagerDuty alerting on gate failures | Planned |

---

## Platform

| Capability | Status |
|------------|--------|
| WebSocket / SSE live dashboard updates | Planned |
| Multi-user trace store with access control | Planned |
| Hosted SaaS option | Under evaluation |
