"""Count narration words in experiment scripts; excludes direction blocks."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1] / "SCRIPTS"
APOSTROPHE = chr(0x2019)
WORD = re.compile(r"[A-Za-z0-9]+(?:['" + APOSTROPHE + r"][A-Za-z0-9]+)*")

for folder in ("ORIGINAL", "REVISED"):
    for path in sorted((ROOT / folder).glob("YS*.md")):
        text = path.read_text(encoding="utf-8")
        blocks = re.findall(r"\*\*\[NARRATION\]\*\*\s*(.*?)(?=\n\s*\*\*\[|\n### |\Z)", text, re.S)
        narration = " ".join(blocks)
        print(f"{folder}/{path.name}: {len(WORD.findall(narration))} narration words")
        if folder in ("ORIGINAL", "REVISED"):
            body = text.split("## Script", 1)[-1].split("## Retention map", 1)[0]
            for section in re.split(r"(?=^### )", body, flags=re.M):
                if not section.startswith("### "):
                    continue
                title = section.splitlines()[0]
                section_blocks = re.findall(r"\*\*\[NARRATION\]\*\*\s*(.*?)(?=\n\s*\*\*\[|\n### |\Z)", section, re.S)
                count = len(WORD.findall(" ".join(section_blocks)))
                print(f"  {title}: {count} words, {count / 115 * 60:.0f}s at 115 wpm")
