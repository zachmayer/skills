"""Validate all SKILL.md files follow the Agent Skills standard."""

from pathlib import Path

import pytest
import yaml

SKILLS_DIR = Path(__file__).resolve().parents[2] / "skills"
SKILL_DIRS = sorted(d for d in SKILLS_DIR.iterdir() if d.is_dir() and d.name != "__pycache__")
MAX_LINES = 500


def parse_frontmatter(text: str) -> dict:
    """Parse YAML frontmatter from a SKILL.md file."""
    if not text.startswith("---"):
        return {}
    end = text.index("---", 3)
    return yaml.safe_load(text[3:end]) or {}


@pytest.fixture(params=[d.name for d in SKILL_DIRS], ids=lambda n: n)
def skill_dir(request: pytest.FixtureRequest) -> Path:
    return SKILLS_DIR / request.param


class TestSkillStructure:
    def test_has_skill_md(self, skill_dir: Path) -> None:
        assert (skill_dir / "SKILL.md").exists(), f"{skill_dir.name}/ missing SKILL.md"

    def test_valid_frontmatter(self, skill_dir: Path) -> None:
        text = (skill_dir / "SKILL.md").read_text()
        fm = parse_frontmatter(text)
        assert "name" in fm, "frontmatter missing 'name'"
        assert "description" in fm, "frontmatter missing 'description'"

    def test_name_matches_directory(self, skill_dir: Path) -> None:
        text = (skill_dir / "SKILL.md").read_text()
        fm = parse_frontmatter(text)
        assert fm.get("name") == skill_dir.name, (
            f"name '{fm.get('name')}' doesn't match directory '{skill_dir.name}'"
        )

    def test_description_not_empty(self, skill_dir: Path) -> None:
        text = (skill_dir / "SKILL.md").read_text()
        fm = parse_frontmatter(text)
        desc = fm.get("description", "").strip()
        assert len(desc) > 20, "description too short — should explain when to use"

    def test_under_line_limit(self, skill_dir: Path) -> None:
        text = (skill_dir / "SKILL.md").read_text()
        fm = parse_frontmatter(text)
        limit = fm.get("max_lines", MAX_LINES)
        lines = text.splitlines()
        assert len(lines) <= limit, f"SKILL.md is {len(lines)} lines (max {limit})"

    def test_kebab_case_name(self, skill_dir: Path) -> None:
        name = skill_dir.name
        assert name == name.lower(), "directory name must be lowercase"
        assert " " not in name, "directory name must not contain spaces"
        assert name.replace("-", "").replace("_", "").isalnum(), (
            "directory name must be alphanumeric with hyphens/underscores"
        )
