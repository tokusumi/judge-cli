from pathlib import Path
from typing import Optional, Tuple

import typer
from onlinejudge import utils
from pydantic.networks import HttpUrl
from pydantic.types import DirectoryPath

from judge.schema import JudgeConfig
from judge.tools.download import DownloadArgs, LoginForm, SaveArgs
from judge.tools.download import download as download_tool
from judge.tools.download import save as save_tool


class DownloadJudgeConfig(JudgeConfig):
    URL: HttpUrl
    testdir: DirectoryPath


class CLILoginForm(LoginForm):
    def get_credentials(self) -> Tuple[str, str]:
        username = typer.prompt("What's your username?")
        password = typer.prompt("What's your password?", hide_input=True)
        return username, password


def main(
    workdir: Path = typer.Argument(".", help="a directory path for working directory"),
    url: Optional[str] = typer.Option(None, help="a download URL"),
    directory: Path = typer.Option(None, help="a directory path for test cases"),
    no_store: bool = typer.Option(False, help="testcases is shown but not saved"),
    format: str = typer.Option("sample-%i.%e", help="custom filename format"),
    login: bool = typer.Option(False, help="login into target service"),
    cookie: Path = typer.Option(utils.default_cookie_path, help="directory for cookie"),
) -> None:
    """
    Here is shortcut for download with `online-judge-tools`.

    At first, call `judge conf` for configuration.
    Pass `problem` at `contest` you want to test.

    Ex) the following leads to download test cases for Problem `C` at `ABC 051`:
    ```download```
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

    if url or directory:
        # check arguments
        if url:
            __config["URL"] = url
        if directory:
            __config["testdir"] = directory.resolve()
    try:
        config = DownloadJudgeConfig(**__config)
    except KeyError as e:
        typer.secho(str(e), fg=typer.colors.BRIGHT_RED)
        raise typer.Abort()

    typer.echo(f"Download {config.URL}")

    try:
        login_form: Optional[LoginForm] = None
        if login:
            login_form = CLILoginForm()
        testcases = download_tool(
            DownloadArgs(
                url=config.URL,
                login_form=login_form,
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
