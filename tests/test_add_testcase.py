import os
import tempfile
from pathlib import Path

import pytest
import typer
from typer.testing import CliRunner

from judge.configure import main as c_main
from judge.testcase import main

app = typer.Typer()
app.command()(main)
app.command("conf")(c_main)

runner = CliRunner()


@pytest.mark.offline
def test_add_testcase():
    with tempfile.TemporaryDirectory() as tempdir:
        result = runner.invoke(app, ["conf", tempdir])
        assert result.exit_code == 0, result.stdout

        samples = Path(tempdir) / "tests"
        result = runner.invoke(app, ["main", tempdir])
        assert result.exit_code == 0, result.stdout
        assert (samples / "sample-u1.in").is_file()
        assert (samples / "sample-u1.out").is_file()

        result = runner.invoke(app, ["main", tempdir])
        assert result.exit_code == 0, result.stdout
        assert (samples / "sample-u2.in").is_file()
        assert (samples / "sample-u2.out").is_file()


@pytest.mark.download
def test_download_and_add():
    with tempfile.TemporaryDirectory() as tempdir:
        result = runner.invoke(
            app, ["conf", tempdir, "--contest", "abc100", "--problem", "a"]
        )
        assert result.exit_code == 0, result.stdout

        samples = Path(tempdir) / "tests"
        result = runner.invoke(app, ["main", tempdir], input="yes")
        assert result.exit_code == 0, result.stdout
        assert len(os.listdir(samples)) > 2
        assert (samples / "sample-u1.in").is_file()
        assert (samples / "sample-u1.out").is_file()
