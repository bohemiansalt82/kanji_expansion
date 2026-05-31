# 한자 확장술 (Kanji Expansion Workbooks)

KanjiVG 획 데이터를 기반으로 한자 학습용 인쇄 워크북. A4 출력에 맞춰 디자인되었으며, 워크북에 따라 부수 강조 또는 받아쓰기 연습용으로 사용 가능합니다.

[**📘 GitHub Pages에서 보기**](https://bohemiansalt82.github.io/kanji_expansion/)

## 워크북

| 파일 | 페이지 | 글자 수 | 설명 |
|---|---|---|---|
| `kanji_expansion_workbook.html` | 180 | 1,006 | 교육한자 전체, 강희 부수별 그룹화. 섹션 부수 획만 진하게. |
| `kyoiku_kanji_workbook.html` | 52 | 1,006 | 교육한자 학년별 정리 (초1~초6). |
| `jlpt_practice_workbook.html` | 269 | 2,136 | JLPT N5→N1 받아쓰기 연습. 한 줄에 같은 한자 10번씩 반투명. |

## 빌드 방법

```bash
mkdir .kdata && cd .kdata
npm install @madcat/kanjivg kanjivg-js kanji kanjidic
cd ..

node scripts/extract_kanji_data.js
node scripts/extract_jlpt_data.js

python3 scripts/build_kyoiku_workbook.py
python3 scripts/build_expansion_workbook.py
python3 scripts/build_jlpt_practice.py
```

## 데이터 출처

- **획 데이터**: [KanjiVG](https://kanjivg.tagaini.net/) (CC BY-SA 3.0)
- **한자 메타데이터**: [kanji](https://www.npmjs.com/package/kanji), [kanjidic](https://www.npmjs.com/package/kanjidic) npm 패키지

## 기술 노트

부수 식별은 `kanjidic`의 `radicalNumber`(Nelson 분류)와 KanjiVG의 `kvg:element` 속성을 매칭합니다. 좌/우 양쪽에 쓰이는 阝(邑/阜)는 `kvg:position`으로 구분합니다. 변형 부수(亻=人, 氵=水, 扌=手, 灬=火 등)는 `VARIANTS` 테이블에서 정의되어 있습니다.

JLPT 받아쓰기 워크북은 SVG `<symbol>` + `<use>`로 한자당 한 번만 정의하여 파일 크기를 최소화합니다 (29MB → 5.8MB).

## 라이센스

코드 MIT, 데이터(KanjiVG) CC BY-SA 3.0.
