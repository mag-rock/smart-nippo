"""Report model for storing daily reports."""

from datetime import datetime

from pydantic import BaseModel, Field


class Report(BaseModel):
    """日報データのモデル."""

    id: int | None = Field(None, description="日報ID")
    template_id: int = Field(..., description="使用したテンプレートのID")
    data: dict[str, str | None] = Field(..., description="フィールド名と値のマッピング")
    created_at: datetime | None = Field(None, description="作成日時")
    updated_at: datetime | None = Field(None, description="更新日時")

    def get_field_value(self, field_name: str) -> str | None:
        """指定されたフィールドの値を取得."""
        return self.data.get(field_name)

    def set_field_value(self, field_name: str, value: str | None) -> None:
        """指定されたフィールドに値を設定."""
        self.data[field_name] = value

    def get_date(self) -> str | None:
        """日付フィールドの値を取得."""
        return self.get_field_value("date")

    def get_project(self) -> str | None:
        """プロジェクト名フィールドの値を取得."""
        return self.get_field_value("project")
