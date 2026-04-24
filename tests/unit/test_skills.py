"""Validate all SKILL.md files follow the Agent Skills standard."""

import shutil
import subprocess
from pathlib import Path

import frontmatter
import pytest

SKILLS_DIR = Path(__file__).resolve().parents[2] / ".claude" / "skills"
SKILL_DIRS = sorted(d for d in SKILLS_DIR.iterdir() if d.is_dir() and d.name != "__pycache__")
SKILL_DIRS_WITH_SCRIPTS = sorted(d for d in SKILL_DIRS if (d / "scripts").exists())
MAX_SKILL_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024


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
        name = post.metadata["name"]
        assert isinstance(name, str), "frontmatter 'name' must be a string"
        assert name == skill_dir.name, f"name '{name}' doesn't match directory '{skill_dir.name}'"

    def test_description_not_empty(self, skill_dir: Path) -> None:
        text = (skill_dir / "SKILL.md").read_text()
        post = frontmatter.loads(text)
        desc = post.metadata["description"]
        assert isinstance(desc, str), "frontmatter 'description' must be a string"
        desc = desc.strip()
        assert len(desc) > 20, "description too short — should explain when to use"
        assert len(desc) <= MAX_DESCRIPTION_LENGTH, (
            f"description too long: {len(desc)} > {MAX_DESCRIPTION_LENGTH}"
        )

    def test_snake_case_name(self, skill_dir: Path) -> None:
        name = skill_dir.name
        assert len(name) <= MAX_SKILL_NAME_LENGTH, (
            f"directory name too long: {len(name)} > {MAX_SKILL_NAME_LENGTH}"
        )
        assert name == name.lower(), "directory name must be lowercase"
        assert " " not in name, "directory name must not contain spaces"
        assert name.replace("-", "").isalnum(), "directory name must be alphanumeric with hyphens"

    def test_no_xml_angle_brackets_in_frontmatter(self, skill_dir: Path) -> None:
        text = (skill_dir / "SKILL.md").read_text()
        post = frontmatter.loads(text)
        name = post.metadata["name"]
        desc = post.metadata["description"]
        assert "<" not in name and ">" not in name, "name must not contain XML angle brackets"
        assert "<" not in desc and ">" not in desc, (
            "description must not contain XML angle brackets"
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


REPO_ROOT = Path(__file__).resolve().parents[2]


class TestCodexRepoSymlink:
    """Validate .agents/skills symlink for Codex discovery."""

    def test_agents_skills_symlink_exists(self) -> None:
        link = REPO_ROOT / ".agents" / "skills"
        assert link.is_symlink(), ".agents/skills should be a symlink"

    def test_agents_skills_resolves_to_claude_skills(self) -> None:
        link = REPO_ROOT / ".agents" / "skills"
        assert link.resolve() == (REPO_ROOT / ".claude" / "skills").resolve()

    def test_agents_skills_contains_skill_md(self) -> None:
        skill_md = REPO_ROOT / ".agents" / "skills" / "mental-models" / "SKILL.md"
        assert skill_md.exists(), "mental-models SKILL.md not reachable via .agents/skills"


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
