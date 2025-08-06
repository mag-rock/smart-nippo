"""Tests for template service."""

import pytest

from smart_nippo.core.database import init_database, reset_database
from smart_nippo.core.models import FieldType, Template, TemplateField
from smart_nippo.core.services import TemplateService


class TestTemplateService:
    """Template service tests."""

    @pytest.fixture(autouse=True)
    def setup_database(self):
        """テスト用データベースのセットアップ."""
        reset_database()
        init_database()
        yield

    def test_create_template(self) -> None:
        """テンプレート作成テスト."""
        # テストデータ準備
        fields = [
            TemplateField(
                name="date",
                label="日付",
                field_type=FieldType.DATE,
                required=True,
                order=1,
            ),
            TemplateField(
                name="project",
                label="プロジェクト",
                field_type=FieldType.SELECTION,
                required=True,
                options=["ProjectA", "ProjectB"],
                order=2,
            ),
        ]

        # テンプレート作成
        template = TemplateService.create_template(
            name="テストテンプレート",
            description="テスト用テンプレート",
            fields=fields,
            is_default=True,
        )

        # 検証
        assert template.id is not None
        assert template.name == "テストテンプレート"
        assert template.description == "テスト用テンプレート"
        assert template.is_default is True
        assert len(template.fields) == 2

        # フィールドの検証
        date_field = next(f for f in template.fields if f.name == "date")
        assert date_field.label == "日付"
        assert date_field.field_type == FieldType.DATE
        assert date_field.required is True

        project_field = next(f for f in template.fields if f.name == "project")
        assert project_field.label == "プロジェクト"
        assert project_field.field_type == FieldType.SELECTION
        assert project_field.options == ["ProjectA", "ProjectB"]

    def test_create_template_duplicate_name(self) -> None:
        """重複名でのテンプレート作成エラーテスト."""
        fields = [
            TemplateField(
                name="test",
                label="Test",
                field_type=FieldType.TEXT,
                required=False,
                order=1,
            )
        ]

        # 最初のテンプレート作成
        TemplateService.create_template(name="重複テスト", fields=fields)

        # 同じ名前で再作成（エラーになるはず）
        with pytest.raises(ValueError, match="既に存在します"):
            TemplateService.create_template(name="重複テスト", fields=fields)

    def test_get_template_by_id(self) -> None:
        """ID指定でのテンプレート取得テスト."""
        # テストデータ作成
        fields = [
            TemplateField(
                name="memo",
                label="メモ",
                field_type=FieldType.MEMO,
                required=False,
                order=1,
            )
        ]
        created = TemplateService.create_template(name="ID取得テスト", fields=fields)

        # ID指定で取得
        template = TemplateService.get_template(template_id=created.id)

        assert template is not None
        assert template.id == created.id
        assert template.name == "ID取得テスト"

    def test_get_template_by_name(self) -> None:
        """名前指定でのテンプレート取得テスト."""
        # テストデータ作成
        fields = [
            TemplateField(
                name="time",
                label="時刻",
                field_type=FieldType.TIME,
                required=True,
                order=1,
            )
        ]
        created = TemplateService.create_template(name="名前取得テスト", fields=fields)

        # 名前指定で取得
        template = TemplateService.get_template(name="名前取得テスト")

        assert template is not None
        assert template.id == created.id
        assert template.name == "名前取得テスト"

    def test_get_template_not_found(self) -> None:
        """存在しないテンプレートの取得テスト."""
        # 存在しないID
        template = TemplateService.get_template(template_id=999)
        assert template is None

        # 存在しない名前
        template = TemplateService.get_template(name="存在しない")
        assert template is None

    def test_get_default_template(self) -> None:
        """デフォルトテンプレート取得テスト."""
        fields = [
            TemplateField(
                name="test",
                label="Test",
                field_type=FieldType.TEXT,
                required=False,
                order=1,
            )
        ]

        # init_databaseで既にデフォルトテンプレートが作成されている
        existing_default = TemplateService.get_default_template()
        assert existing_default is not None

        # デフォルトテンプレート作成
        created = TemplateService.create_template(
            name="デフォルトテスト",
            fields=fields,
            is_default=True,
        )

        # デフォルト取得
        default = TemplateService.get_default_template()
        assert default is not None
        assert default.id == created.id
        assert default.is_default is True

    def test_list_templates(self) -> None:
        """テンプレート一覧取得テスト."""
        # 初期状態（init_databaseで標準テンプレートが1つ作成される）
        initial_templates = TemplateService.list_templates()
        initial_count = len(initial_templates)

        # テンプレート複数作成
        fields = [
            TemplateField(
                name="test",
                label="Test",
                field_type=FieldType.TEXT,
                required=False,
                order=1,
            )
        ]

        TemplateService.create_template(name="テンプレート1", fields=fields)
        TemplateService.create_template(name="テンプレート2", fields=fields)
        TemplateService.create_template(
            name="テンプレート3",
            fields=fields,
            is_default=True,
        )

        # 一覧取得
        templates = TemplateService.list_templates()
        assert len(templates) == initial_count + 3

        names = [t.name for t in templates]
        assert "テンプレート1" in names
        assert "テンプレート2" in names
        assert "テンプレート3" in names

        # デフォルトフラグの確認（テンプレート3を最後にデフォルトにしたので）
        default_templates = [t for t in templates if t.is_default]
        assert len(default_templates) == 1
        assert default_templates[0].name == "テンプレート3"

    def test_update_template(self) -> None:
        """テンプレート更新テスト."""
        # 初期データ作成
        fields = [
            TemplateField(
                name="original",
                label="Original",
                field_type=FieldType.TEXT,
                required=False,
                order=1,
            )
        ]
        created = TemplateService.create_template(
            name="更新前",
            description="更新前の説明",
            fields=fields,
        )

        # 新しいフィールド
        new_fields = [
            TemplateField(
                name="updated",
                label="Updated",
                field_type=FieldType.MEMO,
                required=True,
                order=1,
            ),
            TemplateField(
                name="selection",
                label="選択肢",
                field_type=FieldType.SELECTION,
                required=False,
                options=["A", "B", "C"],
                order=2,
            ),
        ]

        # 更新実行
        updated = TemplateService.update_template(
            template_id=created.id,
            name="更新後",
            description="更新後の説明",
            fields=new_fields,
            is_default=True,
        )

        # 検証
        assert updated.id == created.id
        assert updated.name == "更新後"
        assert updated.description == "更新後の説明"
        assert updated.is_default is True
        assert len(updated.fields) == 2

        # 新しいフィールドが設定されていること
        field_names = [f.name for f in updated.fields]
        assert "updated" in field_names
        assert "selection" in field_names
        assert "original" not in field_names  # 古いフィールドは削除されている

    def test_delete_template(self) -> None:
        """テンプレート削除テスト."""
        fields = [
            TemplateField(
                name="delete_test",
                label="Delete Test",
                field_type=FieldType.TEXT,
                required=False,
                order=1,
            )
        ]
        created = TemplateService.create_template(name="削除テスト", fields=fields)

        # 削除実行
        result = TemplateService.delete_template(created.id)
        assert result is True

        # 削除確認
        template = TemplateService.get_template(template_id=created.id)
        assert template is None

        # 存在しないIDの削除
        result = TemplateService.delete_template(999)
        assert result is False

    def test_delete_default_template_error(self) -> None:
        """デフォルトテンプレート削除エラーテスト."""
        fields = [
            TemplateField(
                name="test",
                label="Test",
                field_type=FieldType.TEXT,
                required=False,
                order=1,
            )
        ]
        created = TemplateService.create_template(
            name="デフォルト削除テスト",
            fields=fields,
            is_default=True,
        )

        # デフォルトテンプレートの削除はエラー
        with pytest.raises(ValueError, match="デフォルトテンプレートは削除できません"):
            TemplateService.delete_template(created.id)

    def test_set_default_template(self) -> None:
        """デフォルトテンプレート設定テスト."""
        fields = [
            TemplateField(
                name="test",
                label="Test",
                field_type=FieldType.TEXT,
                required=False,
                order=1,
            )
        ]

        # テンプレート2つ作成
        template1 = TemplateService.create_template(
            name="テンプレート1",
            fields=fields,
            is_default=True,
        )
        template2 = TemplateService.create_template(name="テンプレート2", fields=fields)

        # 最初はtemplate1がデフォルト
        assert template1.is_default is True
        assert template2.is_default is False

        # template2をデフォルトに変更
        updated = TemplateService.set_default_template(template2.id)
        assert updated.is_default is True

        # データベースから再取得して確認
        template1_reloaded = TemplateService.get_template(template_id=template1.id)
        template2_reloaded = TemplateService.get_template(template_id=template2.id)

        assert template1_reloaded.is_default is False  # 解除されている
        assert template2_reloaded.is_default is True

    def test_validate_template_data(self) -> None:
        """テンプレートデータ検証テスト."""
        # 正常なテンプレート
        valid_template = Template(
            id=1,
            name="有効なテンプレート",
            description="説明",
            fields=[
                TemplateField(
                    name="field1",
                    label="フィールド1",
                    field_type=FieldType.TEXT,
                    required=True,
                    order=1,
                ),
                TemplateField(
                    name="field2",
                    label="フィールド2",
                    field_type=FieldType.SELECTION,
                    required=False,
                    options=["A", "B"],
                    order=2,
                ),
            ],
            is_default=False,
        )
        errors = TemplateService.validate_template_data(valid_template)
        assert len(errors) == 0

        # テンプレート名が空
        invalid_template = Template(
            id=1,
            name="",
            description="説明",
            fields=[
                TemplateField(
                    name="field1",
                    label="フィールド1",
                    field_type=FieldType.TEXT,
                    required=True,
                    order=1,
                )
            ],
            is_default=False,
        )
        errors = TemplateService.validate_template_data(invalid_template)
        assert "テンプレート名は必須です" in errors

        # フィールドなし
        no_fields_template = Template(
            id=1,
            name="フィールドなし",
            description="説明",
            fields=[],
            is_default=False,
        )
        errors = TemplateService.validate_template_data(no_fields_template)
        assert "少なくとも1つのフィールドが必要です" in errors

        # フィールド名重複の検証は、Pydanticが自動でやってくれるのでスキップ
        # （Template作成時に自動的にバリデーションエラーが発生する）

        # 選択型で選択肢なしの検証は、Pydanticレベルで自動的に行われるため
        # サービス層のvalidate_template_dataではその他の検証ロジックをテスト
