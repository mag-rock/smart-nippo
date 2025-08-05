"""Main CLI entry point for smart-nippo"""

import typer
from rich.console import Console

from smart_nippo.cli.commands.hello import hello

app = typer.Typer(
    name="smart-nippo",
    help="日報入力支援ツール",
    add_completion=False,
)
console = Console()

# Add subcommands
app.command("hello")(hello)


@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-v", help="Show version"),
) -> None:
    """Main callback for the CLI application."""
    if version:
        from smart_nippo import __version__
        console.print(f"smart-nippo version {__version__}")
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        console.print(
            "[yellow]No command specified. Use --help for available commands.[/yellow]"
        )
        console.print("\n[bold]Available commands:[/bold]")
        console.print("  hello    Hello World コマンド")


def main() -> None:
    """Entry point for the CLI application."""
    app()


if __name__ == "__main__":
    main()
