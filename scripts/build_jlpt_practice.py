#!/usr/bin/env python3
"""JLPT N5→N1 받아쓰기 (handwriting practice) workbook.

Per row: 10 tracing cells of the same kanji in semi-transparent strokes.
Only the leftmost cell has hiragana label above and English meaning below.
"""
import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
RICH_KVG_DIR = ROOT / ".kdata/node_modules/kanjivg-js/kanji"
DATA_PATH = ROOT / "jlpt-data.json"
OUT_HTML = ROOT / "jlpt_practice_workbook.html"

ROWS_PER_PAGE = 8           # 8 kanji per page, each kanji = 1 row × 10 cells
CELLS_PER_ROW = 10

PATH_RE = re.compile(
    r'<path\s+id="kvg:[0-9a-f]+-s\d+"[^/]*?d="([^"]+)"\s*/>',
    re.DOTALL,
)

def extract_paths_simple(code):
    """Return list of d-attributes (one per stroke)."""
    p = RICH_KVG_DIR / f"{code}.svg"
    if not p.exists():
        return []
    text = p.read_text(encoding="utf-8")
    return PATH_RE.findall(text)


def build_symbol(code):
    """Build a <symbol> definition for a kanji (used 10× per row via <use>)."""
    paths = extract_paths_simple(code)
    if not paths:
        return ""
    path_html = "".join(f'<path class="trace" d="{d}"/>' for d in paths)
    return (
        f'<symbol id="k{code}" viewBox="0 0 109 109" preserveAspectRatio="xMidYMid meet">'
        f'<line class="cross" x1="54.5" y1="2" x2="54.5" y2="107"/>'
        f'<line class="cross" x1="2" y1="54.5" x2="107" y2="54.5"/>'
        f'{path_html}</symbol>'
    )


def build_cell_svg(code):
    """An <svg> that just references the symbol via <use>."""
    return (
        f'<svg viewBox="0 0 109 109" xmlns="http://www.w3.org/2000/svg">'
        f'<use href="#k{code}"/></svg>'
    )


def build_cell(code):
    svg = build_cell_svg(code)
    return f'<div class="cell"><div class="svg-wrap">{svg}</div></div>'


def build_row(k):
    reading = k.get("reading") or "—"
    meaning = k.get("meaning") or ""
    korean = k.get("korean") or ""
    label = (
        f'<div class="row-label">'
        f'<span class="rl-reading">{reading}</span>'
        f'<span class="rl-sep">·</span>'
        f'<span class="rl-meaning">{meaning}</span>'
    )
    if korean:
        label += (
            f'<span class="rl-sep">·</span>'
            f'<span class="rl-korean">{korean}</span>'
        )
    label += '</div>'
    cells = "".join(build_cell(k["code"]) for _ in range(CELLS_PER_ROW))
    return f'<div class="row">{label}<div class="cells">{cells}</div></div>'


def chunk(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def build_page(jlpt, page_idx, total_pages, kanji_list):
    rows_html = "\n".join(build_row(k) for k in kanji_list)
    return f"""<section class="page">
  <div class="header">
    <span class="jlpt-badge jlpt-{jlpt.lower()}">{jlpt}</span>
    <span class="subtitle">JLPT {jlpt} 받아쓰기 연습 · {page_idx}/{total_pages}</span>
  </div>
  <div class="rows">
{rows_html}
  </div>
</section>"""


# Load data and group by JLPT level
data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
by_jlpt = {}
for k in data:
    by_jlpt.setdefault(k["jlpt"], []).append(k)

pages = []
for jlpt in ["N5", "N4", "N3", "N2", "N1"]:
    lst = by_jlpt.get(jlpt, [])
    chunks = list(chunk(lst, ROWS_PER_PAGE))
    for i, c in enumerate(chunks, 1):
        pages.append(build_page(jlpt, i, len(chunks), c))

pages_html = "\n\n".join(pages)
total_pages = len(pages)
total_kanji = sum(len(by_jlpt[j]) for j in by_jlpt)

# Build symbol defs (one per unique kanji)
symbols_html = "".join(build_symbol(k["code"]) for k in data)
symbols_block = (
    f'<svg xmlns="http://www.w3.org/2000/svg" '
    f'style="position:absolute;width:0;height:0;overflow:hidden" aria-hidden="true">'
    f'<defs>{symbols_html}</defs></svg>'
)

HTML = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>JLPT 받아쓰기 워크북 - N5→N1 ({total_kanji}자)</title>
<style>
  @font-face {{
    font-family: 'Noto Sans Mono CJK JP';
    src: url('https://cdn.jsdelivr.net/gh/notofonts/noto-cjk@main/Sans/Mono/NotoSansMonoCJKjp-Regular.otf') format('opentype');
    font-weight: 400; font-style: normal; font-display: swap;
  }}
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;800&display=swap');

  @page {{ size: A4 portrait; margin: 18mm 15mm; }}
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; padding: 0; }}
  body {{
    font-family: 'Noto Sans Mono CJK JP', 'Noto Sans JP',
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
      padding: 18mm 15mm;
      background: #fff;
      box-shadow: 0 2px 16px rgba(0,0,0,0.18);
    }}
  }}

  .header {{
    display: flex;
    align-items: baseline;
    gap: 12pt;
    border-bottom: 1.5px solid #333;
    padding-bottom: 5mm;
    margin-bottom: 8mm;
  }}
  .jlpt-badge {{
    display: inline-block;
    font-size: 18pt;
    font-weight: 800;
    padding: 4pt 10pt;
    border-radius: 5pt;
    color: #fff;
    letter-spacing: 1px;
    line-height: 1;
  }}
  .jlpt-n5 {{ background: #2e7d32; }}
  .jlpt-n4 {{ background: #558b2f; }}
  .jlpt-n3 {{ background: #ef6c00; }}
  .jlpt-n2 {{ background: #c62828; }}
  .jlpt-n1 {{ background: #6a1b9a; }}
  .subtitle {{ font-size: 11pt; color: #555; }}

  .rows {{ display: flex; flex-direction: column; gap: 5mm; }}

  .row {{
    page-break-inside: avoid;
  }}
  .row-label {{
    display: flex;
    align-items: baseline;
    gap: 5pt;
    margin-bottom: 1.5mm;
    font-size: 10pt;
    line-height: 1.3;
    color: #333;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }}
  .rl-reading {{ font-weight: 700; color: #111; }}
  .rl-meaning {{ color: #555; text-transform: capitalize; }}
  .rl-korean  {{ color: #b00020; font-weight: 600; }}
  .rl-sep     {{ color: #bbb; }}

  .cells {{
    display: grid;
    grid-template-columns: repeat(10, 1fr);
    gap: 1.5mm;
  }}
  .cell {{
    display: flex;
    align-items: center;
    justify-content: center;
  }}
  .svg-wrap {{
    width: 100%;
    aspect-ratio: 1 / 1;
    border: 1.2px solid #888;
    background: #fff;
    padding: 1mm;
    overflow: hidden;
  }}
  svg {{ width: 100%; height: 100%; display: block; }}

  .cross {{
    stroke: #ddd;
    stroke-width: 0.5;
    stroke-dasharray: 2,2;
    opacity: 0.7;
    fill: none;
  }}
  .trace {{
    stroke: #000;
    stroke-width: 3.2;
    fill: none;
    stroke-linecap: round;
    stroke-linejoin: round;
    opacity: 0.18;
  }}
</style>
</head>
<body>

{symbols_block}

{pages_html}

</body>
</html>
"""

OUT_HTML.write_text(HTML, encoding="utf-8")
print(f"Wrote {OUT_HTML}")
print(f"Total: {total_kanji} kanji, {total_pages} pages")
for j in ["N5","N4","N3","N2","N1"]:
    n = len(by_jlpt.get(j, []))
    p = -(-n // ROWS_PER_PAGE)
    print(f"  {j}: {n} kanji, {p} pages")
