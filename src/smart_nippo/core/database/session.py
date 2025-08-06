"""Database session management."""

from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


class DatabaseManager:
    """データベースマネージャー."""

    def __init__(self, database_path: str | Path | None = None):
        """
        初期化.

        Args:
            database_path: データベースファイルのパス。
                Noneの場合はデフォルトパスを使用。
        """
        if database_path is None:
            database_path = self._get_default_database_path()

        self.database_path = Path(database_path)
        self.engine: Engine | None = None
        self.SessionLocal: sessionmaker[Session] | None = None

    def _get_default_database_path(self) -> Path:
        """デフォルトのデータベースパスを取得."""
        home = Path.home()
        smart_nippo_dir = home / ".smart-nippo"
        smart_nippo_dir.mkdir(exist_ok=True)
        return smart_nippo_dir / "data.db"

    def initialize(self) -> None:
        """データベースエンジンとセッションを初期化."""
        # データベースディレクトリを作成
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

        # SQLiteエンジンを作成
        database_url = f"sqlite:///{self.database_path}"
        self.engine = create_engine(
            database_url,
            echo=False,  # SQLログの表示（開発時はTrue）
            pool_pre_ping=True,  # 接続の事前チェック
        )

        # セッションファクトリを作成
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False,
        )

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """データベースセッションを取得."""
        if self.SessionLocal is None:
            msg = (
                "データベースが初期化されていません。"
                "initialize()を呼び出してください。"
            )
            raise RuntimeError(msg)

        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def close(self) -> None:
        """データベース接続を閉じる."""
        if self.engine:
            self.engine.dispose()


# グローバルなデータベースマネージャーインスタンス
_database_manager: DatabaseManager | None = None


def get_database_manager() -> DatabaseManager:
    """グローバルなデータベースマネージャーを取得."""
    global _database_manager
    if _database_manager is None:
        _database_manager = DatabaseManager()
        _database_manager.initialize()
    return _database_manager


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """データベースセッションを取得する便利関数."""
    manager = get_database_manager()
    with manager.get_session() as session:
        yield session

