# ADR-002: Python開発エコシステムの採用

## ステータス
**決定済み** - 2024-08-05

## コンテキスト
ADR-001でPython技術スタック（Typer + Questionary + Rich + Click）の採用を決定した。本ADRでは、開発効率と品質を担保するための開発エコシステム（パッケージ管理、型チェック、ドキュメント生成等）について決定する。

### 要件
- **開発効率**: 高速な依存関係管理と開発サイクル
- **型安全性**: エージェントコーディングに耐える堅牢性
- **配布**: PyPIへの標準的なパッケージ公開
- **最小構成**: 過剰なツールを避け、必要最小限の構成

### 検討した選択肢

#### パッケージ管理
1. **Poetry**: 高機能だが学習コストとツール自体が重い
2. **pip-tools**: シンプルだが手動管理が多い
3. **pipenv**: 遅く、メンテナンス不活発
4. **uv**: 高速（pip比10-100倍）、pip互換、シンプル

#### 型チェック
1. **mypy**: 成熟、豊富なプラグイン、CI/CD統合が容易
2. **pyright**: 高速、強力な型推論、VSCode統合
3. **併用**: 冗長で設定が複雑

#### ドキュメント生成
1. **Sphinx**: 高機能だが設定が複雑
2. **mkdocs**: Markdown記法で簡単
3. **pdoc**: 最軽量、ゼロ設定、docstringから自動生成

#### 開発環境
1. **devcontainer**: Webサービス向けで過剰
2. **Docker**: CLIツールには重い
3. **ローカル環境 + 仮想環境**: 軽量、OS固有機能のテストが容易

## 決定

以下の技術スタックを採用する：

### 採用技術
- **パッケージ管理**: uv + hatchling
- **型チェック**: pyright
- **ドキュメント生成**: pdoc
- **コード品質**: ruff
- **テスト**: pytest
- **開発環境**: ローカル環境 + uv仮想環境

## 決定理由

### 1. uv + hatchling の採用
- **高速性**: pip比10-100倍の速度で依存関係解決
- **標準準拠**: PEP 517/518準拠のビルドシステム
- **シンプル**: 最小限の設定で動作
- **互換性**: 既存のpipエコシステムと完全互換

### 2. pyright の採用
- **強力な型推論**: mypyより高度な型推論機能
- **高速**: 大規模プロジェクトでも高速動作
- **VSCode統合**: Pylanceとして標準搭載
- **厳密性**: デフォルトで厳格な型チェック

### 3. pdoc の採用
- **最小構成**: 追加設定なしで動作
- **自動生成**: docstringから自動的にドキュメント生成
- **軽量**: CLIツールのドキュメントには十分な機能

### 4. ローカル環境の採用
- **軽量**: Docker等のオーバーヘッドなし
- **直接テスト**: OS固有機能（クリップボード、エディタ連携）のテストが容易
- **高速**: 起動時間ゼロ

## 実装詳細

### pyproject.toml（最小構成）
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "smart-nippo"
version = "0.1.0"
description = "日報入力支援ツール"
authors = [{name = "Your Name", email = "email@example.com"}]
readme = "README.md"
requires-python = ">=3.11"
license = {text = "MIT"}

dependencies = [
    "typer>=0.9.0",
    "questionary>=2.0.0",
    "rich>=13.0.0",
    "click>=8.1.0",
    "pyperclip>=1.8.0",
    "pydantic>=2.0.0",
    "sqlalchemy>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pyright>=1.1.300",
    "ruff>=0.1.0",
    "pdoc>=14.0.0",
    "build>=1.0.0",
    "twine>=4.0.0",
]

[project.scripts]
smart-nippo = "smart_nippo.cli:main"
```

### 開発フロー
```bash
# 環境構築
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# 開発サイクル
pyright src/        # 型チェック
ruff check src/     # リント
pytest              # テスト
pdoc smart_nippo    # ドキュメント生成

# パッケージ公開
python -m build
python -m twine upload dist/*
```

## トレードオフ

### 採用により得られるもの
- **高速な開発サイクル**: uvによる超高速な依存関係管理
- **強力な型安全性**: pyrightの高度な型推論
- **最小限の設定**: 必要最小限のツールで構成
- **標準準拠**: PEP標準に準拠したパッケージング

### 採用により失うもの
- **高機能なパッケージ管理**: Poetryの便利機能（バージョン管理等）
- **包括的なドキュメント**: Sphinxの高度な機能
- **完全な環境分離**: Dockerによる完全な再現性

### リスク軽減策
- **CI/CD**: GitHub Actionsで複数OS/Pythonバージョンでのテスト
- **型スタブ**: 型定義のない外部ライブラリ用の型スタブ作成
- **ドキュメント規約**: Google docstring styleの強制

## 影響

### 開発者への影響
- より高速な開発サイクル
- シンプルな環境構築（`uv pip install -e ".[dev]"`のみ）
- 強力な型チェックによる早期エラー検出

### エージェントコーディングへの影響
- pyrightの厳密な型チェックにより、AIが理解しやすいコード
- 最小限の設定ファイルで、AIが把握しやすい構成
- 標準的なPythonパッケージング規約の遵守

## 関連ドキュメント
- [ADR-001: Python CLIテクノロジースタックの採用](./001-python-cli-technology-stack.md)
- [uv中心の最小限開発構成](../uv中心の最小限開発構成.md)
- [Python開発エコシステム見直し](../Python開発エコシステム見直し.md)

## 今後の見直し予定
- MVP完成時点での開発効率の評価
- パッケージ公開後のフィードバックに基づく見直し
- 大規模化した場合のツール追加検討

---
**決定者**: 開発チーム  
**決定日**: 2024-08-05  
**次回見直し予定**: MVP完成時またはパッケージ初回公開時