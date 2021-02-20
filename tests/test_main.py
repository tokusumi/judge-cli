from typer.testing import CliRunner

from judge import app

runner = CliRunner()


def test_app():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0, result.stdout

    result = runner.invoke(app, ["download", "--help"])
    assert result.exit_code == 0, result.stdout
