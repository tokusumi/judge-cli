import os
import tempfile

import pytest
import typer
from typer.testing import CliRunner

from judge.testing import main

app = typer.Typer()
app.command()(main)

runner = CliRunner()


@pytest.mark.download
def test_testing():
    with tempfile.TemporaryDirectory() as tempdir:
        solution = """print(input().replace(",", " "))"""
        solution_file = os.path.join(tempdir, "solve.py")
        with open(solution_file, "w") as f:
            f.write(solution)

        # success for download and testing
        result = runner.invoke(app, [solution_file, "abc051", "a", tempdir])
        assert result.exit_code == 0, result.stdout

        # success for capital case for problem
        result = runner.invoke(app, [solution_file, "abc051", "A", tempdir])
        assert result.exit_code == 0, result.stdout

        # success to use Python3 and PyPy3
        result = runner.invoke(
            # app, [solution_file, "abc051", "a", tempdir, "--py", "--pypy"]
            app,
            [solution_file, "abc051", "a", tempdir, "--py"],
        )
        assert result.exit_code == 0, result.stdout


@pytest.mark.download
def test_testing_failed():
    with tempfile.TemporaryDirectory() as tempdir:
        solution = """print(input().replace(",", " "))"""
        solution_file = os.path.join(tempdir, "solve.py")
        with open(solution_file, "w") as f:
            f.write(solution)

        # wrong contest name
        os.makedirs(os.path.join(tempdir, "a-b-c051_a"))
        result = runner.invoke(app, [solution_file, "a-b-c051", "a", tempdir])
        assert result.exit_code == 1, result.stdout

        # invalid problem
        os.makedirs(os.path.join(tempdir, "abc051_g"))
        result = runner.invoke(app, [solution_file, "abc051", "g", tempdir])
        assert result.exit_code == 1, result.stdout

        # invalid verbose
        os.makedirs(os.path.join(tempdir, "abc051_g"))
        result = runner.invoke(
            app, [solution_file, "abc051", "a", tempdir, "--verbose", "-1"]
        )
        assert result.exit_code == 1, result.stdout


@pytest.mark.download
def test_no_confirm():
    with tempfile.TemporaryDirectory() as tempdir:
        solution = """print(input().replace(",", " "))"""
        solution_file = os.path.join(tempdir, "solve.py")
        with open(solution_file, "w") as f:
            f.write(solution)

        # abort for download
        result = runner.invoke(app, [solution_file, "abc051", "a", tempdir], input="n")
        assert result.exit_code == 1, result.stdout
