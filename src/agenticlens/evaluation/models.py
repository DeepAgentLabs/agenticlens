from typing import Any

from agentic_evals import EvalTrace
from pydantic import BaseModel, Field, model_validator


class DatasetLabel(BaseModel):
    score_name: str = Field(min_length=1)
    expected_value: float | None = Field(default=None, ge=0, le=1)
    expected_passed: bool | None = None
    expected_verdict: str | None = None
    threshold: float | None = Field(default=None, ge=0, le=1)
    notes: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def require_reference_judgment(self) -> "DatasetLabel":
        if (
            self.expected_value is None
            and self.expected_passed is None
            and self.expected_verdict is None
        ):
            raise ValueError(
                "dataset labels must define expected_value, expected_passed, or expected_verdict"
            )
        return self


class DatasetRecord(BaseModel):
    case_id: str
    output: str
    trace: EvalTrace
    split: str | None = Field(default=None, pattern="^(train|validation|test)$")
    tags: list[str] = Field(default_factory=list)
    labels: list[DatasetLabel] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvaluationDataset(BaseModel):
    schema_version: str = "1.0"
    name: str
    version: str
    description: str = ""
    records: list[DatasetRecord]
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def unique_record_ids(self) -> "EvaluationDataset":
        ids = [record.case_id for record in self.records]
        if len(ids) != len(set(ids)):
            raise ValueError("dataset case IDs must be unique")
        if not ids:
            raise ValueError("evaluation dataset must contain at least one record")
        return self


class DatasetSummary(BaseModel):
    total_records: int
    split_counts: dict[str, int] = Field(default_factory=dict)
    labeled_records: int
    total_labels: int
    label_counts: dict[str, int] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)


class ConfidenceInterval(BaseModel):
    lower: float
    upper: float
    confidence_level: float = Field(gt=0, lt=1)
    method: str
