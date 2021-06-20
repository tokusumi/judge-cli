import subprocess
from enum import Enum
from pathlib import Path
from typing import List, Optional

import typer
from pydantic import FilePath, ValidationError
from pydantic.types import DirectoryPath

from judge.rendering.history import Verbose, render_history
from judge.rendering.summary import render_summary
from judge.schema import CompareMode, JudgeConfig, VerboseStr
from judge.tools import format, testing
from judge.tools.prompt import to_abs


class Execution(str, Enum):
    py = "py"
    pypy = "pypy"
    cython = "cy"


class TestJudgeConfig(JudgeConfig):
    file: FilePath
    testdir: DirectoryPath


def main(
    workdir: Path = typer.Argument(".", help="a directory path for working directory"),
    file: Optional[Path] = typer.Option(None, "-f", help="execution file"),
    case: Optional[str] = typer.Option(
        None, "--case", help="set target test case manually"
    ),
    py: bool = typer.Option(False, "--py", help="set if you execute Python3"),
    pypy: bool = typer.Option(False, "--pypy", help="set if you execute PyPy3"),
    cython: bool = typer.Option(False, "--cython", help="set if you execute Cython3"),
    mle: Optional[float] = typer.Option(None, "--mle", help=""),
    tle: Optional[float] = typer.Option(None, "--tle", help=""),
    mode: CompareMode = typer.Option(CompareMode.EXACT_MATCH.value, "--mode", help=""),
    tolerance: Optional[float] = typer.Option(None, "--tol", help=""),
    jobs: Optional[int] = typer.Option(None, "--jobs", help=""),
    verbose: VerboseStr = typer.Option(
        VerboseStr.error_detail, "-v", "--verbose", help=""
    ),
) -> None:

    """
    Here is shortcut for testing with `online-judge-tools`.

    Pass `file` you want to test for `problem` at `contest`.

    Ex) the following leads to test `abc_051_b.py` with test cases for Problem `C` at `ABC 051`:
    ```test -f abc_051_b.py```

    If not found test cases, you could let download them.
    """
    typer.echo("Load configuration...")

    if not workdir.exists():
        typer.secho(f"Not exists: {str(workdir.resolve())}", fg=typer.colors.BRIGHT_RED)
        raise typer.Abort(f"Not exists: {str(workdir.resolve())}")

    try:
        config = JudgeConfig.from_toml(workdir)
    except KeyError as e:
        typer.secho(str(e), fg=typer.colors.BRIGHT_RED)
        raise typer.Abort()

    # override options and validate them
    # fmt: off
    abspath = to_abs(workdir)
    _config = config.dict()
    if file is not None: _config["file"] = abspath(file)  # noqa: E701
    if py is not None: _config["py"] = py  # noqa: E701
    if pypy is not None: _config["pypy"] = pypy  # noqa: E701
    if cython is not None: _config["cython"] = cython  # noqa: E701
    if mle is not None: _config["mle"] = mle  # noqa: E701
    if tle is not None: _config["tle"] = tle  # noqa: E701
    if mode is not None: _config["mode"] = mode  # noqa: E701
    if tolerance is not None: _config["tolerance"] = tolerance  # noqa: E701
    if jobs is not None: _config["jobs"] = jobs  # noqa: E701
    if verbose is not None: _config["verbose"] = verbose  # noqa: E701
    # fmt: on
    try:
        config = TestJudgeConfig(**_config)
    except ValidationError as e:
        typer.secho(str(e), fg=typer.colors.BRIGHT_RED)
        raise typer.Abort()

    typer.echo("Check for test cases...")
    test_dir = Path(config.testdir)

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

        test_dir.mkdir(parents=True)
        err = subprocess.run(["judge", "download", workdir, "--directory", test_dir])
        if err.returncode:
            typer.secho(err.stderr.decode(), fg=typer.colors.BRIGHT_RED)
            raise typer.Abort()

    file = Path(config.file)
    testdir = Path(config.testdir)
    colored_file = typer.style(file.name, fg=typer.colors.BRIGHT_CYAN)
    colored_dir = typer.style(f"{testdir.name}", fg=typer.colors.BRIGHT_CYAN)
    typer.echo(f"\nTesting {colored_file} for {colored_dir}...\n")
    execs: List[str] = []

    typer.echo("execution versions:\n")

    if py:
        execs.append(f"python3 {file.name}")
        typer.secho("- Python3: ", fg=typer.colors.BRIGHT_CYAN)
        err = subprocess.run(["python3", "-V"])
        if err.returncode:
            typer.secho(err.stderr.decode(), fg=typer.colors.BRIGHT_RED)
            raise typer.Abort()
    if pypy:
        execs.append(f"pypy3 {file.name}")
        typer.secho("- PyPy3: ", fg=typer.colors.BRIGHT_CYAN)
        err = subprocess.run(["pypy3", "-V"])
        if err.returncode:
            typer.secho(err.stderr.decode(), fg=typer.colors.BRIGHT_RED)
            raise typer.Abort()
    # if cython:
    # pass
    if not execs:
        execs.append(f"python3 {file.name}")

    if case is None:
        tests: List[Path] = []
    else:
        # collect test cases path manually
        tests = format.glob_with_samplename(test_dir, case)
        if not tests:
            typer.secho(
                f"Not found test case: {case} in {test_dir}", fg=typer.colors.RED
            )
            raise typer.Abort()

    testcases = testing.get_testcases(
        testing.GetTestCasesArgs(
            test=tests,
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
                mle=config.mle,
                tle=config.tle,
                compare_mode=config.mode,
                jobs=config.jobs,
                error=config.tolerance,
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
