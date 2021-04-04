import subprocess
from enum import Enum
from pathlib import Path
from typing import Optional

import typer

from judge.rendering.history import Verbose, render_history
from judge.rendering.summary import render_summary
from judge.schema import CompareMode
from judge.tools import testing


class Execution(str, Enum):
    py = "py"
    pypy = "pypy"
    cython = "cy"


class VerboseStr(str, Enum):
    error = "error"
    error_detail = "error_detail"
    all = "all"
    detail = "detail"
    dd = "dd"


def main(
    file: str,
    contest: str,
    problem: str,
    directory: Path = typer.Argument("tests", help="a directory path for test cases"),
    py: bool = typer.Option(False, "--py", help="set if you execute Python3"),
    pypy: bool = typer.Option(False, "--pypy", help="set if you execute PyPy3"),
    cython: bool = typer.Option(False, "--cython", help="set if you execute Cython3"),
    mle: Optional[float] = typer.Option(256, "--mle", help=""),
    tle: Optional[float] = typer.Option(2000, "--tle", help=""),
    mode: CompareMode = typer.Option(CompareMode.EXACT_MATCH.value, "--mode", help=""),
    tolerance: Optional[float] = typer.Option(None, "--tol", help=""),
    jobs: Optional[int] = typer.Option(None, "--jobs", help=""),
    verbose: VerboseStr = typer.Option(VerboseStr.error, "-v", "--verbose", help=""),
) -> None:

    """
    Here is shortcut for testing with `online-judge-tools`.

    Pass `file` you want to test for `problem` at `contest`.

    Ex) the following leads to test `abc_051_b.py` with test cases for Problem `C` at `ABC 051`:
    ```test abc_051_b.py abc051 c```

    If not found test cases, you could let download them.
    """
    typer.echo("Check for test cases...")
    test_dir = directory / f"{contest}_{problem}"

    # only empty test dir is deleted
    try:
        test_dir.rmdir()
    except OSError:
        ...
    if not test_dir.exists():
        confirm: str = typer.prompt(
            "Are you sure you want to download test cases?", default="yes"
        )
        if confirm.lower() not in {"yes", "y"}:
            typer.echo("Canceled download. Make sure to download test cases manually.")
            raise typer.Abort()

        err = subprocess.run(
            ["judge", "download", contest, problem, directory]
        ).returncode
        if err:
            raise typer.Abort()

    colored_file = typer.style(file, fg=typer.colors.BRIGHT_CYAN)
    colored_dir = typer.style(f"{contest}_{problem}", fg=typer.colors.BRIGHT_CYAN)
    typer.echo(f"\nTesting {colored_file} for {colored_dir}...\n")
    execs = []

    typer.echo("execution versions:\n")

    if py:
        execs.append(f"python3 {file}")
        typer.secho("- Python3: ", fg=typer.colors.BRIGHT_CYAN)
        err = subprocess.run(["python3", "-V"]).returncode
        if err:
            raise typer.Abort()
    if pypy:
        execs.append(f"pypy3 {file}")
        typer.secho("- PyPy3: ", fg=typer.colors.BRIGHT_CYAN)
        err = subprocess.run(["pypy3", "-V"]).returncode
        if err:
            raise typer.Abort()
    # if cython:
    # pass
    if not execs:
        execs.append(f"python3 {file}")

    testcases = testing.get_testcases(
        testing.GetTestCasesArgs(
            test=[],
            directory=test_dir,
            format="sample%s.%e",
            ignore_backup=True,
        )
    )
    if not testcases:
        typer.secho("Not found test cases", fg=typer.colors.RED)
        raise typer.Abort()

    _verbose: Optional[Verbose] = Verbose.__members__.get(verbose.name)
    if _verbose is None:
        typer.secho("invalid verbose", fg=typer.colors.RED)
        raise typer.Abort()

    for prog in execs:
        colored_prog = typer.style(prog.split(" ", 1)[0], fg=typer.colors.BRIGHT_CYAN)
        typer.secho(f"\nTesting {colored_prog}...\n")
        histories = testing.test(
            testing.TestingArgs(
                testcases=testcases,
                command=prog,
                gnu_time="gnu-time",
                mle=mle,
                tle=tle,
                compare_mode=mode,
                jobs=jobs,
                error=tolerance,
                silent=True,
            )
        )
        _histories = []

        for history in histories:
            render_history(history, _verbose)
            _histories.append(history)

        if _histories:
            render_summary(_histories)


if __name__ == "__main__":
    typer.run(main)
