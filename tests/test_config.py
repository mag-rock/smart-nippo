"""Tests for configuration management."""

import tempfile
from pathlib import Path

import pytest

from smart_nippo.core.config import (
    Config,
    ConfigManager,
    DatabaseConfig,
    DefaultsConfig,
    DisplayConfig,
    EditorConfig,
)


class TestConfigModels:
    """設定モデルのテスト."""

    def test_database_config_defaults(self):
        """DatabaseConfigのデフォルト値をテスト."""
        config = DatabaseConfig()
        assert config.path == "~/.smart-nippo/data.db"

    def test_editor_config_defaults(self):
        """EditorConfigのデフォルト値をテスト."""
        config = EditorConfig()
        assert config.command == "vim"

    def test_display_config_defaults(self):
        """DisplayConfigのデフォルト値をテスト."""
        config = DisplayConfig()
        assert config.date_format == "%Y-%m-%d"
        assert config.time_format == "%H:%M"
        assert config.language == "ja"
        assert config.timezone == "Asia/Tokyo"

    def test_defaults_config_defaults(self):
        """DefaultsConfigのデフォルト値をテスト."""
        config = DefaultsConfig()
        assert config.project == ""
        assert config.template == "default"
        assert config.export_format == "markdown"

    def test_config_creation(self):
        """設定の作成をテスト."""
        config = Config()
        assert isinstance(config.database, DatabaseConfig)
        assert isinstance(config.editor, EditorConfig)
        assert isinstance(config.display, DisplayConfig)
        assert isinstance(config.defaults, DefaultsConfig)


class TestConfigManager:
    """ConfigManagerクラスのテスト."""

    def test_default_config_path(self):
        """デフォルトの設定ファイルパスが正しく設定されることを確認."""
        manager = ConfigManager()
        assert manager.config_path.name == "config.yaml"
        assert ".smart-nippo" in str(manager.config_path)

    def test_custom_config_path(self):
        """カスタムの設定ファイルパスが正しく設定されることを確認."""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_path = Path(temp_dir) / "custom_config.yaml"
            manager = ConfigManager(custom_path)
            assert manager.config_path == custom_path

    def test_load_creates_default_config(self):
        """設定ファイルが存在しない場合にデフォルト設定が作成されることをテスト."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.yaml"
            manager = ConfigManager(config_path)

            config = manager.load()

            # デフォルト設定が読み込まれることを確認
            assert isinstance(config, Config)
            assert config.database.path == "~/.smart-nippo/data.db"
            assert config.editor.command == "vim"

            # ファイルが作成されることを確認
            assert config_path.exists()

    def test_save_and_load_config(self):
        """設定の保存と読み込みをテスト."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.yaml"
            manager = ConfigManager(config_path)

            # カスタム設定を作成
            config = Config()
            config.database.path = "/custom/path/data.db"
            config.editor.command = "nano"
            config.defaults.project = "デフォルトプロジェクト"

            # 保存
            manager.save(config)
            assert config_path.exists()

            # 新しいマネージャーで読み込み
            manager2 = ConfigManager(config_path)
            loaded_config = manager2.load()

            # 値が正しく保存・読み込みされることを確認
            assert loaded_config.database.path == "/custom/path/data.db"
            assert loaded_config.editor.command == "nano"
            assert loaded_config.defaults.project == "デフォルトプロジェクト"

    def test_get_method(self):
        """get メソッドのテスト."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.yaml"
            manager = ConfigManager(config_path)

            # 値を取得
            assert manager.get("database.path") == "~/.smart-nippo/data.db"
            assert manager.get("editor.command") == "vim"
            assert manager.get("display.language") == "ja"

            # 存在しないキーのデフォルト値
            assert manager.get("nonexistent.key", "default") == "default"

    def test_set_method(self):
        """set メソッドのテスト."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.yaml"
            manager = ConfigManager(config_path)

            # 値を設定
            manager.set("database.path", "/new/path/data.db")
            manager.set("editor.command", "code")

            # 値が正しく設定されることを確認
            assert manager.get("database.path") == "/new/path/data.db"
            assert manager.get("editor.command") == "code"

            # ファイルに保存されることを確認
            manager2 = ConfigManager(config_path)
            assert manager2.get("database.path") == "/new/path/data.db"
            assert manager2.get("editor.command") == "code"

    def test_set_invalid_key(self):
        """無効なキーの設定でエラーが発生することをテスト."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.yaml"
            manager = ConfigManager(config_path)

            with pytest.raises(ValueError, match="設定キー.*が見つかりません"):
                manager.set("invalid.key", "value")

    def test_reload_method(self):
        """reload メソッドのテスト."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.yaml"
            manager = ConfigManager(config_path)

            # 初回読み込み
            config1 = manager.load()
            original_path = config1.database.path

            # 外部でファイルを変更（実際の使用ケースをシミュレート）
            import yaml
            with open(config_path, "w", encoding="utf-8") as f:
                data = {
                    "database": {"path": "/external/change/data.db"},
                    "editor": {"command": "vim"},
                    "display": {
                        "date_format": "%Y-%m-%d",
                        "time_format": "%H:%M",
                        "language": "ja",
                        "timezone": "Asia/Tokyo"
                    },
                    "defaults": {
                        "project": "",
                        "template": "default",
                        "export_format": "markdown"
                    }
                }
                yaml.safe_dump(data, f)

            # リロードして変更が反映されることを確認
            config2 = manager.reload()
            assert config2.database.path == "/external/change/data.db"
            assert config2.database.path != original_path

    def test_get_database_path_expansion(self):
        """データベースパスの環境変数展開をテスト."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.yaml"
            manager = ConfigManager(config_path)

            # ホームディレクトリ展開をテスト
            manager.set("database.path", "~/.smart-nippo/test.db")
            expanded_path = manager.get_database_path()

            assert "~" not in str(expanded_path)
            assert ".smart-nippo/test.db" in str(expanded_path)

    def test_get_editor_command_env_override(self):
        """環境変数でのエディタコマンド上書きをテスト."""
        import os

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.yaml"
            manager = ConfigManager(config_path)

            # 環境変数がない場合は設定ファイルの値
            assert manager.get_editor_command() == "vim"

            # 環境変数を設定
            old_editor = os.environ.get("EDITOR")
            try:
                os.environ["EDITOR"] = "emacs"
                assert manager.get_editor_command() == "emacs"
            finally:
                # 環境変数を元に戻す
                if old_editor is not None:
                    os.environ["EDITOR"] = old_editor
                elif "EDITOR" in os.environ:
                    del os.environ["EDITOR"]
