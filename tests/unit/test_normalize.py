"""Test the normalize_skills.py script."""

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "normalize_skills.py"

SAMPLE_FLAT_SKILL = """\
---
name: my_test_skill
description: >
  Use when testing normalization. Do NOT use in production.
---

This is a test skill.
"""


def test_normalize_creates_directory(tmp_path: Path) -> None:
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    flat_file = skills_dir / "my_test_skill.md"
    flat_file.write_text(SAMPLE_FLAT_SKILL)

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--skills-dir", str(skills_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert (skills_dir / "my_test_skill" / "SKILL.md").exists()
    assert not flat_file.exists()
    assert (skills_dir / "my_test_skill" / "SKILL.md").read_text() == SAMPLE_FLAT_SKILL


def test_normalize_skips_existing_directory(tmp_path: Path) -> None:
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    (skills_dir / "my_test_skill").mkdir()
    (skills_dir / "my_test_skill" / "SKILL.md").write_text("existing")
    flat_file = skills_dir / "my_test_skill.md"
    flat_file.write_text(SAMPLE_FLAT_SKILL)

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--skills-dir", str(skills_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert flat_file.exists()  # flat file NOT consumed
    assert (skills_dir / "my_test_skill" / "SKILL.md").read_text() == "existing"


def test_normalize_dry_run(tmp_path: Path) -> None:
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    flat_file = skills_dir / "my_test_skill.md"
    flat_file.write_text(SAMPLE_FLAT_SKILL)

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--skills-dir", str(skills_dir), "--dry-run"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert flat_file.exists()  # still there
    assert not (skills_dir / "my_test_skill").exists()  # not created


def test_normalize_no_flat_files(tmp_path: Path) -> None:
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--skills-dir", str(skills_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "No flat-file skills found" in result.stdout
