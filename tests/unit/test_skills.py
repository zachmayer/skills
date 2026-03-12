"""Validate all SKILL.md files follow the Agent Skills standard."""

import shutil
import subprocess
from pathlib import Path

import frontmatter
import pytest

SKILLS_DIR = Path(__file__).resolve().parents[2] / ".claude" / "skills"
SKILL_DIRS = sorted(d for d in SKILLS_DIR.iterdir() if d.is_dir() and d.name != "__pycache__")
SKILL_DIRS_WITH_SCRIPTS = sorted(d for d in SKILL_DIRS if (d / "scripts").exists())


@pytest.fixture(params=[d.name for d in SKILL_DIRS], ids=lambda n: n)
def skill_dir(request: pytest.FixtureRequest) -> Path:
    return SKILLS_DIR / request.param


@pytest.fixture(params=[d.name for d in SKILL_DIRS_WITH_SCRIPTS], ids=lambda n: n)
def skill_dir_with_scripts(request: pytest.FixtureRequest) -> Path:
    return SKILLS_DIR / request.param


class TestSkillStructure:
    def test_has_skill_md(self, skill_dir: Path) -> None:
        assert (skill_dir / "SKILL.md").exists(), f"{skill_dir.name}/ missing SKILL.md"

    def test_valid_frontmatter(self, skill_dir: Path) -> None:
        text = (skill_dir / "SKILL.md").read_text()
        post = frontmatter.loads(text)
        assert "name" in post.metadata, "frontmatter missing 'name'"
        assert "description" in post.metadata, "frontmatter missing 'description'"

    def test_name_matches_directory(self, skill_dir: Path) -> None:
        text = (skill_dir / "SKILL.md").read_text()
        post = frontmatter.loads(text)
        assert post.metadata.get("name") == skill_dir.name, (
            f"name '{post.metadata.get('name')}' doesn't match directory '{skill_dir.name}'"
        )

    def test_description_not_empty(self, skill_dir: Path) -> None:
        text = (skill_dir / "SKILL.md").read_text()
        post = frontmatter.loads(text)
        desc = post.metadata.get("description", "").strip()
        assert len(desc) > 20, "description too short — should explain when to use"

    def test_snake_case_name(self, skill_dir: Path) -> None:
        name = skill_dir.name
        assert name == name.lower(), "directory name must be lowercase"
        assert " " not in name, "directory name must not contain spaces"
        assert name.replace("-", "").replace("_", "").isalnum(), (
            "directory name must be alphanumeric with hyphens/underscores"
        )

    def test_description_uses_standard_pattern(self, skill_dir: Path) -> None:
        """Descriptions must use 'Use when'/'Do NOT use' pattern, not 'WHEN'/'WHEN NOT'."""
        text = (skill_dir / "SKILL.md").read_text()
        post = frontmatter.loads(text)
        desc = post.metadata.get("description", "")
        # Reject WHEN:/WHEN NOT: pattern (should be "Use when"/"Do NOT use")
        assert "WHEN:" not in desc and "WHEN NOT:" not in desc, (
            f"{skill_dir.name}: description uses 'WHEN:/WHEN NOT:' pattern — "
            "use 'Use when'/'Do NOT use' instead for consistency"
        )

    def test_scripts_have_allowed_tools(self, skill_dir_with_scripts: Path) -> None:
        """Skills with scripts/ directories should declare allowed-tools."""
        text = (skill_dir_with_scripts / "SKILL.md").read_text()
        post = frontmatter.loads(text)
        assert "allowed-tools" in post.metadata, (
            f"{skill_dir_with_scripts.name}: has scripts/ but no 'allowed-tools' in frontmatter"
        )


class TestJinaGrep:
    """Validate jina-grep skill content."""

    def test_skill_exists(self) -> None:
        assert (SKILLS_DIR / "jina-grep" / "SKILL.md").exists()

    def test_allowed_tools_uses_jina_grep(self) -> None:
        text = (SKILLS_DIR / "jina-grep" / "SKILL.md").read_text()
        post = frontmatter.loads(text)
        assert "jina-grep" in post.metadata.get("allowed-tools", "")

    def test_documents_installation(self) -> None:
        text = (SKILLS_DIR / "jina-grep" / "SKILL.md").read_text()
        assert "uv tool install" in text, "Should document installation via uv tool install"

    def test_documents_modes(self) -> None:
        text = (SKILLS_DIR / "jina-grep" / "SKILL.md").read_text()
        assert "Pipe mode" in text
        assert "Standalone mode" in text
        assert "Code search" in text

    @pytest.mark.skipif(shutil.which("jina-grep") is None, reason="jina-grep not installed")
    def test_pipe_mode(self) -> None:
        """jina-grep reranks piped input by semantic similarity."""
        lines = (
            "This function handles error logging and reporting\n"
            "The database connection pool is initialized here\n"
            "User authentication checks happen in this module\n"
        )
        result = subprocess.run(
            ["jina-grep", "error handling"],
            input=lines,
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert result.returncode == 0
        assert "error" in result.stdout.lower()
