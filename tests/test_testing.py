import os
import tempfile

import pytest
import typer
from typer.testing import CliRunner

from judge.configure import main as c_main
from judge.testing import main

app = typer.Typer()
app.command()(main)
app.command("conf")(c_main)

runner = CliRunner()


@pytest.mark.download
def test_testing():
    with tempfile.TemporaryDirectory() as tempdir:
        solution = """print(input().replace(",", " "))"""
        solution_file = os.path.join(tempdir, "solve.py")
        with open(solution_file, "w") as f:
            f.write(solution)

        result = runner.invoke(
            app, ["conf", tempdir, "--contest", "abc100", "--problem", "a"]
        )
        assert result.exit_code == 0, result.stdout
        # success for download and testing
        result = runner.invoke(app, ["main", tempdir, "-f", solution_file])
        assert result.exit_code == 0, result.stdout
        # success to use Python3 and PyPy3
        result = runner.invoke(app, ["main", tempdir, "-f", solution_file, "--py"])
        assert result.exit_code == 0, result.stdout

    with tempfile.TemporaryDirectory() as tempdir:
        solution = """print(input().replace(",", " "))"""
        solution_file = os.path.join(tempdir, "solve.py")
        with open(solution_file, "w") as f:
            f.write(solution)

        result = runner.invoke(
            app, ["conf", tempdir, "--contest", "abc100", "--problem", "A"]
        )
        assert result.exit_code == 0, result.stdout
        # success for capital case for problem
        result = runner.invoke(app, ["main", tempdir, "-f", solution_file])
        assert result.exit_code == 0, result.stdout


@pytest.mark.download
def test_testing_failed():
    with tempfile.TemporaryDirectory() as tempdir:
        solution_file = os.path.join(tempdir, "solve.py")
        result = runner.invoke(app, ["conf", tempdir, "--file", solution_file])
        assert result.exit_code == 0, result.stdout

        # no target test directory
        result = runner.invoke(app, ["main", tempdir])
        assert result.exit_code == 1, result.stdout

    with tempfile.TemporaryDirectory() as tempdir:
        result = runner.invoke(
            app, ["conf", tempdir, "--contest", "abc100", "--problem", "a"]
        )
        assert result.exit_code == 0, result.stdout

        # no target file
        result = runner.invoke(app, ["main", tempdir])
        assert result.exit_code == 1, result.stdout

    with tempfile.TemporaryDirectory() as tempdir:
        result = runner.invoke(
            app, ["conf", tempdir, "--contest", "abc100", "--problem", "a"]
        )
        assert result.exit_code == 0, result.stdout

        solution = """print(input().replace(",", " "))"""
        solution_file = os.path.join(tempdir, "solve.py")
        with open(solution_file, "w") as f:
            f.write(solution)

        # invalid test case
        result = runner.invoke(
            app, ["main", tempdir, "-f", solution_file, "--case", "sample100"]
        )
        assert result.exit_code == 1, result.stdout

        # invalid verbose
        result = runner.invoke(
            app, ["main", tempdir, "-f", solution_file, "--verbose", "not-supported"]
        )
        assert result.exit_code == 2, result.stdout


@pytest.mark.download
def test_no_confirm():
    with tempfile.TemporaryDirectory() as tempdir:
        solution = """print(input().replace(",", " "))"""
        solution_file = os.path.join(tempdir, "solve.py")
        with open(solution_file, "w") as f:
            f.write(solution)
        result = runner.invoke(
            app, ["conf", tempdir, "--contest", "abc100", "--problem", "a"]
        )
        # abort for download
        result = runner.invoke(app, ["main", tempdir, "-f", solution_file], input="n")
        assert result.exit_code == 1, result.stdout
