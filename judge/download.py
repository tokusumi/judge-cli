from pathlib import Path
from typing import Optional

import typer
from onlinejudge import utils
from pydantic.networks import HttpUrl
from pydantic.types import DirectoryPath

from judge.schema import JudgeConfig
from judge.tools.download import DownloadArgs, SaveArgs
from judge.tools.download import download as download_tool
from judge.tools.download import save as save_tool


class DownloadJudgeConfig(JudgeConfig):
    URL: HttpUrl
    testdir: DirectoryPath


def main(
    workdir: Path = typer.Argument(".", help="a directory path for working directory"),
    url: Optional[str] = typer.Option(None, help="a download URL"),
    directory: Path = typer.Option(None, help="a directory path for test cases"),
    no_store: bool = typer.Option(False, help="testcases is shown but not saved"),
    format: str = typer.Option("sample-%i.%e", help="custom filename format"),
    cookie: Path = typer.Option(utils.default_cookie_path, help="directory for cookie"),
) -> None:
    """
    Here is shortcut for download with `online-judge-tools`.

    Pass `problem` at `contest` you want to test.

    Ex) the following leads to download test cases for Problem `C` at `ABC 051`:
    ```download```
    """
    typer.echo("Load configuration...")

    if not workdir.exists():
        raise typer.Abort(f"Not exists: {str(workdir.resolve())}")

    try:
        _config = JudgeConfig.from_toml(workdir)
    except KeyError as e:
        typer.secho(str(e), fg=typer.colors.BRIGHT_RED)
        raise typer.Abort()

    if url or directory:
        # check arguments
        try:
            __config = _config.dict()
            if url:
                __config["URL"] = url
            if directory:
                __config["testdir"] = directory.resolve()
            config = DownloadJudgeConfig(**__config)
        except KeyError as e:
            typer.secho(str(e), fg=typer.colors.BRIGHT_RED)
            raise typer.Abort()

    typer.echo(f"Download {config.URL}")

    try:
        testcases = download_tool(
            DownloadArgs(
                url=config.URL,
                cookie=cookie,
            )
        )
    except Exception as e:
        typer.secho(str(e), fg=typer.colors.BRIGHT_RED)
        raise typer.Abort()

    if not no_store:
        try:
            save_tool(
                testcases,
                SaveArgs(
                    format=format,
                    directory=Path(config.testdir),
                ),
            )
        except Exception as e:
            typer.secho(str(e), fg=typer.colors.BRIGHT_RED)
            raise typer.Abort()


if __name__ == "__main__":
    typer.run(main)
