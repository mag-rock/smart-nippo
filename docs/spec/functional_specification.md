# Smart-Nippo 機能仕様書

## 1. 概要

### 1.1 プロジェクト名
Smart-Nippo（スマート日報）

### 1.2 目的
日報作成を効率化し、データ分析機能を提供するCLIツール

### 1.3 開発フェーズ
- **フェーズ1（現在）**: CLI版の基本機能実装
- **フェーズ2**: Web版とクラウド連携
- **フェーズ3**: モバイル対応（オプション）

## 2. 機能一覧

### 2.1 基本機能（フェーズ1で実装）

#### 2.1.1 日報入力機能
- **説明**: 日報の作成と編集を行う
- **入力項目**:
  - 日付（デフォルト：当日）
  - プロジェクト名
  - 作業内容
  - 作業時間
  - 進捗状況
  - 課題・問題点
  - 明日の予定
  - 所感・メモ
- **コマンド**: `smart-nippo create`, `smart-nippo edit`

##### 入力項目の型定義
各入力項目はテンプレート作成機能でユーザーが増減可能。以下のいずれかの型を指定する必要がある。

###### 日付型 (date)
- **入力仕様**: カレンダーから選択して入力
- **デフォルト値**: 当日、前日、翌日のいずれか（テンプレート作成時に決定）
- **フォーマット**: YYYY-MM-DD
- **使用例**: 作業日、締切日など

###### 時刻型 (time)
- **入力仕様**: 15分刻みでカーソル入力、または直接入力
- **デフォルト値**: テンプレート作成時に決定
- **フォーマット**: HH:MM（24時間表記）
- **使用例**: 開始時刻、終了時刻など

###### テキスト型 (text)
- **入力仕様**: CLI上で1行入力
- **制限**: 改行不可、その他の記号は可能
- **最大文字数**: 255文字
- **使用例**: プロジェクト名、タスク名など

###### メモ型 (memo)
- **入力仕様**: エディタを起動して入力
- **制限**: 改行可能、文字数制限なし
- **エディタ**: 設定ファイルで指定（vim, nano, code等）
- **使用例**: 作業内容詳細、所感など

###### 選択型 (selection)
- **入力仕様**: テンプレート作成時に定義した選択肢から選択
- **デフォルト値**: テンプレート作成時に指定可能
- **選択方法**: インタラクティブな選択UI（矢印キーで選択）
- **使用例**: 進捗状況（完了/進行中/未着手）、優先度など

#### 2.1.2 日報データベース管理
- **説明**: 日報データをローカルSQLiteデータベースに保存
- **データベース場所**: `~/.smart-nippo/data.db`
- **スキーマ**: 
  - reports テーブル（日報本体）
  - projects テーブル（プロジェクト管理）
  - templates テーブル（テンプレート管理）

#### 2.1.3 テンプレート機能
- **説明**: 日報のテンプレートを管理
- **機能**:
  - テンプレートの作成・編集・削除
  - デフォルトテンプレートの設定
  - プロジェクト別テンプレート
- **コマンド**: `smart-nippo template`

#### 2.1.4 日報検索・表示機能
- **説明**: 保存された日報の検索と表示
- **検索条件**:
  - 日付範囲
  - プロジェクト
  - キーワード
- **コマンド**: `smart-nippo list`, `smart-nippo show`

#### 2.1.5 エクスポート機能
- **説明**: 日報データを各種形式で出力
- **対応形式**:
  - CSV
  - TSV
  - Markdown
  - プレーンテキスト
- **コマンド**: `smart-nippo export`

#### 2.1.6 月報生成機能
- **説明**: 月単位での日報サマリーを生成
- **出力内容**:
  - プロジェクト別作業時間集計
  - 主要成果リスト
  - 課題・問題点のまとめ
- **コマンド**: `smart-nippo monthly`

### 2.2 拡張機能（フェーズ1後半で実装）

#### 2.2.1 サジェスト機能
- **説明**: 過去の日報データから入力内容をサジェスト
- **サジェスト対象**:
  - プロジェクト名
  - 定型文
  - よく使うフレーズ
- **実装方法**: インタラクティブモード with Questionary

#### 2.2.2 バリデーション機能
- **説明**: 入力内容の妥当性チェック
- **チェック項目**:
  - 必須項目の入力
  - 日付の妥当性
  - 作業時間の合計（1日24時間以内）

#### 2.2.3 統計・分析機能
- **説明**: 日報データの統計分析
- **分析内容**:
  - 作業時間の推移
  - プロジェクト別工数
  - 生産性指標
- **コマンド**: `smart-nippo analyze`

### 2.3 将来機能（フェーズ2以降）

#### 2.3.1 AI連携機能
- OpenAI/Gemini APIによる日報文章生成支援
- 自動要約機能
- 改善提案の生成

#### 2.3.2 外部連携機能
- カレンダー連携（Google Calendar, Outlook）
- タスク管理ツール連携（Jira, Trello）
- Slack/Teams通知

#### 2.3.3 Web版機能
- Webブラウザからの日報入力
- ダッシュボード表示
- チーム共有機能

## 3. 技術仕様

### 3.1 使用技術
- **言語**: Python 3.11+
- **CLIフレームワーク**: Typer
- **データベース**: SQLite (SQLAlchemy ORM)
- **データモデリング**: Pydantic
- **UI**: Rich, Questionary
- **テスト**: pytest
- **コード品質**: pyright, ruff

### 3.2 プロジェクト構造
```
src/smart_nippo/
├── cli/           # CLIインターフェース
├── core/          # ビジネスロジック
│   ├── models/    # データモデル
│   ├── database/  # DB操作
│   └── services/  # ビジネスサービス
└── integrations/  # 外部連携
```

### 3.3 データモデル

#### FieldType定義
```python
from enum import Enum

class FieldType(Enum):
    DATE = "date"          # 日付型
    TIME = "time"          # 時刻型
    TEXT = "text"          # テキスト型（1行）
    MEMO = "memo"          # メモ型（複数行）
    SELECTION = "selection" # 選択型

class DateDefault(Enum):
    TODAY = "today"        # 当日
    YESTERDAY = "yesterday" # 前日
    TOMORROW = "tomorrow"   # 翌日
```

#### TemplateFieldモデル
```python
class TemplateField:
    name: str                      # フィールド名
    label: str                     # 表示ラベル
    field_type: FieldType          # フィールドタイプ
    required: bool                 # 必須項目かどうか
    default_value: str | None      # デフォルト値
    options: list[str] | None      # 選択肢（selection型の場合）
    placeholder: str | None        # プレースホルダー
    max_length: int | None         # 最大文字数（text型の場合）
    order: int                     # 表示順序
```

#### Reportモデル
```python
class Report:
    id: int
    template_id: int               # 使用したテンプレート
    data: dict                     # フィールド名と値のマッピング
    created_at: datetime
    updated_at: datetime
```

#### Projectモデル
```python
class Project:
    id: int
    name: str
    description: str | None
    template_id: int | None
    is_active: bool
    created_at: datetime
```

#### Templateモデル
```python
class Template:
    id: int
    name: str
    description: str | None
    fields: list[TemplateField]    # テンプレートフィールドのリスト
    is_default: bool
    created_at: datetime
    updated_at: datetime
```

#### デフォルトテンプレート例
```python
default_template_fields = [
    TemplateField(
        name="date",
        label="日付",
        field_type=FieldType.DATE,
        required=True,
        default_value=DateDefault.TODAY,
        order=1
    ),
    TemplateField(
        name="project",
        label="プロジェクト名",
        field_type=FieldType.TEXT,
        required=True,
        max_length=100,
        order=2
    ),
    TemplateField(
        name="start_time",
        label="開始時刻",
        field_type=FieldType.TIME,
        required=False,
        default_value="09:00",
        order=3
    ),
    TemplateField(
        name="end_time",
        label="終了時刻",
        field_type=FieldType.TIME,
        required=False,
        default_value="18:00",
        order=4
    ),
    TemplateField(
        name="content",
        label="作業内容",
        field_type=FieldType.MEMO,
        required=True,
        order=5
    ),
    TemplateField(
        name="progress",
        label="進捗状況",
        field_type=FieldType.SELECTION,
        required=True,
        options=["完了", "進行中", "未着手"],
        default_value="進行中",
        order=6
    ),
    TemplateField(
        name="issues",
        label="課題・問題点",
        field_type=FieldType.MEMO,
        required=False,
        order=7
    ),
    TemplateField(
        name="tomorrow_plan",
        label="明日の予定",
        field_type=FieldType.MEMO,
        required=False,
        order=8
    ),
    TemplateField(
        name="notes",
        label="備考・メモ",
        field_type=FieldType.MEMO,
        required=False,
        order=9
    )
]
```

## 4. コマンド仕様

### 4.1 基本コマンド構造
```bash
smart-nippo [コマンド] [オプション]
```

### 4.2 主要コマンド一覧

| コマンド | 説明 | 主要オプション |
|---------|------|---------------|
| create | 日報を作成 | --date, --project, --template |
| edit | 日報を編集 | --date, --id |
| list | 日報一覧表示 | --from, --to, --project |
| show | 日報詳細表示 | --date, --id |
| export | データエクスポート | --format, --from, --to |
| monthly | 月報生成 | --month, --year |
| template | テンプレート管理 | create, edit, delete, set-default |
| analyze | 統計分析 | --period, --project |
| config | 設定管理 | --set, --get, --list |

### 4.3 使用例

```bash
# 今日の日報を作成
smart-nippo create

# 特定日の日報を作成
smart-nippo create --date 2024-01-15

# 先週の日報一覧を表示
smart-nippo list --from 2024-01-08 --to 2024-01-14

# 月報をCSVで出力
smart-nippo monthly --month 1 --year 2024 --format csv

# プロジェクト別の作業時間分析
smart-nippo analyze --project "プロジェクトA"
```

## 5. 設定ファイル

### 5.1 設定ファイルパス
`~/.smart-nippo/config.yaml`

### 5.2 設定項目
```yaml
# デフォルト設定
defaults:
  project: ""
  template: "default"
  export_format: "markdown"

# データベース設定
database:
  path: "~/.smart-nippo/data.db"

# エディタ設定
editor:
  command: "vim"  # または "code", "nano" など

# 表示設定
display:
  date_format: "%Y-%m-%d"
  time_format: "%H:%M"
  language: "ja"
```

## 6. エラーハンドリング

### 6.1 エラーコード
- 0: 正常終了
- 1: 一般的なエラー
- 2: データベースエラー
- 3: 入力エラー
- 4: ファイルI/Oエラー

### 6.2 エラーメッセージ
日本語で分かりやすいエラーメッセージを表示

## 7. セキュリティ考慮事項

### 7.1 データ保護
- ローカルデータベースは暗号化オプションを提供（将来）
- 機密情報のマスキング機能

### 7.2 アクセス制御
- ファイルパーミッションの適切な設定
- データベースファイルへのアクセス制限

## 8. パフォーマンス要件

### 8.1 応答時間
- 日報作成・編集: 1秒以内
- 検索・一覧表示: 2秒以内（1000件まで）
- エクスポート: 5秒以内（1年分のデータ）

### 8.2 データ容量
- 1日報あたり: 約1-2KB
- 年間想定: 約500KB（250営業日）

## 9. テスト計画

### 9.1 単体テスト
- 各コマンドの正常系・異常系テスト
- データベース操作のテスト
- バリデーションロジックのテスト

### 9.2 統合テスト
- コマンド間の連携テスト
- データの一貫性テスト

### 9.3 受け入れテスト
- 実際の業務フローでの動作確認
- パフォーマンステスト

## 10. リリース計画

### 10.1 バージョン1.0.0（MVP）
- 基本的な日報CRUD機能
- ローカルデータベース
- CSV/Markdownエクスポート

### 10.2 バージョン1.1.0
- サジェスト機能
- 月報生成
- 統計分析機能

### 10.3 バージョン2.0.0
- Web版リリース
- AI連携機能
- 外部サービス連携

## 付録

### A. 用語集
- **日報**: 1日の業務内容を記録した報告書
- **月報**: 月単位での業務サマリー
- **テンプレート**: 日報の雛形
- **プロジェクト**: 作業を分類する単位

### B. 参考資料
- [Typer Documentation](https://typer.tiangolo.com/)
- [SQLAlchemy Documentation](https://www.sqlalchemy.org/)
- [Rich Documentation](https://rich.readthedocs.io/)