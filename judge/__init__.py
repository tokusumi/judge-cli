import typer

from judge import download, testing

app = typer.Typer()
app.command("download")(download.main)
app.command("test")(testing.main)


@app.callback()
def callback() -> None:
    """Judgement tool"""
