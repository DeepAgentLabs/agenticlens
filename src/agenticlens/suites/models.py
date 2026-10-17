"""Data models for test-suite and dataset management.

Draft suites are plain agentic-evals `TestSuite` files that people edit.
AgenticLens records case lineage, review state, domain, and split in each
case's `metadata` under the keys below, so a draft stays a valid suite that
`evaluate` and `evaluate-live` can run unchanged.

An approved suite version is stored as a `SuiteVersion` envelope: the suite
content exactly as approved, its SHA-256, and who approved it. Reports in
this module never carry the original value of a masked field.
"""

from datetime import datetime
from typing import Any, Literal

from agentic_evals import TestCase
from pydantic import BaseModel, Field, model_validator

SUITE_VERSION_SCHEMA_VERSION = "1.0"

# Case metadata keys managed by agenticlens.suites.
DOMAIN_KEY = "domain"
SPLIT_KEY = "split"
SOURCE_KEY = "source"
REVIEW_STATUS_KEY = "review_status"
REVIEWED_BY_KEY = "reviewed_by"
REVIEW_NOTES_KEY = "review_notes"

ReviewStatus = Literal["needs_review", "accepted", "rejected"]
SplitName = Literal["train", "validation", "test"]
SourceKind = Literal["authored", "imported", "trace", "feedback", "synthetic"]
PIIType = Literal[
    "email",
    "phone",
    "credit_card",
    "us_ssn",
    "ipv4",
    "secret",
    "sensitive_field",
]
MaskingStrategy = Literal["redact", "hash"]


class CaseSource(BaseModel):
    """Where a test case came from. Stored under `metadata["source"]`."""

    kind: SourceKind
    trace_id: str | None = None
    run_id: str | None = None
    feedback_id: str | None = None
    parent_case_id: str | None = Field(
        default=None, description="Case this synthetic variation was derived from."
    )
    variation: str | None = None
    seed: int | None = None
    file: str | None = Field(default=None, description="Import file name, without directories.")
    row: int | None = Field(default=None, description="1-based data row or record in the file.")


class SkippedItem(BaseModel):
    """An input that could not become a test case, and why."""

    source_id: str
    reason: str


class FeedbackRecord(BaseModel):
    """User feedback about one agent response.

    Positive feedback confirms `output`; negative feedback needs a
    `corrected_output` to become a test case. `score` (0-1) is used only when
    `rating` is absent, with 0.5 and above counting as positive.
    """

    feedback_id: str = Field(min_length=1)
    input: Any = None
    output: str | None = None
    rating: Literal["positive", "negative"] | None = None
    score: float | None = Field(default=None, ge=0, le=1)
    corrected_output: str | None = None
    comment: str = ""
    trace_id: str | None = None
    run_id: str | None = None
    submitted_by: str | None = None
    tags: list[str] = Field(default_factory=list)
    domain: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def require_signal(self) -> "FeedbackRecord":
        if self.rating is None and self.score is None and self.corrected_output is None:
            raise ValueError("feedback must define rating, score, or corrected_output")
        return self


class FeedbackBatch(BaseModel):
    schema_version: str = "1.0"
    feedback: list[FeedbackRecord]

    @model_validator(mode="after")
    def unique_ids(self) -> "FeedbackBatch":
        ids = [record.feedback_id for record in self.feedback]
        if len(ids) != len(set(ids)):
            raise ValueError("feedback IDs must be unique")
        return self


class ApprovalCheck(BaseModel):
    """One check run before a suite version was approved."""

    name: str
    passed: bool
    detail: str


class ApprovalRecord(BaseModel):
    approved_by: str = Field(min_length=1)
    approved_at: datetime
    notes: str = ""
    checks: list[ApprovalCheck] = Field(default_factory=list)


class SuiteVersion(BaseModel):
    """An approved, immutable suite version.

    `suite` is the agentic-evals `TestSuite` JSON exactly as approved;
    `content_sha256` is computed over its canonical JSON (sorted keys, no
    whitespace), so any later edit to the stored file is detected.
    """

    schema_version: str = SUITE_VERSION_SCHEMA_VERSION
    name: str
    version: str
    status: Literal["approved"] = "approved"
    content_sha256: str = Field(pattern="^[0-9a-f]{64}$")
    case_count: int = Field(ge=1)
    parent_version: str | None = None
    approval: ApprovalRecord
    suite: dict[str, Any]


class VerificationResult(BaseModel):
    name: str
    version: str
    path: str
    ok: bool
    expected_sha256: str | None = None
    actual_sha256: str | None = None
    error: str | None = None


class SuiteSummary(BaseModel):
    name: str
    version: str
    total_cases: int
    by_split: dict[str, int] = Field(default_factory=dict)
    by_domain: dict[str, int] = Field(default_factory=dict)
    by_tag: dict[str, int] = Field(default_factory=dict)
    by_source: dict[str, int] = Field(default_factory=dict)
    by_review_status: dict[str, int] = Field(default_factory=dict)


class CaseChange(BaseModel):
    case_id: str
    fields: list[str]


class SuiteDiff(BaseModel):
    old: str
    new: str
    added: list[str] = Field(default_factory=list)
    removed: list[str] = Field(default_factory=list)
    changed: list[CaseChange] = Field(default_factory=list)
    unchanged: int = 0

    @property
    def is_empty(self) -> bool:
        return not (self.added or self.removed or self.changed)


class DuplicateGroup(BaseModel):
    kind: Literal["exact", "near"]
    case_ids: list[str] = Field(min_length=2)
    keep: str = Field(description="Case kept when duplicates are dropped (the first one).")
    similarity: float = Field(ge=0, le=1, description="Lowest pairwise similarity in the group.")
    conflicting: bool = Field(
        description="True when the cases share an input but expect different results."
    )


class DuplicateReport(BaseModel):
    schema_version: str = "1.0"
    suite_name: str
    threshold: float = Field(ge=0, le=1)
    total_cases: int
    groups: list[DuplicateGroup] = Field(default_factory=list)
    duplicate_case_ids: list[str] = Field(
        default_factory=list, description="Every grouped case except the one kept."
    )
    conflicting_groups: int = 0


class MaskedLocation(BaseModel):
    case_id: str
    field: str = Field(description="Dotted path to the masked value, e.g. input.customer.email.")
    pii_type: PIIType


class MaskingReport(BaseModel):
    schema_version: str = "1.0"
    suite_name: str
    strategy: MaskingStrategy
    applied: bool = Field(description="False for a scan that reported but changed nothing.")
    total: int = 0
    counts: dict[str, int] = Field(default_factory=dict)
    locations: list[MaskedLocation] = Field(default_factory=list)


class ConversionResult(BaseModel):
    """Cases produced from traces or feedback, plus the inputs that were skipped."""

    cases: list[TestCase] = Field(default_factory=list)
    skipped: list[SkippedItem] = Field(default_factory=list)
