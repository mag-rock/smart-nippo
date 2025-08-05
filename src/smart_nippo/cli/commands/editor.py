"""Editor integration command for smart-nippo"""

import click
import typer
from rich.console import Console

console = Console()


def edit(
    initial_text: str = typer.Option("", "--text", "-t", help="初期テキスト"),
    extension: str = typer.Option(".txt", "--ext", "-e", help="一時ファイルの拡張子"),
    editor: str = typer.Option("", "--editor", help="使用するエディタ"),
    require_save: bool = typer.Option(
        True, "--require-save/--no-require-save", help="保存せず終了時エラー"
    ),
    show_result: bool = typer.Option(True, "--show/--no-show", help="編集結果を表示"),
    copy_to_clipboard: bool = typer.Option(
        False, "--copy", "-c", help="編集結果をクリップボードにコピー"
    ),
) -> None:
    """外部エディタを起動して内容を編集します

    デフォルトのエディタが起動し、編集した内容を取得できます。
    エディタは環境変数 EDITOR で指定できます。
    """

    try:
        # エディタの設定
        original_editor = None
        if editor:
            import os
            original_editor = os.environ.get("EDITOR")
            os.environ["EDITOR"] = editor

        # 初期テキストの設定
        if not initial_text and not initial_text.strip():
            initial_text = "# ここに内容を入力してください\n# この行は削除できます\n\n"

        console.print("[cyan]エディタを起動しています...[/cyan]")
        console.print("[dim]（編集を完了してエディタを閉じてください）[/dim]")

        # エディタを起動
        result = click.edit(initial_text, extension=extension)

        if result is None:
            if require_save:
                console.print("[yellow]⚠[/yellow] 編集内容が保存されませんでした")
                raise typer.Exit(1) from None
            else:
                console.print("[dim]編集がキャンセルされました[/dim]")
                return

        # 結果の処理
        result = result.strip()

        if not result:
            console.print("[yellow]空の内容が入力されました[/yellow]")
            return

        # 結果の表示
        if show_result:
            line_count = len(result.split('\n'))
            char_count = len(result)
            console.print(
                f"\n[bold]編集結果 ([green]{line_count}[/green] 行, "
                f"[green]{char_count}[/green] 文字):[/bold]"
            )
            console.print("[dim]" + "─" * 60 + "[/dim]")
            console.print(result)
            console.print("[dim]" + "─" * 60 + "[/dim]")

        # クリップボードにコピー
        if copy_to_clipboard:
            try:
                import pyperclip
                pyperclip.copy(result)
                console.print("[green]✓[/green] クリップボードにコピーしました")
            except Exception as e:
                console.print(f"[red]✗[/red] クリップボードへのコピーに失敗: {e}")

        # エディタ設定を復元
        if editor and original_editor:
            import os
            os.environ["EDITOR"] = original_editor

    except KeyboardInterrupt:
        console.print("\n[yellow]編集が中断されました[/yellow]")
        raise typer.Exit(1) from None
    except Exception as e:
        console.print(f"[red]✗[/red] エディタ起動エラー: {e}")
        console.print("[dim]EDITOR環境変数の設定を確認してください[/dim]")
        raise typer.Exit(1) from None
