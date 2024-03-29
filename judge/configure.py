from pathlib import Path
from typing import Optional

import typer
from pydantic import ValidationError
from typer import Option as opt

from judge.schema import CompareMode, JudgeConfig, VerboseStr
from judge.tools.download import url_from_contest
from judge.tools.prompt import to_abs


def main(
    # fmt: off
    workdir: Path = typer.Argument("", help="A directory path for working directory"),
    # initial option
    interactive_init: bool = opt(False, "-ii", help="Interactive configuration for basic option: contest, problem, download URL, solution file and test directory."),
    contest: Optional[str] = opt(None, "--contest", help="Contest name. ex: abc100, agc050"),
    problem: Optional[str] = opt(None, "--problem", help="Problem name. ex: a, b, c, ..."),
    url: Optional[str] = opt(None, "--url", help="Testcase download URL. if you set contest and problem correctly, this is automatically determined."),
    file: Optional[Path] = opt(None, "--file", help="Solution file path"),
    test_dir: Path = opt(None, "--dir", help="A directory path for test cases"),
    # problem option
    interactive_prob: bool = opt(False, "-ip", help="Interactive configuration for evaluation option: tolerance, MLE, TLE and compare mode."),
    tolerance: Optional[float] = opt(None, "--tol", help="Set if problem require correctness within absolute or relative error"),
    mle: Optional[float] = opt(None, "--mle", help="Memory limit (default: 1024 MB)"),
    tle: Optional[float] = opt(None, "--tle", help="Time limit (default: 2000 ms)"),
    mode: Optional[CompareMode] = opt(None, "--mode", help="Compare mode. (exact-match): AC if absolutely same answered. (crlf-insensitive-exact-match): ignore escape format (CR, LF, CRLF). (ignore-spaces): ignore extra spaces. (ignore-spaces-and-newlines): ignore extra spaces and extra new lines."),
    # additional option
    interactive_additional: bool = opt(False, "-ia", help="Interactive configuration for additional option: verbose, execution binary type."),
    verbose: Optional[VerboseStr] = opt(None, "--verbose", help="Verbosity. (error): show only wrong answered testcase filename. (error-detail): show only wrong answered outputs. (all): show all sample status and wrong answered outputs. (detail): all answered status and outputs. (dd): only reserved. now same as `detail`"),
    py: Optional[bool] = opt(None, "--py", help="Set if you execute Python3"),
    pypy: Optional[bool] = opt(None, "--pypy", help="Set if you execute PyPy3"),
    cython: Optional[bool] = opt(None, "--cython", help="Only reserved to set if you execute Cython3"),
    jobs: Optional[int] = opt(None, "--jobs", help="Only reserved for the number of concurrency for testing"),
    # fmt: on
) -> None:
    """
    Here is shortcut to optionally configure contest setup for testing.

    (Optional) Pass `working directory` you want to configure.

    Ex) the following leads to setup test configuration interactively:
    ```conf -ii```
    """
    if not workdir.exists():
        workdir.mkdir(parents=True)
    workdir = workdir.resolve()
    try:
        config = JudgeConfig.from_toml(workdir, auto_error=False)
    except KeyError as e:
        typer.secho(str(e), fg=typer.colors.BRIGHT_RED)
        raise typer.Abort()

    abspath = to_abs(workdir)

    _config = config.dict()
    base_test_dir = abspath(Path("tests"))
    if file is not None:
        _config["file"] = abspath(file)
        if not _config["file"].exists():
            _config["file"].parent.mkdir(parents=True, exist_ok=True)
            _config["file"].touch()
    if test_dir is not None:
        testdir = abspath(test_dir)
        if not testdir.exists():
            testdir.mkdir(parents=True)
        _config["testdir"] = testdir.resolve()
    elif not _config.get("testdir"):
        if not base_test_dir.exists():
            base_test_dir.mkdir(parents=True)
        _config["testdir"] = base_test_dir.resolve()
    # fmt: off
    if contest is not None: _config["contest"] = contest  # noqa: E701
    if problem is not None: _config["problem"] = problem  # noqa: E701
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
