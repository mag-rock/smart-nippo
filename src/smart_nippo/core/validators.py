"""Field validators for report input."""

import re
from datetime import date, datetime, timedelta

from .models import DateDefault, FieldType, TemplateField


class FieldValidator:
    """フィールド値のバリデーター."""

    @staticmethod
    def validate_date(value: str, field: TemplateField) -> str:  # noqa: ARG004
        """日付型の値を検証."""
        # デフォルト値の処理
        if value in [
            DateDefault.TODAY.value,
            DateDefault.YESTERDAY.value,
            DateDefault.TOMORROW.value,
        ]:
            today = date.today()
            if value == DateDefault.TODAY.value:
                return today.isoformat()
            elif value == DateDefault.YESTERDAY.value:
                return (today - timedelta(days=1)).isoformat()
            elif value == DateDefault.TOMORROW.value:
                return (today + timedelta(days=1)).isoformat()

        # YYYY-MM-DD形式のチェック
        try:
            parsed_date = datetime.strptime(value, "%Y-%m-%d").date()
            return parsed_date.isoformat()
        except ValueError as e:
            msg = f"日付は YYYY-MM-DD 形式で入力してください: {value}"
            raise ValueError(msg) from e

    @staticmethod
    def validate_time(value: str, field: TemplateField) -> str:  # noqa: ARG004
        """時刻型の値を検証."""
        # HH:MM形式のチェック
        time_pattern = re.compile(r"^([0-1]?[0-9]|2[0-3]):([0-5][0-9])$")
        if not time_pattern.match(value):
            raise ValueError(f"時刻は HH:MM 形式で入力してください: {value}")

        # 15分刻みのチェック（オプション）
        try:
            hour, minute = map(int, value.split(":"))
            if minute % 15 != 0:
                # 最も近い15分刻みに丸める
                rounded_minute = round(minute / 15) * 15
                if rounded_minute == 60:
                    hour = (hour + 1) % 24
                    rounded_minute = 0
                value = f"{hour:02d}:{rounded_minute:02d}"
        except Exception as e:
            raise ValueError(f"時刻の処理中にエラーが発生しました: {value}") from e

        return value

    @staticmethod
    def validate_text(value: str, field: TemplateField) -> str:
        """テキスト型の値を検証."""
        # 改行チェック
        if "\n" in value or "\r" in value:
            raise ValueError("テキスト型に改行を含めることはできません")

        # 最大文字数チェック
        max_length = field.max_length or 255
        if len(value) > max_length:
            msg = (
                f"テキストは{max_length}文字以内で入力してください"
                f"（現在: {len(value)}文字）"
            )
            raise ValueError(msg)

        return value.strip()

    @staticmethod
    def validate_memo(value: str, field: TemplateField) -> str:  # noqa: ARG004
        """メモ型の値を検証."""
        # メモ型は特に制限なし、前後の空白のみ削除
        return value.strip()

    @staticmethod
    def validate_selection(value: str, field: TemplateField) -> str:
        """選択型の値を検証."""
        if not field.options:
            raise ValueError("選択肢が定義されていません")

        if value not in field.options:
            raise ValueError(
                f"選択された値 '{value}' は有効な選択肢ではありません。"
                f"選択可能な値: {', '.join(field.options)}"
            )

        return value

    @classmethod
    def validate(cls, value: str | None, field: TemplateField) -> str | None:
        """フィールドの値を検証."""
        # 必須チェック
        if field.required and not value:
            raise ValueError(f"'{field.label}' は必須項目です")

        # 値がない場合はデフォルト値を使用
        if not value:
            return field.default_value

        # 型別の検証
        validators = {
            FieldType.DATE: cls.validate_date,
            FieldType.TIME: cls.validate_time,
            FieldType.TEXT: cls.validate_text,
            FieldType.MEMO: cls.validate_memo,
            FieldType.SELECTION: cls.validate_selection,
        }

        validator = validators.get(field.field_type)
        if not validator:
            raise ValueError(f"未対応のフィールドタイプ: {field.field_type}")

        return validator(value, field)


def validate_report_data(
    data: dict[str, str | None], template_fields: list[TemplateField]
) -> dict[str, str | None]:
    """日報データ全体を検証."""
    validated_data = {}
    errors = []

    for field in template_fields:
        try:
            value = data.get(field.name)
            validated_value = FieldValidator.validate(value, field)
            if validated_value is not None:
                validated_data[field.name] = validated_value
        except ValueError as e:
            errors.append(f"{field.label}: {e}")

    if errors:
        raise ValueError("入力エラー:\n" + "\n".join(errors))

    return validated_data
