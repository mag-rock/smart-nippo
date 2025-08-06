"""Field type definitions for report templates."""

from enum import Enum


class FieldType(Enum):
    """入力フィールドの型定義."""

    DATE = "date"              # 日付型
    TIME = "time"              # 時刻型
    TEXT = "text"              # テキスト型（1行）
    MEMO = "memo"              # メモ型（複数行）
    SELECTION = "selection"    # 選択型


class DateDefault(Enum):
    """日付型のデフォルト値の種類."""

    TODAY = "today"            # 当日
    YESTERDAY = "yesterday"    # 前日
    TOMORROW = "tomorrow"      # 翌日
