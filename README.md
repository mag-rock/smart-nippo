# smart-nippo

日報入力支援ツール

## 概要

smart-nippoは日報作成を効率化するCLIツールです。

## インストール

```bash
pip install smart-nippo
```

## 使用方法

```bash
smart-nippo hello  # Hello World表示
```

## 開発環境構築

```bash
# 仮想環境作成
uv venv
source .venv/bin/activate

# 開発用依存関係のインストール
uv pip install -e ".[dev]"
```

## テスト実行

```bash
pytest
```

## 型チェック

```bash
pyright src/
```

## リント

```bash
ruff check src/
```