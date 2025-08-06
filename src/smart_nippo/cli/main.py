"""Main CLI entry point for smart-nippo"""

import typer
from rich.console import Console

from smart_nippo.cli.commands.clipboard import clipboard, paste
from smart_nippo.cli.commands.editor import edit
from smart_nippo.cli.commands.hello import hello
from smart_nippo.cli.commands.template import app as template_app

app = typer.Typer(
    name="smart-nippo",
    help="日報入力支援ツール",
    add_completion=False,
)
console = Console()

# Add subcommands
app.command("hello")(hello)
app.command("copy")(clipboard)
app.command("paste")(paste)
app.command("edit")(edit)
app.add_typer(template_app, name="template", help="テンプレート管理")


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
        console.print("  hello      Hello World コマンド")
        console.print("  copy       テキストをクリップボードにコピー")
        console.print("  paste      クリップボードの内容を表示")
        console.print("  edit       外部エディタを起動して内容を編集")
        console.print("  template   テンプレート管理")


def main() -> None:
    """Entry point for the CLI application."""
    app()


if __name__ == "__main__":
    main()
