from pathlib import Path
from enum import Enum
from typing import Any, Type, Optional, TypeVar, TYPE_CHECKING
from pydantic import BaseSettings, HttpUrl, FilePath, DirectoryPath
from pydantic.error_wrappers import ValidationError
import toml

import typer
from typer import Option as opt, prompt as pr
from judge.schema import CompareMode


if TYPE_CHECKING:
    Model = TypeVar("Model", bound="BaseJudgeConfig")


class BaseJudgeConfig(BaseSettings):
    """Global configurations."""

    @classmethod
    def from_toml(cls: Type["Model"], path: Path, auto_error: bool = True) -> "Model":
        _path = path / ".judgecli"
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
            if isinstance(value, Path):
                value = str(value.resolve())
            part[key] = value
        body["judgecli"] = part
        toml.dump(body, c_file.open("w"))

    def ask(self, key: str, msg: str) -> None:
        if key is not None:
            return
        while True:
            item = pr(msg, default=config.__getattribute__(key))
            try:
                config.validate({key: item})
                config.__setattr__(key, item)
            except ValidationError as e:
                if e:
                    typer.secho(
                        "\n".join([f.get("msg", "") for f in e.errors()]),
                        fg=typer.colors.RED,
                    )
                continue
            return


class JudgeConfig(BaseJudgeConfig):
    URL: Optional[HttpUrl] = None
    file: Optional[FilePath] = None
    contest: Optional[str] = None
    problem: Optional[str] = None
    directory: Optional[DirectoryPath] = None
    py: bool = False
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
    interactive: bool = opt(False, "-i", help=""),
    file: Optional[str] = opt(None, "--file", help=""),
    contest: Optional[str] = opt(None, "--contest", help=""),
    problem: Optional[str] = opt(None, "--problem", help=""),
    py: Optional[bool] = opt(None, "--py", help="set if you execute Python3"),
    pypy: Optional[bool] = opt(None, "--pypy", help="set if you execute PyPy3"),
    cython: Optional[bool] = opt(None, "--cython", help="set if you execute Cython3"),
    mle: Optional[float] = opt(None, "--mle", help=""),
    tle: Optional[float] = opt(None, "--tle", help=""),
    mode: Optional[CompareMode] = opt(None, "--mode", help=""),
    tolerance: Optional[float] = opt(None, "--tol", help=""),
    jobs: Optional[int] = opt(None, "--jobs", help=""),
    verbose: Optional[int] = opt(None, "--verbose", help=""),
) -> None:
    """
    Here is shortcut to configure contest setup for testing.

    Pass `directory` you want to configure.

    Ex) the following leads to download test cases for Problem `C` at `ABC 051`:
    ```conf tests/abc051_c ```
    """
    config = JudgeConfig.from_toml(directory, auto_error=False)

    # fmt: off
    if file is not None: config.file = file
    if contest is not None: config.contest = contest
    if problem is not None: config.problem = problem
    if py is not None: config.py = py
    if pypy is not None: config.pypy = pypy
    if cython is not None: config.cython = cython
    if mle is not None: config.mle = mle
    if tle is not None: config.tle = tle
    if mode is not None: config.mode = mode
    if tolerance is not None: config.tolerance = tolerance
    if jobs is not None: config.jobs = jobs
    if verbose is not None: config.verbose = verbose
    # fmt: on

    if interactive:
        # fmt: off
        if file is None: config.ask("file", "file")
        if contest is None: config.ask("contest", "contest")
        if problem is None: config.ask("problem", "problem")
        if py is None: config.ask("py", "py")
        if pypy is None: config.ask("pypy", "pypy")
        if cython is None: config.ask("cython", "cython")
        if mle is None: config.ask("mle", "mle")
        if tle is None: config.ask("tle", "tle")
        if mode is None: config.ask("mode", "mode")
        if tolerance is None: config.ask("tolerance", "tolerance")
        if jobs is None: config.ask("jobs", "jobs")
        if verbose is None: config.ask("verbose", "verbose")
        # fmt: on
        pass

    pretty_config = "\n".join(
        [" = ".join([str(f) for f in c]) for c in config if c[1] is not None]
    )
    msg = typer.style(
        "Are you sure to save the following configurations?", fg=typer.colors.CYAN
    )
    confirm: str = typer.prompt(f"{msg}\n{pretty_config}", default="yes")
    if confirm.lower() not in {"yes", "y"}:
        typer.echo("Canceled interactive configure mode.")
        raise typer.Abort()

    JudgeConfig(**config.dict()).save(directory)
