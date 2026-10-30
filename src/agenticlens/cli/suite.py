"""`agenticlens suite ...`: build, review, approve, and export regression suites.

Editing commands rewrite the suite file in place unless `--save` names another
file. Exit codes: 1 for unusable input, 6 when approval is refused or a stored
version fails verification, 7 when `suite mask --check` finds unmasked PII.
"""

import json
from collections.abc import Callable
from pathlib import Path
from typing import TypeVar

import typer
from agentic_evals import TestCase, TestSuite
from pydantic import BaseModel, ValidationError
from rich.console import Console
from rich.table import Table

from agenticlens.models.trace import Run
from agenticlens.suites import (
    VARIATIONS,
    ApprovalError,
    ConversionResult,
    PIIMasker,
    SuiteImportError,
    SuiteStore,
    SuiteStoreError,
    add_case,
    assign_splits,
    cases_from_feedback,
    cases_from_runs,
    diff_suites,
    drop_duplicates,
    filter_suite,
    find_duplicates,
    generate_variations,
    import_cases,
    load_feedback,
    load_suite_file,
    mask_suite,
    merge_suites,
    parse_ref,
    remove_cases,
    review_cases,
    save_suite_file,
    summarize_suite,
    tag_cases,
)
from agenticlens.suites.models import DOMAIN_KEY, MaskingStrategy, ReviewStatus

suite_app = typer.Typer(
    help="Build, review, approve, and export versioned regression test suites.",
    no_args_is_help=True,
)
console = Console()

APPROVAL_EXIT = 6
PII_EXIT = 7

T = TypeVar("T")

_USER_ERRORS = (OSError, ValueError, KeyError, ValidationError, SuiteImportError)


def _run(action: str, operation: Callable[[], T]) -> T:
    try:
        return operation()
    except ApprovalError:
        raise
    except SuiteStoreError as exc:
        console.print(f"[red]Unable to {action}:[/red] {exc}")
        raise typer.Exit(code=APPROVAL_EXIT) from exc
    except _USER_ERRORS as exc:
        message = exc.args[0] if isinstance(exc, KeyError) and exc.args else exc
        console.print(f"[red]Unable to {action}:[/red] {message}")
        raise typer.Exit(code=1) from exc


def _load(path: Path) -> TestSuite:
    return _run("load suite", lambda: load_suite_file(path))


def _write(suite: TestSuite, source: Path, save: Path | None) -> Path:
    target = save or source
    save_suite_file(suite, target)
    return target


def _write_json(model: BaseModel, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(model.model_dump_json(indent=2) + "\n", encoding="utf-8")


def _store(path: Path) -> SuiteStore:
    return SuiteStore(path)


def _resolve(ref: str, store: Path | None) -> TestSuite:
    """A suite file path, or NAME@VERSION from `--store`."""
    path = Path(ref)
    if path.exists() or store is None:
        return _load(path)
    name, version = _run("read suite reference", lambda: parse_ref(ref))
    return _run("load suite version", lambda: _store(store).load_suite(name, version))


def _report_conversion(result: ConversionResult, kind: str) -> None:
    console.print(f"Converted {len(result.cases)} {kind} into draft case(s) needing review.")
    for item in result.skipped:
        console.print(f"  [yellow]skipped[/yellow] {item.source_id}: {item.reason}")


def _finish_new_suite(
    cases: list[TestCase],
    *,
    name: str | None,
    version: str | None,
    into: Path | None,
    save: Path,
    mask: bool,
    strategy: MaskingStrategy,
    salt: str,
) -> None:
    if not cases:
        console.print("[red]No cases to save.[/red]")
        raise typer.Exit(code=1)
    if into is not None:
        base = _load(into)
        suite = _run(
            "merge cases",
            lambda: merge_suites(
                base, TestSuite(name=base.name, version=base.version, cases=cases)
            ),
        )
    else:
        if not name or not version:
            console.print("[red]--name and --version are required without --into.[/red]")
            raise typer.Exit(code=1)
        suite = _run("build suite", lambda: TestSuite(name=name, version=version, cases=cases))
    if mask:
        suite, report = mask_suite(suite, PIIMasker(strategy=strategy, salt=salt))
        if report.total:
            counts = ", ".join(f"{kind}={count}" for kind, count in report.counts.items())
            console.print(f"Masked {report.total} PII value(s) before saving ({counts}).")
    save_suite_file(suite, save)
    console.print(f"Saved {len(suite.cases)} case(s) to {save}")


_MASK_OPTION = typer.Option(True, "--mask/--no-mask", help="Mask PII before saving.")
_STRATEGY_OPTION = typer.Option("redact", "--strategy", help="PII masking: 'redact' or 'hash'.")
_SALT_OPTION = typer.Option("", "--salt", help="Salt for the 'hash' masking strategy.")
_INTO_OPTION = typer.Option(
    None, "--into", help="Append to this existing suite instead of creating one."
)


def _strategy(value: str) -> MaskingStrategy:
    if value not in ("redact", "hash"):
        console.print("[red]--strategy must be 'redact' or 'hash'.[/red]")
        raise typer.Exit(code=1)
    return "redact" if value == "redact" else "hash"


@suite_app.command("summary")
def suite_summary(
    suite_file: Path = typer.Argument(..., help="Suite JSON or YAML."),
    json_output: bool = typer.Option(False, "--json", help="Print the summary as JSON."),
) -> None:
    """Count cases by split, domain, tag, source, and review status."""
    summary = summarize_suite(_load(suite_file))
    if json_output:
        console.print_json(summary.model_dump_json())
        return
    table = Table(title=f"Suite · {summary.name}@{summary.version}")
    table.add_column("Breakdown")
    table.add_column("Counts")
    table.add_row("Cases", str(summary.total_cases))
    for label, counts in (
        ("Splits", summary.by_split),
        ("Domains", summary.by_domain),
        ("Sources", summary.by_source),
        ("Review", summary.by_review_status),
        ("Tags", summary.by_tag),
    ):
        table.add_row(label, ", ".join(f"{key}={value}" for key, value in counts.items()) or "none")
    console.print(table)


@suite_app.command("import")
def suite_import(
    source: Path = typer.Argument(..., help="CSV, JSON, JSON Lines, or YAML cases."),
    save: Path = typer.Option(..., "--save", help="Suite file to write (.json, .yaml)."),
    name: str | None = typer.Option(None, "--name", help="Suite name (new suites)."),
    version: str | None = typer.Option(None, "--version", help="Suite version (new suites)."),
    into: Path | None = _INTO_OPTION,
    mask: bool = _MASK_OPTION,
    strategy: str = _STRATEGY_OPTION,
    salt: str = _SALT_OPTION,
) -> None:
    """Import test cases from CSV or JSON into a new or existing suite."""
    cases = _run("import cases", lambda: import_cases(source))
    _finish_new_suite(
        cases,
        name=name,
        version=version,
        into=into,
        save=save,
        mask=mask,
        strategy=_strategy(strategy),
        salt=salt,
    )


def _load_runs(paths: list[Path]) -> list[Run]:
    def load() -> list[Run]:
        files: list[Path] = []
        for path in paths:
            files.extend(sorted(path.glob("*.json")) if path.is_dir() else [path])
        return [Run.model_validate_json(file.read_text(encoding="utf-8")) for file in files]

    return _run("load traces", load)


@suite_app.command("from-traces")
def suite_from_traces(
    traces: list[Path] = typer.Argument(..., help="Trace JSON files or directories of them."),
    save: Path = typer.Option(..., "--save", help="Suite file to write."),
    name: str | None = typer.Option(None, "--name"),
    version: str | None = typer.Option(None, "--version"),
    into: Path | None = _INTO_OPTION,
    latency_margin: float = typer.Option(
        1.5, "--latency-margin", min=1.0, help="max_latency_ms = observed x margin."
    ),
    cost_margin: float = typer.Option(
        1.5, "--cost-margin", min=1.0, help="max_cost_usd = observed x margin."
    ),
    include_output: bool = typer.Option(
        False, "--include-output", help="Also expect the recorded output exactly."
    ),
    mask: bool = _MASK_OPTION,
    strategy: str = _STRATEGY_OPTION,
    salt: str = _SALT_OPTION,
) -> None:
    """Convert successful production traces into draft cases for review."""
    result = cases_from_runs(
        _load_runs(traces),
        latency_margin=latency_margin,
        cost_margin=cost_margin,
        include_output=include_output,
    )
    _report_conversion(result, "trace(s)")
    _finish_new_suite(
        result.cases,
        name=name,
        version=version,
        into=into,
        save=save,
        mask=mask,
        strategy=_strategy(strategy),
        salt=salt,
    )


@suite_app.command("from-feedback")
def suite_from_feedback(
    feedback: Path = typer.Argument(..., help="Feedback JSON, JSON Lines, or YAML."),
    save: Path = typer.Option(..., "--save", help="Suite file to write."),
    name: str | None = typer.Option(None, "--name"),
    version: str | None = typer.Option(None, "--version"),
    into: Path | None = _INTO_OPTION,
    traces: list[Path] = typer.Option(
        [], "--traces", help="Traces that feedback refers to (fills a missing input)."
    ),
    mask: bool = _MASK_OPTION,
    strategy: str = _STRATEGY_OPTION,
    salt: str = _SALT_OPTION,
) -> None:
    """Convert user feedback (ratings and corrections) into draft cases for review."""
    records = _run("load feedback", lambda: load_feedback(feedback))
    result = cases_from_feedback(records, runs=_load_runs(traces) if traces else [])
    _report_conversion(result, "feedback record(s)")
    _finish_new_suite(
        result.cases,
        name=name,
        version=version,
        into=into,
        save=save,
        mask=mask,
        strategy=_strategy(strategy),
        salt=salt,
    )


def _parse_input(value: str | None) -> object:
    if value is None:
        return None
    try:
        return json.loads(value) if value.strip().startswith(("{", "[")) else value
    except json.JSONDecodeError:
        return value


@suite_app.command("add-case")
def suite_add_case(
    suite_file: Path = typer.Argument(..., help="Suite to edit."),
    case_id: str = typer.Option(..., "--id"),
    name: str | None = typer.Option(None, "--name"),
    input_value: str | None = typer.Option(None, "--input", help="Text, or a JSON object."),
    expected_output: str | None = typer.Option(None, "--expected-output"),
    contains: list[str] = typer.Option([], "--contains", help="Repeatable expected substring."),
    required_tools: list[str] = typer.Option([], "--required-tool"),
    forbidden_tools: list[str] = typer.Option([], "--forbidden-tool"),
    max_latency_ms: float | None = typer.Option(None, "--max-latency-ms"),
    max_cost_usd: float | None = typer.Option(None, "--max-cost-usd"),
    tags: list[str] = typer.Option([], "--tag"),
    domain: str | None = typer.Option(None, "--domain"),
    save: Path | None = typer.Option(None, "--save", help="Write here instead of in place."),
) -> None:
    """Add an authored case (at least one expectation is required)."""
    suite = _load(suite_file)
    case: dict[str, object] = {
        "id": case_id,
        "name": name or case_id,
        "input": _parse_input(input_value),
        "expected_output": expected_output,
        "expected_contains": contains,
        "required_tools": required_tools,
        "forbidden_tools": forbidden_tools,
        "max_latency_ms": max_latency_ms,
        "max_cost_usd": max_cost_usd,
        "tags": tags,
        "metadata": {DOMAIN_KEY: domain} if domain else {},
    }
    updated = _run("add case", lambda: add_case(suite, case))
    console.print(f"Added {case_id}; saved to {_write(updated, suite_file, save)}")


@suite_app.command("remove-case")
def suite_remove_case(
    suite_file: Path = typer.Argument(..., help="Suite to edit."),
    case_ids: list[str] = typer.Argument(..., help="Case IDs to remove."),
    save: Path | None = typer.Option(None, "--save"),
) -> None:
    """Remove cases by ID."""
    suite = _load(suite_file)
    updated = _run("remove cases", lambda: remove_cases(suite, case_ids))
    console.print(f"Removed {len(case_ids)} case(s); saved to {_write(updated, suite_file, save)}")


@suite_app.command("tag")
def suite_tag(
    suite_file: Path = typer.Argument(..., help="Suite to edit."),
    case_ids: list[str] = typer.Option([], "--case", help="Repeatable; all cases when omitted."),
    add: list[str] = typer.Option([], "--add", help="Tag to add (repeatable)."),
    remove: list[str] = typer.Option([], "--remove", help="Tag to remove (repeatable)."),
    domain: str | None = typer.Option(None, "--domain", help="Domain category to set."),
    save: Path | None = typer.Option(None, "--save"),
) -> None:
    """Add or remove tags and set domain categories."""
    suite = _load(suite_file)
    updated = _run(
        "tag cases",
        lambda: tag_cases(suite, case_ids=case_ids or None, add=add, remove=remove, domain=domain),
    )
    console.print(
        f"Tagged {len(case_ids) or len(suite.cases)} case(s); saved to "
        f"{_write(updated, suite_file, save)}"
    )


@suite_app.command("review")
def suite_review(
    suite_file: Path = typer.Argument(..., help="Suite to edit."),
    status: str = typer.Option(..., "--status", help="accepted, rejected, or needs_review."),
    reviewer: str = typer.Option(..., "--reviewer"),
    case_ids: list[str] = typer.Option([], "--case", help="Repeatable; all cases when omitted."),
    notes: str = typer.Option("", "--notes"),
    save: Path | None = typer.Option(None, "--save"),
) -> None:
    """Record a review decision on cases."""
    if status not in ("accepted", "rejected", "needs_review"):
        console.print("[red]--status must be accepted, rejected, or needs_review.[/red]")
        raise typer.Exit(code=1)
    review_status: ReviewStatus = (
        "accepted"
        if status == "accepted"
        else "rejected"
        if status == "rejected"
        else "needs_review"
    )
    suite = _load(suite_file)
    updated = _run(
        "review cases",
        lambda: review_cases(
            suite,
            status=review_status,
            reviewer=reviewer,
            case_ids=case_ids or None,
            notes=notes,
        ),
    )
    count = len(case_ids) or len(suite.cases)
    console.print(f"Marked {count} case(s) {status}; saved to {_write(updated, suite_file, save)}")


@suite_app.command("mask")
def suite_mask(
    suite_file: Path = typer.Argument(..., help="Suite to mask."),
    strategy: str = _STRATEGY_OPTION,
    salt: str = _SALT_OPTION,
    check: bool = typer.Option(
        False, "--check", help="Only scan; exit 7 when unmasked PII is found."
    ),
    report: Path | None = typer.Option(None, "--report", help="Save the masking report JSON."),
    save: Path | None = typer.Option(None, "--save"),
) -> None:
    """Mask emails, phones, cards, SSNs, IPs, secrets, and sensitive fields."""
    suite = _load(suite_file)
    masked, result = mask_suite(
        suite, PIIMasker(strategy=_strategy(strategy), salt=salt), apply=not check
    )
    if report is not None:
        _write_json(result, report)
    counts = ", ".join(f"{kind}={count}" for kind, count in result.counts.items()) or "none"
    if check:
        console.print(f"Unmasked PII: {result.total} ({counts})")
        for location in result.locations:
            console.print(f"  {location.case_id} · {location.field} · {location.pii_type}")
        if result.total:
            raise typer.Exit(code=PII_EXIT)
        return
    console.print(
        f"Masked {result.total} value(s) ({counts}); saved to {_write(masked, suite_file, save)}"
    )


@suite_app.command("dedupe")
def suite_dedupe(
    suite_file: Path = typer.Argument(..., help="Suite to check."),
    threshold: float = typer.Option(
        0.85, "--threshold", min=0.01, max=1.0, help="Near-duplicate Jaccard threshold."
    ),
    include_variants: bool = typer.Option(
        False, "--include-variants", help="Also compare variants of the same original."
    ),
    drop: bool = typer.Option(False, "--drop", help="Remove duplicates, keeping the first."),
    report: Path | None = typer.Option(None, "--report", help="Save the duplicate report JSON."),
    save: Path | None = typer.Option(None, "--save"),
) -> None:
    """Find exact, near, and conflicting duplicate cases."""
    suite = _load(suite_file)
    result = _run(
        "find duplicates",
        lambda: find_duplicates(suite, threshold=threshold, include_variants=include_variants),
    )
    if report is not None:
        _write_json(result, report)
    console.print(
        f"{len(result.groups)} duplicate group(s), {result.conflicting_groups} conflicting, "
        f"{len(result.duplicate_case_ids)} removable case(s)"
    )
    for group in result.groups:
        marker = "[red]conflict[/red]" if group.conflicting else group.kind
        console.print(f"  {marker} ({group.similarity:.2f}): {', '.join(group.case_ids)}")
    if drop:
        updated = _run("drop duplicates", lambda: drop_duplicates(suite, result))
        console.print(f"Saved {len(updated.cases)} case(s) to {_write(updated, suite_file, save)}")


@suite_app.command("vary")
def suite_vary(
    suite_file: Path = typer.Argument(..., help="Suite to extend."),
    per_case: int = typer.Option(2, "--per-case", min=1, help="Variants per original case."),
    kinds: list[str] = typer.Option(
        [], "--kind", help=f"Repeatable; default all: {', '.join(VARIATIONS)}."
    ),
    seed: int = typer.Option(0, "--seed"),
    save: Path | None = typer.Option(None, "--save"),
) -> None:
    """Add deterministic synthetic input variations (marked needs_review)."""
    suite = _load(suite_file)
    variants = _run(
        "generate variations",
        lambda: generate_variations(suite, per_case=per_case, kinds=kinds or None, seed=seed),
    )
    if not variants:
        console.print("No new variations (inputs unchanged or already present).")
        return
    updated = _run(
        "add variations",
        lambda: merge_suites(
            suite, TestSuite(name=suite.name, version=suite.version, cases=variants)
        ),
    )
    console.print(f"Added {len(variants)} variant(s); saved to {_write(updated, suite_file, save)}")


@suite_app.command("split")
def suite_split(
    suite_file: Path = typer.Argument(..., help="Suite to split."),
    train_ratio: float = typer.Option(0.7, "--train", min=0.0, max=1.0),
    validation_ratio: float = typer.Option(0.15, "--validation", min=0.0, max=1.0),
    test_ratio: float = typer.Option(0.15, "--test", min=0.0, max=1.0),
    seed: int = typer.Option(0, "--seed"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Reassign existing splits too."),
    save: Path | None = typer.Option(None, "--save"),
) -> None:
    """Assign stable train/validation/test splits (variants follow their original)."""
    suite = _load(suite_file)
    updated = _run(
        "assign splits",
        lambda: assign_splits(
            suite,
            train_ratio=train_ratio,
            validation_ratio=validation_ratio,
            test_ratio=test_ratio,
            seed=seed,
            overwrite=overwrite,
        ),
    )
    counts = summarize_suite(updated).by_split
    console.print(", ".join(f"{name}={count}" for name, count in counts.items()))
    for split, ratio in (
        ("train", train_ratio),
        ("validation", validation_ratio),
        ("test", test_ratio),
    ):
        if ratio > 0 and not counts.get(split):
            console.print(f"[yellow]warning:[/yellow] the {split} split is empty")
    console.print(f"Saved to {_write(updated, suite_file, save)}")


@suite_app.command("filter")
def suite_filter(
    suite_file: Path = typer.Argument(..., help="Suite to filter."),
    save: Path = typer.Option(..., "--save"),
    tags: list[str] = typer.Option([], "--tag", help="Keep cases with any of these tags."),
    exclude_tags: list[str] = typer.Option([], "--exclude-tag"),
    domains: list[str] = typer.Option([], "--domain"),
    splits: list[str] = typer.Option([], "--split"),
) -> None:
    """Write the subset of cases matching tags, domains, and splits."""
    suite = _load(suite_file)
    subset = _run(
        "filter suite",
        lambda: filter_suite(
            suite, tags=tags, exclude_tags=exclude_tags, domains=domains, splits=splits
        ),
    )
    save_suite_file(subset, save)
    console.print(f"Saved {len(subset.cases)} of {len(suite.cases)} case(s) to {save}")


@suite_app.command("approve")
def suite_approve(
    suite_file: Path = typer.Argument(..., help="Draft suite to approve."),
    store: Path = typer.Option(..., "--store", help="Suite store directory."),
    approver: str = typer.Option(..., "--approver", help="Who is approving this version."),
    notes: str = typer.Option("", "--notes"),
    parent_version: str | None = typer.Option(
        None, "--parent-version", help="Approved version this one supersedes."
    ),
    allow_unreviewed: bool = typer.Option(
        False, "--allow-unreviewed", help="Approve cases still marked needs_review."
    ),
    allow_pii: bool = typer.Option(False, "--allow-pii", help="Approve unmasked PII as-is."),
) -> None:
    """Check and store a suite as an immutable approved version (exit 6 when refused)."""
    suite = _load(suite_file)
    try:
        record = _run(
            "approve suite",
            lambda: _store(store).approve(
                suite,
                approved_by=approver,
                notes=notes,
                parent_version=parent_version,
                allow_unreviewed=allow_unreviewed,
                allow_pii=allow_pii,
            ),
        )
    except ApprovalError as exc:
        console.print("[red]Approval refused.[/red]")
        for check in exc.checks:
            marker = "[green]✓[/green]" if check.passed else "[red]✗[/red]"
            console.print(f"  {marker} {check.name}: {check.detail}")
        raise typer.Exit(code=APPROVAL_EXIT) from exc
    for check in record.approval.checks:
        console.print(f"  [green]✓[/green] {check.name}: {check.detail}")
    console.print(
        f"Approved {record.name}@{record.version} ({record.case_count} cases, "
        f"sha256 {record.content_sha256[:12]}) by {record.approval.approved_by}"
    )


@suite_app.command("versions")
def suite_versions(
    store: Path = typer.Option(..., "--store", help="Suite store directory."),
    name: str | None = typer.Option(None, "--name", help="Only this suite."),
) -> None:
    """List approved suite versions."""
    records = _run("list versions", lambda: _store(store).versions(name))
    table = Table(title=f"Approved suites · {store}")
    for column in ("Suite", "Version", "Cases", "Approved by", "Approved at", "SHA-256"):
        table.add_column(column)
    for record in records:
        table.add_row(
            record.name,
            record.version,
            str(record.case_count),
            record.approval.approved_by,
            record.approval.approved_at.isoformat(),
            record.content_sha256[:12],
        )
    console.print(table)


@suite_app.command("verify")
def suite_verify(
    refs: list[str] = typer.Argument(None, help="NAME@VERSION refs; all versions when omitted."),
    store: Path = typer.Option(..., "--store", help="Suite store directory."),
    json_output: bool = typer.Option(False, "--json", help="Print results as JSON."),
) -> None:
    """Re-hash stored versions; exit 6 when any is missing or was changed."""
    parsed = _run("read suite references", lambda: [parse_ref(ref) for ref in refs or []])
    results = _run("verify store", lambda: _store(store).verify(parsed or None))
    if json_output:
        console.print_json(json.dumps([result.model_dump(mode="json") for result in results]))
    else:
        for result in results:
            marker = "[green]✓[/green]" if result.ok else "[red]✗[/red]"
            detail = (result.expected_sha256 or "")[:12] if result.ok else result.error
            console.print(f"{marker} {result.name}@{result.version} {detail}")
    if not results:
        if not json_output:
            console.print("[red]No suite versions found.[/red]")
        raise typer.Exit(code=APPROVAL_EXIT)
    if not all(result.ok for result in results):
        raise typer.Exit(code=APPROVAL_EXIT)


@suite_app.command("export")
def suite_export(
    ref: str = typer.Argument(..., help="NAME@VERSION of an approved suite."),
    store: Path = typer.Option(..., "--store", help="Suite store directory."),
    save: Path = typer.Option(..., "--save", help="Suite file for evaluate/evaluate-live."),
    tags: list[str] = typer.Option([], "--tag"),
    exclude_tags: list[str] = typer.Option([], "--exclude-tag"),
    domains: list[str] = typer.Option([], "--domain"),
    splits: list[str] = typer.Option([], "--split"),
) -> None:
    """Export a verified approved version (optionally filtered) for evaluation in CI."""
    name, version = _run("read suite reference", lambda: parse_ref(ref))
    suite = _run("load suite version", lambda: _store(store).load_suite(name, version))
    if tags or exclude_tags or domains or splits:
        suite = _run(
            "filter suite",
            lambda: filter_suite(
                suite, tags=tags, exclude_tags=exclude_tags, domains=domains, splits=splits
            ),
        )
    save_suite_file(suite, save)
    console.print(f"Exported {len(suite.cases)} case(s) of {name}@{version} to {save}")


@suite_app.command("diff")
def suite_diff(
    old: str = typer.Argument(..., help="Suite file, or NAME@VERSION with --store."),
    new: str = typer.Argument(..., help="Suite file, or NAME@VERSION with --store."),
    store: Path | None = typer.Option(None, "--store"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Show cases added, removed, and changed between two suites."""
    result = diff_suites(_resolve(old, store), _resolve(new, store))
    if json_output:
        console.print_json(result.model_dump_json())
        return
    console.print(
        f"{result.old} → {result.new}: {len(result.added)} added, "
        f"{len(result.removed)} removed, {len(result.changed)} changed, "
        f"{result.unchanged} unchanged"
    )
    for case_id in result.added:
        console.print(f"  [green]+[/green] {case_id}")
    for case_id in result.removed:
        console.print(f"  [red]-[/red] {case_id}")
    for change in result.changed:
        console.print(f"  [yellow]~[/yellow] {change.case_id}: {', '.join(change.fields)}")
