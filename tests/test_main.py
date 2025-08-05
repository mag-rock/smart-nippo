"""Tests for main CLI application"""

from typer.testing import CliRunner

from smart_nippo.cli.main import app

runner = CliRunner()


def test_app_help():
    """Test main application help"""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "日報入力支援ツール" in result.stdout


def test_app_version():
    """Test that app loads without errors"""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
