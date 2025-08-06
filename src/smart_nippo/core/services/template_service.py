"""Template management service."""



from ..database import TemplateDB, TemplateFieldDB, get_session
from ..models import FieldType, Template, TemplateField


class TemplateService:
    """テンプレート管理サービス."""

    @staticmethod
    def create_template(
        name: str,
        fields: list[TemplateField],
        description: str | None = None,
        is_default: bool = False,
    ) -> Template:
        """
        テンプレートを作成.

        Args:
            name: テンプレート名
            fields: フィールドのリスト
            description: テンプレートの説明
            is_default: デフォルトテンプレートにするか

        Returns:
            作成されたテンプレート

        Raises:
            ValueError: テンプレート名が重複している場合
        """
        with get_session() as session:
            # 名前の重複チェック
            existing = session.query(TemplateDB).filter_by(name=name).first()
            if existing:
                raise ValueError(f"テンプレート名 '{name}' は既に存在します")

            # デフォルトテンプレートの処理
            if is_default:
                # 既存のデフォルトを解除
                session.query(TemplateDB).filter_by(is_default=True).update(
                    {"is_default": False}
                )

            # テンプレートを作成
            template_db = TemplateDB(
                name=name,
                description=description,
                is_default=is_default,
            )
            session.add(template_db)
            session.flush()

            # フィールドを追加
            for field in fields:
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
                if field.options:
                    field_db.options = field.options
                session.add(field_db)

            session.commit()

            # Pydanticモデルに変換して返す
            return TemplateService._db_to_model(template_db)

    @staticmethod
    def get_template(
        template_id: int | None = None, name: str | None = None
    ) -> Template | None:
        """
        テンプレートを取得.

        Args:
            template_id: テンプレートID
            name: テンプレート名

        Returns:
            テンプレート（見つからない場合はNone）
        """
        with get_session() as session:
            query = session.query(TemplateDB)

            if template_id is not None:
                template_db = query.filter_by(id=template_id).first()
            elif name is not None:
                template_db = query.filter_by(name=name).first()
            else:
                return None

            if template_db:
                return TemplateService._db_to_model(template_db)
            return None

    @staticmethod
    def get_default_template() -> Template | None:
        """デフォルトテンプレートを取得."""
        with get_session() as session:
            template_db = session.query(TemplateDB).filter_by(is_default=True).first()
            if template_db:
                return TemplateService._db_to_model(template_db)
            return None

    @staticmethod
    def list_templates() -> list[Template]:
        """全テンプレートを取得."""
        with get_session() as session:
            templates_db = session.query(TemplateDB).all()
            return [TemplateService._db_to_model(t) for t in templates_db]

    @staticmethod
    def update_template(
        template_id: int,
        name: str | None = None,
        description: str | None = None,
        fields: list[TemplateField] | None = None,
        is_default: bool | None = None,
    ) -> Template:
        """
        テンプレートを更新.

        Args:
            template_id: テンプレートID
            name: 新しいテンプレート名
            description: 新しい説明
            fields: 新しいフィールドリスト
            is_default: デフォルトテンプレートにするか

        Returns:
            更新されたテンプレート

        Raises:
            ValueError: テンプレートが見つからない場合
        """
        with get_session() as session:
            template_db = session.query(TemplateDB).filter_by(id=template_id).first()
            if not template_db:
                raise ValueError(f"テンプレートID {template_id} が見つかりません")

            # 名前の更新と重複チェック
            if name is not None and name != template_db.name:
                existing = session.query(TemplateDB).filter_by(name=name).first()
                if existing:
                    raise ValueError(f"テンプレート名 '{name}' は既に存在します")
                template_db.name = name

            # 説明の更新
            if description is not None:
                template_db.description = description

            # デフォルトフラグの更新
            if is_default is not None:
                if is_default:
                    # 既存のデフォルトを解除
                    session.query(TemplateDB).filter_by(is_default=True).update(
                        {"is_default": False}
                    )
                template_db.is_default = is_default

            # フィールドの更新
            if fields is not None:
                # 既存のフィールドを削除
                session.query(TemplateFieldDB).filter_by(
                    template_id=template_id
                ).delete()

                # 新しいフィールドを追加
                for field in fields:
                    field_db = TemplateFieldDB(
                        template_id=template_id,
                        name=field.name,
                        label=field.label,
                        field_type=field.field_type.value,
                        required=field.required,
                        default_value=field.default_value,
                        placeholder=field.placeholder,
                        max_length=field.max_length,
                        order=field.order,
                    )
                    if field.options:
                        field_db.options = field.options
                    session.add(field_db)

            session.commit()
            return TemplateService._db_to_model(template_db)

    @staticmethod
    def delete_template(template_id: int) -> bool:
        """
        テンプレートを削除.

        Args:
            template_id: テンプレートID

        Returns:
            削除に成功した場合True

        Raises:
            ValueError: デフォルトテンプレートを削除しようとした場合
        """
        with get_session() as session:
            template_db = session.query(TemplateDB).filter_by(id=template_id).first()
            if not template_db:
                return False

            if template_db.is_default:
                raise ValueError("デフォルトテンプレートは削除できません")

            session.delete(template_db)
            session.commit()
            return True

    @staticmethod
    def set_default_template(template_id: int) -> Template:
        """
        テンプレートをデフォルトに設定.

        Args:
            template_id: テンプレートID

        Returns:
            更新されたテンプレート

        Raises:
            ValueError: テンプレートが見つからない場合
        """
        with get_session() as session:
            template_db = session.query(TemplateDB).filter_by(id=template_id).first()
            if not template_db:
                raise ValueError(f"テンプレートID {template_id} が見つかりません")

            # 既存のデフォルトを解除
            session.query(TemplateDB).filter_by(is_default=True).update(
                {"is_default": False}
            )

            # 新しいデフォルトを設定
            template_db.is_default = True
            session.commit()

            return TemplateService._db_to_model(template_db)

    @staticmethod
    def _db_to_model(template_db: TemplateDB) -> Template:
        """データベースモデルをPydanticモデルに変換."""
        fields = []
        for field_db in sorted(template_db.fields, key=lambda f: f.order):
            field = TemplateField(
                name=field_db.name,
                label=field_db.label,
                field_type=FieldType(field_db.field_type),
                required=field_db.required,
                default_value=field_db.default_value,
                options=field_db.options,
                placeholder=field_db.placeholder,
                max_length=field_db.max_length,
                order=field_db.order,
            )
            fields.append(field)

        return Template(
            id=template_db.id,
            name=template_db.name,
            description=template_db.description,
            fields=fields,
            is_default=template_db.is_default,
            created_at=template_db.created_at,
            updated_at=template_db.updated_at,
        )

    @staticmethod
    def validate_template_data(template: Template) -> list[str]:
        """
        テンプレートデータを検証.

        Args:
            template: 検証するテンプレート

        Returns:
            エラーメッセージのリスト（エラーがない場合は空リスト）
        """
        errors = []

        # テンプレート名の検証
        if not template.name or not template.name.strip():
            errors.append("テンプレート名は必須です")

        # フィールドの検証
        if not template.fields:
            errors.append("少なくとも1つのフィールドが必要です")

        # フィールド名の重複チェック
        field_names = [f.name for f in template.fields]
        if len(field_names) != len(set(field_names)):
            errors.append("フィールド名が重複しています")

        # 各フィールドの検証
        for i, field in enumerate(template.fields):
            if not field.name or not field.name.strip():
                errors.append(f"フィールド{i+1}: 名前は必須です")
            if not field.label or not field.label.strip():
                errors.append(f"フィールド{i+1}: ラベルは必須です")
            if field.field_type == FieldType.SELECTION and not field.options:
                errors.append(
                    f"フィールド{i+1} ({field.name}): 選択型には選択肢が必要です"
                )

        return errors
