"""Offline evidence verification; trust keys stay outside evidence artifacts."""

import json
from pathlib import Path

import typer
from pydantic import ValidationError

from agenticlens.integrity import Manifest, Verification, verify

integrity_app = typer.Typer(help="Verify authenticated Lens evidence snapshots.")


@integrity_app.command("verify")
def verify_command(
    records: Path,
    manifest: Path,
    stream_id: str = typer.Option(..., help="Expected stream from trusted caller context."),
    key_file: Path = typer.Option(..., help="JSON mapping of trusted key IDs to hex keys."),
) -> None:
    """Read a JSON array and manifest. Exit 0 only for verified coverage."""
    try:
        raw = json.loads(records.read_text())
        if not isinstance(raw, list) or any(not isinstance(item, dict) for item in raw):
            raise ValueError("Records must be a JSON array of objects")
        keys = json.loads(key_file.read_text())
        result = verify(
            raw,
            Manifest.model_validate_json(manifest.read_text()),
            trusted_keys={name: bytes.fromhex(value) for name, value in keys.items()},
            expected_stream_id=stream_id,
        )
    except (OSError, ValueError, TypeError, AttributeError, ValidationError):
        result = Verification(status="failed", reason="Invalid evidence, manifest or trust store")
    typer.echo(result.model_dump_json(indent=2))
    if result.status != "verified":
        raise typer.Exit(1)


@integrity_app.command("export")
def export_command(
    run: Path,
    records: Path,
    output: Path,
    key_id: str = typer.Option(...),
    key_file: Path = typer.Option(...),
    complete: bool = typer.Option(False, help="Declare supplied capture complete explicitly."),
) -> None:
    """Export native Run + explicit records to an authenticated AIOS execution bundle."""
    from agenticlens.integrity import Coverage
    from agenticlens.integrity.execution import ExecutionRecord, capture_execution
    from agenticlens.models.trace import Run

    try:
        native = Run.model_validate_json(run.read_text())
        observations = [ExecutionRecord.model_validate(r) for r in json.loads(records.read_text())]
        keys = json.loads(key_file.read_text())
        bundle = capture_execution(
            native,
            observations,
            coverage=Coverage(
                stream_id=native.run_id,
                description="supplied Run and execution records",
                complete=complete,
            ),
            key_id=key_id,
            key=bytes.fromhex(keys[key_id]),
        )
        output.write_text(bundle.model_dump_json(indent=2), encoding="utf-8")
    except (OSError, ValueError, TypeError, KeyError):
        typer.echo("Invalid capture inputs or trust configuration", err=True)
        raise typer.Exit(1) from None


@integrity_app.command("replay")
def replay_command(
    bundle: Path,
    run_id: str = typer.Option(...),
    key_file: Path = typer.Option(...),
) -> None:
    """Verify/import saved AIOS evidence, then print capture-order records offline."""
    from agenticlens.integrity.execution import ExecutionBundle, replay_execution

    try:
        keys = {
            name: bytes.fromhex(value) for name, value in json.loads(key_file.read_text()).items()
        }
        run, records = replay_execution(
            ExecutionBundle.model_validate_json(bundle.read_text()),
            trusted_keys=keys,
            expected_run_id=run_id,
        )
    except (OSError, ValueError, TypeError, AttributeError):
        typer.echo("Execution replay refused: invalid, untrusted or incomplete evidence", err=True)
        raise typer.Exit(1) from None
    typer.echo(json.dumps({"run_id": run.run_id, "records": [r.model_dump() for r in records]}))
