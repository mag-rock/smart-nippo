"""Configuration management for smart-nippo."""

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class DatabaseConfig(BaseModel):
    """データベース設定."""

    path: str = Field(
        default="~/.smart-nippo/data.db", description="データベースファイルパス"
    )


class EditorConfig(BaseModel):
    """エディタ設定."""

    command: str = Field(default="vim", description="エディタコマンド")


class DisplayConfig(BaseModel):
    """表示設定."""

    date_format: str = Field(default="%Y-%m-%d", description="日付フォーマット")
    time_format: str = Field(default="%H:%M", description="時刻フォーマット")
    language: str = Field(default="ja", description="表示言語")
    timezone: str = Field(default="Asia/Tokyo", description="タイムゾーン")


class DefaultsConfig(BaseModel):
    """デフォルト設定."""

    project: str = Field(default="", description="デフォルトプロジェクト")
    template: str = Field(default="default", description="デフォルトテンプレート")
    export_format: str = Field(
        default="markdown", description="デフォルトエクスポート形式"
    )


class Config(BaseModel):
    """アプリケーション設定."""

    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    editor: EditorConfig = Field(default_factory=EditorConfig)
    display: DisplayConfig = Field(default_factory=DisplayConfig)
    defaults: DefaultsConfig = Field(default_factory=DefaultsConfig)


class ConfigManager:
    """設定管理クラス."""

    def __init__(self, config_path: str | Path | None = None):
        """
        初期化.

        Args:
            config_path: 設定ファイルのパス。Noneの場合はデフォルトパスを使用。
        """
        if config_path is None:
            config_path = self._get_default_config_path()

        self.config_path = Path(config_path)
        self._config: Config | None = None

    def _get_default_config_path(self) -> Path:
        """デフォルトの設定ファイルパスを取得."""
        home = Path.home()
        smart_nippo_dir = home / ".smart-nippo"
        smart_nippo_dir.mkdir(exist_ok=True)
        return smart_nippo_dir / "config.yaml"

    def load(self) -> Config:
        """設定を読み込み."""
        if self._config is None:
            self._config = self._load_from_file()
        return self._config

    def _load_from_file(self) -> Config:
        """ファイルから設定を読み込み."""
        if not self.config_path.exists():
            # 設定ファイルが存在しない場合はデフォルト設定を作成
            config = Config()
            self.save(config)
            return config

        try:
            with open(self.config_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if data is None:
                data = {}

            return Config(**data)
        except Exception as e:
            raise RuntimeError(f"設定ファイルの読み込みに失敗しました: {e}") from e

    def save(self, config: Config | None = None) -> None:
        """設定をファイルに保存."""
        if config is None:
            config = self.load()

        # ディレクトリを作成
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(
                    config.model_dump(),
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                )
        except Exception as e:
            raise RuntimeError(f"設定ファイルの保存に失敗しました: {e}") from e

    def reload(self) -> Config:
        """設定を再読み込み."""
        self._config = None
        return self.load()

    def get(self, key: str, default: Any = None) -> Any:
        """設定値を取得."""
        config = self.load()
        keys = key.split(".")

        value = config
        for k in keys:
            if hasattr(value, k):
                value = getattr(value, k)
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """設定値を設定."""
        config = self.load()
        keys = key.split(".")

        # 最後のキー以外を辿る
        target = config
        for k in keys[:-1]:
            if hasattr(target, k):
                target = getattr(target, k)
            else:
                raise ValueError(f"設定キー '{key}' が見つかりません")

        # 最後のキーに値を設定
        final_key = keys[-1]
        if hasattr(target, final_key):
            setattr(target, final_key, value)
            self.save(config)
        else:
            raise ValueError(f"設定キー '{key}' が見つかりません")

    def get_database_path(self) -> Path:
        """データベースパスを取得（環境変数展開済み）."""
        config = self.load()
        path_str = config.database.path

        # 環境変数を展開
        path_str = os.path.expanduser(path_str)
        path_str = os.path.expandvars(path_str)

        return Path(path_str)

    def get_editor_command(self) -> str:
        """エディタコマンドを取得."""
        config = self.load()

        # 環境変数からエディタを取得することも可能
        env_editor = os.environ.get("EDITOR")
        if env_editor:
            return env_editor

        return config.editor.command


# グローバルな設定マネージャーインスタンス
_config_manager: ConfigManager | None = None


def get_config_manager() -> ConfigManager:
    """グローバルな設定マネージャーを取得."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config() -> Config:
    """設定を取得する便利関数."""
    manager = get_config_manager()
    return manager.load()

