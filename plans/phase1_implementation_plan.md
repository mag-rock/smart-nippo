# Smart-Nippo フェーズ1 実装計画

## 概要
日報作成支援ツールの基本機能（フェーズ1）を9週間で実装する詳細計画。

## 実装スケジュール

### 🏗️ **Week 1-2: 基盤レイヤー**

#### Week 1: データベース基盤
- [ ] SQLiteデータベースセットアップ
- [ ] SQLAlchemyモデルの実装
  - [ ] `Report` テーブル
  - [ ] `Template` テーブル  
  - [ ] `Project` テーブル
  - [ ] `TemplateField` テーブル
- [ ] データベース初期化・マイグレーション機能
- [ ] `~/.smart-nippo/` ディレクトリの自動作成
- [ ] 基本CRUD操作のテスト

**成果物**: `src/smart_nippo/core/database/` パッケージ

#### Week 2: 設定管理システム
- [ ] YAML設定ファイルの読み込み機能
- [ ] `~/.smart-nippo/config.yaml` の管理
- [ ] デフォルト設定の定義
- [ ] 設定の初期化・更新機能
- [ ] 環境変数サポート

**成果物**: `src/smart_nippo/core/config.py`

### 📝 **Week 3-5: コア機能レイヤー**

#### Week 3: テンプレート管理システム
- [ ] テンプレートサービスの実装
  - [ ] テンプレート作成機能
  - [ ] テンプレート編集機能
  - [ ] テンプレート削除機能
  - [ ] デフォルトテンプレート設定
- [ ] `smart-nippo template` コマンドの実装
- [ ] デフォルトテンプレートの自動作成
- [ ] テンプレート管理のテスト

**成果物**: `src/smart_nippo/core/services/template_service.py`

#### Week 4: インタラクティブ入力システム
- [ ] 型別入力ハンドラーの実装
  - [ ] 日付型入力（カレンダー選択）
  - [ ] 時刻型入力（15分刻み）
  - [ ] テキスト型入力（1行）
  - [ ] メモ型入力（エディタ起動）
  - [ ] 選択型入力（矢印キー選択）
- [ ] Questionaryとの統合
- [ ] 入力バリデーションの統合
- [ ] エラーハンドリング

**成果物**: `src/smart_nippo/cli/interactive/input_handlers.py`

#### Week 5: 日報作成・編集機能
- [ ] 日報サービスの実装
- [ ] `smart-nippo create` コマンド
  - [ ] テンプレート選択
  - [ ] インタラクティブ入力
  - [ ] データ保存
- [ ] `smart-nippo edit` コマンド
  - [ ] 既存日報の検索・選択
  - [ ] データ編集
  - [ ] 更新保存
- [ ] 作成・編集フローのテスト

**成果物**: `src/smart_nippo/core/services/report_service.py`

### 🔍 **Week 6-7: データ活用レイヤー**

#### Week 6: 検索・表示機能
- [ ] `smart-nippo list` コマンド
  - [ ] 日付範囲フィルタ
  - [ ] プロジェクトフィルタ
  - [ ] キーワード検索
  - [ ] Rich表での表示
- [ ] `smart-nippo show` コマンド
  - [ ] 日報の詳細表示
  - [ ] 複数フォーマット対応
- [ ] ページネーション機能
- [ ] 検索・表示のテスト

**成果物**: 検索・表示機能の完成

#### Week 7: エクスポート機能
- [ ] エクスポーターの実装
  - [ ] CSVエクスポーター
  - [ ] TSVエクスポーター
  - [ ] Markdownエクスポーター
  - [ ] プレーンテキストエクスポーター
- [ ] `smart-nippo export` コマンド
- [ ] フィルタリングとの連携
- [ ] エクスポート機能のテスト

**成果物**: `src/smart_nippo/core/exporters/` パッケージ

### 📊 **Week 8: 月報生成機能**
- [ ] 月報生成サービス
  - [ ] プロジェクト別作業時間集計
  - [ ] 主要成果の抽出
  - [ ] 課題・問題点のまとめ
- [ ] `smart-nippo monthly` コマンド
- [ ] 月報テンプレートシステム
- [ ] 月報生成のテスト

**成果物**: 月報生成機能の完成

### 🚀 **Week 9: 拡張機能・統合**
- [ ] サジェスト機能
  - [ ] プロジェクト名の補完
  - [ ] 定型文のサジェスト
  - [ ] よく使うフレーズの推薦
- [ ] 統合・最適化
  - [ ] エラーハンドリングの統一
  - [ ] パフォーマンスチューニング
  - [ ] ユーザビリティ改善
- [ ] 最終テスト・ドキュメント更新

**成果物**: 完全なフェーズ1システム

## 技術スタック

### 依存関係
```toml
dependencies = [
    "typer>=0.9.0",        # CLI framework
    "questionary>=2.0.0",  # Interactive prompts
    "rich>=13.0.0",        # Rich text and tables
    "pydantic>=2.0.0",     # Data validation
    "sqlalchemy>=2.0.0",   # ORM
    "pyyaml>=6.0",         # Configuration files
    "click>=8.1.0",        # CLI utilities
    "pyperclip>=1.8.0",    # Clipboard operations
]
```

### ディレクトリ構造
```
src/smart_nippo/
├── cli/                    # CLI interface
│   ├── commands/          # Command implementations
│   ├── interactive/       # Interactive input handlers
│   └── utils/             # CLI utilities
├── core/                  # Core business logic
│   ├── database/          # Database layer
│   ├── services/          # Business services
│   ├── exporters/         # Export functionality
│   ├── models/            # Pydantic models (existing)
│   ├── config.py          # Configuration management
│   └── validators.py      # Field validators (existing)
├── integrations/          # External integrations
└── __init__.py
```

## テスト戦略

### テストカテゴリ
1. **単体テスト**: 各関数・クラスの個別テスト
2. **統合テスト**: データベース操作、コマンド実行テスト
3. **E2Eテスト**: 実際のユーザーフロー全体テスト

### カバレッジ目標
- 全体カバレッジ: 80%以上
- クリティカルパス: 95%以上
- 新規実装コード: 90%以上

### テスト自動化
```bash
# 全テスト実行
pytest

# カバレッジレポート付き
pytest --cov=smart_nippo --cov-report=html

# 型チェック
pyright src/

# リンティング
ruff check src/
```

## 配信マイルストーン

### Milestone 1 (Week 2): データベース基盤
- SQLiteデータベースの作成・接続
- 基本的なCRUD操作が可能

### Milestone 2 (Week 5): 基本機能
- 日報の新規作成が可能
- テンプレートシステムが動作
- インタラクティブ入力が動作

### Milestone 3 (Week 7): データ活用
- 日報の検索・表示が可能
- エクスポート機能が動作
- データの永続化が完全動作

### Milestone 4 (Week 9): 完成版
- 全フェーズ1機能が動作
- パフォーマンスが要件を満たす
- ユーザビリティが十分なレベル

## 成功指標

### 機能要件
- [ ] 全17個の既存テストが継続してパス
- [ ] 仕様書記載の全フェーズ1機能が動作
- [ ] 全コマンドが期待通りに実行される

### 品質要件
- [ ] pyright型チェックにパス
- [ ] ruffリンティングにパス
- [ ] テストカバレッジ80%以上
- [ ] パフォーマンス要件を満たす（仕様書記載）

### ユーザビリティ要件
- [ ] 直感的なCLIインターフェース
- [ ] わかりやすいエラーメッセージ（日本語）
- [ ] ヘルプドキュメントが充実

## リスク管理

### 技術リスク
- **SQLAlchemy移行**: 既存Pydanticモデルとの整合性
- **対策**: 段階的移行、既存テストの活用

### スケジュールリスク
- **複雑な入力UI**: 実装が予定より時間がかかる可能性
- **対策**: Week 4でプロトタイプを早期作成、フィードバックを得る

### 品質リスク
- **パフォーマンス**: 大量データでの動作が遅い
- **対策**: Week 7でパフォーマンステスト実施、必要に応じて最適化

## 次フェーズへの準備

### Web版への準備
- APIエンドポイント設計の考慮
- データモデルの拡張性確保
- 認証・認可の基盤準備

### AI機能への準備
- データ構造の柔軟性確保
- 外部API連携の基盤準備
- プライバシー保護機能の検討