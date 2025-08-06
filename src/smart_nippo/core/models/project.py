"""Project model for managing projects."""

from datetime import datetime

from pydantic import BaseModel, Field


class Project(BaseModel):
    """プロジェクトのモデル."""

    id: int | None = Field(None, description="プロジェクトID")
    name: str = Field(..., description="プロジェクト名")
    description: str | None = Field(None, description="プロジェクトの説明")
    template_id: int | None = Field(None, description="デフォルトのテンプレートID")
    is_active: bool = Field(True, description="アクティブなプロジェクトかどうか")
    created_at: datetime | None = Field(None, description="作成日時")
