from typer.testing import CliRunner

from tokenlens.cli.main import app

runner = CliRunner()


def test_cli_profile_command_exists_but_not_implemented(tmp_path) -> None:
    script = tmp_path / "app.py"
    script.write_text("print('hello')")

    result = runner.invoke(app, ["profile", str(script)])
    assert result.exit_code == 1
    assert "Not yet implemented" in result.output


def test_cli_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "tokenlens" in result.output.lower() or "Usage" in result.output
