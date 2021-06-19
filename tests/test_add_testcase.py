import os
import tempfile
from pathlib import Path

import pytest
import typer
from typer.testing import CliRunner

from judge.testcase import main

app = typer.Typer()
app.command()(main)

runner = CliRunner()


@pytest.mark.offline
def test_add_testcase():
    with tempfile.TemporaryDirectory() as tempdir:
        samples = Path(tempdir) / "abc001_a"
        samples.mkdir(parents=True)
        result = runner.invoke(app, ["abc001", "a", tempdir])
        assert result.exit_code == 0, result.stdout
        assert (samples / "sample-u1.in").is_file()
        assert (samples / "sample-u1.out").is_file()

        result = runner.invoke(app, ["abc001", "a", tempdir])
        assert result.exit_code == 0, result.stdout
        assert (samples / "sample-u2.in").is_file()
        assert (samples / "sample-u2.out").is_file()


@pytest.mark.download
def test_download_and_add():
    with tempfile.TemporaryDirectory() as tempdir:
        samples = Path(tempdir) / "abc051_b"
        result = runner.invoke(app, ["abc051", "b", tempdir], input="yes")
        assert result.exit_code == 0, result.stdout
        assert len(os.listdir(samples)) > 2
        assert (samples / "sample-u1.in").is_file()
        assert (samples / "sample-u1.out").is_file()
