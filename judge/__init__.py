import typer

from judge import configure, download, testcase, testing

app = typer.Typer()
app.command("download")(download.main)
app.command("add")(testcase.main)
app.command("test")(testing.main)
app.command("conf")(configure.main)


@app.callback()
def callback() -> None:
    """Judgement tool"""
