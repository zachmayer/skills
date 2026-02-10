"""Sync external skills from URLs listed in external_skills.txt."""

import re
from pathlib import Path
from urllib.request import urlopen

urls = [
    line.strip()
    for line in Path("external_skills.txt").read_text().splitlines()
    if line.strip() and not line.strip().startswith("#")
]

for url in urls:
    name = url.rstrip("/").split("/")[-2].lower()
    dest = Path("skills") / name / "SKILL.md"
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"  {name}")
    content = urlopen(url).read().decode()  # noqa: S310
    content = re.sub(r"^(name:\s*)\S+", rf"\1{name}", content, count=1, flags=re.MULTILINE)
    dest.write_text(content)

print(f"Synced {len(urls)} external skills.")
