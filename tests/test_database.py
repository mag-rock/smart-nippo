"""Tests for database functionality."""

import tempfile
from pathlib import Path

import pytest

from smart_nippo.core.database import (
    DatabaseManager,
    ReportDB,
    TemplateDB,
    TemplateFieldDB,
    create_tables,
    database_exists,
    get_session,
    init_database,
    reset_database,
)
from smart_nippo.core.models.field_types import FieldType


class TestDatabaseManager:
    """DatabaseManagerクラスのテスト."""

    def test_default_database_path(self):
        """デフォルトのデータベースパスが正しく設定されることを確認."""
        manager = DatabaseManager()
        assert manager.database_path.name == "data.db"
        assert ".smart-nippo" in str(manager.database_path)

    def test_custom_database_path(self):
        """カスタムのデータベースパスが正しく設定されることを確認."""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_path = Path(temp_dir) / "test.db"
            manager = DatabaseManager(custom_path)
            assert manager.database_path == custom_path

    def test_initialize(self):
        """データベースの初期化が正しく動作することを確認."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            manager = DatabaseManager(db_path)
            
            manager.initialize()
            
            assert manager.engine is not None
            assert manager.SessionLocal is not None
            assert db_path.parent.exists()

    def test_get_session(self):
        """セッション取得が正しく動作することを確認."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            manager = DatabaseManager(db_path)
            manager.initialize()
            
            with manager.get_session() as session:
                assert session is not None

    def test_get_session_before_initialize(self):
        """初期化前のセッション取得でエラーが発生することを確認."""
        manager = DatabaseManager()
        
        with pytest.raises(RuntimeError, match="データベースが初期化されていません"):
            with manager.get_session():
                pass


class TestDatabaseModels:
    """データベースモデルのテスト."""

    @pytest.fixture(autouse=True)
    def setup_database(self):
        """テスト用データベースのセットアップ."""
        reset_database()
        yield
        # テスト後のクリーンアップは不要（一時ファイル使用のため）

    def test_create_tables(self):
        """テーブル作成が正しく動作することを確認."""
        create_tables()
        assert database_exists()

    def test_init_database(self):
        """データベース初期化が正しく動作することを確認."""
        init_database()
        
        # デフォルトテンプレートが作成されることを確認
        with get_session() as session:
            templates = session.query(TemplateDB).all()
            assert len(templates) >= 1
            
            default_template = session.query(TemplateDB).filter_by(is_default=True).first()
            assert default_template is not None
            assert default_template.name == "標準テンプレート"

    def test_template_model(self):
        """TemplateDBモデルの基本機能をテスト."""
        init_database()
        
        with get_session() as session:
            template = TemplateDB(
                name="テストテンプレート",
                description="テスト用のテンプレート",
                is_default=False,
            )
            session.add(template)
            session.commit()
            
            # 取得してチェック
            saved_template = session.query(TemplateDB).filter_by(name="テストテンプレート").first()
            assert saved_template is not None
            assert saved_template.description == "テスト用のテンプレート"
            assert saved_template.is_default is False

    def test_template_field_model(self):
        """TemplateFieldDBモデルの基本機能をテスト."""
        init_database()
        
        with get_session() as session:
            # テンプレートを作成
            template = TemplateDB(name="テストテンプレート")
            session.add(template)
            session.flush()
            
            # フィールドを作成
            field = TemplateFieldDB(
                template_id=template.id,
                name="test_field",
                label="テストフィールド",
                field_type=FieldType.TEXT.value,
                required=True,
                max_length=100,
                order=1,
            )
            session.add(field)
            session.commit()
            
            # 取得してチェック
            saved_field = session.query(TemplateFieldDB).filter_by(name="test_field").first()
            assert saved_field is not None
            assert saved_field.label == "テストフィールド"
            assert saved_field.field_type == FieldType.TEXT.value

    def test_template_field_options(self):
        """TemplateFieldDBの選択肢機能をテスト."""
        init_database()
        
        with get_session() as session:
            template = TemplateDB(name="テストテンプレート")
            session.add(template)
            session.flush()
            
            # 選択型フィールドを作成
            field = TemplateFieldDB(
                template_id=template.id,
                name="status",
                label="ステータス",
                field_type=FieldType.SELECTION.value,
            )
            
            # 選択肢を設定
            field.options = ["完了", "進行中", "未着手"]
            session.add(field)
            session.commit()
            
            # 取得してチェック
            saved_field = session.query(TemplateFieldDB).filter_by(name="status").first()
            assert saved_field is not None
            assert saved_field.options == ["完了", "進行中", "未着手"]

    def test_report_model(self):
        """ReportDBモデルの基本機能をテスト."""
        init_database()
        
        with get_session() as session:
            # デフォルトテンプレートを取得
            template = session.query(TemplateDB).filter_by(is_default=True).first()
            assert template is not None
            
            # 日報を作成
            report_data = {
                "date": "2024-01-15",
                "project": "テストプロジェクト",
                "content": "今日の作業内容",
            }
            
            report = ReportDB(
                template_id=template.id,
                data=report_data,
            )
            session.add(report)
            session.commit()
            
            # 取得してチェック
            saved_report = session.query(ReportDB).first()
            assert saved_report is not None
            assert saved_report.get_date() == "2024-01-15"
            assert saved_report.get_project_name() == "テストプロジェクト"
            assert saved_report.get_field_value("content") == "今日の作業内容"

    def test_report_data_operations(self):
        """ReportDBのデータ操作をテスト."""
        init_database()
        
        with get_session() as session:
            template = session.query(TemplateDB).filter_by(is_default=True).first()
            
            report = ReportDB(
                template_id=template.id,
                data={"date": "2024-01-15"},
            )
            session.add(report)
            session.flush()
            
            # フィールド値を設定
            report.set_field_value("project", "新プロジェクト")
            report.set_field_value("content", "新しい作業内容")
            session.commit()
            
            # データが正しく保存されているかチェック
            saved_report = session.query(ReportDB).filter_by(id=report.id).first()
            assert saved_report.get_field_value("project") == "新プロジェクト"
            assert saved_report.get_field_value("content") == "新しい作業内容"