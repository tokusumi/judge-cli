from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Type, TypeVar

import toml
import typer
from pydantic import BaseSettings, DirectoryPath, HttpUrl, ValidationError
from typer import Option as opt

from judge.schema import CompareMode
from judge.tools.prompt import BasePrompt
from judge.tools.download import url_from_contest

if TYPE_CHECKING:
    Model = TypeVar("Model", bound="BaseJudgeConfig")


class BaseJudgeConfig(BasePrompt, BaseSettings):
    """Global configurations."""

    @classmethod
    def from_toml(cls: Type["Model"], path: Path, auto_error: bool = True) -> "Model":
        _path = path / ".judgecli"
        if not path.exists():
            path.mkdir(parents=True)
        if not _path.exists():
            _path.touch()

        d = toml.load(open(_path)).get("judgecli", {})
        d["directory"] = path
        if not d:
            return cls()
        if auto_error:
            return cls(**d)
        else:
            return cls.construct(**d)

    def save(self, path: Path) -> None:
        c_file = path / ".judgecli"
        if not c_file.exists():
            c_file.touch()

        body = toml.load(c_file.open())

        part = body.get("judgecli", {})
        if not isinstance(part, dict):
            raise ValueError("check [judgecli] section in .judgecli")

        for key, value in self.dict().items():
            if isinstance(value, Enum):
                value = value.value
            elif isinstance(value, Path):
                value = str(value.resolve())
            elif isinstance(value, HttpUrl):
                value = str(value)
            part[key] = value
        body["judgecli"] = part
        toml.dump(body, c_file.open("w"))


class JudgeConfig(BaseJudgeConfig):
    URL: Optional[HttpUrl] = None
    file: Optional[Path] = None
    contest: Optional[str] = None
    problem: Optional[str] = None
    directory: Optional[DirectoryPath] = None
    py: bool = True
    pypy: bool = False
    cython: bool = False
    mle: Optional[float] = 256
    tle: Optional[float] = 2000
    mode: CompareMode = CompareMode.EXACT_MATCH
    tolerance: Optional[float] = None
    jobs: Optional[int] = None
    verbose: int = 10


def main(
    directory: Path = typer.Argument("tests", help="a directory path for test cases"),
    # initial option
    contest: Optional[str] = opt(None, "--contest", help=""),
    problem: Optional[str] = opt(None, "--problem", help=""),
    url: Optional[str] = opt(None, "--url", help=""),
    interactive_init: bool = opt(False, "-ii", help=""),
    file: Optional[Path] = opt(None, "--file", help=""),
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
    ```conf tests/abc051_c -ii```
    """
    # TODO: add help and messages
    config = JudgeConfig.from_toml(directory, auto_error=False)

    # fmt: off
    _config = config.dict()
    if file is not None: _config["file"] = file  # noqa: E701
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
        raise typer.Abort(e)

    URL: Optional[str] = None
    # fmt: off
    if interactive_init:
        if file is None: config.ask("file", "file")  # noqa: E701
        if contest is None: config.ask("contest", "contest")  # noqa: E701
        if problem is None: config.ask("problem", "problem")  # noqa: E701
        if config.URL is None and config.contest and config.problem: 
            URL = url_from_contest(config.contest, config.problem)  # noqa: E701
        if url is None: config.ask("URL", "URL")  # noqa: E701
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
    if URL:
        _dict["URL"] = URL
    try:
        config = JudgeConfig(**_dict)
    except ValidationError as e:
        typer.Abort(e)

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

    config.save(directory)
    typer.echo("Success for configuration.")
