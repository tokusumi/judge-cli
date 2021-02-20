import typer


app = typer.Typer()


@app.callback()
def callback() -> None:
    """Judgement tool"""