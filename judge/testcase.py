import subprocess
from pathlib import Path

import typer
from onlinejudge import utils
from pydantic.types import DirectoryPath

from judge.schema import JudgeConfig

MAX_SAMPLE_NUM = 100


class AddJudgeConfig(JudgeConfig):
    testdir: DirectoryPath


def main(
    workdir: Path = typer.Argument(".", help="a directory path for working directory"),
    directory: Path = typer.Option(None, help="a directory path for test cases"),
    format: str = typer.Option("sample-u%i.%e", help="custom filename format"),
    cookie: Path = typer.Option(utils.default_cookie_path, help="directory for cookie"),
) -> None:
    """
    Here is shortcut for add new brank testcase files.

    At first, call `judge conf` for configuration.

    Ex) the following leads to download test cases and add testcase for it:
    ```add```
    """
    typer.echo("Load configuration...")
    if not workdir.exists():
        typer.secho(f"Not exists: {str(workdir.resolve())}", fg=typer.colors.BRIGHT_RED)
        raise typer.Abort()

    try:
        _config = JudgeConfig.from_toml(workdir)
    except KeyError as e:
        typer.secho(str(e), fg=typer.colors.BRIGHT_RED)
        raise typer.Abort()

    __config = _config.dict()

    if directory:
        __config["testdir"] = directory.resolve()
    try:
        config = AddJudgeConfig(**__config)
    except KeyError as e:
        typer.secho(str(e), fg=typer.colors.BRIGHT_RED)
        raise typer.Abort()

    typer.echo(f"Add testcase for {config.testdir}")

    typer.echo("Check for test cases...")
    test_dir = Path(config.testdir)

    # only empty test dir is deleted
    try:
        test_dir.rmdir()
    except OSError:
        ...

    if not test_dir.exists():
        confirm: str = typer.prompt(
            "Are you sure you want to download test cases?", default="no"
        )
        test_dir.mkdir(parents=True)
        if confirm.lower() in {"yes", "y"}:
            err = subprocess.run(
                ["judge", "download", config.workdir, "--directory", test_dir]
            )
            if err.returncode:
                typer.secho(str(err.stderr), fg=typer.colors.BRIGHT_RED)
                raise typer.Abort()
        else:
            typer.echo("Skip to download system testcase.")

    embbed = format.replace("%e", "in")
    idx = 1
    for i in range(1, MAX_SAMPLE_NUM + 1):
        if not (test_dir / embbed.replace("%i", f"{i}")).exists():
            idx = i
            break
    else:
        typer.secho("Can't create new sample", fg=typer.colors.BRIGHT_RED)
        raise typer.Abort()

    sample_in = test_dir / format.replace("%i", f"{idx}").replace("%e", "in")
    sample_out = test_dir / format.replace("%i", f"{idx}").replace("%e", "out")
    sample_in.touch()
    sample_out.touch()
    typer.echo(f"Created: {sample_in.stem}")


if __name__ == "__main__":
    typer.run(main)
