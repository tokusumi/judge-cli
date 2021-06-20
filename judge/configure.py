from pathlib import Path
from typing import Optional

import typer
from pydantic import ValidationError
from typer import Option as opt

from judge.schema import CompareMode, JudgeConfig
from judge.tools.download import url_from_contest
from judge.tools.prompt import to_abs


def main(
    workdir: Path = typer.Argument("", help=""),
    # initial option
    interactive_init: bool = opt(False, "-ii", help=""),
    contest: Optional[str] = opt(None, "--contest", help=""),
    problem: Optional[str] = opt(None, "--problem", help=""),
    url: Optional[str] = opt(None, "--url", help=""),
    file: Optional[Path] = opt(None, "--file", help=""),
    test_dir: Path = opt(None, "--dir", help="a directory path for test cases"),
    # problem option
    interactive_prob: bool = opt(False, "-ip", help=""),
    tolerance: Optional[float] = opt(None, "--tol", help=""),
    mle: Optional[float] = opt(None, "--mle", help=""),
    tle: Optional[float] = opt(None, "--tle", help=""),
    mode: Optional[CompareMode] = opt(None, "--mode", help=""),
    # additional option
    interactive_additional: bool = opt(False, "-ia", help=""),
    verbose: Optional[int] = opt(None, "--verbose", help=""),
    py: Optional[bool] = opt(None, "--py", help="set if you execute Python3"),
    pypy: Optional[bool] = opt(None, "--pypy", help="set if you execute PyPy3"),
    cython: Optional[bool] = opt(None, "--cython", help="set if you execute Cython3"),
    jobs: Optional[int] = opt(None, "--jobs", help=""),
) -> None:
    """
    Here is shortcut to optionally configure contest setup for testing.

    Pass `directory` you want to configure.

    Ex) the following leads to setup test configuration for Problem `C` at `ABC 051`:
    ```conf -ii```
    """
    # TODO: add help and messages
    if not workdir.exists():
        workdir.mkdir(parents=True)
    workdir = workdir.resolve()
    try:
        config = JudgeConfig.from_toml(workdir, auto_error=False)
    except KeyError as e:
        typer.secho(str(e), fg=typer.colors.BRIGHT_RED)
        raise typer.Abort()

    abspath = to_abs(workdir)

    # fmt: off
    _config = config.dict()
    base_test_dir = abspath(Path("tests"))
    if file is not None: _config["file"] = abspath(file)  # noqa: E701
    if contest is not None: _config["contest"] = contest  # noqa: E701
    if problem is not None: _config["problem"] = problem  # noqa: E701
    if test_dir is not None:
        testdir = abspath(test_dir)
        if not testdir.exists():
            testdir.mkdir(parents=True)
        _config["testdir"] = testdir.resolve()
    elif not _config.get("testdir"):
        if not base_test_dir.exists():
            base_test_dir.mkdir(parents=True)
        _config["testdir"] = base_test_dir.resolve()
    if contest and problem: _config["URL"] = url_from_contest(contest, problem)  # noqa: E701
    if url is not None: _config["URL"] = url  # noqa: E701
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
        config = JudgeConfig(**_config)
    except ValidationError as e:
        typer.secho(str(e), fg=typer.colors.BRIGHT_RED)
        raise typer.Abort()

    # fmt: off
    if interactive_init:
        if file is None: config.ask("file", "file")  # noqa: E701
        if contest is None: config.ask("contest", "contest")  # noqa: E701
        if problem is None: config.ask("problem", "problem")  # noqa: E701
        if config.URL is None and config.contest and config.problem:
            config.URL = url_from_contest(config.contest, config.problem)  # type: ignore
        if url is None: config.ask("URL", "URL")  # noqa: E701
        if test_dir is None: config.ask("testdir", "testdir")  # noqa: E701
    if interactive_prob:
        if tolerance is None: config.ask("tolerance", "tolerance")  # noqa: E701
        if mle is None: config.ask("mle", "mle")  # noqa: E701
        if tle is None: config.ask("tle", "tle")  # noqa: E701
        if mode is None: config.ask("mode", "mode")  # noqa: E701
    if interactive_additional:
        if verbose is None: config.ask("verbose", "verbose")  # noqa: E701
        if py is None: config.ask("py", "py")  # noqa: E701
        if pypy is None: config.ask("pypy", "pypy")  # noqa: E701
        if cython is None: config.ask("cython", "cython")  # noqa: E701
        if jobs is None: config.ask("jobs", "jobs")  # noqa: E701
    # fmt: on
    _dict = config.dict()

    try:
        config = JudgeConfig(**_dict)
    except ValidationError as e:
        typer.secho(str(e), fg=typer.colors.BRIGHT_RED)
        typer.Abort()

    pretty_config = "\n".join(
        [" = ".join([str(f) for f in c]) for c in config if c[1] is not None]
    )
    msg = typer.style(
        "Are you sure to save the following configurations?", fg=typer.colors.CYAN
    )
    confirm: str = typer.prompt(f"{msg}\n{pretty_config}\n", default="yes")
    if confirm.lower() not in {"yes", "y"}:
        typer.echo("Canceled interactive configure mode.")
        return

    config.save(workdir)
    if config.file:
        target = Path(config.file)
        if not target.exists():
            target.touch()
    typer.echo("Success for configuration.")
