# uv中心の最小限開発構成

## 概要
uvを中心に、パッケージ公開まで含めた最小限の開発環境構成を定義します。

## 1. パッケージ管理とビルド構成

### uv + hatchling による構成

**uvの役割:**
- 依存関係管理
- 仮想環境管理
- パッケージインストール

**hatchlingの役割:**
- パッケージビルド
- PyPIへの公開

### pyproject.toml設定
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
keywords = ["cli", "daily-report", "productivity"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: End Users/Desktop",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Office/Business",
]

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
    "build>=1.0.0",  # パッケージビルド用
    "twine>=4.0.0",  # PyPIアップロード用
]

[project.scripts]
smart-nippo = "smart_nippo.cli:main"

[project.urls]
Repository = "https://github.com/yourusername/smart-nippo"
Issues = "https://github.com/yourusername/smart-nippo/issues"

# Hatchling specific
[tool.hatch.build.targets.sdist]
include = [
    "/src",
    "/tests",
    "/README.md",
    "/LICENSE",
]

[tool.hatch.build.targets.wheel]
packages = ["src/smart_nippo"]
```

## 2. 型チェック: Pyright設定

### pyrightconfig.json
```json
{
  "include": [
    "src"
  ],
  "exclude": [
    "**/node_modules",
    "**/__pycache__",
    ".venv"
  ],
  "defineConstant": {
    "DEBUG": true
  },
  "reportMissingImports": true,
  "reportMissingTypeStubs": false,
  "pythonVersion": "3.11",
  "pythonPlatform": "All",
  "typeCheckingMode": "strict",
  "useLibraryCodeForTypes": true,
  "reportGeneralTypeIssues": "error",
  "reportPropertyTypeMismatch": "error",
  "reportFunctionMemberAccess": "error",
  "reportMissingTypeArgument": "error",
  "reportPrivateUsage": "error",
  "reportTypeCommentUsage": "error",
  "reportPrivateImportUsage": "error",
  "reportConstantRedefinition": "error",
  "reportIncompatibleMethodOverride": "error",
  "reportIncompatibleVariableOverride": "error",
  "reportInconsistentConstructor": "error",
  "reportOverlappingOverload": "error",
  "reportUninitializedInstanceVariable": "error"
}
```

### VSCode設定（Pyright用）
```json
// .vscode/settings.json
{
    "python.analysis.typeCheckingMode": "strict",
    "python.analysis.autoSearchPaths": true,
    "python.analysis.useLibraryCodeForTypes": true,
    "python.analysis.diagnosticMode": "workspace",
    "python.analysis.stubPath": "typings",
    "python.languageServer": "Pylance",  // VSCodeでのPyright
}
```

### 型スタブ対応
```python
# typings/pyperclip/__init__.pyi
def copy(text: str) -> None: ...
def paste() -> str: ...

# typings/questionary/__init__.pyi
from typing import Any, List, Optional

def select(
    message: str,
    choices: List[str],
    default: Optional[str] = None
) -> Any: ...
```

## 3. ドキュメント: pdoc最小構成

### pdoc設定
```python
# scripts/generate_docs.py
import pdoc
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# ドキュメント生成
pdoc.pdoc(
    "smart_nippo",
    output_directory=Path("docs/api"),
    format="html",
    template_directory=None,
    show_source=True,
)
```

### Makefile統合
```makefile
.PHONY: docs
docs:
	python scripts/generate_docs.py
	@echo "Documentation generated in docs/api/"

.PHONY: docs-serve
docs-serve:
	python -m pdoc smart_nippo --host localhost --port 8080
```

## 4. 開発ワークフロー

### 環境構築
```bash
# Python環境の準備（pyenvなど）
python --version  # 3.11以上を確認

# 仮想環境作成とアクティベート
uv venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# 開発用依存関係インストール
uv pip install -e ".[dev]"
```

### 日常開発
```bash
# 型チェック
pyright src/

# リント・フォーマット
ruff check src/ tests/
ruff format src/ tests/

# テスト実行
pytest

# ドキュメント生成
make docs
```

### パッケージ公開フロー

#### 1. バージョン更新
```toml
# pyproject.toml
[project]
version = "0.2.0"  # 更新
```

#### 2. ビルド
```bash
# ビルドツールのインストール（初回のみ）
uv pip install build twine

# パッケージビルド
python -m build

# 生成されるファイル:
# dist/
#   smart_nippo-0.2.0-py3-none-any.whl
#   smart_nippo-0.2.0.tar.gz
```

#### 3. テストPyPIでの確認（推奨）
```bash
# テストPyPIへアップロード
python -m twine upload --repository testpypi dist/*

# テスト環境でインストール確認
uv pip install --index-url https://test.pypi.org/simple/ smart-nippo
```

#### 4. 本番PyPIへ公開
```bash
# 本番PyPIへアップロード
python -m twine upload dist/*

# 公開確認
uv pip install smart-nippo
```

### GitHub Actions による自動公開
```yaml
# .github/workflows/publish.yml
name: Publish Package

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install uv
      run: |
        curl -LsSf https://astral.sh/uv/install.sh | sh
        echo "$HOME/.cargo/bin" >> $GITHUB_PATH
    
    - name: Install dependencies
      run: |
        uv venv
        source .venv/bin/activate
        uv pip install build twine
    
    - name: Build package
      run: |
        source .venv/bin/activate
        python -m build
    
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: |
        source .venv/bin/activate
        python -m twine upload dist/*
```

## 5. 最小限のプロジェクト構造

```
smart-nippo/
├── src/
│   └── smart_nippo/
│       ├── __init__.py
│       ├── cli.py          # エントリポイント
│       ├── core/           # ビジネスロジック
│       └── utils/          # ユーティリティ
├── tests/
│   └── test_*.py
├── typings/                # 型スタブ（必要時）
│   └── questionary/
├── scripts/
│   └── generate_docs.py
├── .vscode/
│   └── settings.json
├── pyproject.toml
├── pyrightconfig.json
├── README.md
├── LICENSE
├── Makefile
└── .gitignore
```

## 6. .gitignore
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
ENV/

# Distribution / packaging
build/
dist/
*.egg-info/
.eggs/

# Testing
.coverage
.pytest_cache/
htmlcov/

# Documentation
docs/api/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project specific
*.db
*.sqlite
```

## 7. Makefile（最小構成）
```makefile
.PHONY: setup lint test docs build publish-test publish clean

setup:
	uv venv
	. .venv/bin/activate && uv pip install -e ".[dev]"

lint:
	pyright src/
	ruff check src/ tests/

test:
	pytest

docs:
	python scripts/generate_docs.py

build:
	python -m build

publish-test:
	python -m twine upload --repository testpypi dist/*

publish:
	python -m twine upload dist/*

clean:
	rm -rf dist/ build/ *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
```

## まとめ

### 採用技術スタック
- **パッケージ管理**: uv（開発）+ hatchling（ビルド）
- **型チェック**: Pyright（より強力な型推論）
- **ドキュメント**: pdoc（最小構成）
- **リンター**: Ruff
- **テスト**: pytest

### 特徴
1. **最小限構成**: 必要最小限のツールのみ
2. **uv中心**: 高速なパッケージ管理
3. **標準準拠**: PEP 517/518準拠のビルドシステム
4. **簡単な公開**: `python -m build` → `twine upload`

### パッケージ公開の流れ
```bash
# 1. 開発
uv pip install -e ".[dev]"

# 2. ビルド
python -m build

# 3. 公開
python -m twine upload dist/*
```

この構成により、uvの高速性を活かしつつ、標準的な方法でPyPIへのパッケージ公開が可能になります。