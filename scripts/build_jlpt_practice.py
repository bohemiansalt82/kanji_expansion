#!/usr/bin/env python3
"""JLPT N5→N1 받아쓰기 (handwriting practice) workbook.

Per row: 10 tracing cells of the same kanji in semi-transparent strokes.
Only the leftmost cell has hiragana label above and English meaning below.

Styled with the Toss Design System palette + N5-N1 tab navigation on screen
(print mode shows every page).
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RICH_KVG_DIR = ROOT / ".kdata/node_modules/kanjivg-js/kanji"
DATA_PATH = ROOT / "jlpt-data.json"
OUT_HTML = ROOT / "jlpt_practice_workbook.html"

ROWS_PER_PAGE = 8
CELLS_PER_ROW = 10

PATH_RE = re.compile(
    r'<path\s+id="kvg:[0-9a-f]+-s\d+"[^/]*?d="([^"]+)"\s*/>',
    re.DOTALL,
)

def extract_paths_simple(code):
    p = RICH_KVG_DIR / f"{code}.svg"
    if not p.exists():
        return []
    return PATH_RE.findall(p.read_text(encoding="utf-8"))

def build_symbol(code):
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
    return (
        f'<svg viewBox="0 0 109 109" xmlns="http://www.w3.org/2000/svg">'
        f'<use href="#k{code}"/></svg>'
    )

def build_cell(code):
    return f'<div class="cell"><div class="svg-wrap">{build_cell_svg(code)}</div></div>'

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
    return f"""<section class="page" data-level="{jlpt}">
  <div class="header">
    <span class="jlpt-badge jlpt-{jlpt.lower()}">{jlpt}</span>
    <span class="subtitle">JLPT {jlpt} 받아쓰기 연습 · {page_idx}/{total_pages}</span>
  </div>
  <div class="rows">
{rows_html}
  </div>
</section>"""


data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
by_jlpt = {}
for k in data:
    by_jlpt.setdefault(k["jlpt"], []).append(k)

pages = []
level_page_counts = {}
for jlpt in ["N5", "N4", "N3", "N2", "N1"]:
    lst = by_jlpt.get(jlpt, [])
    chunks = list(chunk(lst, ROWS_PER_PAGE))
    level_page_counts[jlpt] = len(chunks)
    for i, c in enumerate(chunks, 1):
        pages.append(build_page(jlpt, i, len(chunks), c))

pages_html = "\n\n".join(pages)
total_pages = len(pages)
total_kanji = sum(len(by_jlpt[j]) for j in by_jlpt)

symbols_html = "".join(build_symbol(k["code"]) for k in data)
symbols_block = (
    f'<svg xmlns="http://www.w3.org/2000/svg" '
    f'style="position:absolute;width:0;height:0;overflow:hidden" aria-hidden="true">'
    f'<defs>{symbols_html}</defs></svg>'
)

# Tab bar with per-level kanji counts
tab_buttons = "".join(
    f'<button class="tab tab-{lv.lower()}" data-level="{lv}" type="button">'
    f'<span class="tab-label">{lv}</span>'
    f'<span class="tab-meta">{len(by_jlpt.get(lv, []))}자 · {level_page_counts[lv]}p</span>'
    f'</button>'
    for lv in ["N5","N4","N3","N2","N1"]
)

HTML = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>JLPT 받아쓰기 워크북 · N5→N1 ({total_kanji}자)</title>
<style>
  @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;800&display=swap');
  :root {{
    --tds-blue: #3182F6;
    --tds-blue-pressed: #1B64DA;
    --tds-blue-bg: #E8F3FF;
    --tds-green: #15B981;
    --tds-orange: #FF9500;
    --tds-red: #F04452;
    --tds-purple: #8B5CF6;
    --tds-bg: #F9FAFB;
    --tds-surface: #FFFFFF;
    --tds-strong: #191F28;
    --tds-medium: #4E5968;
    --tds-weak: #8B95A1;
    --tds-divider: #E5E8EB;
    --tds-divider-soft: #F2F4F6;
  }}

  @page {{ size: A4 portrait; margin: 18mm 15mm; }}
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; padding: 0; }}
  body {{
    font-family: 'Pretendard', 'Noto Sans JP', -apple-system, BlinkMacSystemFont,
                 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif;
    color: var(--tds-strong);
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
    -webkit-font-smoothing: antialiased;
  }}

  .page {{ page-break-after: always; }}
  .page:last-child {{ page-break-after: auto; }}

  /* ───── SCREEN MODE ───── */
  @media screen {{
    html {{ background: var(--tds-bg); }}
    body {{ background: var(--tds-bg); padding-top: 76px; }}

    /* Sticky toolbar with level tabs */
    .toolbar {{
      position: fixed; top: 0; left: 0; right: 0; z-index: 50;
      background: var(--tds-surface);
      border-bottom: 1px solid var(--tds-divider);
      padding: 12px 16px;
      backdrop-filter: blur(8px);
    }}
    .toolbar-inner {{
      max-width: 1100px; margin: 0 auto;
      display: flex; align-items: center; gap: 16px;
      flex-wrap: wrap;
    }}
    .brand {{
      font-size: 14pt; font-weight: 800; color: var(--tds-strong);
      letter-spacing: -0.3px;
      display: flex; align-items: center; gap: 8px;
    }}
    .brand a {{
      color: var(--tds-weak); font-size: 10pt; font-weight: 500;
      text-decoration: none; margin-left: 4px;
    }}
    .brand a:hover {{ color: var(--tds-blue); }}
    .tabs {{
      display: flex; gap: 6px; flex: 1; justify-content: flex-end;
      flex-wrap: wrap;
    }}
    .tab {{
      display: inline-flex; flex-direction: column; align-items: center;
      gap: 1px;
      padding: 7px 14px; border: none; cursor: pointer;
      background: var(--tds-divider-soft); border-radius: 10px;
      font-family: inherit; transition: all .15s;
      color: var(--tds-medium);
    }}
    .tab-label {{ font-size: 11pt; font-weight: 800; letter-spacing: -0.3px; }}
    .tab-meta  {{ font-size: 8.5pt; font-weight: 500; opacity: 0.7; }}
    .tab:hover {{ background: var(--tds-blue-bg); color: var(--tds-blue); }}
    .tab.active {{ color: #fff; }}
    .tab-n5.active {{ background: var(--tds-green); }}
    .tab-n4.active {{ background: #20C997; }}
    .tab-n3.active {{ background: var(--tds-orange); }}
    .tab-n2.active {{ background: var(--tds-red); }}
    .tab-n1.active {{ background: var(--tds-purple); }}
    .tab-print {{ background: var(--tds-strong) !important; color: #fff !important; }}
    .tab-print:hover {{ background: #000 !important; }}

    /* A4-shaped pages with Toss-card chrome */
    .page {{
      width: 210mm;
      min-height: 297mm;
      margin: 0 auto 20px;
      padding: 18mm 15mm;
      background: var(--tds-surface);
      border-radius: 16px;
      box-shadow: 0 4px 24px rgba(25, 31, 40, 0.06);
    }}
    /* Hide pages not matching active level */
    body[data-active-level="N5"] .page:not([data-level="N5"]) {{ display: none; }}
    body[data-active-level="N4"] .page:not([data-level="N4"]) {{ display: none; }}
    body[data-active-level="N3"] .page:not([data-level="N3"]) {{ display: none; }}
    body[data-active-level="N2"] .page:not([data-level="N2"]) {{ display: none; }}
    body[data-active-level="N1"] .page:not([data-level="N1"]) {{ display: none; }}
  }}

  @media print {{
    .toolbar {{ display: none; }}
  }}

  .header {{
    display: flex;
    align-items: baseline;
    gap: 12pt;
    border-bottom: 1.5px solid var(--tds-divider);
    padding-bottom: 5mm;
    margin-bottom: 8mm;
  }}
  .jlpt-badge {{
    display: inline-block;
    font-size: 18pt; font-weight: 800;
    padding: 4pt 12pt;
    border-radius: 8pt;
    color: #fff;
    letter-spacing: 0px;
    line-height: 1;
  }}
  .jlpt-n5 {{ background: var(--tds-green); }}
  .jlpt-n4 {{ background: #20C997; }}
  .jlpt-n3 {{ background: var(--tds-orange); }}
  .jlpt-n2 {{ background: var(--tds-red); }}
  .jlpt-n1 {{ background: var(--tds-purple); }}
  .subtitle {{ font-size: 11pt; color: var(--tds-medium); font-weight: 500; }}

  .rows {{ display: flex; flex-direction: column; gap: 5mm; }}

  .row {{ page-break-inside: avoid; }}
  .row-label {{
    display: flex;
    align-items: baseline;
    gap: 5pt;
    margin-bottom: 1.8mm;
    font-size: 10.5pt;
    line-height: 1.3;
    color: var(--tds-strong);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }}
  .rl-reading {{ font-weight: 700; color: var(--tds-strong); }}
  .rl-meaning {{ color: var(--tds-medium); text-transform: capitalize; }}
  .rl-korean  {{ color: var(--tds-blue); font-weight: 700; }}
  .rl-sep     {{ color: var(--tds-weak); opacity: 0.5; }}

  .cells {{
    display: grid;
    grid-template-columns: repeat(10, 1fr);
    gap: 1.5mm;
  }}
  .cell {{ display: flex; align-items: center; justify-content: center; }}
  .svg-wrap {{
    width: 100%;
    aspect-ratio: 1 / 1;
    border: 1.2px solid var(--tds-divider);
    border-radius: 6px;
    background: var(--tds-surface);
    padding: 1mm;
    overflow: hidden;
  }}
  svg {{ width: 100%; height: 100%; display: block; }}

  .cross {{
    stroke: var(--tds-divider);
    stroke-width: 0.5;
    stroke-dasharray: 2,2;
    opacity: 0.8;
    fill: none;
  }}
  .trace {{
    stroke: var(--tds-strong);
    stroke-width: 3.2;
    fill: none;
    stroke-linecap: round;
    stroke-linejoin: round;
    opacity: 0.18;
  }}
</style>
</head>
<body data-active-level="N5">

<nav class="toolbar">
  <div class="toolbar-inner">
    <div class="brand">JLPT 받아쓰기 <a href="./">← 워크북 목록</a></div>
    <div class="tabs">
      {tab_buttons}
      <button class="tab tab-print" type="button" onclick="window.print()">
        <span class="tab-label">인쇄</span>
        <span class="tab-meta">전체</span>
      </button>
    </div>
  </div>
</nav>

{symbols_block}

{pages_html}

<script>
  const body = document.body;
  document.querySelectorAll('.tab[data-level]').forEach(btn => {{
    btn.addEventListener('click', () => {{
      const lv = btn.dataset.level;
      body.setAttribute('data-active-level', lv);
      document.querySelectorAll('.tab[data-level]').forEach(b => b.classList.toggle('active', b === btn));
      window.scrollTo({{ top: 0, behavior: 'instant' }});
    }});
  }});
  // Init default active tab
  const initial = body.getAttribute('data-active-level') || 'N5';
  const initBtn = document.querySelector(`.tab[data-level="${{initial}}"]`);
  if (initBtn) initBtn.classList.add('active');
</script>

</body>
</html>
"""

OUT_HTML.write_text(HTML, encoding="utf-8")
print(f"Wrote {OUT_HTML}")
print(f"Total: {total_kanji} kanji, {total_pages} pages")
for j in ["N5","N4","N3","N2","N1"]:
    n = len(by_jlpt.get(j, []))
    print(f"  {j}: {n} kanji, {level_page_counts[j]} pages")
