"""SQLAlchemy database models."""

import json
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """データベースモデルのベースクラス."""
    pass


class TemplateDB(Base):
    """テンプレートのデータベースモデル."""

    __tablename__ = "templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    fields: Mapped[list["TemplateFieldDB"]] = relationship(
        "TemplateFieldDB", back_populates="template", cascade="all, delete-orphan"
    )
    projects: Mapped[list["ProjectDB"]] = relationship(
        "ProjectDB", back_populates="template"
    )
    reports: Mapped[list["ReportDB"]] = relationship(
        "ReportDB", back_populates="template"
    )


class TemplateFieldDB(Base):
    """テンプレートフィールドのデータベースモデル."""

    __tablename__ = "template_fields"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    template_id: Mapped[int] = mapped_column(ForeignKey("templates.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    field_type: Mapped[str] = mapped_column(String(50), nullable=False)
    required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    default_value: Mapped[str | None] = mapped_column(String(255), nullable=True)
    options_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    placeholder: Mapped[str | None] = mapped_column(String(255), nullable=True)
    max_length: Mapped[int | None] = mapped_column(Integer, nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    template: Mapped[TemplateDB] = relationship("TemplateDB", back_populates="fields")

    @property
    def options(self) -> list[str] | None:
        """選択肢を取得."""
        if self.options_json:
            return json.loads(self.options_json)
        return None

    @options.setter
    def options(self, value: list[str] | None) -> None:
        """選択肢を設定."""
        if value:
            self.options_json = json.dumps(value, ensure_ascii=False)
        else:
            self.options_json = None


class ProjectDB(Base):
    """プロジェクトのデータベースモデル."""

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    template_id: Mapped[int | None] = mapped_column(
        ForeignKey("templates.id"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    template: Mapped[TemplateDB | None] = relationship(
        "TemplateDB", back_populates="projects"
    )
    reports: Mapped[list["ReportDB"]] = relationship(
        "ReportDB", back_populates="project"
    )


class ReportDB(Base):
    """日報のデータベースモデル."""

    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    template_id: Mapped[int] = mapped_column(ForeignKey("templates.id"), nullable=False)
    project_id: Mapped[int | None] = mapped_column(
        ForeignKey("projects.id"), nullable=True
    )
    data_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    template: Mapped[TemplateDB] = relationship("TemplateDB", back_populates="reports")
    project: Mapped[ProjectDB | None] = relationship(
        "ProjectDB", back_populates="reports"
    )

    @property
    def data(self) -> dict[str, Any]:
        """日報データを取得."""
        return json.loads(self.data_json)

    @data.setter
    def data(self, value: dict[str, Any]) -> None:
        """日報データを設定."""
        self.data_json = json.dumps(value, ensure_ascii=False)

    def get_field_value(self, field_name: str) -> Any:
        """指定されたフィールドの値を取得."""
        return self.data.get(field_name)

    def set_field_value(self, field_name: str, value: Any) -> None:
        """指定されたフィールドに値を設定."""
        data = self.data
        data[field_name] = value
        self.data = data

    def get_date(self) -> str | None:
        """日付フィールドの値を取得."""
        return self.get_field_value("date")

    def get_project_name(self) -> str | None:
        """プロジェクト名フィールドの値を取得."""
        return self.get_field_value("project")

