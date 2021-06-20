import tempfile
from pathlib import Path

import pytest
import typer
from typer.testing import CliRunner

from judge.configure import main

app = typer.Typer()
app.command()(main)

runner = CliRunner()


def dummy():
    return ""


@pytest.mark.offline
def test_conf(mocker):

    mocker.patch("judge.tools.prompt.pydantic_prompt", return_value=dummy)

    with tempfile.TemporaryDirectory() as tempdir:
        test_dir = Path(tempdir) / "tests"
        # success to create configuration file
        result = runner.invoke(app, [tempdir, "--dir", test_dir])
        assert result.exit_code == 0, result.stdout

        # modify it
        result = runner.invoke(app, [tempdir, "--problem", "a"])
        assert result.exit_code == 0, result.stdout

    with tempfile.TemporaryDirectory() as tempdir:
        # success to create configuration file
        result = runner.invoke(app, [tempdir, "-ii"])
        assert result.exit_code == 0, result.stdout

    with tempfile.TemporaryDirectory() as tempdir:
        # success to create configuration file
        result = runner.invoke(app, [tempdir, "-ip"])
        assert result.exit_code == 0, result.stdout

    with tempfile.TemporaryDirectory() as tempdir:
        # success to create configuration file
        result = runner.invoke(app, [tempdir, "-ia"])
        assert result.exit_code == 0, result.stdout
