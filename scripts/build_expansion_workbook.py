#!/usr/bin/env python3
"""Build kanji-expansion workbook from RICH KanjiVG data.
Uses kvg:radical metadata to correctly identify radical strokes
regardless of position (left, right, top, bottom, surround).
"""
import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
RICH_KVG_DIR = ROOT / ".kdata/node_modules/kanjivg-js/kanji"
DATA_PATH = ROOT / "kanji-data.json"
OUT_HTML = ROOT / "kanji_expansion_workbook.html"

CELLS_PER_PAGE = 20
KVG_NS = "http://kanjivg.tagaini.net"

# 214 Kangxi radicals: number → (display char, stroke count)
KANGXI = {
    1: ("一",1), 2: ("丨",1), 3: ("丶",1), 4: ("丿",1), 5: ("乙",1), 6: ("亅",1),
    7: ("二",2), 8: ("亠",2), 9: ("人",2), 10: ("儿",2), 11: ("入",2), 12: ("八",2),
    13: ("冂",2), 14: ("冖",2), 15: ("冫",2), 16: ("几",2), 17: ("凵",2), 18: ("刀",2),
    19: ("力",2), 20: ("勹",2), 21: ("匕",2), 22: ("匚",2), 23: ("匸",2), 24: ("十",2),
    25: ("卜",2), 26: ("卩",2), 27: ("厂",2), 28: ("厶",2), 29: ("又",2),
    30: ("口",3), 31: ("囗",3), 32: ("土",3), 33: ("士",3), 34: ("夂",3), 35: ("夊",3),
    36: ("夕",3), 37: ("大",3), 38: ("女",3), 39: ("子",3), 40: ("宀",3), 41: ("寸",3),
    42: ("小",3), 43: ("尢",3), 44: ("尸",3), 45: ("屮",3), 46: ("山",3), 47: ("巛",3),
    48: ("工",3), 49: ("己",3), 50: ("巾",3), 51: ("干",3), 52: ("幺",3), 53: ("广",3),
    54: ("廴",3), 55: ("廾",3), 56: ("弋",3), 57: ("弓",3), 58: ("彐",3), 59: ("彡",3),
    60: ("彳",3),
    61: ("心",4), 62: ("戈",4), 63: ("戶",4), 64: ("手",4), 65: ("支",4), 66: ("攴",4),
    67: ("文",4), 68: ("斗",4), 69: ("斤",4), 70: ("方",4), 71: ("无",4), 72: ("日",4),
    73: ("曰",4), 74: ("月",4), 75: ("木",4), 76: ("欠",4), 77: ("止",4), 78: ("歹",4),
    79: ("殳",4), 80: ("毋",4), 81: ("比",4), 82: ("毛",4), 83: ("氏",4), 84: ("气",4),
    85: ("水",4), 86: ("火",4), 87: ("爪",4), 88: ("父",4), 89: ("爻",4), 90: ("爿",4),
    91: ("片",4), 92: ("牙",4), 93: ("牛",4), 94: ("犬",4),
    95: ("玄",5), 96: ("玉",5), 97: ("瓜",5), 98: ("瓦",5), 99: ("甘",5), 100: ("生",5),
    101: ("用",5), 102: ("田",5), 103: ("疋",5), 104: ("疒",5), 105: ("癶",5), 106: ("白",5),
    107: ("皮",5), 108: ("皿",5), 109: ("目",5), 110: ("矛",5), 111: ("矢",5), 112: ("石",5),
    113: ("示",5), 114: ("禸",5), 115: ("禾",5), 116: ("穴",5), 117: ("立",5),
    118: ("竹",6), 119: ("米",6), 120: ("糸",6), 121: ("缶",6), 122: ("网",6), 123: ("羊",6),
    124: ("羽",6), 125: ("老",6), 126: ("而",6), 127: ("耒",6), 128: ("耳",6), 129: ("聿",6),
    130: ("肉",6), 131: ("臣",6), 132: ("自",6), 133: ("至",6), 134: ("臼",6), 135: ("舌",6),
    136: ("舛",6), 137: ("舟",6), 138: ("艮",6), 139: ("色",6), 140: ("艸",6), 141: ("虍",6),
    142: ("虫",6), 143: ("血",6), 144: ("行",6), 145: ("衣",6), 146: ("襾",6),
    147: ("見",7), 148: ("角",7), 149: ("言",7), 150: ("谷",7), 151: ("豆",7), 152: ("豕",7),
    153: ("豸",7), 154: ("貝",7), 155: ("赤",7), 156: ("走",7), 157: ("足",7), 158: ("身",7),
    159: ("車",7), 160: ("辛",7), 161: ("辰",7), 162: ("辵",7), 163: ("邑",7), 164: ("酉",7),
    165: ("釆",7), 166: ("里",7),
    167: ("金",8), 168: ("長",8), 169: ("門",8), 170: ("阜",8), 171: ("隶",8), 172: ("隹",8),
    173: ("雨",8), 174: ("靑",8), 175: ("非",8),
    176: ("面",9), 177: ("革",9), 178: ("韋",9), 179: ("韭",9), 180: ("音",9), 181: ("頁",9),
    182: ("風",9), 183: ("飛",9), 184: ("食",9), 185: ("首",9), 186: ("香",9),
    187: ("馬",10), 188: ("骨",10), 189: ("高",10), 190: ("髟",10), 191: ("鬥",10),
    192: ("鬯",10), 193: ("鬲",10), 194: ("鬼",10),
    195: ("魚",11), 196: ("鳥",11), 197: ("鹵",11), 198: ("鹿",11), 199: ("麥",11), 200: ("麻",11),
    201: ("黃",12), 202: ("黍",12), 203: ("黑",12), 204: ("黹",12),
    205: ("黽",13), 206: ("鼎",13), 207: ("鼓",13), 208: ("鼠",13),
    209: ("鼻",14), 210: ("齊",14),
    211: ("齒",15),
    212: ("龍",16), 213: ("龜",16),
    214: ("龠",17),
}

RADICAL_KR = {
    1:"한 일", 2:"뚫을 곤", 3:"점 주", 4:"삐침", 5:"새 을", 6:"갈고리 궐",
    7:"두 이", 8:"돼지해머리", 9:"사람 인", 10:"어진사람 인", 11:"들 입", 12:"여덟 팔",
    13:"멀 경", 14:"덮을 멱", 15:"얼음 빙", 16:"안석 궤", 17:"입벌릴 감", 18:"칼 도",
    19:"힘 력", 20:"쌀 포", 21:"비수 비", 22:"상자 방", 23:"감출 혜", 24:"열 십",
    25:"점 복", 26:"병부 절", 27:"기슭 한", 28:"마늘모", 29:"또 우",
    30:"입 구", 31:"에울 위", 32:"흙 토", 33:"선비 사", 34:"뒤져올 치", 35:"천천히걸을 쇠",
    36:"저녁 석", 37:"큰 대", 38:"여자 녀", 39:"아들 자", 40:"갓머리", 41:"마디 촌",
    42:"작을 소", 43:"절름발이 왕", 44:"주검 시", 45:"왼손 좌", 46:"뫼 산", 47:"개미허리",
    48:"장인 공", 49:"몸 기", 50:"수건 건", 51:"방패 간", 52:"작을 요", 53:"엄호 밑",
    54:"민책받침", 55:"받들 공", 56:"주살 익", 57:"활 궁", 58:"튼가로왈", 59:"터럭 삼",
    60:"두인변",
    61:"마음 심", 62:"창 과", 63:"지게 호", 64:"손 수", 65:"지탱할 지", 66:"등글월문",
    67:"글월 문", 68:"말 두", 69:"도끼 근", 70:"모 방", 71:"이미기방", 72:"날 일",
    73:"가로 왈", 74:"달 월", 75:"나무 목", 76:"하품 흠", 77:"그칠 지", 78:"죽을사변",
    79:"창 수", 80:"말 무", 81:"견줄 비", 82:"털 모", 83:"성씨 씨", 84:"기운 기",
    85:"물 수", 86:"불 화", 87:"손톱 조", 88:"아비 부", 89:"점괘 효", 90:"장수장변",
    91:"조각 편", 92:"어금니 아", 93:"소 우", 94:"개사슴록변",
    95:"검을 현", 96:"구슬 옥", 97:"오이 과", 98:"기와 와", 99:"달 감", 100:"날 생",
    101:"쓸 용", 102:"밭 전", 103:"발 소", 104:"병질엄", 105:"필발머리", 106:"흰 백",
    107:"가죽 피", 108:"그릇 명", 109:"눈 목", 110:"창 모", 111:"화살 시", 112:"돌 석",
    113:"보일시변", 114:"짐승발자국 유", 115:"벼 화", 116:"구멍 혈", 117:"설 립",
    118:"대 죽", 119:"쌀 미", 120:"실 사", 121:"장군 부", 122:"그물 망", 123:"양 양",
    124:"깃 우", 125:"늙을 로", 126:"말이을 이", 127:"쟁기 뢰", 128:"귀 이", 129:"붓 율",
    130:"고기 육", 131:"신하 신", 132:"스스로 자", 133:"이를 지", 134:"절구 구", 135:"혀 설",
    136:"어그러질 천", 137:"배 주", 138:"머무를 간", 139:"빛 색", 140:"초두머리", 141:"범호엄",
    142:"벌레 충", 143:"피 혈", 144:"다닐 행", 145:"옷 의", 146:"덮을 아",
    147:"볼 견", 148:"뿔 각", 149:"말씀 언", 150:"골 곡", 151:"콩 두", 152:"돼지 시",
    153:"발없는벌레 치", 154:"조개 패", 155:"붉을 적", 156:"달릴 주", 157:"발 족",
    158:"몸 신", 159:"수레 거", 160:"매울 신", 161:"별 진", 162:"책받침", 163:"우부방",
    164:"닭 유", 165:"분별할 변", 166:"마을 리",
    167:"쇠 금", 168:"긴 장", 169:"문 문", 170:"좌부변", 171:"미칠 이", 172:"새 추",
    173:"비 우", 174:"푸를 청", 175:"아닐 비",
    176:"낯 면", 177:"가죽 혁", 178:"가죽 위", 179:"부추 구", 180:"소리 음", 181:"머리 혈",
    182:"바람 풍", 183:"날 비", 184:"먹을 식", 185:"머리 수", 186:"향기 향",
    187:"말 마", 188:"뼈 골", 189:"높을 고", 190:"머리털드리워질 표", 191:"싸울 투",
    192:"울창주 창", 193:"오지병 력", 194:"귀신 귀",
    195:"물고기 어", 196:"새 조", 197:"소금밭 로", 198:"사슴 록", 199:"보리 맥", 200:"삼 마",
    201:"누를 황", 202:"기장 서", 203:"검을 흑", 204:"수놓을 치",
    205:"맹꽁이 맹", 206:"솥 정", 207:"북 고", 208:"쥐 서",
    209:"코 비", 210:"가지런할 제",
    211:"이 치",
    212:"용 룡", 213:"거북 귀",
    214:"피리 약",
}

# SVG namespace for tag stripping
SVG_NS = "http://www.w3.org/2000/svg"

# Variant forms of radicals: when a Kangxi radical appears in compound kanji,
# KanjiVG sometimes labels it with a simplified/variant element name.
# Map: Kangxi radical # → list of acceptable kvg:element values (incl. the canonical char).
VARIANTS = {
    1:  ["一"],
    6:  ["亅"],
    8:  ["亠"],
    9:  ["人", "亻", "⺅"],
    10: ["儿"],
    11: ["入"],
    12: ["八", "丷"],
    13: ["冂"],
    14: ["冖"],
    15: ["冫"],
    18: ["刀", "刂"],
    19: ["力"],
    24: ["十"],
    27: ["厂"],
    30: ["口"],
    31: ["囗"],
    32: ["土", "圡"],
    37: ["大"],
    38: ["女"],
    39: ["子"],
    40: ["宀"],
    41: ["寸"],
    46: ["山"],
    50: ["巾"],
    53: ["广"],
    60: ["彳"],
    61: ["心", "忄", "⺗"],
    62: ["戈"],
    64: ["手", "扌", "龵"],
    66: ["攴", "攵"],
    72: ["日"],
    74: ["月"],
    75: ["木"],
    79: ["殳"],
    85: ["水", "氵", "氺", "⺡"],
    86: ["火", "灬"],
    93: ["牛"],
    94: ["犬", "犭"],
    96: ["玉", "王"],
    100: ["生"],
    102: ["田"],
    104: ["疒"],
    109: ["目"],
    113: ["示", "礻"],
    115: ["禾"],
    116: ["穴"],
    117: ["立"],
    118: ["竹", "⺮"],
    119: ["米"],
    120: ["糸", "纟"],
    122: ["网", "罒", "⺲"],
    123: ["羊"],
    128: ["耳"],
    130: ["肉", "月", "⺝"],
    140: ["艸", "艹", "⺾", "⺿"],
    142: ["虫"],
    144: ["行"],
    145: ["衣", "衤"],
    147: ["見"],
    149: ["言", "讠"],
    154: ["貝"],
    157: ["足"],
    159: ["車"],
    162: ["辵", "辶", "⻌"],
    163: ["邑", "阝"],
    164: ["酉"],
    167: ["金", "釒"],
    169: ["門"],
    170: ["阜", "阝"],
    172: ["隹"],
    173: ["雨"],
    181: ["頁"],
    184: ["食", "飠"],
    187: ["馬"],
    195: ["魚"],
    196: ["鳥"],
}

# 阝 is shared between 邑 (right) and 阜 (left). Disambiguate by kvg:position.
LEFT_RIGHT_AMBIG = {
    163: "right",  # 邑 → right 阝
    170: "left",   # 阜 → left 阝
}

def acceptable_elements(rad_num):
    if rad_num in VARIANTS:
        return VARIANTS[rad_num]
    if rad_num in KANGXI:
        return [KANGXI[rad_num][0]]
    return []

def parse_kvg(code, rad_num):
    """Return (all_paths_in_order, radical_path_ids_set).

    Strategy:
    1) Match KanjiVG `<g>` whose `kvg:element` equals the section radical (or variant).
       For 阝-ambiguous radicals (163, 170), also check kvg:position.
    2) If no match, fall back to any group marked `kvg:radical="tradit"` or "general".
    3) If still no match, treat all strokes as the radical (kanji IS the radical).
    """
    p = RICH_KVG_DIR / f"{code}.svg"
    if not p.exists():
        return [], set()
    text = p.read_text(encoding="utf-8")
    text = re.sub(r'<!DOCTYPE.*?\]>', '', text, flags=re.DOTALL)
    text = re.sub(
        r'<svg\b([^>]*)>',
        r'<svg xmlns:kvg="http://kanjivg.tagaini.net"\1>',
        text, count=1
    )
    try:
        root = ET.fromstring(text)
    except ET.ParseError as e:
        print(f"Parse error for {code}: {e}")
        return [], set()

    all_paths = []
    for path in root.iter(f"{{{SVG_NS}}}path"):
        pid = path.get("id", "")
        d = path.get("d", "")
        if pid and d:
            all_paths.append((pid, d))

    elem_targets = set(acceptable_elements(rad_num))
    pos_constraint = LEFT_RIGHT_AMBIG.get(rad_num)

    # Step 1: element-match search
    matched_groups = []
    for g in root.iter(f"{{{SVG_NS}}}g"):
        elem = g.get(f"{{{KVG_NS}}}element")
        if elem and elem in elem_targets:
            if pos_constraint:
                pos = g.get(f"{{{KVG_NS}}}position")
                if pos != pos_constraint:
                    continue
            matched_groups.append(g)

    # Step 2: tradit/general fallback
    if not matched_groups:
        tradit = [g for g in root.iter(f"{{{SVG_NS}}}g")
                  if g.get(f"{{{KVG_NS}}}radical") == "tradit"]
        general = [g for g in root.iter(f"{{{SVG_NS}}}g")
                   if g.get(f"{{{KVG_NS}}}radical") == "general"]
        matched_groups = tradit or general

    rad_ids = set()
    for g in matched_groups:
        for path in g.iter(f"{{{SVG_NS}}}path"):
            pid = path.get("id", "")
            if pid:
                rad_ids.add(pid)

    # Step 3: if still nothing, mark all as radical
    if not rad_ids:
        rad_ids = {pid for pid, _ in all_paths}

    return all_paths, rad_ids


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
        yield seq[i:i+n]


def build_page(rad_char, rad_kr, rad_strokes, rad_num, page_idx, total_pages, kanji_list):
    cells = "\n\n".join(build_cell(k, rad_num) for k in kanji_list)
    page_label = f"{page_idx}/{total_pages}" if total_pages > 1 else ""
    return f"""<section class="page">
  <div class="header">
    <h1 class="title"><span class="root">{rad_char}</span></h1>
    <p class="subtitle">{rad_kr} · 부수 {rad_strokes}획 {page_label}</p>
  </div>

  <div class="grid">

{cells}

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

pages = []
for rad_num in sorted(by_rad.keys()):
    if rad_num not in KANGXI:
        continue
    rad_char, rad_strokes = KANGXI[rad_num]
    rad_kr = RADICAL_KR.get(rad_num, "")
    kanji_list = by_rad[rad_num]
    chunks = list(chunk(kanji_list, CELLS_PER_PAGE))
    for i, c in enumerate(chunks, 1):
        pages.append(build_page(rad_char, rad_kr, rad_strokes, rad_num, i, len(chunks), c))

pages_html = "\n\n".join(pages)
total_pages = len(pages)
total_kanji = sum(len(by_rad[r]) for r in by_rad if r in KANGXI)

HTML = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>한자 확장술 워크북 - 부수별 ({total_kanji}자)</title>
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

  .header {{ text-align: center; margin-bottom: 10mm; }}
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
</style>
</head>
<body>

{pages_html}

</body>
</html>
"""

OUT_HTML.write_text(HTML, encoding="utf-8")
print(f"Wrote {OUT_HTML}")
print(f"Total: {total_kanji} kanji, {total_pages} pages, {len(by_rad)} radicals")
