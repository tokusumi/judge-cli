import pytest
from typer.testing import CliRunner

from judge import app

runner = CliRunner()


@pytest.mark.cli
@pytest.mark.offline
def test_app():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0, result.stdout

    result = runner.invoke(app, ["conf", "--help"])
    assert result.exit_code == 0, result.stdout

    result = runner.invoke(app, ["download", "--help"])
    assert result.exit_code == 0, result.stdout

    result = runner.invoke(app, ["test", "--help"])
    assert result.exit_code == 0, result.stdout
