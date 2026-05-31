#!/usr/bin/env python3
"""Build hanja expansion HTML from KanjiVG stroke data."""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
KVG_DIR = REPO / ".kdata/node_modules/@madcat/kanjivg/dist/main"
OUT_HTML = REPO / "hanja_expansion_jin.html"

# (code, char, reading_hiragana, meaning_en, jin_stroke_indices_1based, jlpt_level)
PAGE1 = [
    ("04eba", "人", "ひと",   "person",  [1, 2], "N5"),
    ("05165", "入", "いる",   "enter",   [1, 2], "N5"),
    ("0516b", "八", "や",     "eight",   [1, 2], "N5"),
    ("05927", "大", "おお",   "big",     [2, 3], "N5"),
    ("0706b", "火", "ひ",     "fire",    [3, 4], "N5"),
    ("05929", "天", "あめ",   "sky",     [3, 4], "N5"),
    ("0592b", "夫", "おっと", "husband", [3, 4], "N4"),
    ("0592a", "太", "ふとい", "thick",   [2, 3], "N3"),
    ("072ac", "犬", "いぬ",   "dog",     [2, 3], "N5"),
    ("0592e", "央", "おう",   "center",  [4, 5], "N3"),
    ("077e2", "矢", "や",     "arrow",   [4, 5], "N2"),
    ("05931", "失", "うしなう","lose",   [4, 5], "N3"),
    ("04ecb", "介", "かい",   "mediate", [1, 2], "N2"),
    ("04eca", "今", "いま",   "now",     [1, 2], "N5"),
    ("04ee4", "令", "れい",   "order",   [1, 2], "N3"),
    ("05168", "全", "まったく","all",    [1, 2], "N3"),
    ("05185", "内", "うち",   "inside",  [3, 4], "N4"),
    ("05408", "合", "あう",   "fit",     [1, 2], "N4"),
    ("04f1a", "会", "あう",   "meet",    [1, 2], "N5"),
    ("04f59", "余", "あまる", "surplus", [1, 2], "N3"),
]

# 亻 (사람인변) - 人 is always the first 2 strokes
PAGE2 = [
    ("04ec1", "仁", "にん",   "benevolence", [1, 2], "N1"),
    ("04ed5", "仕", "つかえる","serve",      [1, 2], "N4"),
    ("04ed6", "他", "ほか",   "other",       [1, 2], "N4"),
    ("04ee3", "代", "かわる", "replace",     [1, 2], "N4"),
    ("04ed8", "付", "つける", "attach",      [1, 2], "N4"),
    ("04efb", "任", "まかせる","entrust",    [1, 2], "N3"),
    ("04ef6", "件", "けん",   "matter",      [1, 2], "N3"),
    ("04f11", "休", "やすむ", "rest",        [1, 2], "N5"),
    ("04ef2", "仲", "なか",   "between",     [1, 2], "N3"),
    ("04f1d", "伝", "つたえる","convey",     [1, 2], "N4"),
    ("04f4d", "位", "くらい", "rank",        [1, 2], "N4"),
    ("04f53", "体", "からだ", "body",        [1, 2], "N4"),
    ("04f55", "何", "なに",   "what",        [1, 2], "N5"),
    ("04f5c", "作", "つくる", "make",        [1, 2], "N4"),
    ("04f7f", "使", "つかう", "use",         [1, 2], "N4"),
    ("04f8b", "例", "たとえ", "example",     [1, 2], "N3"),
    ("04fa1", "価", "か",     "value",       [1, 2], "N3"),
    ("04f8d", "侍", "さむらい","samurai",    [1, 2], "N1"),
    ("04fbf", "便", "べん",   "convenience", [1, 2], "N4"),
    ("04fe1", "信", "しん",   "trust",       [1, 2], "N3"),
]

PAGES = [
    ("漢字 拡張", "人", PAGE1, "기본 人 한자의 확장 — 진한 부분이 人, 연한 부분이 추가 획입니다."),
    ("漢字 拡張", "亻", PAGE2, "사람인변(亻) — 왼쪽의 亻이 人의 변형, 오른쪽이 결합되는 부분입니다."),
]

PATH_RE = re.compile(r'<path\s+id="kvg:([0-9a-f]+)-s(\d+)"\s+d="([^"]+)"\s*/>')

def extract_paths(code):
    """Return list of (stroke_index, d_attr) for a kanji."""
    svg_text = (KVG_DIR / f"{code}.svg").read_text(encoding="utf-8")
    return [(int(m.group(2)), m.group(3)) for m in PATH_RE.finditer(svg_text)]

def build_inner_svg(code, jin_indices):
    """Build inner SVG content: cross guide + paths classified as base/guide."""
    parts = [
        '<line class="cross" x1="54.5" y1="2" x2="54.5" y2="107"/>',
        '<line class="cross" x1="2" y1="54.5" x2="107" y2="54.5"/>',
    ]
    for idx, d in extract_paths(code):
        cls = "base" if idx in jin_indices else "guide"
        parts.append(f'<path class="{cls}" d="{d}"/>')
    return "\n        ".join(parts)

def build_cell(code, char, reading, meaning, jin_indices, jlpt):
    inner = build_inner_svg(code, jin_indices)
    return f"""  <div class="cell">
    <div class="cell-top">
      <span class="reading">{reading}</span>
      <span class="jlpt jlpt-{jlpt.lower()}">{jlpt}</span>
    </div>
    <div class="svg-wrap">
      <svg viewBox="0 0 109 109" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg">
        {inner}
      </svg>
    </div>
    <div class="meaning">{meaning}</div>
  </div>"""

def build_page(root, kanji_list, subtitle):
    cells = "\n\n".join(
        build_cell(code, char, reading, meaning, jin, jlpt)
        for code, char, reading, meaning, jin, jlpt in kanji_list
    )
    return f"""<section class="page">
  <div class="header">
    <h1 class="title"><span class="root">{root}</span></h1>
    <p class="subtitle">{subtitle}</p>
  </div>

  <div class="grid">

{cells}

  </div>
</section>"""

pages_html = "\n\n".join(build_page(r, kl, s) for _, r, kl, s in PAGES)

HTML = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>한자 확장 연습 - 人</title>
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

  /* 화면에서도 A4 사이즈 고정 */
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
    font-size: 40pt;
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
  }}
  .reading {{
    font-size: 11pt;
    font-weight: 600;
    color: #333;
    letter-spacing: 0.5px;
  }}
  .jlpt {{
    display: inline-block;
    font-size: 7.5pt;
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
  .base   {{ stroke: #000; stroke-width: 4.2; fill: none; stroke-linecap: round; stroke-linejoin: round; opacity: 1; }}
  .guide  {{ stroke: #c4c4c4; stroke-width: 3; fill: none; stroke-linecap: round; stroke-linejoin: round; }}

  .meaning {{
    font-size: 9.5pt;
    color: #666;
    margin-top: 1.5mm;
    letter-spacing: 0.3px;
    text-transform: capitalize;
  }}

  .footer {{
    margin-top: 10mm;
    font-size: 9.5pt;
    color: #555;
    text-align: center;
  }}
  .legend-swatch {{
    display: inline-block;
    width: 18pt;
    height: 4pt;
    background: #000;
    vertical-align: middle;
    margin-right: 4pt;
    border-radius: 2pt;
  }}
  .legend-swatch.faded {{ opacity: 0.22; }}
  .legend-item {{ margin: 0 12pt; }}
  .credit {{ margin-top: 3mm; font-size: 8pt; color: #999; }}
</style>
</head>
<body>

{pages_html}

</body>
</html>
"""

OUT_HTML.write_text(HTML, encoding="utf-8")
print(f"Wrote {OUT_HTML} ({len(HTML)} chars)")
print(f"Pages: {len(PAGES)}, total cells: {sum(len(kl) for _, _, kl, _ in PAGES)}")
