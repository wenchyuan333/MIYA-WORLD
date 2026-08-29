import typer
from tools.miya_gateway.registry import list_functions
from tools.miya_gateway.executor import invoke

app = typer.Typer()

@app.command()
def list():
    functions = list_functions()
    for k, v in functions.items():
        typer.echo(f"{k} {v['signature']} — {v['description']}")

@app.command()
def call(name: str, args_json: str = "{}", caller: str = "cli"):
    import json
    args = json.loads(args_json)
    res = invoke(name, args, caller=caller)
    typer.echo(res)

if __name__ == "__main__":
    app()
