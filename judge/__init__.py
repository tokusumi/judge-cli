import typer

from judge import download, testcase, testing

app = typer.Typer()
app.command("download")(download.main)
app.command("add")(testcase.main)
app.command("test")(testing.main)


@app.callback()
def callback() -> None:
    """Judgement tool"""
