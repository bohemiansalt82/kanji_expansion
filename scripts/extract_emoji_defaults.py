#!/usr/bin/env python3
"""Extract the EMOJI map currently embedded in kanji_game.html and
write it out as emoji-defaults.json. Run after manual edits to the
game's EMOJI const so admin.html and the game stay in sync."""
import json, re
from pathlib import Path

ROOT = Path(__file__).parent
HTML = ROOT / "kanji_game.html"
OUT  = ROOT / "emoji-defaults.json"

text = HTML.read_text(encoding="utf-8")
m = re.search(r'const EMOJI = \{(.*?)\};', text, re.DOTALL)
if not m:
    raise SystemExit("EMOJI const not found in kanji_game.html")
block = m.group(1)

# Match "char":"emoji" pairs (handle multi-codepoint emoji values)
mapping = {}
for km in re.finditer(r'"([^"]+)"\s*:\s*"([^"]+)"', block):
    mapping[km.group(1)] = km.group(2)

OUT.write_text(json.dumps(mapping, ensure_ascii=False, indent=0), encoding="utf-8")
print(f"Wrote {OUT}: {len(mapping)} entries")
