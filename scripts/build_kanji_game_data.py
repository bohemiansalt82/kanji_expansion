#!/usr/bin/env python3
"""Build kanji-game-data.json for the kanji game.

For each JLPT kanji, extract:
  - all strokes (id + path d)
  - top-level components (kvg:element + their stroke ids)

The game uses this to: draw the kanji, check user emoji clicks against
components, and highlight matching strokes.
"""
import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
RICH_KVG_DIR = ROOT / ".kdata/node_modules/kanjivg-js/kanji"
JLPT_PATH = ROOT / "jlpt-data.json"
OUT = ROOT / "kanji-game-data.json"

SVG_NS = "http://www.w3.org/2000/svg"
KVG_NS = "http://kanjivg.tagaini.net"


def parse_kanji(code):
    p = RICH_KVG_DIR / f"{code}.svg"
    if not p.exists():
        return None
    text = p.read_text(encoding="utf-8")
    text = re.sub(r'<!DOCTYPE.*?\]>', '', text, flags=re.DOTALL)
    text = re.sub(
        r'<svg\b([^>]*)>',
        r'<svg xmlns:kvg="http://kanjivg.tagaini.net"\1>',
        text, count=1
    )
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        return None

    # Collect all paths and a quick id-lookup
    strokes = []
    path_id_to_idx = {}
    for path in root.iter(f"{{{SVG_NS}}}path"):
        pid = path.get("id", "")
        d = path.get("d", "")
        if not (pid and d):
            continue
        sid = int(pid.split("-s")[-1])
        strokes.append({"id": sid, "d": d})
        path_id_to_idx[pid] = sid

    if not strokes:
        return None

    # Find the kanji's root <g> (first one with kvg:element)
    char_root = None
    for g in root.iter(f"{{{SVG_NS}}}g"):
        if g.get(f"{{{KVG_NS}}}element"):
            char_root = g
            break
    if char_root is None:
        return None

    def collect_strokes(g):
        ids = []
        for p in g.iter(f"{{{SVG_NS}}}path"):
            pid = p.get("id", "")
            if pid in path_id_to_idx:
                ids.append(path_id_to_idx[pid])
        return sorted(set(ids))

    # Top-level components: direct children with kvg:element,
    # descending through unnamed wrapper groups.
    def descend(g, out):
        for child in g:
            if child.tag != f"{{{SVG_NS}}}g":
                continue
            elem = child.get(f"{{{KVG_NS}}}element")
            if elem:
                # Prefer the canonical original char if present
                orig = child.get(f"{{{KVG_NS}}}original") or elem
                out.append({
                    "element": elem,
                    "original": orig,
                    "position": child.get(f"{{{KVG_NS}}}position") or "",
                    "strokes": collect_strokes(child),
                })
            else:
                descend(child, out)

    components = []
    descend(char_root, components)

    # If no sub-components, the kanji itself is the only component
    if not components:
        root_elem = char_root.get(f"{{{KVG_NS}}}element")
        components.append({
            "element": root_elem,
            "original": root_elem,
            "position": "",
            "strokes": sorted(s["id"] for s in strokes),
        })

    # Re-attach orphan strokes (strokes not in any component) to the
    # nearest preceding component by stroke order. This handles KanjiVG
    # quirks like 今 where a stroke sits inside an unnamed wrapper but
    # not in any kvg:element subgroup.
    all_sids = [s["id"] for s in strokes]
    assigned = set()
    for c in components:
        assigned.update(c["strokes"])
    orphans = [sid for sid in all_sids if sid not in assigned]
    for orphan_sid in orphans:
        # Find component with max stroke id <= orphan_sid - 1 (i.e. preceding)
        best, best_max = None, -1
        for c in components:
            if not c["strokes"]:
                continue
            cmax = max(c["strokes"])
            if cmax < orphan_sid and cmax > best_max:
                best, best_max = c, cmax
        if best is None and components:
            best = components[0]
        if best is not None:
            best["strokes"] = sorted(set(best["strokes"]) | {orphan_sid})

    # If a kanji has exactly 1 component that covers ALL strokes AND the
    # component's element isn't the kanji itself, this means KanjiVG didn't
    # decompose it meaningfully (e.g. 円 — all 4 strokes inside one <g
    # element="冂"> group). In that case, present the kanji's own character
    # as the clickable button instead of a partial radical name.
    root_char = char_root.get(f"{{{KVG_NS}}}element")
    if len(components) == 1 and root_char:
        c = components[0]
        if set(c["strokes"]) == set(all_sids) and c["element"] != root_char:
            c["element"] = root_char
            c["original"] = root_char

    return {"strokes": strokes, "components": components}


def main():
    jlpt = json.loads(JLPT_PATH.read_text(encoding="utf-8"))
    result = []
    missing = 0
    for k in jlpt:
        parsed = parse_kanji(k["code"])
        if not parsed:
            missing += 1
            continue
        result.append({
            "ch": k["ch"],
            "code": k["code"],
            "jlpt": k["jlpt"],
            "reading": k.get("reading", ""),
            "meaning": k.get("meaning", ""),
            "korean": k.get("korean", ""),
            "strokes": parsed["strokes"],
            "components": parsed["components"],
        })
    OUT.write_text(
        json.dumps(result, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8"
    )
    print(f"Wrote {OUT}: {len(result)} kanji ({missing} missing)")
    # Per-level breakdown
    counts = {}
    for k in result:
        counts[k["jlpt"]] = counts.get(k["jlpt"], 0) + 1
    print("Per level:", counts)


if __name__ == "__main__":
    main()
