"""Database initialization functions."""

from sqlalchemy import inspect

from ..models.template import create_default_template
from .models import Base, TemplateDB, TemplateFieldDB
from .session import get_database_manager, get_session


def create_tables() -> None:
    """全テーブルを作成."""
    manager = get_database_manager()
    if manager.engine is None:
        raise RuntimeError("データベースエンジンが初期化されていません")

    Base.metadata.create_all(bind=manager.engine)


def init_database() -> None:
    """データベースを初期化."""
    # テーブルを作成
    create_tables()

    # デフォルトテンプレートが存在しない場合は作成
    with get_session() as session:
        default_template = session.query(TemplateDB).filter_by(is_default=True).first()
        if default_template is None:
            _create_default_template(session)


def _create_default_template(session) -> None:
    """デフォルトテンプレートをデータベースに作成."""
    # Pydanticモデルからデフォルトテンプレートを取得
    template_model = create_default_template()

    # SQLAlchemyモデルに変換
    template_db = TemplateDB(
        name=template_model.name,
        description=template_model.description,
        is_default=template_model.is_default,
    )

    session.add(template_db)
    session.flush()  # IDを取得するためにflush

    # フィールドを追加
    for field in template_model.fields:
        field_db = TemplateFieldDB(
            template_id=template_db.id,
            name=field.name,
            label=field.label,
            field_type=field.field_type.value,
            required=field.required,
            default_value=field.default_value,
            placeholder=field.placeholder,
            max_length=field.max_length,
            order=field.order,
        )

        # 選択肢を設定
        if field.options:
            field_db.options = field.options

        session.add(field_db)

    session.commit()


def reset_database() -> None:
    """データベースをリセット（テスト用）."""
    manager = get_database_manager()
    if manager.engine is None:
        raise RuntimeError("データベースエンジンが初期化されていません")

    Base.metadata.drop_all(bind=manager.engine)
    init_database()


def database_exists() -> bool:
    """データベースが存在し、テーブルが作成されているかチェック."""
    try:
        manager = get_database_manager()
        if manager.engine is None:
            return False

        inspector = inspect(manager.engine)
        tables = inspector.get_table_names()

        # 必要なテーブルがすべて存在するかチェック
        required_tables = {"templates", "template_fields", "projects", "reports"}
        return required_tables.issubset(set(tables))
    except Exception:
        return False

