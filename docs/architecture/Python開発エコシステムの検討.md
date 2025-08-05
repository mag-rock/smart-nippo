# Python開発エコシステムの検討

## 概要
smart-nippoプロジェクトにおいて、型安全性とエージェントコーディングに耐える堅牢性を重視したモダンなPython開発環境を構築するための技術選定を行います。

## 要件定義

### 必須要件
- **型安全性**: 静的型チェックによる早期エラー検出
- **テスト充実**: 自動テスト実行とカバレッジ測定
- **パッケージ管理**: 再現可能な依存関係管理
- **開発環境**: 一貫した開発環境の提供
- **エージェント対応**: AI/LLMがコードを理解・修正しやすい構造

### 優先事項
- **開発効率**: モダンなツールチェーンによる高い生産性
- **保守性**: 長期間にわたって保守しやすいコード品質
- **CI/CD統合**: 自動化されたテスト・デプロイメント
- **セキュリティ**: 脆弱性の早期検出と対応

## 技術選定

### 1. パッケージ管理・依存関係

#### 選択肢比較

| ツール | メリット | デメリット | 評価 |
|--------|----------|------------|------|
| **Poetry** | ✅ pyproject.toml統合<br>✅ 仮想環境自動管理<br>✅ ロックファイル<br>✅ ビルド・公開機能 | ⚠️ 学習コスト<br>⚠️ やや重い | ⭐⭐⭐⭐⭐ |
| **uv** (Astral) | ✅ 超高速<br>✅ Rust製で信頼性<br>✅ pip互換 | ❌ 新しく実績不足<br>❌ 機能制限 | ⭐⭐⭐⭐ |
| **pip-tools** | ✅ シンプル<br>✅ pip互換<br>✅ 軽量 | ❌ 手動管理多い<br>❌ 仮想環境別管理 | ⭐⭐⭐ |
| **pipenv** | ✅ Pipfile<br>✅ セキュリティスキャン | ❌ 遅い<br>❌ メンテナンス不活発 | ⭐⭐ |

**推奨: Poetry + uv（ハイブリッド）**
```toml
# pyproject.toml
[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.poetry]
name = "smart-nippo"
version = "0.1.0"
description = "日報入力支援ツール"
authors = ["Your Name <email@example.com>"]
readme = "README.md"
packages = [{include = "smart_nippo", from = "src"}]

[tool.poetry.dependencies]
python = "^3.11"
typer = "^0.9.0"
questionary = "^2.0.0"
rich = "^13.0.0"
click = "^8.1.0"
pyperclip = "^1.8.0"
pydantic = "^2.0.0"
sqlalchemy = "^2.0.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-cov = "^4.1.0"
mypy = "^1.5.0"
ruff = "^0.0.287"
black = "^23.7.0"
pre-commit = "^3.3.0"

[tool.poetry.scripts]
smart-nippo = "smart_nippo.cli:main"
```

### 2. 型安全性

#### 型チェッカー比較

| ツール | 特徴 | パフォーマンス | エージェント対応 | 評価 |
|--------|------|---------------|-----------------|------|
| **mypy** | ✅ 最も成熟<br>✅ 豊富な設定<br>✅ プラグイン充実 | 中程度 | ◎ | ⭐⭐⭐⭐⭐ |
| **pyright** | ✅ 高速<br>✅ VSCode統合<br>✅ 厳密な型チェック | 高速 | ◎ | ⭐⭐⭐⭐ |
| **pyre** | ✅ Facebook製<br>✅ インクリメンタル | 高速 | △ | ⭐⭐⭐ |

**推奨: mypy + pyright併用**
```toml
# pyproject.toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true
show_error_codes = true

[[tool.mypy.overrides]]
module = [
    "questionary.*",
    "pyperclip.*",
]
ignore_missing_imports = true

[tool.pyright]
include = ["src"]
exclude = ["**/node_modules", "**/__pycache__"]
defineConstant = { DEBUG = true }
pythonVersion = "3.11"
pythonPlatform = "All"
typeCheckingMode = "strict"
```

#### 型ヒント戦略
```python
from typing import Optional, Union, List, Dict, Any, Protocol
from pydantic import BaseModel, Field
from datetime import datetime
from pathlib import Path

# Pydanticモデルで構造化データ
class DailyReport(BaseModel):
    date: datetime
    project: str
    tasks: List[str]
    content: str
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        frozen = True  # イミュータブル

# Protocolで構造的サブタイピング
class ReportStorage(Protocol):
    def save(self, report: DailyReport) -> bool: ...
    def load(self, date: datetime) -> Optional[DailyReport]: ...

# 厳密な型ヒント
def create_report(
    date: datetime,
    project: str,
    content: str,
    storage: ReportStorage
) -> DailyReport:
    report = DailyReport(
        date=date,
        project=project,
        tasks=extract_tasks(content),
        content=content
    )
    
    if not storage.save(report):
        raise RuntimeError("レポートの保存に失敗しました")
    
    return report
```

### 3. テストフレームワーク

#### pytest設定
```toml
# pyproject.toml
[tool.pytest.ini_options]
minversion = "7.0"
addopts = [
    "-ra",
    "--strict-markers",
    "--strict-config",
    "--cov=src/smart_nippo",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-report=xml",
    "--cov-fail-under=80",
]
testpaths = ["tests"]
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
]

[tool.coverage.run]
source = ["src"]
omit = [
    "*/tests/*",
    "*/test_*.py",
    "*/__pycache__/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]
```

#### テスト構造
```python
# tests/conftest.py
import pytest
from pathlib import Path
from unittest.mock import Mock
from smart_nippo.core.models import DailyReport
from smart_nippo.storage.sqlite import SQLiteStorage
import tempfile

@pytest.fixture
def temp_db():
    """テスト用の一時データベース"""
    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        yield Path(f.name)

@pytest.fixture
def storage(temp_db):
    """テスト用ストレージ"""
    return SQLiteStorage(temp_db)

@pytest.fixture
def sample_report():
    """サンプルレポート"""
    return DailyReport(
        date=datetime(2024, 1, 1),
        project="TestProject",
        tasks=["タスク1", "タスク2"],
        content="テスト内容"
    )

# tests/test_report_creation.py
import pytest
from datetime import datetime
from smart_nippo.core.report import create_report

class TestReportCreation:
    def test_create_valid_report(self, storage, sample_report):
        """正常なレポート作成のテスト"""
        report = create_report(
            date=sample_report.date,
            project=sample_report.project,
            content=sample_report.content,
            storage=storage
        )
        
        assert report.project == sample_report.project
        assert report.date == sample_report.date
        assert len(report.tasks) > 0
    
    @pytest.mark.parametrize("invalid_project", ["", None, "  "])
    def test_create_report_invalid_project(self, storage, invalid_project):
        """無効なプロジェクト名のテスト"""
        with pytest.raises(ValueError):
            create_report(
                date=datetime.now(),
                project=invalid_project,
                content="内容",
                storage=storage
            )
```

### 4. コード品質管理

#### Ruff設定（オールインワンツール）
```toml
# pyproject.toml
[tool.ruff]
target-version = "py311"
line-length = 88
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "C",  # flake8-comprehensions
    "B",  # flake8-bugbear
    "UP", # pyupgrade
    "N",  # pep8-naming
    "S",  # bandit (security)
    "T20", # flake8-print
    "PTH", # flake8-use-pathlib
]
ignore = [
    "E501",  # line too long, handled by black
    "B008",  # do not perform function calls in argument defaults
]

[tool.ruff.per-file-ignores]
"tests/*" = ["S101"]  # Use of assert in tests is OK

[tool.ruff.isort]
known-first-party = ["smart_nippo"]

[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''
```

### 5. 開発環境仮想化

#### Docker構成
```dockerfile
# Dockerfile.dev
FROM python:3.11-slim

WORKDIR /app

# システム依存関係
RUN apt-get update && apt-get install -y \
    git \
    curl \
    xclip \
    && rm -rf /var/lib/apt/lists/*

# Poetry インストール
RUN pip install poetry
RUN poetry config virtualenvs.create false

# 依存関係のインストール
COPY pyproject.toml poetry.lock ./
RUN poetry install --with dev

# アプリケーションコピー
COPY . .

CMD ["bash"]
```

```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  smart-nippo-dev:
    build:
      context: .
      dockerfile: Dockerfile.dev
    volumes:
      - .:/app
      - /tmp/.X11-unix:/tmp/.X11-unix:rw
    environment:
      - DISPLAY=${DISPLAY}
      - PYTHONPATH=/app/src
    working_dir: /app
    tty: true
    stdin_open: true
```

#### devcontainer設定
```json
// .devcontainer/devcontainer.json
{
    "name": "Smart Nippo Development",
    "build": {
        "dockerfile": "../Dockerfile.dev"
    },
    "features": {
        "ghcr.io/devcontainers/features/git:1": {},
        "ghcr.io/devcontainers/features/github-cli:1": {}
    },
    "customizations": {
        "vscode": {
            "extensions": [
                "ms-python.python",
                "ms-python.mypy-type-checker",
                "ms-python.black-formatter",
                "charliermarsh.ruff",
                "ms-python.pytest"
            ],
            "settings": {
                "python.defaultInterpreterPath": "/usr/local/bin/python",
                "python.testing.pytestEnabled": true,
                "python.testing.unittestEnabled": false,
                "python.linting.enabled": true,
                "python.linting.mypyEnabled": true,
                "python.formatting.provider": "black",
                "[python]": {
                    "editor.formatOnSave": true,
                    "editor.codeActionsOnSave": {
                        "source.organizeImports": true
                    }
                }
            }
        }
    },
    "postCreateCommand": "poetry install --with dev",
    "remoteUser": "root"
}
```

### 6. CI/CD設定

#### GitHub Actions
```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ["3.11", "3.12"]

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install Poetry
      uses: snok/install-poetry@v1
      with:
        version: latest
        virtualenvs-create: true
        virtualenvs-in-project: true
    
    - name: Load cached venv
      id: cached-poetry-dependencies
      uses: actions/cache@v3
      with:
        path: .venv
        key: venv-${{ runner.os }}-${{ matrix.python-version }}-${{ hashFiles('**/poetry.lock') }}
    
    - name: Install dependencies
      if: steps.cached-poetry-dependencies.outputs.cache-hit != 'true'
      run: poetry install --with dev
    
    - name: Run type checking
      run: |
        poetry run mypy src/
        poetry run pyright src/
    
    - name: Run linting
      run: poetry run ruff check src/ tests/
    
    - name: Run formatting check
      run: poetry run black --check src/ tests/
    
    - name: Run tests
      run: poetry run pytest --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v4
      with:
        python-version: "3.11"
    
    - name: Install Poetry
      uses: snok/install-poetry@v1
    
    - name: Install dependencies
      run: poetry install --with dev
    
    - name: Run security scan
      run: |
        poetry run bandit -r src/
        poetry run safety check
```

#### pre-commit設定
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict

  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.0.287
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ["-c", "pyproject.toml"]
        additional_dependencies: ["bandit[toml]"]
```

## プロジェクト構造

```
smart-nippo/
├── .devcontainer/
│   └── devcontainer.json
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── release.yml
├── src/
│   └── smart_nippo/
│       ├── __init__.py
│       ├── cli/
│       │   ├── __init__.py
│       │   ├── main.py
│       │   └── commands/
│       ├── core/
│       │   ├── __init__.py
│       │   ├── models.py
│       │   └── services.py
│       ├── storage/
│       │   ├── __init__.py
│       │   └── sqlite.py
│       └── utils/
│           ├── __init__.py
│           └── helpers.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docs/
├── pyproject.toml
├── poetry.lock
├── .pre-commit-config.yaml
├── Dockerfile.dev
├── docker-compose.dev.yml
└── README.md
```

## エージェントコーディング対応

### 1. 明確な型定義
```python
from typing import TypeVar, Generic, Protocol
from abc import ABC, abstractmethod

T = TypeVar('T')

class Repository(Protocol[T]):
    """リポジトリの共通インターフェース"""
    def save(self, entity: T) -> bool: ...
    def find_by_id(self, id: str) -> Optional[T]: ...
    def find_all(self) -> List[T]: ...

class Service(ABC, Generic[T]):
    """サービス層の基底クラス"""
    def __init__(self, repository: Repository[T]) -> None:
        self._repository = repository
    
    @abstractmethod
    def create(self, **kwargs) -> T:
        """エンティティを作成"""
        pass
```

### 2. 包括的なドキュメント
```python
def create_daily_report(
    date: datetime,
    project: str,
    content: str,
    storage: ReportStorage
) -> DailyReport:
    """
    日報を作成して保存します。
    
    Args:
        date: 日報の対象日
        project: プロジェクト名（空文字不可）
        content: 日報の内容
        storage: 保存先ストレージ
    
    Returns:
        作成された日報オブジェクト
    
    Raises:
        ValueError: プロジェクト名が無効な場合
        RuntimeError: 保存に失敗した場合
    
    Examples:
        >>> report = create_daily_report(
        ...     date=datetime(2024, 1, 1),
        ...     project="MyProject",
        ...     content="今日の作業内容",
        ...     storage=SQLiteStorage("db.sqlite")
        ... )
        >>> report.project
        'MyProject'
    """
```

### 3. 設定ファイルの統合
```toml
# pyproject.toml - すべての設定を一元化
[tool.smart-nippo]
database_path = "~/.smart-nippo/reports.db"
editor = "code"
default_template = "templates/daily.md"

[tool.smart-nippo.ai]
openai_api_key_env = "OPENAI_API_KEY"
model = "gpt-4"
max_tokens = 1000
```

## 推奨構成

### 必須ツール
1. **Poetry**: パッケージ管理・依存関係
2. **mypy**: 型チェック
3. **pytest**: テストフレームワーク
4. **ruff**: リンター・フォーマッター
5. **pre-commit**: Git フック

### オプションツール
1. **pyright**: 追加型チェック
2. **bandit**: セキュリティスキャン
3. **safety**: 脆弱性チェック
4. **codecov**: カバレッジレポート

### 開発環境
1. **devcontainer**: 一貫した開発環境
2. **Docker**: コンテナ化開発
3. **GitHub Actions**: CI/CD

## 結論

この構成により以下を実現：

- **型安全性**: mypy + pyright による静的解析
- **テスト充実**: pytest + カバレッジ測定
- **品質保証**: ruff + pre-commit による自動化
- **再現性**: Poetry + Docker による環境統一
- **エージェント対応**: 明確な型定義と包括的ドキュメント

エージェントコーディングにおいて、型ヒントと明確な構造により、AIが容易にコードを理解・修正できる環境を提供します。