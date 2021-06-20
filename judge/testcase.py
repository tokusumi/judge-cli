import subprocess
from pathlib import Path

import typer
from onlinejudge import utils

MAX_SAMPLE_NUM = 100


def main(
    contest: str,
    problem: str,
    directory: Path = typer.Argument("tests", help="a directory path for test cases"),
    format: str = typer.Option("sample-u%i.%e", help="custom filename format"),
    cookie: Path = typer.Option(utils.default_cookie_path, help="directory for cookie"),
) -> None:
    """
    Here is shortcut for add new brank testcase files.

    Pass `problem` at `contest` you want to add testcase for.

    Ex) the following leads to download test cases and add testcase for Problem `C` at `ABC 051`:
    ```add abc051 c```
    """
    typer.echo(f"Add testcase for {contest}")

    typer.echo("Check for test cases...")
    test_dir = directory / f"{contest}_{problem}"

    # only empty test dir is deleted
    try:
        test_dir.rmdir()
    except OSError:
        ...

    if not test_dir.exists():
        confirm: str = typer.prompt(
            "Are you sure you want to download test cases?", default="no"
        )
        if confirm.lower() in {"yes", "y"}:
            err = subprocess.run(
                ["judge", "download", contest, problem, directory]
            ).returncode
            if err:
                raise typer.Abort()
        else:
            typer.echo("Skip to download system testcase.")
            test_dir.mkdir(parents=True)

    embbed = format.replace("%e", "in")
    idx = 1
    for i in range(1, MAX_SAMPLE_NUM + 1):
        if not (test_dir / embbed.replace("%i", f"{i}")).exists():
            idx = i
            break
    else:
        raise typer.Abort("Can't create new sample")

    sample_in = test_dir / format.replace("%i", f"{idx}").replace("%e", "in")
    sample_out = test_dir / format.replace("%i", f"{idx}").replace("%e", "out")
    sample_in.touch()
    sample_out.touch()
    typer.echo(f"Created: {sample_in.stem}")


if __name__ == "__main__":
    typer.run(main)
