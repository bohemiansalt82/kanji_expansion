#!/usr/bin/env python3
"""Build kanji-expansion workbook organized by SEMANTIC DOMAIN.

Five-domain taxonomy: 自然 → 人間 → 行為 → 社會 → 抽象
Within each domain, radicals are ordered by Kangxi number; each radical
gets its own page(s) of derived kanji with the radical strokes highlighted.
"""
import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET

# Reuse parse_kvg and constants from the existing radical-ordered builder
import sys
sys.path.insert(0, str(Path(__file__).parent))
from build_expansion_workbook import (  # noqa: E402
    parse_kvg, KANGXI, RADICAL_KR, RICH_KVG_DIR, DATA_PATH,
)

ROOT = Path(__file__).resolve().parent.parent
OUT_HTML = ROOT / "kanji_domain_workbook.html"

CELLS_PER_PAGE = 20

# Domain ordering (display order)
DOMAINS = [
    ("자연", "自然", "Nature",   "#1b5e20"),
    ("인간", "人間", "Human",    "#0d47a1"),
    ("행위", "行為", "Action",   "#bf360c"),
    ("사회", "社會", "Society",  "#4a148c"),
    ("추상", "抽象", "Abstract", "#37474f"),
]

# Radical → domain mapping (Kangxi radical # → domain key)
RAD_DOMAIN = {
    # 자연 — elements, weather, geography, plants, animals
    15:"자연", 27:"자연", 32:"자연", 36:"자연", 45:"자연", 46:"자연", 47:"자연",
    72:"자연", 74:"자연", 75:"자연", 84:"자연", 85:"자연", 86:"자연",
    93:"자연", 94:"자연", 97:"자연", 100:"자연", 102:"자연",
    106:"자연", 107:"자연", 112:"자연", 114:"자연", 115:"자연", 116:"자연",
    118:"자연", 119:"자연", 123:"자연", 124:"자연",
    140:"자연", 141:"자연", 142:"자연", 148:"자연", 150:"자연", 151:"자연",
    152:"자연", 153:"자연", 170:"자연", 172:"자연", 173:"자연", 174:"자연",
    179:"자연", 182:"자연", 187:"자연", 195:"자연", 196:"자연",
    198:"자연", 199:"자연", 200:"자연", 201:"자연", 202:"자연", 203:"자연",
    205:"자연", 208:"자연", 212:"자연", 213:"자연",

    # 인간 — body, family, identity
    9:"인간", 10:"인간", 30:"인간", 33:"인간", 37:"인간", 38:"인간", 39:"인간",
    43:"인간", 44:"인간", 49:"인간", 61:"인간", 64:"인간", 76:"인간", 78:"인간",
    80:"인간", 82:"인간", 83:"인간", 87:"인간", 88:"인간", 92:"인간",
    103:"인간", 104:"인간", 109:"인간", 125:"인간", 128:"인간", 130:"인간",
    132:"인간", 135:"인간", 143:"인간", 157:"인간", 158:"인간", 176:"인간",
    181:"인간", 185:"인간", 188:"인간", 190:"인간", 209:"인간", 211:"인간",

    # 행위 — actions, movement, senses, tools-of-action
    11:"행위", 18:"행위", 19:"행위", 21:"행위", 29:"행위",
    34:"행위", 35:"행위", 41:"행위", 48:"행위", 51:"행위",
    54:"행위", 55:"행위", 56:"행위", 57:"행위", 60:"행위", 62:"행위",
    65:"행위", 66:"행위", 69:"행위", 73:"행위", 77:"행위", 79:"행위",
    101:"행위", 105:"행위", 110:"행위", 111:"행위",
    117:"행위", 133:"행위", 144:"행위", 147:"행위", 149:"행위",
    156:"행위", 162:"행위", 165:"행위", 171:"행위",
    183:"행위", 184:"행위", 191:"행위",

    # 사회 — culture, materials, buildings, commerce, civilization
    14:"사회", 16:"사회", 25:"사회", 26:"사회", 31:"사회", 40:"사회",
    50:"사회", 53:"사회", 63:"사회", 67:"사회", 68:"사회",
    90:"사회", 91:"사회", 96:"사회", 98:"사회", 108:"사회",
    113:"사회", 120:"사회", 121:"사회", 122:"사회", 127:"사회", 129:"사회",
    131:"사회", 134:"사회", 137:"사회", 145:"사회", 146:"사회",
    154:"사회", 159:"사회", 163:"사회", 164:"사회", 166:"사회",
    167:"사회", 169:"사회", 177:"사회", 178:"사회", 180:"사회",
    186:"사회", 192:"사회", 193:"사회", 194:"사회",
    197:"사회", 204:"사회", 206:"사회", 207:"사회", 214:"사회",

    # 추상 — basic strokes, abstract concepts, quantity, qualifiers
    1:"추상", 2:"추상", 3:"추상", 4:"추상", 5:"추상", 6:"추상",
    7:"추상", 8:"추상", 12:"추상", 13:"추상", 17:"추상", 20:"추상",
    22:"추상", 23:"추상", 24:"추상", 28:"추상", 42:"추상", 52:"추상",
    58:"추상", 59:"추상", 70:"추상", 71:"추상", 81:"추상", 89:"추상",
    95:"추상", 99:"추상", 126:"추상", 136:"추상", 138:"추상", 139:"추상",
    155:"추상", 160:"추상", 161:"추상", 168:"추상", 175:"추상", 189:"추상",
    210:"추상",
}

# Verify mapping covers 1..214
_MISSING = [n for n in range(1, 215) if n not in RAD_DOMAIN]
if _MISSING:
    print(f"[warn] no domain set for radicals: {_MISSING}")


def build_inner_svg(code, rad_num):
    all_paths, rad_ids = parse_kvg(code, rad_num)
    parts = [
        '<line class="cross" x1="54.5" y1="2" x2="54.5" y2="107"/>',
        '<line class="cross" x1="2" y1="54.5" x2="107" y2="54.5"/>',
    ]
    for pid, d in all_paths:
        cls = "base" if pid in rad_ids else "guide"
        parts.append(f'<path class="{cls}" d="{d}"/>')
    return "\n        ".join(parts)


def build_cell(k, rad_num):
    inner = build_inner_svg(k["code"], rad_num)
    jlpt = k.get("jlpt") or ""
    jlpt_html = f'<span class="jlpt jlpt-{jlpt.lower()}">{jlpt}</span>' if jlpt else ''
    reading = k.get("reading") or "—"
    meaning = k.get("meaning") or ""
    return f"""  <div class="cell">
    <div class="cell-top">
      <span class="reading">{reading}</span>
      {jlpt_html}
    </div>
    <div class="svg-wrap">
      <svg viewBox="0 0 109 109" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg">
        {inner}
      </svg>
    </div>
    <div class="meaning">{meaning}</div>
  </div>"""


def chunk(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def build_page(domain_kr, domain_color, rad_char, rad_kr, rad_strokes,
               rad_num, page_idx, total_pages, kanji_list):
    cells = "\n\n".join(build_cell(k, rad_num) for k in kanji_list)
    page_label = f"{page_idx}/{total_pages}" if total_pages > 1 else ""
    return f"""<section class="page" data-domain="{domain_kr}">
  <div class="header">
    <span class="domain-tag" style="background:{domain_color}">{domain_kr}</span>
    <h1 class="title"><span class="root">{rad_char}</span></h1>
    <p class="subtitle">{rad_kr} · 부수 {rad_strokes}획 {page_label}</p>
  </div>
  <div class="grid">
{cells}
  </div>
</section>"""


def build_section_divider(domain_kr, domain_cn, domain_en, domain_color,
                           radicals_in_domain):
    """A dedicated full-page section divider before each domain's pages."""
    rad_chips = " ".join(
        f'<span class="rchip">{KANGXI[r][0]}</span>'
        for r in radicals_in_domain if r in KANGXI
    )
    return f"""<section class="page divider" data-domain="{domain_kr}">
  <div class="divider-body">
    <div class="divider-domain" style="color:{domain_color}">{domain_kr}</div>
    <div class="divider-cn">{domain_cn} · {domain_en}</div>
    <div class="divider-rads">{rad_chips}</div>
  </div>
</section>"""


# Load data and group by radical
data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
by_rad = {}
for k in data:
    r = k.get("radical")
    if not r:
        continue
    by_rad.setdefault(r, []).append(k)

# Sort radicals into the 5-domain order
def domain_order_key(domain_kr):
    for i, (kr, _, _, _) in enumerate(DOMAINS):
        if kr == domain_kr:
            return i
    return 999

pages = []
domain_to_color = {kr: c for (kr, _, _, c) in DOMAINS}
domain_to_cn = {kr: cn for (kr, cn, _, _) in DOMAINS}
domain_to_en = {kr: en for (kr, _, en, _) in DOMAINS}

# For each domain, collect its radicals and build divider + radical pages
for dom_kr, dom_cn, dom_en, dom_color in DOMAINS:
    rads_in_domain = sorted(
        r for r in by_rad
        if RAD_DOMAIN.get(r) == dom_kr and r in KANGXI
    )
    if not rads_in_domain:
        continue
    # Section divider
    pages.append(build_section_divider(
        dom_kr, dom_cn, dom_en, dom_color, rads_in_domain
    ))
    # Pages for each radical
    for rad_num in rads_in_domain:
        rad_char, rad_strokes = KANGXI[rad_num]
        rad_kr = RADICAL_KR.get(rad_num, "")
        chunks = list(chunk(by_rad[rad_num], CELLS_PER_PAGE))
        for i, c in enumerate(chunks, 1):
            pages.append(build_page(
                dom_kr, dom_color, rad_char, rad_kr, rad_strokes,
                rad_num, i, len(chunks), c
            ))

pages_html = "\n\n".join(pages)
total_pages = len(pages)
total_kanji = sum(
    len(by_rad[r]) for r in by_rad
    if RAD_DOMAIN.get(r) in {d[0] for d in DOMAINS} and r in KANGXI
)

HTML = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>한자 의미 도메인 워크북 - 자연·인간·행위·사회·추상</title>
<style>
  @font-face {{
    font-family: 'Noto Sans Mono CJK JP';
    src: url('https://cdn.jsdelivr.net/gh/notofonts/noto-cjk@main/Sans/Mono/NotoSansMonoCJKjp-Regular.otf') format('opentype');
    font-weight: 400; font-style: normal; font-display: swap;
  }}
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;800&display=swap');

  @page {{ size: A4 portrait; margin: 25mm; }}
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; padding: 0; }}
  body {{
    font-family: 'Noto Sans Mono CJK JP', 'Noto Sans JP', 'Noto Sans CJK JP',
                 'Hiragino Kaku Gothic Pro', 'Yu Gothic', sans-serif;
    color: #111;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }}

  .page {{ page-break-after: always; }}
  .page:last-child {{ page-break-after: auto; }}

  @media screen {{
    html {{ background: #d8d8d8; padding: 16px 0; }}
    body {{ background: transparent; }}
    .page {{
      width: 210mm;
      min-height: 297mm;
      margin: 0 auto 16px;
      padding: 25mm;
      background: #fff;
      box-shadow: 0 2px 16px rgba(0,0,0,0.18);
    }}
  }}

  .header {{
    text-align: center;
    margin-bottom: 10mm;
    position: relative;
  }}
  .domain-tag {{
    display: inline-block;
    font-size: 9pt;
    font-weight: 700;
    padding: 2pt 8pt;
    border-radius: 3pt;
    color: #fff;
    letter-spacing: 2px;
    margin-bottom: 3mm;
  }}
  .title {{ margin: 0; line-height: 1; }}
  .title .root {{
    color: #b00020;
    font-size: 40pt;
    font-weight: 800;
    letter-spacing: -1px;
  }}
  .subtitle {{ font-size: 10pt; color: #555; margin: 3mm 0 0 0; }}

  .grid {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 10mm 7mm;
  }}
  .cell {{ text-align: center; page-break-inside: avoid; }}
  .cell-top {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 4pt;
    margin-bottom: 2mm;
    min-height: 14pt;
  }}
  .reading {{
    font-size: 10.5pt;
    font-weight: 600;
    color: #333;
    letter-spacing: 0.5px;
  }}
  .jlpt {{
    display: inline-block;
    font-size: 7pt;
    font-weight: 700;
    padding: 1pt 4pt;
    border-radius: 3pt;
    color: #fff;
    letter-spacing: 0.3px;
    line-height: 1.2;
  }}
  .jlpt-n5 {{ background: #2e7d32; }}
  .jlpt-n4 {{ background: #558b2f; }}
  .jlpt-n3 {{ background: #ef6c00; }}
  .jlpt-n2 {{ background: #c62828; }}
  .jlpt-n1 {{ background: #6a1b9a; }}

  .svg-wrap {{
    width: 75%;
    max-width: 24mm;
    aspect-ratio: 1 / 1;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1.5px solid #333;
    background: #fff;
    padding: 1.5mm;
    overflow: hidden;
  }}
  svg {{ width: 100%; height: 100%; display: block; }}

  .cross  {{ stroke: #bbb; stroke-width: 0.5; stroke-dasharray: 2,2; opacity: 0.55; fill: none; }}
  .base   {{ stroke: #000; stroke-width: 4.2; fill: none; stroke-linecap: round; stroke-linejoin: round; opacity: 1; }}
  .guide  {{ stroke: #c4c4c4; stroke-width: 3; fill: none; stroke-linecap: round; stroke-linejoin: round; }}

  .meaning {{
    font-size: 9pt;
    color: #666;
    margin-top: 1.5mm;
    letter-spacing: 0.3px;
    text-transform: capitalize;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }}

  /* Section divider page */
  .divider {{
    display: flex;
    align-items: center;
    justify-content: center;
  }}
  .divider-body {{ text-align: center; }}
  .divider-domain {{
    font-size: 80pt;
    font-weight: 800;
    line-height: 1;
    letter-spacing: -2px;
  }}
  .divider-cn {{
    font-size: 14pt;
    color: #666;
    margin: 8mm 0 16mm;
    letter-spacing: 4px;
  }}
  .divider-rads {{
    max-width: 140mm;
    margin: 0 auto;
    line-height: 1.8;
  }}
  .rchip {{
    display: inline-block;
    font-size: 22pt;
    font-weight: 700;
    color: #444;
    margin: 0 6pt;
  }}
</style>
</head>
<body>

{pages_html}

</body>
</html>
"""

OUT_HTML.write_text(HTML, encoding="utf-8")
print(f"Wrote {OUT_HTML}")
print(f"Total: {total_kanji} kanji, {total_pages} pages")
# Per-domain summary
for dom_kr, _, _, _ in DOMAINS:
    rads = [r for r in by_rad
            if RAD_DOMAIN.get(r) == dom_kr and r in KANGXI]
    n_kanji = sum(len(by_rad[r]) for r in rads)
    print(f"  {dom_kr}: {len(rads)} radicals, {n_kanji} kanji")
