"""Tests for clipboard commands"""

from unittest.mock import patch

import pyperclip
from typer.testing import CliRunner

from smart_nippo.cli.main import app

runner = CliRunner()


class TestClipboardCopy:
    """Test clipboard copy functionality"""

    def test_copy_basic_text(self):
        """Test basic text copying to clipboard"""
        result = runner.invoke(app, ["copy", "Hello, World!"])
        assert result.exit_code == 0
        assert "コピー完了" in result.stdout
        assert "13 文字" in result.stdout
        # Verify actual clipboard content
        assert pyperclip.paste() == "Hello, World!"

    def test_copy_with_prefix(self):
        """Test copying with prefix option"""
        result = runner.invoke(app, ["copy", "test", "--prefix", "prefix: "])
        assert result.exit_code == 0
        assert pyperclip.paste() == "prefix: test"

    def test_copy_with_suffix(self):
        """Test copying with suffix option"""
        result = runner.invoke(app, ["copy", "test", "--suffix", " :suffix"])
        assert result.exit_code == 0
        assert pyperclip.paste() == "test :suffix"

    def test_copy_with_prefix_and_suffix(self):
        """Test copying with both prefix and suffix"""
        result = runner.invoke(
            app, ["copy", "content", "--prefix", "[", "--suffix", "]"]
        )
        assert result.exit_code == 0
        assert pyperclip.paste() == "[content]"

    def test_copy_with_template(self):
        """Test copying with template formatting"""
        result = runner.invoke(app, ["copy", "world", "--template", "Hello, {text}!"])
        assert result.exit_code == 0
        assert pyperclip.paste() == "Hello, world!"

    def test_copy_template_overrides_prefix_suffix(self):
        """Test that template overrides prefix and suffix"""
        result = runner.invoke(app, [
            "copy", "test",
            "--template", "Template: {text}",
            "--prefix", "ignored",
            "--suffix", "ignored"
        ])
        assert result.exit_code == 0
        assert pyperclip.paste() == "Template: test"

    def test_copy_with_show_option(self):
        """Test copying with show option"""
        result = runner.invoke(app, ["copy", "visible", "--show"])
        assert result.exit_code == 0
        assert "コピー完了" in result.stdout
        assert "クリップボードの内容:" in result.stdout
        assert "visible" in result.stdout

    def test_copy_with_quiet_option(self):
        """Test copying with quiet option"""
        result = runner.invoke(app, ["copy", "quiet", "--quiet"])
        assert result.exit_code == 0
        assert "コピー完了" not in result.stdout
        assert pyperclip.paste() == "quiet"

    def test_copy_japanese_text(self):
        """Test copying Japanese text"""
        japanese_text = "こんにちは、世界！"
        result = runner.invoke(app, ["copy", japanese_text])
        assert result.exit_code == 0
        assert pyperclip.paste() == japanese_text

    @patch('pyperclip.copy')
    def test_copy_handles_pyperclip_error(self, mock_copy):
        """Test error handling when pyperclip fails"""
        mock_copy.side_effect = Exception("Clipboard access denied")
        result = runner.invoke(app, ["copy", "test"])
        assert result.exit_code == 1
        assert "クリップボードへのコピーに失敗しました" in result.stdout


class TestClipboardPaste:
    """Test clipboard paste functionality"""

    def test_paste_basic(self):
        """Test basic paste functionality"""
        # Set clipboard content first
        test_content = "Test clipboard content"
        pyperclip.copy(test_content)

        result = runner.invoke(app, ["paste"])
        assert result.exit_code == 0
        assert "内容" in result.stdout
        assert test_content in result.stdout
        assert f"{len(test_content)} 文字" in result.stdout

    def test_paste_empty_clipboard(self):
        """Test paste with empty clipboard"""
        pyperclip.copy("")

        result = runner.invoke(app, ["paste"])
        assert result.exit_code == 0
        assert "クリップボードは空です" in result.stdout

    def test_paste_japanese_content(self):
        """Test paste with Japanese content"""
        japanese_content = "日本語のテスト内容です"
        pyperclip.copy(japanese_content)

        result = runner.invoke(app, ["paste"])
        assert result.exit_code == 0
        assert japanese_content in result.stdout

    @patch('pyperclip.paste')
    def test_paste_handles_pyperclip_error(self, mock_paste):
        """Test error handling when pyperclip paste fails"""
        mock_paste.side_effect = Exception("Clipboard read failed")
        result = runner.invoke(app, ["paste"])
        assert result.exit_code == 1
        assert "クリップボードの読み取りに失敗しました" in result.stdout


class TestClipboardIntegration:
    """Test clipboard command integration"""

    def test_copy_and_paste_workflow(self):
        """Test complete copy and paste workflow"""
        test_text = "Integration test content"

        # Copy text
        copy_result = runner.invoke(app, ["copy", test_text])
        assert copy_result.exit_code == 0

        # Paste text
        paste_result = runner.invoke(app, ["paste"])
        assert paste_result.exit_code == 0
        assert test_text in paste_result.stdout

    def test_command_help(self):
        """Test clipboard command help"""
        copy_help = runner.invoke(app, ["copy", "--help"])
        assert copy_help.exit_code == 0
        assert "指定されたテキストをクリップボードにコピーします" in copy_help.stdout

        paste_help = runner.invoke(app, ["paste", "--help"])
        assert paste_help.exit_code == 0
        assert "クリップボードの内容を表示します" in paste_help.stdout
