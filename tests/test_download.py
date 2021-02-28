import os
import shutil
import tempfile

import typer
import pytest
from typer.testing import CliRunner

from judge.download import main

app = typer.Typer()
app.command()(main)

runner = CliRunner()


@pytest.mark.download
def test_download():
    result = runner.invoke(app, ["abc051", "c"])
    assert result.exit_code == 0, result.stdout
    assert os.listdir(os.path.join(os.path.dirname(__file__), "abc051_c"))
    shutil.rmtree(
        os.path.join(os.path.dirname(__file__), "abc051_c"),
    )

    with tempfile.TemporaryDirectory() as tempdir:
        result = runner.invoke(app, ["abc051", "b", tempdir])
        assert result.exit_code == 0, result.stdout
        assert os.listdir(os.path.join(tempdir, "abc051_b"))


@pytest.mark.download
def test_download_failed():
    with tempfile.TemporaryDirectory() as tempdir:
        result = runner.invoke(app, ["a-b-c051", "b", tempdir])
        assert result.exit_code == 1, result.stdout
