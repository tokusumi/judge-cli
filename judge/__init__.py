import typer

from judge import download

app = typer.Typer()
app.command("download")(download.main)


@app.callback()
def callback() -> None:
    """Judgement tool"""
