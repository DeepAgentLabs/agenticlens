# Export Formats

AgenticLens supports exporting profiled workflow data in multiple formats.
Below is a preview of what each format looks like with a sample workflow.

---

## JSON

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "name": "Customer Support Agent",
  "start_time": "2026-07-08T10:00:00Z",
  "end_time": "2026-07-08T10:00:02.340Z",
  "steps": [
    {
      "id": "step-001",
      "name": "Planner",
      "type": "planner",
      "provider": "openai",
      "model": "gpt-4o-mini",
      "metrics": {
        "prompt_tokens": 150,
        "completion_tokens": 45,
        "total_tokens": 195,
        "latency": 0.82,
        "ttft": 0.12,
        "cost": 0.000135
      },
      "metadata": {}
    },
    {
      "id": "step-002",
      "name": "Retriever",
      "type": "retriever",
      "provider": null,
      "model": null,
      "metrics": {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "latency": 0.45,
        "ttft": null,
        "cost": null
      },
      "metadata": {"chunk_count": 8, "avg_tokens_per_chunk": 100}
    },
    {
      "id": "step-003",
      "name": "Final Answer",
      "type": "final_response",
      "provider": "openai",
      "model": "gpt-4o-mini",
      "metrics": {
        "prompt_tokens": 320,
        "completion_tokens": 95,
        "total_tokens": 415,
        "latency": 1.07,
        "ttft": 0.15,
        "cost": 0.000367
      },
      "metadata": {}
    }
  ]
}
```

**Usage:**

```python
from agenticlens.exporters import JSONExporter

JSONExporter().export(workflow, "workflow.json")
```

---

## CSV

```csv
step_id,step_name,step_type,provider,model,prompt_tokens,completion_tokens,total_tokens,latency,ttft,cost
step-001,Planner,planner,openai,gpt-4o-mini,150,45,195,0.82,0.12,0.000135
step-002,Retriever,retriever,,,0,0,0,0.45,,
step-003,Final Answer,final_response,openai,gpt-4o-mini,320,95,415,1.07,0.15,0.000367
```

**Usage:**

```python
from agenticlens.exporters import CSVExporter

CSVExporter().export(workflow, "workflow.csv")
```

---

## Markdown

```markdown
# Workflow Report: Customer Support Agent

## Summary

| Metric | Value |
| --- | --- |
| Total Tokens | 610 |
| Total Cost | $0.000502 |
| Latency | 2.34s |
| Steps | 3 |

## Steps

| # | Name | Type | Provider | Model | Prompt Tokens | Completion Tokens | Total Tokens | Latency | Cost |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Planner | planner | openai | gpt-4o-mini | 150 | 45 | 195 | 0.82s | $0.000135 |
| 2 | Retriever | retriever | - | - | 0 | 0 | 0 | 0.45s | - |
| 3 | Final Answer | final_response | openai | gpt-4o-mini | 320 | 95 | 415 | 1.07s | $0.000367 |
```

**Rendered preview:**

| # | Name | Type | Provider | Model | Prompt Tokens | Completion Tokens | Total Tokens | Latency | Cost |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Planner | planner | openai | gpt-4o-mini | 150 | 45 | 195 | 0.82s | $0.000135 |
| 2 | Retriever | retriever | - | - | 0 | 0 | 0 | 0.45s | - |
| 3 | Final Answer | final_response | openai | gpt-4o-mini | 320 | 95 | 415 | 1.07s | $0.000367 |

**Usage:**

```python
from agenticlens.exporters import MarkdownExporter

MarkdownExporter().export(workflow, "report.md")
```

---

## Jira

The Jira exporter posts a formatted comment on an existing Jira issue using Jira's wiki markup syntax.

**How it looks in Jira:**

```text
*AgenticLens Workflow Report: Customer Support Agent*

||Metric||Value||
|Total Tokens|610|
|Total Cost|$0.000502|
|Latency|2.34s|
|Steps|3|

*Step Breakdown:*

||#||Name||Type||Provider||Model||Prompt Tokens||Completion Tokens||Total Tokens||Latency||Cost||
|1|Planner|planner|openai|gpt-4o-mini|150|45|195|0.82s|$0.000135|
|2|Retriever|retriever|-|-|0|0|0|0.45s|-|
|3|Final Answer|final_response|openai|gpt-4o-mini|320|95|415|1.07s|$0.000367|
```

**Rendered in Jira it appears as:**

> **AgenticLens Workflow Report: Customer Support Agent**
>
> | Metric | Value |
> |--------|-------|
> | Total Tokens | 610 |
> | Total Cost | $0.000502 |
> | Latency | 2.34s |
> | Steps | 3 |
>
> **Step Breakdown:**
>
> | # | Name | Type | Provider | Model | Prompt Tokens | Completion Tokens | Total Tokens | Latency | Cost |
> |---|------|------|----------|-------|---------------|-------------------|--------------|---------|------|
> | 1 | Planner | planner | openai | gpt-4o-mini | 150 | 45 | 195 | 0.82s | $0.000135 |
> | 2 | Retriever | retriever | - | - | 0 | 0 | 0 | 0.45s | - |
> | 3 | Final Answer | final_response | openai | gpt-4o-mini | 320 | 95 | 415 | 1.07s | $0.000367 |

**Usage:**

```python
import os
from agenticlens.exporters import JiraExporter

JiraExporter(
    base_url="https://yourteam.atlassian.net",
    user_email=os.environ["JIRA_USER_EMAIL"],
    api_token=os.environ["JIRA_API_TOKEN"],
    issue_key="PROJ-123",
).export(workflow)
```

**Required environment variables:**

| Variable | Description |
|----------|-------------|
| `JIRA_BASE_URL` | Your Jira instance URL (e.g. `https://yourteam.atlassian.net`) |
| `JIRA_USER_EMAIL` | Jira account email |
| `JIRA_API_TOKEN` | API token from [Atlassian settings](https://id.atlassian.com/manage-profile/security/api-tokens) |
| `JIRA_ISSUE_KEY` | Issue to comment on (e.g. `PROJ-123`) |

---

## Choosing a Format

| Format | Best for |
|--------|----------|
| JSON | Programmatic consumption, CI pipelines, dashboards |
| CSV | Spreadsheets, data analysis, pandas workflows |
| Markdown | GitHub PRs/issues, documentation, sharing with team |
| Jira | Sprint tracking, cost-per-ticket attribution, team visibility |
