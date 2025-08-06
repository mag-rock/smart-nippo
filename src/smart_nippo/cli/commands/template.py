"""Template management commands."""

import json

import questionary
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from smart_nippo.core.database import database_exists, init_database
from smart_nippo.core.models import FieldType, TemplateField
from smart_nippo.core.services import TemplateService

console = Console()
app = typer.Typer(help="テンプレート管理コマンド")


def ensure_database() -> None:
    """データベースが存在しない場合は初期化."""
    if not database_exists():
        init_database()
        console.print("[green]データベースを初期化しました[/green]")


@app.command("list")
def list_templates() -> None:
    """テンプレート一覧を表示."""
    ensure_database()

    templates = TemplateService.list_templates()

    if not templates:
        console.print("[yellow]テンプレートが登録されていません[/yellow]")
        return

    table = Table(title="テンプレート一覧", show_header=True)
    table.add_column("ID", style="cyan", width=6)
    table.add_column("名前", style="green")
    table.add_column("説明", style="white")
    table.add_column("フィールド数", justify="center")
    table.add_column("デフォルト", justify="center")

    for template in templates:
        is_default = "✓" if template.is_default else ""
        table.add_row(
            str(template.id),
            template.name,
            template.description or "",
            str(len(template.fields)),
            is_default,
        )

    console.print(table)


@app.command("show")
def show_template(
    template_id: int | None = typer.Argument(None, help="テンプレートID"),
    name: str | None = typer.Option(None, "--name", "-n", help="テンプレート名"),
) -> None:
    """テンプレートの詳細を表示."""
    ensure_database()

    if template_id is None and name is None:
        # デフォルトテンプレートを表示
        template = TemplateService.get_default_template()
        if not template:
            console.print("[yellow]デフォルトテンプレートが設定されていません[/yellow]")
            return
    else:
        template = TemplateService.get_template(template_id, name)
        if not template:
            console.print("[red]テンプレートが見つかりません[/red]")
            return

    # テンプレート情報を表示
    info_lines = [
        f"[bold]名前:[/bold] {template.name}",
        f"[bold]ID:[/bold] {template.id}",
    ]
    if template.description:
        info_lines.append(f"[bold]説明:[/bold] {template.description}")
    if template.is_default:
        info_lines.append("[green]✓ デフォルトテンプレート[/green]")

    console.print(Panel("\n".join(info_lines), title="テンプレート情報"))

    # フィールド一覧を表示
    table = Table(title="フィールド一覧", show_header=True)
    table.add_column("#", width=3)
    table.add_column("名前", style="cyan")
    table.add_column("ラベル", style="green")
    table.add_column("型", style="yellow")
    table.add_column("必須", justify="center")
    table.add_column("デフォルト値")

    for field in sorted(template.fields, key=lambda f: f.order):
        required = "✓" if field.required else ""
        field_type = field.field_type.value
        default = field.default_value or ""

        # 選択型の場合は選択肢を表示
        if field.field_type == FieldType.SELECTION and field.options:
            field_type = f"{field_type} ({', '.join(field.options)})"

        table.add_row(
            str(field.order),
            field.name,
            field.label,
            field_type,
            required,
            default,
        )

    console.print(table)


@app.command("create")
def create_template(
    interactive: bool = typer.Option(True, "--interactive/--no-interactive", "-i/-n",
                                     help="インタラクティブモードで作成"),
) -> None:
    """新しいテンプレートを作成."""
    ensure_database()

    if not interactive:
        console.print("[yellow]非インタラクティブモードは未実装です[/yellow]")
        return

    console.print("[bold cyan]新しいテンプレートを作成します[/bold cyan]\n")

    # テンプレート名と説明を入力
    name = questionary.text("テンプレート名:").ask()
    if not name:
        console.print("[red]キャンセルされました[/red]")
        return

    description = questionary.text("説明 (省略可):").ask()
    is_default = questionary.confirm("デフォルトテンプレートにしますか？").ask()

    # フィールドを追加
    fields = []
    console.print(
        "\n[bold]フィールドを追加します "
        "(終了するには空のフィールド名を入力)[/bold]"
    )

    order = 1
    while True:
        console.print(f"\n[cyan]フィールド {order}:[/cyan]")

        field_name = questionary.text("  フィールド名 (例: date, project):").ask()
        if not field_name:
            break

        field_label = questionary.text("  表示ラベル (例: 日付, プロジェクト名):").ask()
        if not field_label:
            field_label = field_name

        # フィールドタイプを選択
        field_type_choices = [
            {"name": "date - 日付型", "value": "date"},
            {"name": "time - 時刻型", "value": "time"},
            {"name": "text - テキスト型（1行）", "value": "text"},
            {"name": "memo - メモ型（複数行）", "value": "memo"},
            {"name": "selection - 選択型", "value": "selection"},
        ]
        field_type_value = questionary.select(
            "  フィールドタイプ:",
            choices=field_type_choices,
        ).ask()
        field_type = FieldType(field_type_value)

        # 必須フィールドかどうか
        required = questionary.confirm("  必須項目にしますか？", default=True).ask()

        # デフォルト値
        default_value = questionary.text("  デフォルト値 (省略可):").ask() or None

        # プレースホルダー
        placeholder = None
        if field_type in [FieldType.TEXT, FieldType.MEMO]:
            placeholder = questionary.text("  プレースホルダー (省略可):").ask() or None

        # 最大文字数（テキスト型の場合）
        max_length = None
        if field_type == FieldType.TEXT:
            max_length_str = questionary.text(
                "  最大文字数 (省略可, デフォルト: 255):"
            ).ask()
            if max_length_str:
                try:
                    max_length = int(max_length_str)
                except ValueError:
                    console.print(
                        "[yellow]    無効な数値です。"
                        "デフォルト値を使用します[/yellow]"
                    )

        # 選択肢（選択型の場合）
        options = None
        if field_type == FieldType.SELECTION:
            console.print("  選択肢を入力 (カンマ区切り):")
            options_str = questionary.text("    例: 完了,進行中,未着手").ask()
            if options_str:
                options = [opt.strip() for opt in options_str.split(",")]

        # フィールドを追加
        field = TemplateField(
            name=field_name,
            label=field_label,
            field_type=field_type,
            required=required,
            default_value=default_value,
            options=options,
            placeholder=placeholder,
            max_length=max_length,
            order=order,
        )
        fields.append(field)
        order += 1

    if not fields:
        console.print("[red]フィールドが1つも追加されませんでした[/red]")
        return

    # テンプレートを作成
    try:
        template = TemplateService.create_template(
            name=name,
            description=description,
            fields=fields,
            is_default=is_default,
        )
        console.print(
            f"\n[green]✓ テンプレート '{template.name}' を作成しました "
            f"(ID: {template.id})[/green]"
        )
    except ValueError as e:
        console.print(f"[red]エラー: {e}[/red]")


@app.command("delete")
def delete_template(
    template_id: int = typer.Argument(..., help="削除するテンプレートのID"),
    force: bool = typer.Option(False, "--force", "-f", help="確認なしで削除"),
) -> None:
    """テンプレートを削除."""
    ensure_database()

    template = TemplateService.get_template(template_id)
    if not template:
        console.print("[red]テンプレートが見つかりません[/red]")
        return

    if template.is_default:
        console.print("[red]デフォルトテンプレートは削除できません[/red]")
        return

    if not force:
        confirm = questionary.confirm(
            f"テンプレート '{template.name}' を削除しますか？"
        ).ask()
        if not confirm:
            console.print("[yellow]キャンセルされました[/yellow]")
            return

    try:
        TemplateService.delete_template(template_id)
        console.print(f"[green]✓ テンプレート '{template.name}' を削除しました[/green]")
    except ValueError as e:
        console.print(f"[red]エラー: {e}[/red]")


@app.command("set-default")
def set_default_template(
    template_id: int = typer.Argument(..., help="デフォルトに設定するテンプレートのID"),
) -> None:
    """テンプレートをデフォルトに設定."""
    ensure_database()

    try:
        template = TemplateService.set_default_template(template_id)
        console.print(
            f"[green]✓ テンプレート '{template.name}' を"
            f"デフォルトに設定しました[/green]"
        )
    except ValueError as e:
        console.print(f"[red]エラー: {e}[/red]")


@app.command("export")
def export_template(
    template_id: int | None = typer.Argument(
        None, help="エクスポートするテンプレートのID"
    ),
    output: str | None = typer.Option(None, "--output", "-o", help="出力ファイルパス"),
) -> None:
    """テンプレートをJSON形式でエクスポート."""
    ensure_database()

    if template_id is None:
        # デフォルトテンプレートをエクスポート
        template = TemplateService.get_default_template()
        if not template:
            console.print("[yellow]デフォルトテンプレートが設定されていません[/yellow]")
            return
    else:
        template = TemplateService.get_template(template_id)
        if not template:
            console.print("[red]テンプレートが見つかりません[/red]")
            return

    # JSON形式に変換
    data = {
        "name": template.name,
        "description": template.description,
        "fields": [
            {
                "name": f.name,
                "label": f.label,
                "field_type": f.field_type.value,
                "required": f.required,
                "default_value": f.default_value,
                "options": f.options,
                "placeholder": f.placeholder,
                "max_length": f.max_length,
                "order": f.order,
            }
            for f in template.fields
        ],
    }

    json_str = json.dumps(data, ensure_ascii=False, indent=2)

    if output:
        # ファイルに出力
        try:
            with open(output, "w", encoding="utf-8") as f:
                f.write(json_str)
            console.print(f"[green]✓ テンプレートを {output} に出力しました[/green]")
        except Exception as e:
            console.print(f"[red]ファイル出力エラー: {e}[/red]")
    else:
        # 標準出力に表示
        console.print(json_str)


if __name__ == "__main__":
    app()
