"""Report management commands."""

from datetime import datetime, date
from typing import Optional

import questionary
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from smart_nippo.core.database import database_exists, init_database
from smart_nippo.core.services import ReportService, TemplateService
from smart_nippo.cli.interactive import collect_report_data

console = Console()
app = typer.Typer(help="日報作成・編集コマンド")


def ensure_database() -> None:
    """データベースが存在しない場合は初期化."""
    if not database_exists():
        init_database()
        console.print("[green]データベースを初期化しました[/green]")


@app.command("create")
def create_report(
    template_id: Optional[int] = typer.Option(None, "--template", "-t", help="使用するテンプレートID"),
    report_date: Optional[str] = typer.Option(None, "--date", "-d", help="日報の日付 (YYYY-MM-DD)"),
    interactive: bool = typer.Option(True, "--interactive/--no-interactive", "-i/-n",
                                     help="インタラクティブモードで作成"),
) -> None:
    """新しい日報を作成."""
    ensure_database()
    
    if not interactive:
        console.print("[yellow]非インタラクティブモードは未実装です[/yellow]")
        return
    
    console.print("[bold cyan]新しい日報を作成します[/bold cyan]\n")
    
    # テンプレート選択
    template = None
    if template_id:
        template = TemplateService.get_template(template_id)
        if not template:
            console.print(f"[red]テンプレートID {template_id} が見つかりません[/red]")
            return
    else:
        # テンプレート一覧から選択
        templates = TemplateService.list_templates()
        if not templates:
            console.print("[red]テンプレートが登録されていません。まずテンプレートを作成してください[/red]")
            console.print("例: smart-nippo template create")
            return
        
        # デフォルトテンプレートを先頭に
        default_template = next((t for t in templates if t.is_default), None)
        if default_template:
            template_choices = [
                questionary.Choice(
                    f"{default_template.name} (デフォルト)",
                    default_template
                )
            ]
            other_templates = [t for t in templates if not t.is_default]
            template_choices.extend([
                questionary.Choice(f"{t.name}", t) for t in other_templates
            ])
        else:
            template_choices = [questionary.Choice(f"{t.name}", t) for t in templates]
        
        template = questionary.select(
            "使用するテンプレートを選択:",
            choices=template_choices,
        ).ask()
        
        if template is None:
            console.print("[yellow]キャンセルされました[/yellow]")
            return
    
    # 日付の処理
    target_date = None
    if report_date:
        try:
            target_date = datetime.strptime(report_date, "%Y-%m-%d").date()
        except ValueError:
            console.print(f"[red]無効な日付形式です: {report_date}[/red]")
            return
    
    # 同じ日付の日報が既に存在するかチェック
    if target_date:
        existing_report = ReportService.get_report(
            report_date=target_date,
            template_id=template.id
        )
        if existing_report:
            console.print(
                f"[yellow]{target_date.strftime('%Y-%m-%d')} の日報は既に存在します[/yellow]"
            )
            
            action = questionary.select(
                "どうしますか？",
                choices=[
                    questionary.Choice("編集する", "edit"),
                    questionary.Choice("キャンセル", "cancel"),
                ]
            ).ask()
            
            if action == "edit":
                return _edit_existing_report(existing_report)
            else:
                return
    
    # インタラクティブデータ収集
    try:
        data = collect_report_data(template)
        if data is None:
            console.print("[yellow]作成がキャンセルされました[/yellow]")
            return
        
        # 日報作成
        report = ReportService.create_report(
            template_id=template.id,
            data=data,
            report_date=target_date,
        )
        
        console.print(
            f"\n[green]✓ 日報を作成しました "
            f"(ID: {report.id}, 日付: {report.get_date()})[/green]"
        )
        
        # 作成した日報の概要を表示
        _display_report_summary(report)
        
    except ValueError as e:
        console.print(f"[red]エラー: {e}[/red]")
    except KeyboardInterrupt:
        console.print("\n[yellow]作成がキャンセルされました[/yellow]")
    except Exception as e:
        console.print(f"[red]予期しないエラー: {e}[/red]")


@app.command("edit")
def edit_report(
    report_id: Optional[int] = typer.Option(None, "--id", help="編集する日報のID"),
    report_date: Optional[str] = typer.Option(None, "--date", "-d", help="編集する日報の日付 (YYYY-MM-DD)"),
) -> None:
    """既存の日報を編集."""
    ensure_database()
    
    console.print("[bold cyan]日報を編集します[/bold cyan]\n")
    
    # 日報を特定
    report = None
    if report_id:
        report = ReportService.get_report(report_id=report_id)
        if not report:
            console.print(f"[red]日報ID {report_id} が見つかりません[/red]")
            return
    
    elif report_date:
        try:
            target_date = datetime.strptime(report_date, "%Y-%m-%d").date()
            report = ReportService.get_report(report_date=target_date)
            if not report:
                console.print(f"[red]{target_date.strftime('%Y-%m-%d')} の日報が見つかりません[/red]")
                return
        except ValueError:
            console.print(f"[red]無効な日付形式です: {report_date}[/red]")
            return
    
    else:
        # 最近の日報から選択
        recent_reports = ReportService.list_reports(limit=10, order_by="created_desc")
        if not recent_reports:
            console.print("[yellow]編集可能な日報がありません[/yellow]")
            return
        
        report_choices = [
            questionary.Choice(
                f"{r.get_date()} - {r.template.name} - {r.get_project_name() or '未分類'}",
                r
            )
            for r in recent_reports
        ]
        
        report = questionary.select(
            "編集する日報を選択:",
            choices=report_choices,
        ).ask()
        
        if report is None:
            console.print("[yellow]キャンセルされました[/yellow]")
            return
    
    _edit_existing_report(report)


def _edit_existing_report(report) -> None:
    """既存日報の編集処理."""
    console.print(f"[blue]編集対象: {report.get_date()} - {report.template.name}[/blue]\n")
    
    # 現在のデータを表示
    _display_report_summary(report)
    
    # 編集確認
    confirm = questionary.confirm("この日報を編集しますか？").ask()
    if not confirm:
        console.print("[yellow]編集がキャンセルされました[/yellow]")
        return
    
    try:
        # インタラクティブデータ収集（既存データ付き）
        new_data = collect_report_data(report.template, report.data)
        if new_data is None:
            console.print("[yellow]編集がキャンセルされました[/yellow]")
            return
        
        # 日報更新
        updated_report = ReportService.update_report(report.id, new_data)
        
        console.print(f"\n[green]✓ 日報を更新しました (ID: {updated_report.id})[/green]")
        
        # 更新後の概要を表示
        _display_report_summary(updated_report)
        
    except ValueError as e:
        console.print(f"[red]エラー: {e}[/red]")
    except KeyboardInterrupt:
        console.print("\n[yellow]編集がキャンセルされました[/yellow]")
    except Exception as e:
        console.print(f"[red]予期しないエラー: {e}[/red]")


@app.command("list")
def list_reports(
    start_date: Optional[str] = typer.Option(None, "--from", help="開始日 (YYYY-MM-DD)"),
    end_date: Optional[str] = typer.Option(None, "--to", help="終了日 (YYYY-MM-DD)"),
    template_id: Optional[int] = typer.Option(None, "--template", "-t", help="テンプレートID"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="プロジェクト名"),
    keyword: Optional[str] = typer.Option(None, "--keyword", "-k", help="キーワード検索"),
    limit: int = typer.Option(20, "--limit", "-l", help="表示件数"),
) -> None:
    """日報一覧を表示."""
    ensure_database()
    
    # 日付パラメータの解析
    start_date_obj = None
    end_date_obj = None
    
    try:
        if start_date:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        if end_date:
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError as e:
        console.print(f"[red]日付形式エラー: {e}[/red]")
        return
    
    # 日報を取得
    reports = ReportService.list_reports(
        start_date=start_date_obj,
        end_date=end_date_obj,
        template_id=template_id,
        project_name=project,
        keyword=keyword,
        limit=limit,
        order_by="date_desc",
    )
    
    if not reports:
        console.print("[yellow]該当する日報がありません[/yellow]")
        return
    
    # 表形式で表示
    table = Table(title="日報一覧", show_header=True)
    table.add_column("ID", style="cyan", width=6)
    table.add_column("日付", style="green")
    table.add_column("テンプレート", style="blue")
    table.add_column("プロジェクト", style="yellow")
    table.add_column("作成日時", style="dim")
    
    for report in reports:
        table.add_row(
            str(report.id),
            report.get_date() or "不明",
            report.template.name,
            report.get_project_name() or "未分類",
            report.created_at.strftime("%m/%d %H:%M"),
        )
    
    console.print(table)
    console.print(f"\n[dim]表示件数: {len(reports)} 件[/dim]")


@app.command("show")
def show_report(
    report_id: Optional[int] = typer.Argument(None, help="表示する日報のID"),
    report_date: Optional[str] = typer.Option(None, "--date", "-d", help="表示する日報の日付 (YYYY-MM-DD)"),
) -> None:
    """日報の詳細を表示."""
    ensure_database()
    
    # 日報を特定
    report = None
    if report_id:
        report = ReportService.get_report(report_id=report_id)
    elif report_date:
        try:
            target_date = datetime.strptime(report_date, "%Y-%m-%d").date()
            report = ReportService.get_report(report_date=target_date)
        except ValueError:
            console.print(f"[red]無効な日付形式です: {report_date}[/red]")
            return
    else:
        console.print("[red]日報IDまたは日付を指定してください[/red]")
        return
    
    if not report:
        if report_id:
            console.print(f"[red]日報ID {report_id} が見つかりません[/red]")
        else:
            console.print(f"[red]{report_date} の日報が見つかりません[/red]")
        return
    
    _display_report_detail(report)


def _display_report_summary(report) -> None:
    """日報の概要を表示."""
    info_lines = [
        f"[bold]ID:[/bold] {report.id}",
        f"[bold]日付:[/bold] {report.get_date()}",
        f"[bold]テンプレート:[/bold] {report.template.name}",
    ]
    
    project_name = report.get_project_name()
    if project_name:
        info_lines.append(f"[bold]プロジェクト:[/bold] {project_name}")
    
    info_lines.extend([
        f"[bold]作成:[/bold] {report.created_at.strftime('%Y-%m-%d %H:%M')}",
        f"[bold]更新:[/bold] {report.updated_at.strftime('%Y-%m-%d %H:%M')}",
    ])
    
    console.print(Panel("\n".join(info_lines), title="日報情報"))


def _display_report_detail(report) -> None:
    """日報の詳細を表示."""
    # 基本情報
    _display_report_summary(report)
    
    # フィールド別データ表示
    console.print("\n[bold]日報内容:[/bold]")
    
    for field in sorted(report.template.fields, key=lambda f: f.order):
        value = report.data.get(field.name)
        if value is None:
            continue
        
        # 値の表示形式を調整
        if field.field_type.value == "memo" and len(str(value)) > 100:
            # 長いメモは折り畳み表示
            display_value = str(value)[:100] + "..."
        else:
            display_value = str(value)
        
        console.print(f"  [cyan]{field.label}:[/cyan] {display_value}")


@app.command("delete")
def delete_report(
    report_id: int = typer.Argument(..., help="削除する日報のID"),
    force: bool = typer.Option(False, "--force", "-f", help="確認なしで削除"),
) -> None:
    """日報を削除."""
    ensure_database()
    
    # 日報の存在確認
    report = ReportService.get_report(report_id=report_id)
    if not report:
        console.print(f"[red]日報ID {report_id} が見つかりません[/red]")
        return
    
    # 削除確認
    if not force:
        console.print(f"[yellow]削除対象: {report.get_date()} - {report.template.name}[/yellow]")
        confirm = questionary.confirm(
            f"日報 ID:{report_id} を削除しますか？"
        ).ask()
        if not confirm:
            console.print("[yellow]キャンセルされました[/yellow]")
            return
    
    # 削除実行
    try:
        if ReportService.delete_report(report_id):
            console.print(f"[green]✓ 日報 ID:{report_id} を削除しました[/green]")
        else:
            console.print(f"[red]日報の削除に失敗しました[/red]")
    except Exception as e:
        console.print(f"[red]エラー: {e}[/red]")


if __name__ == "__main__":
    app()