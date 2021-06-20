import os
import shutil
import tempfile
from pathlib import Path

import pytest
import typer
from typer.testing import CliRunner

from judge.download import main

app = typer.Typer()
app.command()(main)

runner = CliRunner()


@pytest.mark.download
def test_download():
    url = "https://atcoder.jp/contests/abc100/tasks/abc100_a"
    testdir = Path(os.path.join(os.path.dirname(__file__), "temp-for-test-delete-this"))
    testdir.mkdir(parents=True, exist_ok=False)
    result = runner.invoke(app, ["--url", url, "--directory", testdir])
    assert result.exit_code == 0, result.stdout
    assert os.listdir(str(testdir))
    shutil.rmtree(str(testdir))

    with tempfile.TemporaryDirectory() as tempdir:
        testdir = Path(tempdir) / "tests"
        testdir.mkdir(parents=True, exist_ok=False)
        result = runner.invoke(app, [tempdir, "--url", url, "--directory", testdir])
        assert result.exit_code == 0, result.stdout
        assert os.listdir(str(testdir))


@pytest.mark.download
def test_download_failed():
    with tempfile.TemporaryDirectory() as tempdir:
        # working directory does not exists
        result = runner.invoke(app, [str(Path(tempdir) / "nonexists")])
        assert result.exit_code == 1, result.stdout

        # invalid URL
        inv_url = "https://atcoder.jp/contests/invalid-contest/tasks/invalid-problem"
        result = runner.invoke(app, [tempdir, "--url", inv_url])
        assert result.exit_code == 1, result.stdout

        # no download URL
        result = runner.invoke(app, [tempdir, "--directory", tempdir])
        assert result.exit_code == 1, result.stdout

        # invalid testdir
        inv_testdir = Path(tempdir) / "invalid"
        result = runner.invoke(app, [tempdir, "--directory", inv_testdir])
        assert result.exit_code == 1, result.stdout

        # no test directory
        url = "https://atcoder.jp/contests/abc100/tasks/abc100_a"
        result = runner.invoke(app, [tempdir, "--url", url])
        assert result.exit_code == 1, result.stdout
