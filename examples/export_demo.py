"""Example: Exporting workflow reports to Markdown and Jira.

This demonstrates how to use the MarkdownExporter and JiraExporter
to share profiling results as human-readable reports or Jira comments.
"""

import os
from datetime import datetime, timezone

from agenticlens import profile, step
from agenticlens.exporters import JiraExporter, MarkdownExporter


class FakeUsage:
    def __init__(self, prompt_tokens: int, completion_tokens: int) -> None:
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens


class FakeResponse:
    def __init__(self, prompt_tokens: int, completion_tokens: int) -> None:
        self.usage = FakeUsage(prompt_tokens, completion_tokens)


def fake_llm_call(prompt: str, tokens: tuple[int, int]) -> FakeResponse:
    return FakeResponse(prompt_tokens=tokens[0], completion_tokens=tokens[1])


def run_workflow():
    """Simulate a multi-step agent workflow and export results."""
    with profile("Customer Support Agent") as workflow:
        with step("Planner", type="planner", provider="openai", model="gpt-4o-mini") as s:
            response = fake_llm_call("Plan the response", (150, 45))
            s.record(response)

        with step("Retriever", type="retriever", chunk_count=8, avg_tokens_per_chunk=100):
            pass  # Simulate retrieval

        with step(
            "Final Answer",
            type="final_response",
            provider="openai",
            model="gpt-4o-mini",
        ) as s:
            response = fake_llm_call("Generate final answer", (320, 95))
            s.record(response)

    return workflow


def export_markdown(workflow) -> None:
    """Export workflow report to a Markdown file."""
    MarkdownExporter().export(workflow, "workflow_report.md")
    print("Markdown report saved to workflow_report.md")


def export_to_jira(workflow) -> None:
    """Export workflow report as a Jira issue comment.

    Requires these environment variables:
      JIRA_BASE_URL   - e.g. https://yourteam.atlassian.net
      JIRA_USER_EMAIL - your Jira account email
      JIRA_API_TOKEN  - API token from https://id.atlassian.com/manage-profile/security/api-tokens
      JIRA_ISSUE_KEY  - e.g. PROJ-123
    """
    base_url = os.environ.get("JIRA_BASE_URL")
    email = os.environ.get("JIRA_USER_EMAIL")
    token = os.environ.get("JIRA_API_TOKEN")
    issue_key = os.environ.get("JIRA_ISSUE_KEY")

    if not all([base_url, email, token, issue_key]):
        print(
            "Skipping Jira export — set JIRA_BASE_URL, JIRA_USER_EMAIL, "
            "JIRA_API_TOKEN, and JIRA_ISSUE_KEY environment variables."
        )
        return

    exporter = JiraExporter(
        base_url=base_url,
        user_email=email,
        api_token=token,
        issue_key=issue_key,
    )
    exporter.export(workflow)
    print(f"Posted workflow report as comment on {issue_key}")


if __name__ == "__main__":
    workflow = run_workflow()

    # Always export Markdown
    export_markdown(workflow)

    # Optionally post to Jira (if env vars are set)
    export_to_jira(workflow)
