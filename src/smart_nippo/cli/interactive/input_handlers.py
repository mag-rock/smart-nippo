"""Interactive input handlers for different field types."""

import tempfile
import subprocess
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Any

import questionary
from rich.console import Console

from smart_nippo.core.config import get_config
from smart_nippo.core.models import FieldType, TemplateField
from smart_nippo.core.validators import validate_report_data

console = Console()


class InputHandler:
    """Base class for input handlers."""
    
    def __init__(self, field: TemplateField):
        """Initialize input handler.
        
        Args:
            field: Template field definition
        """
        self.field = field
    
    def get_input(self, current_value: str | None = None) -> str | None:
        """Get input value for the field.
        
        Args:
            current_value: Current value (for editing)
            
        Returns:
            Input value or None if cancelled
        """
        raise NotImplementedError


class DateInputHandler(InputHandler):
    """Handler for date type input."""
    
    def get_input(self, current_value: str | None = None) -> str | None:
        """Get date input with calendar-like selection."""
        default_date = self._get_default_date(current_value)
        
        # カレンダー風の選択肢を提供
        today = date.today()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        
        choices = [
            questionary.Choice(f"今日 ({today.strftime('%Y-%m-%d')})", today.strftime('%Y-%m-%d')),
            questionary.Choice(f"昨日 ({yesterday.strftime('%Y-%m-%d')})", yesterday.strftime('%Y-%m-%d')),
            questionary.Choice(f"明日 ({tomorrow.strftime('%Y-%m-%d')})", tomorrow.strftime('%Y-%m-%d')),
            questionary.Choice("その他の日付を入力", "custom"),
        ]
        
        # デフォルト値がある場合は選択肢に追加
        if default_date and default_date not in [today.strftime('%Y-%m-%d'), yesterday.strftime('%Y-%m-%d'), tomorrow.strftime('%Y-%m-%d')]:
            choices.insert(0, questionary.Choice(f"デフォルト ({default_date})", default_date))
        
        result = questionary.select(
            f"{self.field.label}:",
            choices=choices,
            default=default_date if default_date in [c.value for c in choices] else choices[0].value
        ).ask()
        
        if result is None:
            return None
        
        if result == "custom":
            # 手動入力
            while True:
                custom_date = questionary.text(
                    f"{self.field.label} (YYYY-MM-DD形式):",
                    default=current_value or default_date or ""
                ).ask()
                
                if custom_date is None:
                    return None
                
                if not custom_date and not self.field.required:
                    return None
                
                try:
                    # 日付形式の検証
                    datetime.strptime(custom_date, '%Y-%m-%d')
                    return custom_date
                except ValueError:
                    console.print("[red]無効な日付形式です。YYYY-MM-DD形式で入力してください。[/red]")
                    continue
        
        return result
    
    def _get_default_date(self, current_value: str | None) -> str | None:
        """Get default date value."""
        if current_value:
            return current_value
        
        if self.field.default_value:
            if self.field.default_value == "today":
                return date.today().strftime('%Y-%m-%d')
            elif self.field.default_value == "yesterday":
                return (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
            elif self.field.default_value == "tomorrow":
                return (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
            else:
                return self.field.default_value
        
        return None


class TimeInputHandler(InputHandler):
    """Handler for time type input."""
    
    def get_input(self, current_value: str | None = None) -> str | None:
        """Get time input with 15-minute increments."""
        # 15分刻みの時刻選択肢を生成
        time_choices = []
        for hour in range(24):
            for minute in [0, 15, 30, 45]:
                time_str = f"{hour:02d}:{minute:02d}"
                display_str = f"{time_str}"
                if hour < 12:
                    display_str += f" (午前)"
                elif hour == 12:
                    display_str += f" (正午)"
                else:
                    display_str += f" (午後)"
                
                time_choices.append(questionary.Choice(display_str, time_str))
        
        # よく使う時間を先頭に追加
        common_times = [
            ("09:00", "午前9時 (開始時間)"),
            ("12:00", "正午 (昼休み)"),
            ("18:00", "午後6時 (終了時間)"),
            ("custom", "その他の時刻を入力"),
        ]
        
        common_choices = [questionary.Choice(label, value) for value, label in common_times]
        
        # デフォルト値を考慮
        default_value = current_value or self.field.default_value
        
        result = questionary.select(
            f"{self.field.label}:",
            choices=common_choices + [questionary.Choice("---", None)] + time_choices[:24],  # 最初の24個だけ表示
            default=default_value
        ).ask()
        
        if result is None:
            return None
        
        if result == "custom":
            # 手動入力
            while True:
                custom_time = questionary.text(
                    f"{self.field.label} (HH:MM形式):",
                    default=current_value or self.field.default_value or ""
                ).ask()
                
                if custom_time is None:
                    return None
                
                if not custom_time and not self.field.required:
                    return None
                
                try:
                    # 時刻形式の検証
                    datetime.strptime(custom_time, '%H:%M')
                    return custom_time
                except ValueError:
                    console.print("[red]無効な時刻形式です。HH:MM形式で入力してください。[/red]")
                    continue
        
        return result


class TextInputHandler(InputHandler):
    """Handler for text type input."""
    
    def get_input(self, current_value: str | None = None) -> str | None:
        """Get single-line text input."""
        default_value = current_value or self.field.default_value or ""
        
        result = questionary.text(
            f"{self.field.label}:",
            default=default_value,
            validate=self._validate_text
        ).ask()
        
        if result is None:
            return None
        
        if not result and not self.field.required:
            return None
        
        return result
    
    def _validate_text(self, value: str) -> bool | str:
        """Validate text input."""
        if not value and self.field.required:
            return "この項目は必須です"
        
        if self.field.max_length and len(value) > self.field.max_length:
            return f"最大{self.field.max_length}文字まで入力できます"
        
        return True


class MemoInputHandler(InputHandler):
    """Handler for memo type input."""
    
    def get_input(self, current_value: str | None = None) -> str | None:
        """Get multi-line memo input using external editor."""
        # まず簡易入力か外部エディタか選択
        if current_value:
            preview = current_value[:50] + "..." if len(current_value) > 50 else current_value
            choice = questionary.select(
                f"{self.field.label} (現在の値: {preview}):",
                choices=[
                    questionary.Choice("簡易入力 (1行)", "simple"),
                    questionary.Choice("外部エディタで編集", "editor"),
                    questionary.Choice("現在の値を保持", "keep"),
                ]
            ).ask()
        else:
            choice = questionary.select(
                f"{self.field.label}:",
                choices=[
                    questionary.Choice("簡易入力 (1行)", "simple"),
                    questionary.Choice("外部エディタで編集", "editor"),
                ]
            ).ask()
        
        if choice is None:
            return None
        
        if choice == "keep":
            return current_value
        
        if choice == "simple":
            # 簡易入力モード
            result = questionary.text(
                f"{self.field.label} (簡易入力):",
                default=current_value or self.field.default_value or ""
            ).ask()
            
            if result is None:
                return None
            
            if not result and not self.field.required:
                return None
            
            return result
        
        elif choice == "editor":
            # 外部エディタモード
            return self._open_editor(current_value)
        
        return None
    
    def _open_editor(self, current_value: str | None) -> str | None:
        """Open external editor for memo input."""
        config = get_config()
        editor_command = config.get("editor.command", "vim")
        
        # 一時ファイルを作成
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
            
            # 既存の値があれば書き込み
            if current_value:
                tmp_file.write(current_value)
            elif self.field.placeholder:
                tmp_file.write(f"# {self.field.placeholder}\n\n")
        
        try:
            # エディタを起動
            console.print(f"[blue]外部エディタ ({editor_command}) を起動します...[/blue]")
            
            result = subprocess.run(
                [editor_command, str(tmp_path)],
                check=False
            )
            
            if result.returncode != 0:
                console.print(f"[red]エディタの実行に失敗しました (終了コード: {result.returncode})[/red]")
                return current_value
            
            # 編集結果を読み込み
            with open(tmp_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # プレースホルダー行を除去
            if self.field.placeholder and content.startswith(f"# {self.field.placeholder}"):
                lines = content.split('\n')
                content = '\n'.join(lines[2:]).strip()  # 最初の2行（プレースホルダーと空行）を除去
            
            if not content and not self.field.required:
                return None
            
            return content or None
        
        except Exception as e:
            console.print(f"[red]エディタの起動に失敗しました: {e}[/red]")
            return current_value
        
        finally:
            # 一時ファイルを削除
            try:
                tmp_path.unlink()
            except Exception:
                pass


class SelectionInputHandler(InputHandler):
    """Handler for selection type input."""
    
    def get_input(self, current_value: str | None = None) -> str | None:
        """Get selection input from predefined options."""
        if not self.field.options:
            console.print("[red]選択肢が定義されていません[/red]")
            return None
        
        choices = [questionary.Choice(option, option) for option in self.field.options]
        
        # デフォルト値を決定
        default_value = current_value or self.field.default_value
        if default_value not in self.field.options:
            default_value = self.field.options[0]
        
        result = questionary.select(
            f"{self.field.label}:",
            choices=choices,
            default=default_value
        ).ask()
        
        return result


def get_input_handler(field: TemplateField) -> InputHandler:
    """Get appropriate input handler for field type.
    
    Args:
        field: Template field definition
        
    Returns:
        Input handler instance
        
    Raises:
        ValueError: If field type is not supported
    """
    handlers = {
        FieldType.DATE: DateInputHandler,
        FieldType.TIME: TimeInputHandler,
        FieldType.TEXT: TextInputHandler,
        FieldType.MEMO: MemoInputHandler,
        FieldType.SELECTION: SelectionInputHandler,
    }
    
    handler_class = handlers.get(field.field_type)
    if handler_class is None:
        raise ValueError(f"Unsupported field type: {field.field_type}")
    
    return handler_class(field)


def collect_report_data(template, existing_data: dict | None = None) -> dict[str, Any] | None:
    """Collect report data interactively using template fields.
    
    Args:
        template: Template definition
        existing_data: Existing data for editing
        
    Returns:
        Collected data dict or None if cancelled
    """
    console.print(f"\n[bold cyan]{template.name}[/bold cyan]")
    if template.description:
        console.print(f"[dim]{template.description}[/dim]")
    console.print()
    
    data = {}
    existing_data = existing_data or {}
    
    # フィールドを順序通りに処理
    sorted_fields = sorted(template.fields, key=lambda f: f.order)
    
    for field in sorted_fields:
        console.print(f"[bold]{field.order}. {field.label}[/bold]")
        if field.required:
            console.print("[red]* 必須項目[/red]")
        
        # フィールド固有の入力ハンドラーを取得
        handler = get_input_handler(field)
        
        # 現在の値を取得
        current_value = existing_data.get(field.name)
        
        # 入力を取得
        try:
            value = handler.get_input(current_value)
            
            if value is None and field.required:
                console.print("[red]必須項目です。入力をキャンセルしました。[/red]")
                return None
            
            # バリデーション
            if value is not None:
                # 個別フィールドではなく、全体バリデーションは後で実行
                # ここでは基本的な型チェックのみ
                try:
                    if field.field_type == FieldType.DATE:
                        datetime.strptime(value, '%Y-%m-%d')
                    elif field.field_type == FieldType.TIME:
                        datetime.strptime(value, '%H:%M')
                except ValueError as e:
                    console.print(f"[red]入力形式エラー: {e}[/red]")
                    return None
            
            data[field.name] = value
            
        except KeyboardInterrupt:
            console.print("\n[yellow]入力がキャンセルされました[/yellow]")
            return None
        except Exception as e:
            console.print(f"[red]入力エラー: {e}[/red]")
            return None
        
        console.print()  # 空行で区切り
    
    return data