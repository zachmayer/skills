"""Tests for the context_compiler compile_context.py CLI."""

import importlib.util
import sys
from pathlib import Path
from unittest.mock import patch

import click
import pytest
from click.testing import CliRunner

# Import compile_context.py from the skill directory
_spec = importlib.util.spec_from_file_location(
    "compile_context",
    Path(__file__).resolve().parents[2]
    / "skills"
    / "context_compiler"
    / "scripts"
    / "compile_context.py",
)
assert _spec is not None and _spec.loader is not None
compile_context = importlib.util.module_from_spec(_spec)
sys.modules["compile_context"] = compile_context
_spec.loader.exec_module(compile_context)


class TestParsePrRef:
    """Test _parse_pr_ref PR reference parsing."""

    def test_plain_number(self) -> None:
        repo, number = compile_context._parse_pr_ref("33")
        assert repo is None
        assert number == "33"

    def test_hash_number(self) -> None:
        repo, number = compile_context._parse_pr_ref("#33")
        assert repo is None
        assert number == "33"

    def test_repo_hash_number(self) -> None:
        repo, number = compile_context._parse_pr_ref("owner/repo#33")
        assert repo == "owner/repo"
        assert number == "33"

    def test_url(self) -> None:
        repo, number = compile_context._parse_pr_ref("https://github.com/owner/repo/pull/33")
        assert repo == "owner/repo"
        assert number == "33"

    def test_invalid_ref_raises(self) -> None:
        with pytest.raises(click.BadParameter, match="Can't parse"):
            compile_context._parse_pr_ref("not-a-ref")


class TestTruncate:
    """Test _truncate helper."""

    def test_no_truncation_needed(self) -> None:
        result = compile_context._truncate("short", 100, "test")
        assert result == "short"

    def test_truncation_applied(self) -> None:
        result = compile_context._truncate("a" * 200, 50, "test")
        assert len(result) < 200
        assert "TRUNCATED" in result

    def test_exact_boundary(self) -> None:
        text = "x" * 100
        result = compile_context._truncate(text, 100, "test")
        assert result == text


class TestEscapeXml:
    """Test _escape_xml helper."""

    def test_escapes_ampersand(self) -> None:
        assert compile_context._escape_xml("a&b") == "a&amp;b"

    def test_escapes_angle_brackets(self) -> None:
        assert compile_context._escape_xml("<b>") == "&lt;b&gt;"

    def test_escapes_quotes(self) -> None:
        assert compile_context._escape_xml('"hi"') == "&quot;hi&quot;"

    def test_no_escaping_needed(self) -> None:
        assert compile_context._escape_xml("hello") == "hello"


class TestContextCompiler:
    """Test ContextCompiler class."""

    def test_compile_no_sources_exits(self) -> None:
        compiler = compile_context.ContextCompiler()
        with pytest.raises(SystemExit):
            compiler.compile()

    def test_add_file(self, tmp_path: Path) -> None:
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello world")

        compiler = compile_context.ContextCompiler(fmt="xml")
        compiler.add_file(str(test_file))
        result = compiler.compile()

        assert "<context>" in result
        assert "hello world" in result
        assert 'type="file"' in result

    def test_add_file_markdown(self, tmp_path: Path) -> None:
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello world")

        compiler = compile_context.ContextCompiler(fmt="markdown")
        compiler.add_file(str(test_file))
        result = compiler.compile()

        assert "## File:" in result
        assert "hello world" in result

    def test_add_file_missing(self) -> None:
        compiler = compile_context.ContextCompiler()
        compiler.add_file("/nonexistent/path/file.txt")
        # Should not crash, just warn
        assert len(compiler.sections) == 0

    def test_add_memory(self, tmp_path: Path) -> None:
        memory_file = tmp_path / "memory" / "test.md"
        memory_file.parent.mkdir()
        memory_file.write_text("# Session Notes\nDid stuff.")

        compiler = compile_context.ContextCompiler(fmt="xml", obsidian_dir=tmp_path)
        compiler.add_memory("memory/test.md")
        result = compiler.compile()

        assert "Session Notes" in result
        assert 'type="memory"' in result

    def test_add_memory_no_obsidian_dir(self) -> None:
        compiler = compile_context.ContextCompiler(fmt="xml", obsidian_dir=None)
        compiler.add_memory("test.md")
        assert len(compiler.sections) == 0

    def test_add_obsidian_search(self, tmp_path: Path) -> None:
        note = tmp_path / "notes" / "auth.md"
        note.parent.mkdir()
        note.write_text("# Authentication\nUse OAuth2 for auth.")

        compiler = compile_context.ContextCompiler(fmt="xml", obsidian_dir=tmp_path)
        compiler.add_obsidian_search("authentication")
        result = compiler.compile()

        assert "OAuth2" in result
        assert 'type="obsidian-search"' in result

    def test_add_obsidian_search_no_results(self, tmp_path: Path) -> None:
        compiler = compile_context.ContextCompiler(fmt="xml", obsidian_dir=tmp_path)
        compiler.add_obsidian_search("nonexistent-query-xyz")
        assert len(compiler.sections) == 0

    def test_add_glob(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        (tmp_path / "a.txt").write_text("file a")
        (tmp_path / "b.txt").write_text("file b")

        compiler = compile_context.ContextCompiler(fmt="xml")
        compiler.add_glob("*.txt")
        result = compiler.compile()

        assert "file a" in result
        assert "file b" in result

    def test_max_chars_truncation(self, tmp_path: Path) -> None:
        test_file = tmp_path / "big.txt"
        test_file.write_text("x" * 10000)

        compiler = compile_context.ContextCompiler(fmt="xml", max_chars=500)
        compiler.add_file(str(test_file))
        result = compiler.compile()

        assert len(result) <= 600  # max_chars + overhead

    def test_add_diff(self) -> None:
        compiler = compile_context.ContextCompiler(fmt="xml")
        with patch.object(compile_context, "_run", return_value="diff output here"):
            compiler.add_diff("HEAD~1")
        result = compiler.compile()
        assert "diff output here" in result
        assert 'type="diff"' in result

    def test_add_log(self) -> None:
        compiler = compile_context.ContextCompiler(fmt="xml")
        with patch.object(compile_context, "_run", return_value="abc123 commit msg"):
            compiler.add_log("-5")
        result = compiler.compile()
        assert "abc123 commit msg" in result
        assert 'type="log"' in result


class TestCLI:
    """Test CLI invocation."""

    def test_no_args_exits_with_error(self) -> None:
        result = CliRunner().invoke(compile_context.main, [])
        assert result.exit_code != 0

    def test_file_arg(self, tmp_path: Path) -> None:
        test_file = tmp_path / "test.txt"
        test_file.write_text("content here")

        result = CliRunner().invoke(compile_context.main, ["--file", str(test_file)])
        assert result.exit_code == 0
        assert "content here" in result.output
        assert "<context>" in result.output

    def test_markdown_format(self, tmp_path: Path) -> None:
        test_file = tmp_path / "test.txt"
        test_file.write_text("content here")

        result = CliRunner().invoke(
            compile_context.main, ["--file", str(test_file), "--format", "markdown"]
        )
        assert result.exit_code == 0
        assert "## File:" in result.output
        assert "<context>" not in result.output

    def test_diff_with_mock(self) -> None:
        with patch.object(compile_context, "_run", return_value="mock diff"):
            result = CliRunner().invoke(compile_context.main, ["--diff", "HEAD~1"])
        assert result.exit_code == 0
        assert "mock diff" in result.output

    def test_multiple_sources(self, tmp_path: Path) -> None:
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("file a")
        f2.write_text("file b")

        result = CliRunner().invoke(compile_context.main, ["--file", str(f1), "--file", str(f2)])
        assert result.exit_code == 0
        assert "file a" in result.output
        assert "file b" in result.output


class TestSearchObsidian:
    """Test _search_obsidian helper."""

    def test_finds_by_content(self, tmp_path: Path) -> None:
        note = tmp_path / "test.md"
        note.write_text("Some unique content about widgets")
        results = compile_context._search_obsidian("widgets", tmp_path)
        assert len(results) == 1
        assert "widgets" in results[0][1]

    def test_finds_by_filename(self, tmp_path: Path) -> None:
        note = tmp_path / "widgets.md"
        note.write_text("Nothing about the query in body")
        results = compile_context._search_obsidian("widgets", tmp_path)
        assert len(results) == 1

    def test_case_insensitive(self, tmp_path: Path) -> None:
        note = tmp_path / "test.md"
        note.write_text("WIDGETS are great")
        results = compile_context._search_obsidian("widgets", tmp_path)
        assert len(results) == 1

    def test_max_results_capped(self, tmp_path: Path) -> None:
        for i in range(10):
            (tmp_path / f"note{i}.md").write_text("common query term")
        results = compile_context._search_obsidian("common", tmp_path)
        assert len(results) <= 5

    def test_no_results(self, tmp_path: Path) -> None:
        (tmp_path / "note.md").write_text("something else entirely")
        results = compile_context._search_obsidian("nonexistent", tmp_path)
        assert len(results) == 0
