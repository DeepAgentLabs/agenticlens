from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.parse import quote
from urllib.request import Request, urlopen

from agenticlens.exporters.base import BaseExporter
from agenticlens.models.recommendation import Recommendation
from agenticlens.models.workflow import Workflow


class JiraExporter(BaseExporter):
    """Exports a workflow profiling summary as a comment on a Jira issue.

    Parameters
    ----------
    base_url:
        Jira instance URL, e.g. ``https://yourteam.atlassian.net``.
    user_email:
        Email address of the Jira user (for basic auth).
    api_token:
        Jira API token (generate at https://id.atlassian.com/manage-profile/security/api-tokens).
    issue_key:
        The Jira issue key to comment on, e.g. ``PROJ-123``.
    """

    def __init__(
        self,
        base_url: str,
        user_email: str,
        api_token: str,
        issue_key: str,
    ) -> None:
        if not base_url.startswith("https://"):
            raise ValueError(
                "base_url must start with https:// to avoid sending"
                " credentials over an insecure connection"
            )
        self.base_url = base_url.rstrip("/")
        self.user_email = user_email
        self.api_token = api_token
        self.issue_key = issue_key

    def export(
        self,
        workflow: Workflow,
        path: str | Path | None = None,
        recommendations: list[Recommendation] | None = None,
    ) -> None:
        """Post workflow metrics as a comment on the configured Jira issue.

        The *path* parameter is accepted for interface compatibility but is not
        used.  If provided, the formatted comment body is also written to that
        file for local reference.
        """
        comment_body = self._build_comment(workflow)

        self._post_comment(comment_body)

        if path is not None:
            Path(path).write_text(comment_body, encoding="utf-8")

    def _build_comment(self, workflow: Workflow) -> str:
        """Build a plain-text summary suitable for a Jira comment."""

        def _jira_text(value: str) -> str:
            return (
                value.replace("\\", "\\\\")
                .replace("|", "\\|")
                .replace("*", "\\*")
                .replace("\r", "")
                .replace("\n", " ")
            )

        lines: list[str] = []
        lines.append(f"*AgenticLens Workflow Report: {_jira_text(workflow.name)}*")
        lines.append("")
        lines.append("||Metric||Value||")
        lines.append(f"|Total Tokens|{workflow.total_tokens:,}|")
        lines.append(f"|Total Cost|{self._fmt_cost(workflow.total_cost)}|")
        lines.append(f"|Latency|{workflow.latency:.2f}s|")
        lines.append(f"|Steps|{len(workflow.steps)}|")
        lines.append("")
        lines.append("*Step Breakdown:*")
        lines.append("")
        lines.append(
            "||#||Name||Type||Provider||Model||Prompt Tokens"
            "||Completion Tokens||Total Tokens||Latency||Cost||"
        )
        for i, s in enumerate(workflow.steps, 1):
            provider = _jira_text(s.provider) if s.provider else "-"
            model = _jira_text(s.model) if s.model else "-"
            lines.append(
                f"|{i}|{_jira_text(s.name)}|{s.type.value}|{provider}"
                f"|{model}|{s.metrics.prompt_tokens:,}"
                f"|{s.metrics.completion_tokens:,}|{s.metrics.total_tokens:,}"
                f"|{s.metrics.latency:.2f}s|{self._fmt_cost(s.metrics.cost)}|"
            )
        return "\n".join(lines)

    def _post_comment(self, body: str) -> Any:
        """Post a comment to the Jira issue via REST API v2 (wiki markup body)."""
        from base64 import b64encode
        from urllib.error import HTTPError, URLError

        url = f"{self.base_url}/rest/api/2/issue/{quote(self.issue_key, safe='')}/comment"
        payload = {"body": body}
        data = json.dumps(payload).encode("utf-8")

        credentials = b64encode(f"{self.user_email}:{self.api_token}".encode()).decode("ascii")

        req = Request(
            url,
            data=data,
            headers={
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )

        try:
            # noqa: S310 — controlled outbound request to user-configured Jira instance
            with urlopen(req, timeout=10) as resp:  # noqa: S310
                return json.loads(resp.read())
        except HTTPError as e:
            raise RuntimeError(f"Jira comment post failed ({e.code}): {e.reason}") from e
        except URLError as e:
            raise RuntimeError(f"Jira comment post failed: {e}") from e

    @staticmethod
    def _fmt_cost(cost: float | None) -> str:
        if cost is None:
            return "-"
        return f"${cost:.6f}"
