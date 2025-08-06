"""Tests for core models."""

import pytest
from datetime import date, datetime, timedelta

from smart_nippo.core.models import (
    FieldType,
    DateDefault,
    TemplateField,
    Template,
    Report,
    Project,
)
from smart_nippo.core.models.template import create_default_template
from smart_nippo.core.validators import FieldValidator, validate_report_data


class TestFieldTypes:
    """FieldType と DateDefault のテスト."""

    def test_field_type_values(self):
        """FieldTypeの値が正しいことを確認."""
        assert FieldType.DATE.value == "date"
        assert FieldType.TIME.value == "time"
        assert FieldType.TEXT.value == "text"
        assert FieldType.MEMO.value == "memo"
        assert FieldType.SELECTION.value == "selection"

    def test_date_default_values(self):
        """DateDefaultの値が正しいことを確認."""
        assert DateDefault.TODAY.value == "today"
        assert DateDefault.YESTERDAY.value == "yesterday"
        assert DateDefault.TOMORROW.value == "tomorrow"


class TestTemplateField:
    """TemplateFieldモデルのテスト."""

    def test_create_text_field(self):
        """テキスト型フィールドの作成."""
        field = TemplateField(
            name="project",
            label="プロジェクト名",
            field_type=FieldType.TEXT,
            required=True,
            max_length=100,
        )
        assert field.name == "project"
        assert field.field_type == FieldType.TEXT
        assert field.required is True
        assert field.max_length == 100

    def test_create_selection_field(self):
        """選択型フィールドの作成."""
        field = TemplateField(
            name="progress",
            label="進捗状況",
            field_type=FieldType.SELECTION,
            options=["完了", "進行中", "未着手"],
            default_value="進行中",
        )
        assert field.field_type == FieldType.SELECTION
        assert field.options == ["完了", "進行中", "未着手"]
        assert field.default_value == "進行中"

    def test_selection_field_without_options(self):
        """選択型フィールドでoptionsが未指定の場合エラー."""
        with pytest.raises(ValueError, match="選択肢（options）が必要"):
            TemplateField(
                name="status",
                label="ステータス",
                field_type=FieldType.SELECTION,
            )

    def test_text_field_max_length_limit(self):
        """テキスト型フィールドの最大文字数制限."""
        with pytest.raises(ValueError, match="最大文字数は255文字"):
            TemplateField(
                name="title",
                label="タイトル",
                field_type=FieldType.TEXT,
                max_length=300,
            )


class TestTemplate:
    """Templateモデルのテスト."""

    def test_create_template(self):
        """テンプレートの作成."""
        fields = [
            TemplateField(
                name="date",
                label="日付",
                field_type=FieldType.DATE,
                required=True,
            ),
            TemplateField(
                name="content",
                label="内容",
                field_type=FieldType.MEMO,
                required=True,
            ),
        ]
        template = Template(
            name="シンプルテンプレート",
            description="最小限のテンプレート",
            fields=fields,
        )
        assert template.name == "シンプルテンプレート"
        assert len(template.fields) == 2
        assert template.is_default is False

    def test_duplicate_field_names(self):
        """フィールド名の重複チェック."""
        fields = [
            TemplateField(
                name="date",
                label="日付1",
                field_type=FieldType.DATE,
            ),
            TemplateField(
                name="date",  # 重複
                label="日付2",
                field_type=FieldType.DATE,
            ),
        ]
        with pytest.raises(ValueError, match="フィールド名が重複"):
            Template(name="重複テスト", fields=fields)

    def test_create_default_template(self):
        """デフォルトテンプレートの作成."""
        template = create_default_template()
        assert template.name == "標準テンプレート"
        assert template.is_default is True
        assert len(template.fields) == 9

        # 必須フィールドの確認
        date_field = next(f for f in template.fields if f.name == "date")
        assert date_field.required is True
        assert date_field.field_type == FieldType.DATE


class TestFieldValidator:
    """FieldValidatorのテスト."""

    def test_validate_date_with_default(self):
        """日付型のデフォルト値検証."""
        field = TemplateField(
            name="date",
            label="日付",
            field_type=FieldType.DATE,
            default_value=DateDefault.TODAY.value,
        )
        result = FieldValidator.validate_date("today", field)
        assert result == date.today().isoformat()

        result = FieldValidator.validate_date("yesterday", field)
        assert result == (date.today() - timedelta(days=1)).isoformat()

    def test_validate_date_with_value(self):
        """日付型の値検証."""
        field = TemplateField(
            name="date",
            label="日付",
            field_type=FieldType.DATE,
        )
        result = FieldValidator.validate_date("2024-01-15", field)
        assert result == "2024-01-15"

        with pytest.raises(ValueError, match="YYYY-MM-DD 形式"):
            FieldValidator.validate_date("2024/01/15", field)

    def test_validate_time(self):
        """時刻型の検証."""
        field = TemplateField(
            name="start_time",
            label="開始時刻",
            field_type=FieldType.TIME,
        )
        
        # 正しい形式
        assert FieldValidator.validate_time("09:00", field) == "09:00"
        assert FieldValidator.validate_time("23:45", field) == "23:45"
        
        # 15分刻みでない場合の丸め
        assert FieldValidator.validate_time("09:07", field) == "09:00"
        assert FieldValidator.validate_time("09:08", field) == "09:15"
        assert FieldValidator.validate_time("09:23", field) == "09:30"
        
        # 不正な形式
        with pytest.raises(ValueError, match="HH:MM 形式"):
            FieldValidator.validate_time("9時30分", field)

    def test_validate_text(self):
        """テキスト型の検証."""
        field = TemplateField(
            name="project",
            label="プロジェクト",
            field_type=FieldType.TEXT,
            max_length=10,
        )
        
        # 正常な値
        assert FieldValidator.validate_text("プロジェクトA", field) == "プロジェクトA"
        
        # 改行を含む場合
        with pytest.raises(ValueError, match="改行を含めることはできません"):
            FieldValidator.validate_text("プロジェクト\nA", field)
        
        # 文字数超過
        with pytest.raises(ValueError, match="10文字以内"):
            FieldValidator.validate_text("あ" * 11, field)

    def test_validate_selection(self):
        """選択型の検証."""
        field = TemplateField(
            name="status",
            label="ステータス",
            field_type=FieldType.SELECTION,
            options=["完了", "進行中", "未着手"],
        )
        
        # 正しい選択肢
        assert FieldValidator.validate_selection("完了", field) == "完了"
        
        # 無効な選択肢
        with pytest.raises(ValueError, match="有効な選択肢ではありません"):
            FieldValidator.validate_selection("中断", field)

    def test_validate_required_field(self):
        """必須フィールドの検証."""
        field = TemplateField(
            name="content",
            label="内容",
            field_type=FieldType.TEXT,
            required=True,
        )
        
        # 値がない場合
        with pytest.raises(ValueError, match="必須項目"):
            FieldValidator.validate(None, field)
        with pytest.raises(ValueError, match="必須項目"):
            FieldValidator.validate("", field)


class TestValidateReportData:
    """validate_report_data関数のテスト."""

    def test_validate_complete_data(self):
        """完全なデータの検証."""
        fields = [
            TemplateField(
                name="date",
                label="日付",
                field_type=FieldType.DATE,
                required=True,
            ),
            TemplateField(
                name="content",
                label="内容",
                field_type=FieldType.MEMO,
                required=True,
            ),
        ]
        
        data = {
            "date": "2024-01-15",
            "content": "今日の作業内容",
        }
        
        result = validate_report_data(data, fields)
        assert result["date"] == "2024-01-15"
        assert result["content"] == "今日の作業内容"

    def test_validate_with_missing_required(self):
        """必須項目が不足している場合."""
        fields = [
            TemplateField(
                name="date",
                label="日付",
                field_type=FieldType.DATE,
                required=True,
            ),
            TemplateField(
                name="content",
                label="内容",
                field_type=FieldType.MEMO,
                required=True,
            ),
        ]
        
        data = {
            "date": "2024-01-15",
            # contentが不足
        }
        
        with pytest.raises(ValueError, match="内容: .* は必須項目"):
            validate_report_data(data, fields)