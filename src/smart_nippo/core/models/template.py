"""Template models for report creation."""

from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from .field_types import DateDefault, FieldType


class TemplateField(BaseModel):
    """テンプレートフィールドの定義."""

    name: str = Field(..., description="フィールド名（識別子）")
    label: str = Field(..., description="表示ラベル")
    field_type: FieldType = Field(..., description="フィールドタイプ")
    required: bool = Field(True, description="必須項目かどうか")
    default_value: str | None = Field(None, description="デフォルト値")
    options: list[str] | None = Field(None, description="選択肢（selection型の場合）")
    placeholder: str | None = Field(None, description="プレースホルダー")
    max_length: int | None = Field(None, description="最大文字数（text型の場合）")
    order: int = Field(0, description="表示順序")

    @model_validator(mode="after")
    def validate_field_type_constraints(self):
        """フィールドタイプに応じた制約をチェック."""
        # 選択型の場合は選択肢が必須
        if self.field_type == FieldType.SELECTION and not self.options:
            raise ValueError("selection型には選択肢（options）が必要です")

        # テキスト型の最大文字数チェック
        if (
            self.field_type == FieldType.TEXT
            and self.max_length
            and self.max_length > 255
        ):
            raise ValueError("text型の最大文字数は255文字です")

        return self


class Template(BaseModel):
    """日報テンプレートの定義."""

    id: int | None = Field(None, description="テンプレートID")
    name: str = Field(..., description="テンプレート名")
    description: str | None = Field(None, description="テンプレートの説明")
    fields: list[TemplateField] = Field(..., description="フィールドのリスト")
    is_default: bool = Field(False, description="デフォルトテンプレートかどうか")
    created_at: datetime | None = Field(None, description="作成日時")
    updated_at: datetime | None = Field(None, description="更新日時")

    @model_validator(mode="after")
    def validate_unique_field_names(self):
        """フィールド名の重複チェック."""
        names = [field.name for field in self.fields]
        if len(names) != len(set(names)):
            raise ValueError("フィールド名が重複しています")
        return self


def create_default_template() -> Template:
    """デフォルトテンプレートを作成."""
    fields = [
        TemplateField(
            name="date",
            label="日付",
            field_type=FieldType.DATE,
            required=True,
            default_value=DateDefault.TODAY.value,
            options=None,
            placeholder=None,
            max_length=None,
            order=1,
        ),
        TemplateField(
            name="project",
            label="プロジェクト名",
            field_type=FieldType.TEXT,
            required=True,
            default_value=None,
            options=None,
            placeholder="例: プロジェクトA",
            max_length=100,
            order=2,
        ),
        TemplateField(
            name="start_time",
            label="開始時刻",
            field_type=FieldType.TIME,
            required=False,
            default_value="09:00",
            options=None,
            placeholder=None,
            max_length=None,
            order=3,
        ),
        TemplateField(
            name="end_time",
            label="終了時刻",
            field_type=FieldType.TIME,
            required=False,
            default_value="18:00",
            options=None,
            placeholder=None,
            max_length=None,
            order=4,
        ),
        TemplateField(
            name="content",
            label="作業内容",
            field_type=FieldType.MEMO,
            required=True,
            default_value=None,
            options=None,
            placeholder="今日の作業内容を記入してください",
            max_length=None,
            order=5,
        ),
        TemplateField(
            name="progress",
            label="進捗状況",
            field_type=FieldType.SELECTION,
            required=True,
            default_value="進行中",
            options=["完了", "進行中", "未着手"],
            placeholder=None,
            max_length=None,
            order=6,
        ),
        TemplateField(
            name="issues",
            label="課題・問題点",
            field_type=FieldType.MEMO,
            required=False,
            default_value=None,
            options=None,
            placeholder="課題や問題点があれば記入してください",
            max_length=None,
            order=7,
        ),
        TemplateField(
            name="tomorrow_plan",
            label="明日の予定",
            field_type=FieldType.MEMO,
            required=False,
            default_value=None,
            options=None,
            placeholder="明日の作業予定を記入してください",
            max_length=None,
            order=8,
        ),
        TemplateField(
            name="notes",
            label="備考・メモ",
            field_type=FieldType.MEMO,
            required=False,
            default_value=None,
            options=None,
            placeholder="その他のメモや備考",
            max_length=None,
            order=9,
        ),
    ]

    return Template(
        id=None,
        name="標準テンプレート",
        description="日報作成用の標準テンプレート",
        fields=fields,
        is_default=True,
        created_at=None,
        updated_at=None,
    )
