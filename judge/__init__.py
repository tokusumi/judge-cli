import typer

from judge import download, testing, configure

app = typer.Typer()
app.command("download")(download.main)
app.command("test")(testing.main)
app.command("conf")(configure.main)


@app.callback()
def callback() -> None:
    """Judgement tool"""
