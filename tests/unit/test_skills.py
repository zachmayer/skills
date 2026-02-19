"""Validate all SKILL.md files follow the Agent Skills standard."""

from pathlib import Path

import frontmatter
import pytest

SKILLS_DIR = Path(__file__).resolve().parents[2] / "skills"
SKILL_DIRS = sorted(d for d in SKILLS_DIR.iterdir() if d.is_dir() and d.name != "__pycache__")
FLAT_SKILLS = sorted(f for f in SKILLS_DIR.glob("*.md") if f.is_file())


@pytest.fixture(params=[d.name for d in SKILL_DIRS], ids=lambda n: n)
def skill_dir(request: pytest.FixtureRequest) -> Path:
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

    def test_scripts_have_allowed_tools(self, skill_dir: Path) -> None:
        """Skills with scripts/ directories should declare allowed-tools."""
        scripts_dir = skill_dir / "scripts"
        if not scripts_dir.exists():
            pytest.skip("no scripts directory")
        text = (skill_dir / "SKILL.md").read_text()
        post = frontmatter.loads(text)
        assert "allowed-tools" in post.metadata, (
            f"{skill_dir.name}: has scripts/ but no 'allowed-tools' in frontmatter"
        )


if FLAT_SKILLS:

    @pytest.fixture(params=[f.stem for f in FLAT_SKILLS], ids=lambda n: f"flat:{n}")
    def flat_skill(request: pytest.FixtureRequest) -> Path:
        return SKILLS_DIR / f"{request.param}.md"

    class TestFlatSkillStructure:
        """Validate flat-file skills (skills/<name>.md)."""

        def test_valid_frontmatter(self, flat_skill: Path) -> None:
            text = flat_skill.read_text()
            post = frontmatter.loads(text)
            assert "name" in post.metadata, "frontmatter missing 'name'"
            assert "description" in post.metadata, "frontmatter missing 'description'"

        def test_name_matches_filename(self, flat_skill: Path) -> None:
            text = flat_skill.read_text()
            post = frontmatter.loads(text)
            assert post.metadata.get("name") == flat_skill.stem, (
                f"name '{post.metadata.get('name')}' doesn't match filename '{flat_skill.stem}'"
            )

        def test_description_not_empty(self, flat_skill: Path) -> None:
            text = flat_skill.read_text()
            post = frontmatter.loads(text)
            desc = post.metadata.get("description", "").strip()
            assert len(desc) > 20, "description too short — should explain when to use"

        def test_snake_case_name(self, flat_skill: Path) -> None:
            name = flat_skill.stem
            assert name == name.lower(), "filename must be lowercase"
            assert " " not in name, "filename must not contain spaces"
            assert name.replace("-", "").replace("_", "").isalnum(), (
                "filename must be alphanumeric with hyphens/underscores"
            )

        def test_description_uses_standard_pattern(self, flat_skill: Path) -> None:
            text = flat_skill.read_text()
            post = frontmatter.loads(text)
            desc = post.metadata.get("description", "")
            assert "WHEN:" not in desc and "WHEN NOT:" not in desc, (
                f"{flat_skill.stem}: description uses 'WHEN:/WHEN NOT:' pattern — "
                "use 'Use when'/'Do NOT use' instead for consistency"
            )
