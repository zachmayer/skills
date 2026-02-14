"""Tests for the prompt_report analyze_prompt.py CLI."""

import importlib.util
import json
import sys
from pathlib import Path
from textwrap import dedent

import pytest
from click.testing import CliRunner

# Import analyze_prompt.py from the skill directory
_spec = importlib.util.spec_from_file_location(
    "analyze_prompt",
    Path(__file__).resolve().parents[2]
    / "skills"
    / "prompt_report"
    / "scripts"
    / "analyze_prompt.py",
)
assert _spec is not None and _spec.loader is not None
analyze_prompt = importlib.util.module_from_spec(_spec)
sys.modules["analyze_prompt"] = analyze_prompt
_spec.loader.exec_module(analyze_prompt)


class TestEstimateTokens:
    """Test token estimation heuristic."""

    def test_empty_string(self) -> None:
        assert analyze_prompt._estimate_tokens("") == 0

    def test_short_text(self) -> None:
        # 12 chars -> 3 tokens
        assert analyze_prompt._estimate_tokens("hello world!") == 3

    def test_longer_text(self) -> None:
        text = "a" * 400
        assert analyze_prompt._estimate_tokens(text) == 100


class TestClassifyLine:
    """Test line classification logic."""

    def test_blank_line(self) -> None:
        assert analyze_prompt._classify_line("") == "blank"
        assert analyze_prompt._classify_line("   ") == "blank"

    def test_header_is_structural(self) -> None:
        assert analyze_prompt._classify_line("## Section") == "structural"
        assert analyze_prompt._classify_line("# Top") == "structural"

    def test_frontmatter_delimiter(self) -> None:
        assert analyze_prompt._classify_line("---") == "structural"

    def test_numbered_step_is_signal(self) -> None:
        assert analyze_prompt._classify_line("1. Do the thing") == "signal"
        assert analyze_prompt._classify_line("  3. Another step") == "signal"

    def test_bold_list_item_is_signal(self) -> None:
        assert analyze_prompt._classify_line("- **Important**: details") == "signal"

    def test_prohibition_is_signal(self) -> None:
        assert analyze_prompt._classify_line("Never use eval()") == "signal"
        assert analyze_prompt._classify_line("You must always verify") == "signal"
        assert analyze_prompt._classify_line("Do not skip tests") == "signal"
        assert analyze_prompt._classify_line("Avoid using globals") == "signal"

    def test_table_row_is_signal(self) -> None:
        assert analyze_prompt._classify_line("| col1 | col2 | col3 |") == "signal"

    def test_code_fence_is_signal(self) -> None:
        assert analyze_prompt._classify_line("```python") == "signal"
        assert analyze_prompt._classify_line("```") == "signal"

    def test_example_is_filler(self) -> None:
        assert analyze_prompt._classify_line("- e.g. this is an example") == "filler"
        assert analyze_prompt._classify_line("- For example, consider") == "filler"

    def test_note_is_filler(self) -> None:
        assert analyze_prompt._classify_line("Tip: remember to check") == "filler"

    def test_link_is_filler(self) -> None:
        assert analyze_prompt._classify_line("See [docs](https://example.com)") == "filler"

    def test_blockquote_is_filler(self) -> None:
        assert analyze_prompt._classify_line("> Some quoted text") == "filler"

    def test_plain_text_defaults_to_signal(self) -> None:
        assert analyze_prompt._classify_line("Use the tool to check results") == "signal"


class TestIsStructuralLine:
    """Test structural line detection."""

    def test_header(self) -> None:
        assert analyze_prompt._is_structural_line("## Header")

    def test_frontmatter_delimiter(self) -> None:
        assert analyze_prompt._is_structural_line("---")

    def test_regular_text(self) -> None:
        assert not analyze_prompt._is_structural_line("regular text")


class TestCheckDirectoryName:
    """Test directory name matching."""

    def test_matching_name(self, tmp_path: Path) -> None:
        skill_dir = tmp_path / "my_skill"
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        skill_file.touch()
        result = analyze_prompt._check_directory_name(skill_file, "my_skill")
        assert result.passed

    def test_mismatched_name(self, tmp_path: Path) -> None:
        skill_dir = tmp_path / "my_skill"
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        skill_file.touch()
        result = analyze_prompt._check_directory_name(skill_file, "other_name")
        assert not result.passed
        assert "other_name" in result.detail

    def test_no_name(self, tmp_path: Path) -> None:
        skill_dir = tmp_path / "my_skill"
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        skill_file.touch()
        result = analyze_prompt._check_directory_name(skill_file, None)
        assert not result.passed
        assert "no name" in result.detail

    def test_scripts_subdirectory(self, tmp_path: Path) -> None:
        skill_dir = tmp_path / "my_skill" / "scripts"
        skill_dir.mkdir(parents=True)
        script = skill_dir / "run.py"
        script.touch()
        result = analyze_prompt._check_directory_name(script, "my_skill")
        assert result.passed


class TestAnalyzeFile:
    """Test full file analysis."""

    def test_well_formed_skill(self, tmp_path: Path) -> None:
        skill_dir = tmp_path / "good_skill"
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text(
            dedent("""\
            ---
            name: good_skill
            description: >
              Use when testing. Do NOT use in production.
            ---

            ## Overview

            1. Do step one
            2. Do step two
            3. Never skip step three

            ## Output

            ```
            result: value
            ```
        """)
        )
        report = analyze_prompt.analyze_file(skill_file)
        assert report.line_count > 0
        assert report.token_estimate > 0
        assert report.context_pct > 0
        # All structure checks should pass
        for check in report.structure_checks:
            assert check.passed, f"{check.name} failed: {check.detail}"

    def test_missing_frontmatter(self, tmp_path: Path) -> None:
        f = tmp_path / "bare.md"
        f.write_text("Just some text\nwith no frontmatter\n")
        report = analyze_prompt.analyze_file(f)
        fm_check = next(c for c in report.structure_checks if c.name == "YAML frontmatter")
        assert not fm_check.passed
        assert any("frontmatter" in r.lower() for r in report.recommendations)

    def test_over_500_lines(self, tmp_path: Path) -> None:
        f = tmp_path / "long.md"
        lines = ["---", "name: long", "description: test", "---"] + [
            f"Line {i}" for i in range(600)
        ]
        f.write_text("\n".join(lines))
        report = analyze_prompt.analyze_file(f)
        under_500 = next(c for c in report.structure_checks if c.name == "Under 500 lines")
        assert not under_500.passed
        assert any("500" in r for r in report.recommendations)

    def test_no_headers(self, tmp_path: Path) -> None:
        f = tmp_path / "flat.md"
        f.write_text("---\nname: flat\ndescription: test when\n---\nJust text no headers\n" * 5)
        report = analyze_prompt.analyze_file(f)
        header_check = next(c for c in report.structure_checks if c.name == "Has section headers")
        assert not header_check.passed
        assert any("header" in r.lower() for r in report.recommendations)

    def test_custom_context_window(self, tmp_path: Path) -> None:
        f = tmp_path / "test.md"
        # 4000 chars -> ~1000 tokens -> 1% of 100k
        f.write_text("x" * 4000)
        report = analyze_prompt.analyze_file(f, context_window=100_000)
        assert report.context_window == 100_000
        assert report.context_pct == pytest.approx(1.0, abs=0.1)

    def test_large_context_warning(self, tmp_path: Path) -> None:
        f = tmp_path / "huge.md"
        # ~6% of 10k context
        f.write_text("x" * 2400)
        report = analyze_prompt.analyze_file(f, context_window=10_000)
        assert any("context" in r.lower() for r in report.recommendations)

    def test_blank_and_structural_counting(self, tmp_path: Path) -> None:
        f = tmp_path / "mixed.md"
        f.write_text(
            dedent("""\
            ---
            name: test
            description: test when
            ---

            ## Section

            Never do this.

            > Some quote here.

        """)
        )
        report = analyze_prompt.analyze_file(f)
        assert report.blank_lines >= 3
        assert report.structural_lines >= 3  # ---, ---, ##
        assert report.signal_lines >= 1  # "Never do this"
        assert report.filler_lines >= 1  # blockquote

    def test_signal_ratio(self, tmp_path: Path) -> None:
        f = tmp_path / "ratio.md"
        f.write_text(
            dedent("""\
            Never do X
            Always do Y
            > quote filler
            - e.g. example filler
        """)
        )
        report = analyze_prompt.analyze_file(f)
        assert report.signal_lines == 2
        assert report.filler_lines == 2
        assert report.signal_ratio == pytest.approx(0.5)

    def test_no_numbered_steps_recommendation(self, tmp_path: Path) -> None:
        f = tmp_path / "nosteps.md"
        lines = ["---", "name: x", "description: when test", "---"]
        lines += ["Some content line"] * 25
        f.write_text("\n".join(lines))
        report = analyze_prompt.analyze_file(f)
        assert any("numbered steps" in r.lower() for r in report.recommendations)

    def test_when_not_in_description(self, tmp_path: Path) -> None:
        f = tmp_path / "notwhen.md"
        f.write_text("---\nname: x\ndescription: just a plain description\n---\n")
        report = analyze_prompt.analyze_file(f)
        when_check = next(c for c in report.structure_checks if "WHEN" in c.name)
        assert not when_check.passed

    def test_skill_md_checks_dir_name(self, tmp_path: Path) -> None:
        skill_dir = tmp_path / "my_skill"
        skill_dir.mkdir()
        f = skill_dir / "SKILL.md"
        f.write_text("---\nname: wrong_name\ndescription: when test\n---\n")
        report = analyze_prompt.analyze_file(f)
        name_check = next(
            (c for c in report.structure_checks if "directory" in c.name.lower()),
            None,
        )
        assert name_check is not None
        assert not name_check.passed

    def test_non_skill_md_skips_dir_check(self, tmp_path: Path) -> None:
        f = tmp_path / "prompt.txt"
        f.write_text("---\nname: x\ndescription: when\n---\n")
        report = analyze_prompt.analyze_file(f)
        name_checks = [c for c in report.structure_checks if "directory" in c.name.lower()]
        assert len(name_checks) == 0


class TestFormatText:
    """Test text formatting."""

    def test_contains_sections(self, tmp_path: Path) -> None:
        f = tmp_path / "test.md"
        f.write_text("---\nname: x\ndescription: when\n---\n## H\n1. step\n")
        report = analyze_prompt.analyze_file(f)
        text = analyze_prompt.format_text(report)
        assert "## Prompt Report:" in text
        assert "### Budget" in text
        assert "### Structure" in text
        assert "### Content" in text
        assert "### Recommendations" in text

    def test_no_issues_message(self, tmp_path: Path) -> None:
        skill_dir = tmp_path / "clean"
        skill_dir.mkdir()
        f = skill_dir / "SKILL.md"
        f.write_text("---\nname: clean\ndescription: Use when testing.\n---\n## H\n1. step\n")
        report = analyze_prompt.analyze_file(f)
        text = analyze_prompt.format_text(report)
        assert "No issues found" in text


class TestFormatJson:
    """Test JSON formatting."""

    def test_valid_json(self, tmp_path: Path) -> None:
        f = tmp_path / "test.md"
        f.write_text("---\nname: x\ndescription: when\n---\n")
        report = analyze_prompt.analyze_file(f)
        output = analyze_prompt.format_json(report)
        data = json.loads(output)
        assert "file_path" in data
        assert "token_estimate" in data
        assert "signal_ratio" in data
        assert "structure_checks" in data

    def test_signal_ratio_in_json(self, tmp_path: Path) -> None:
        f = tmp_path / "test.md"
        f.write_text("Never do this\nAlways do that\n")
        report = analyze_prompt.analyze_file(f)
        data = json.loads(analyze_prompt.format_json(report))
        assert isinstance(data["signal_ratio"], float)


class TestCLI:
    """Test the Click CLI entry point."""

    def test_single_file(self, tmp_path: Path) -> None:
        f = tmp_path / "test.md"
        f.write_text("---\nname: x\ndescription: when\n---\n## H\n1. step\n")
        runner = CliRunner()
        result = runner.invoke(analyze_prompt.main, [str(f)])
        assert result.exit_code == 0
        assert "Prompt Report" in result.output

    def test_multiple_files(self, tmp_path: Path) -> None:
        f1 = tmp_path / "a.md"
        f2 = tmp_path / "b.md"
        f1.write_text("---\nname: a\ndescription: when\n---\n")
        f2.write_text("---\nname: b\ndescription: when\n---\n")
        runner = CliRunner()
        result = runner.invoke(analyze_prompt.main, [str(f1), str(f2)])
        assert result.exit_code == 0
        assert result.output.count("Prompt Report") == 2
        assert "---" in result.output

    def test_json_output(self, tmp_path: Path) -> None:
        f = tmp_path / "test.md"
        f.write_text("---\nname: x\ndescription: when\n---\n")
        runner = CliRunner()
        result = runner.invoke(analyze_prompt.main, [str(f), "--format", "json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "token_estimate" in data

    def test_json_multiple_files(self, tmp_path: Path) -> None:
        f1 = tmp_path / "a.md"
        f2 = tmp_path / "b.md"
        f1.write_text("text a\n")
        f2.write_text("text b\n")
        runner = CliRunner()
        result = runner.invoke(analyze_prompt.main, [str(f1), str(f2), "--format", "json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) == 2

    def test_custom_context_window(self, tmp_path: Path) -> None:
        f = tmp_path / "test.md"
        f.write_text("x" * 4000)
        runner = CliRunner()
        result = runner.invoke(
            analyze_prompt.main, [str(f), "--context-window", "100000", "--format", "json"]
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["context_window"] == 100000

    def test_no_files_shows_error(self) -> None:
        runner = CliRunner()
        result = runner.invoke(analyze_prompt.main, [])
        assert result.exit_code != 0

    def test_nonexistent_file(self) -> None:
        runner = CliRunner()
        result = runner.invoke(analyze_prompt.main, ["/nonexistent/file.md"])
        assert result.exit_code != 0


class TestOnRealSkills:
    """Smoke tests against actual skills in the repo."""

    SKILLS_DIR = Path(__file__).resolve().parents[2] / "skills"

    @pytest.mark.skipif(
        not (
            Path(__file__).resolve().parents[2] / "skills" / "staff_engineer" / "SKILL.md"
        ).exists(),
        reason="skills directory not available",
    )
    def test_staff_engineer(self) -> None:
        f = self.SKILLS_DIR / "staff_engineer" / "SKILL.md"
        report = analyze_prompt.analyze_file(f)
        assert report.line_count > 0
        assert report.token_estimate > 0
        for check in report.structure_checks:
            assert check.passed, f"{check.name} failed"

    @pytest.mark.skipif(
        not (
            Path(__file__).resolve().parents[2] / "skills" / "prompt_report" / "SKILL.md"
        ).exists(),
        reason="skills directory not available",
    )
    def test_prompt_report_self(self) -> None:
        """The prompt_report skill should pass its own analysis."""
        f = self.SKILLS_DIR / "prompt_report" / "SKILL.md"
        report = analyze_prompt.analyze_file(f)
        assert report.line_count > 0
        for check in report.structure_checks:
            assert check.passed, f"{check.name} failed: {check.detail}"
