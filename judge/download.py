from pathlib import Path

import typer
from onlinejudge import utils

from judge.tools.download import DownloadArgs, SaveArgs
from judge.tools.download import download as download_tool
from judge.tools.download import save as save_tool


def main(
    contest: str,
    problem: str,
    directory: Path = typer.Argument("tests", help="a directory path for test cases"),
    no_store: bool = typer.Option(False, help="testcases is shown but not saved"),
    format: str = typer.Option("sample-%i.%e", help="custom filename format"),
    cookie: Path = typer.Option(utils.default_cookie_path, help="directory for cookie"),
) -> None:
    """
    Here is shortcut for download with `online-judge-tools`.

    Pass `problem` at `contest` you want to test.

    Ex) the following leads to download test cases for Problem `C` at `ABC 051`:
    ```download abc051 c```
    """
    typer.echo(f"Download {contest}")

    try:
        testcases = download_tool(
            DownloadArgs(
                contest=contest,
                no=problem,
                cookie=cookie,
            )
        )
    except Exception as e:
        typer.echo(e)
        raise typer.Abort()

    if not no_store:
        try:
            save_tool(
                testcases,
                SaveArgs(
                    format=format,
                    directory=directory / f"{contest}_{problem}",
                ),
            )
        except Exception as e:
            typer.echo(e)
            raise typer.Abort()


if __name__ == "__main__":
    typer.run(main)
