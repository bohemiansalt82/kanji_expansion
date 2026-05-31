#!/usr/bin/env python3
"""Build full Kyoiku Kanji (elementary) workbook — 52 A4 pages."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KVG_DIR = ROOT / ".kdata/node_modules/@madcat/kanjivg/dist/main"
DATA_PATH = ROOT / "kanji-data.json"
OUT_HTML = ROOT / "kyoiku_kanji_workbook.html"

CELLS_PER_PAGE = 20  # 5 cols × 4 rows

PATH_RE = re.compile(r'<path\s+id="kvg:([0-9a-f]+)-s(\d+)"\s+d="([^"]+)"\s*/>')

def extract_paths(code):
    p = KVG_DIR / f"{code}.svg"
    if not p.exists():
        return []
    text = p.read_text(encoding="utf-8")
    return [m.group(3) for m in PATH_RE.finditer(text)]

def build_inner_svg(code):
    parts = [
        '<line class="cross" x1="54.5" y1="2" x2="54.5" y2="107"/>',
        '<line class="cross" x1="2" y1="54.5" x2="107" y2="54.5"/>',
    ]
    for d in extract_paths(code):
        parts.append(f'<path class="stroke" d="{d}"/>')
    return "\n        ".join(parts)

def build_cell(k):
    inner = build_inner_svg(k["code"])
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
        yield seq[i:i+n]

def build_page(grade, page_idx, total_in_grade, kanji_list):
    cells = "\n\n".join(build_cell(k) for k in kanji_list)
    return f"""<section class="page">
  <div class="header">
    <h1 class="title"><span class="root">小{grade}</span></h1>
    <p class="subtitle">초등 {grade}학년 교육한자 — {page_idx}/{total_in_grade}</p>
  </div>

  <div class="grid">

{cells}

  </div>
</section>"""

# Load data
data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
by_grade = {}
for k in data:
    by_grade.setdefault(k["grade"], []).append(k)

pages = []
for grade in sorted(by_grade.keys()):
    chunks = list(chunk(by_grade[grade], CELLS_PER_PAGE))
    for i, c in enumerate(chunks, 1):
        pages.append(build_page(grade, i, len(chunks), c))

pages_html = "\n\n".join(pages)
total_pages = len(pages)
total_kanji = sum(len(by_grade[g]) for g in by_grade)

HTML = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>교육한자 워크북 - 초등 (1006자)</title>
<style>
  @font-face {{
    font-family: 'Noto Sans Mono CJK JP';
    src: url('https://cdn.jsdelivr.net/gh/notofonts/noto-cjk@main/Sans/Mono/NotoSansMonoCJKjp-Regular.otf') format('opentype');
    font-weight: 400;
    font-style: normal;
    font-display: swap;
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

  .page {{
    page-break-after: always;
  }}
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
  }}
  .title {{
    margin: 0;
    line-height: 1;
  }}
  .title .root {{
    color: #b00020;
    font-size: 32pt;
    font-weight: 800;
    letter-spacing: -1px;
  }}
  .subtitle {{
    font-size: 10pt;
    color: #555;
    margin: 3mm 0 0 0;
  }}

  .grid {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 10mm 7mm;
  }}
  .cell {{
    text-align: center;
    page-break-inside: avoid;
  }}
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
  svg {{
    width: 100%;
    height: 100%;
    display: block;
  }}

  .cross  {{ stroke: #bbb; stroke-width: 0.5; stroke-dasharray: 2,2; opacity: 0.55; fill: none; }}
  .stroke {{ stroke: #000; stroke-width: 3.5; fill: none; stroke-linecap: round; stroke-linejoin: round; opacity: 0.75; }}

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
for g in sorted(by_grade.keys()):
    n = len(by_grade[g])
    p = -(-n // CELLS_PER_PAGE)
    print(f"  Grade {g}: {n} kanji, {p} pages")
