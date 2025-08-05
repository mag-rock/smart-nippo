"""Tests for hello command"""

from typer.testing import CliRunner

from smart_nippo.cli.main import app

runner = CliRunner()


def test_hello_default():
    """Test hello command with default arguments"""
    result = runner.invoke(app, ["hello"])
    assert result.exit_code == 0
    assert "Hello, World!" in result.stdout


def test_hello_with_name():
    """Test hello command with name argument"""
    result = runner.invoke(app, ["hello", "Alice"])
    assert result.exit_code == 0
    assert "Hello, Alice!" in result.stdout


def test_hello_japanese():
    """Test hello command with Japanese flag"""
    result = runner.invoke(app, ["hello", "--japanese"])
    assert result.exit_code == 0
    assert "こんにちは、世界！" in result.stdout


def test_hello_japanese_with_name():
    """Test hello command with Japanese flag and name"""
    result = runner.invoke(app, ["hello", "太郎", "--japanese"])
    assert result.exit_code == 0
    assert "こんにちは、太郎さん！" in result.stdout


def test_hello_count():
    """Test hello command with count option"""
    result = runner.invoke(app, ["hello", "--count", "3"])
    assert result.exit_code == 0
    # Should contain numbered greetings
    assert "1: Hello, World!" in result.stdout
    assert "2: Hello, World!" in result.stdout
    assert "3: Hello, World!" in result.stdout


def test_hello_help():
    """Test hello command help"""
    result = runner.invoke(app, ["hello", "--help"])
    assert result.exit_code == 0
    assert "Hello World コマンド" in result.stdout
