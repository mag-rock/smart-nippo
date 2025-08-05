"""Clipboard operations command for smart-nippo"""

import pyperclip
import typer
from rich.console import Console

console = Console()


def clipboard(
    text: str = typer.Argument(..., help="クリップボードにコピーするテキスト"),
    prefix: str = typer.Option("", "--prefix", "-p", help="前に追加する文字列"),
    suffix: str = typer.Option("", "--suffix", "-s", help="後に追加する文字列"),
    format_template: str = typer.Option(
        "", "--template", "-t", help="フォーマットテンプレート（{text}を置換）"
    ),
    show: bool = typer.Option(False, "--show", help="内容を表示"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="メッセージを表示しない"),
) -> None:
    """指定されたテキストをクリップボードにコピーします"""

    try:
        # テキストをフォーマット
        if format_template:
            formatted_text = format_template.format(text=text)
        else:
            formatted_text = f"{prefix}{text}{suffix}"

        # クリップボードにコピー
        pyperclip.copy(formatted_text)

        if not quiet:
            console.print(
                f"[green]✓[/green] コピー完了: [bold]{len(formatted_text)}[/bold] 文字"
            )

        if show:
            console.print("\n[bold]クリップボードの内容:[/bold]")
            console.print(f"[dim]{formatted_text}[/dim]")

    except Exception as e:
        console.print(f"[red]✗[/red] クリップボードへのコピーに失敗しました: {e}")
        raise typer.Exit(1) from e


def paste() -> None:
    """クリップボードの内容を表示します"""

    try:
        clipboard_content = pyperclip.paste()

        if not clipboard_content:
            console.print("[yellow]クリップボードは空です[/yellow]")
            return

        console.print(
            f"[bold]内容 ([green]{len(clipboard_content)}[/green] 文字):[/bold]"
        )
        console.print(clipboard_content)

    except Exception as e:
        console.print(f"[red]✗[/red] クリップボードの読み取りに失敗しました: {e}")
        raise typer.Exit(1) from e
