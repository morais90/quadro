import click
from rich.console import Console


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx: click.Context) -> None:
    if ctx.invoked_subcommand is None:
        ctx.invoke(list_tasks)


@main.command("list")
def list_tasks() -> None:
    console = Console()
    console.print("List command not yet implemented")
