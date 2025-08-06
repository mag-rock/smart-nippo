"""Main CLI entry point for smart-nippo"""

import typer
from rich.console import Console

from smart_nippo.cli.commands.clipboard import clipboard, paste
from smart_nippo.cli.commands.editor import edit
from smart_nippo.cli.commands.hello import hello
from smart_nippo.cli.commands.template import app as template_app
from smart_nippo.cli.commands.report import app as report_app

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

# Add report commands directly to main app
app.add_typer(report_app, name="report", help="日報管理")

# Convenience aliases for common report commands
@app.command("create")
def create_alias(
    template_id: int | None = typer.Option(None, "--template", "-t", help="使用するテンプレートID"),
    report_date: str | None = typer.Option(None, "--date", "-d", help="日報の日付 (YYYY-MM-DD)"),
) -> None:
    """日報を作成 (report create のエイリアス)."""
    from smart_nippo.cli.commands.report import create_report
    create_report(template_id, report_date, True)

@app.command("list")  
def list_alias(
    start_date: str | None = typer.Option(None, "--from", help="開始日 (YYYY-MM-DD)"),
    end_date: str | None = typer.Option(None, "--to", help="終了日 (YYYY-MM-DD)"),
    template_id: int | None = typer.Option(None, "--template", "-t", help="テンプレートID"),
    project: str | None = typer.Option(None, "--project", "-p", help="プロジェクト名"),
    keyword: str | None = typer.Option(None, "--keyword", "-k", help="キーワード検索"),
    limit: int = typer.Option(20, "--limit", "-l", help="表示件数"),
) -> None:
    """日報一覧を表示 (report list のエイリアス)."""
    from smart_nippo.cli.commands.report import list_reports
    list_reports(start_date, end_date, template_id, project, keyword, limit)


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
        console.print("  create     日報を作成")
        console.print("  list       日報一覧を表示")
        console.print("  template   テンプレート管理")
        console.print("  report     日報管理（詳細コマンド）")


def main() -> None:
    """Entry point for the CLI application."""
    app()


if __name__ == "__main__":
    main()
