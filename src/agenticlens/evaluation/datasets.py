import json
import random
from pathlib import Path

import yaml

from agenticlens.evaluation.models import (
    DatasetLabel,
    DatasetRecord,
    DatasetSummary,
    EvaluationDataset,
    EvaluationSample,
)


def _load_data(path: Path) -> object:
    text = path.read_text(encoding="utf-8")
    return json.loads(text) if path.suffix.lower() == ".json" else yaml.safe_load(text)


def load_dataset(path: Path) -> EvaluationDataset:
    return EvaluationDataset.model_validate(_load_data(path))


def save_dataset(dataset: EvaluationDataset, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dataset.model_dump_json(indent=2), encoding="utf-8")


def dataset_from_samples(
    *,
    name: str,
    version: str,
    samples: list[EvaluationSample],
    description: str = "",
) -> EvaluationDataset:
    return EvaluationDataset(
        name=name,
        version=version,
        description=description,
        records=[
            DatasetRecord(
                case_id=sample.case_id,
                output=sample.output,
                trace=sample.trace,
            )
            for sample in samples
        ],
    )


def dataset_to_samples(
    dataset: EvaluationDataset,
    *,
    split: str | None = None,
) -> list[EvaluationSample]:
    records = [record for record in dataset.records if split is None or record.split == split]
    return [
        EvaluationSample(
            case_id=record.case_id,
            output=record.output,
            trace=record.trace,
        )
        for record in records
    ]


def summarize_dataset(dataset: EvaluationDataset) -> DatasetSummary:
    split_counts: dict[str, int] = {}
    label_counts: dict[str, int] = {}
    total_labels = 0

    for record in dataset.records:
        split_name = record.split or "unassigned"
        split_counts[split_name] = split_counts.get(split_name, 0) + 1
        total_labels += len(record.labels)
        for label in record.labels:
            label_counts[label.score_name] = label_counts.get(label.score_name, 0) + 1

    return DatasetSummary(
        total_records=len(dataset.records),
        split_counts=split_counts,
        labeled_records=sum(1 for record in dataset.records if record.labels),
        total_labels=total_labels,
        label_counts=label_counts,
        tags=sorted({tag for record in dataset.records for tag in record.tags}),
    )


def split_dataset(
    dataset: EvaluationDataset,
    *,
    train_ratio: float = 0.7,
    validation_ratio: float = 0.15,
    test_ratio: float = 0.15,
    seed: int = 0,
) -> EvaluationDataset:
    ratio_sum = train_ratio + validation_ratio + test_ratio
    if min(train_ratio, validation_ratio, test_ratio) < 0:
        raise ValueError("split ratios must be non-negative")
    if abs(ratio_sum - 1.0) > 1e-9:
        raise ValueError("split ratios must add up to 1.0")
    if len(dataset.records) < 3:
        raise ValueError("dataset split requires at least three records")

    shuffled = list(dataset.records)
    random.Random(seed).shuffle(shuffled)
    total = len(shuffled)
    train_end = round(total * train_ratio)
    validation_end = train_end + round(total * validation_ratio)

    if train_end <= 0 or validation_end <= train_end or validation_end >= total:
        raise ValueError(
            "split ratios must produce at least one train, validation, and test record"
        )

    assignments: list[tuple[DatasetRecord, str]] = []
    for index, record in enumerate(shuffled):
        split_name = (
            "train" if index < train_end else "validation" if index < validation_end else "test"
        )
        assignments.append((record, split_name))

    assigned_by_case = {
        record.case_id: record.model_copy(update={"split": split_name})
        for record, split_name in assignments
    }
    return dataset.model_copy(
        update={"records": [assigned_by_case[record.case_id] for record in dataset.records]}
    )


def find_dataset_label(record: DatasetRecord, score_name: str) -> DatasetLabel | None:
    for label in record.labels:
        if label.score_name == score_name:
            return label
    return None
