# 한자 확장술 (Kanji Expansion Workbooks)

KanjiVG 획 데이터를 기반으로 한자 학습용 인쇄 워크북. A4 출력에 맞춰 디자인되었으며, 워크북에 따라 부수 강조 또는 받아쓰기 연습용으로 사용 가능합니다.

[**📘 GitHub Pages에서 보기**](https://bohemiansalt82.github.io/kanji_expansion/)

## 워크북

| 파일 | 페이지 | 글자 수 | 설명 |
|---|---|---|---|
| `kanji_domain_workbook.html` | 185 | 1,006 | 의미 도메인별 정렬 (자연·인간·행위·사회·추상) |
| `kanji_expansion_workbook.html` | 180 | 1,006 | 강희 부수 번호 순 (一 → 龠) |
| `kyoiku_kanji_workbook.html` | 52 | 1,006 | 학년별 (초1~초6) |
| `jlpt_practice_workbook.html` | 269 | 2,136 | JLPT N5→N1 받아쓰기, 한 줄에 10번씩 반투명 |

## 의미 도메인 (Domain Workbook)

한자 설계자의 사고 체계를 따라 5개 카테고리로 분류:

| 도메인 | 부수 수 | 한자 수 | 대표 부수 |
|---|---|---|---|
| **자연** | 42 | 291 | 水 火 木 山 日 月 雨 風 牛 犬 鳥 魚 |
| **인간** | 34 | 200 | 人 女 子 心 手 目 口 耳 肉 骨 父 老 |
| **행위** | 33 | 164 | 言 走 行 足 見 食 刀 力 弓 矢 |
| **사회** | 30 | 188 | 宀 門 車 舟 金 玉 糸 衣 食 邑 |
| **추상** | 27 | 163 | 一 二 八 十 大 小 方 高 長 |

## 빌드 방법

```bash
mkdir .kdata && cd .kdata
npm install @madcat/kanjivg kanjivg-js kanji kanjidic hanja
cd ..

node scripts/extract_kanji_data.js
node scripts/extract_jlpt_data.js

python3 scripts/build_kyoiku_workbook.py
python3 scripts/build_expansion_workbook.py
python3 scripts/build_domain_workbook.py
python3 scripts/build_jlpt_practice.py
```

## 데이터 출처

- **획 데이터**: [KanjiVG](https://kanjivg.tagaini.net/) (CC BY-SA 3.0)
- **한자 메타데이터**: [kanji](https://www.npmjs.com/package/kanji), [kanjidic](https://www.npmjs.com/package/kanjidic), [hanja](https://www.npmjs.com/package/hanja) npm 패키지

## 라이센스

코드 MIT, 데이터(KanjiVG) CC BY-SA 3.0.
