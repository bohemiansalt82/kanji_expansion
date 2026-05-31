# 한자 확장술 (Kanji Expansion Workbooks)

KanjiVG 획 데이터를 기반으로 한자의 부수가 어떻게 결합하여 새 글자를 만드는지 시각적으로 보여주는 인쇄용 워크북. A4 출력에 맞춰 디자인되었으며, 각 셀에서 **섹션 부수의 획은 진하게**, 나머지 결합 획은 연하게 표시됩니다.

[**📘 GitHub Pages에서 보기**](https://bohemiansalt82.github.io/kanji_expansion/)

## 워크북

| 파일 | 페이지 | 글자 수 | 설명 |
|---|---|---|---|
| `hanja_expansion_jin.html` | 2 | 40 | 人 / 亻 부수 확장 |
| `kanji_expansion_workbook.html` | 180 | 1,006 | 교육한자 전체, 강희 부수별 그룹화 |
| `kyoiku_kanji_workbook.html` | 52 | 1,006 | 교육한자 학년별 정리 |

각 글자에는 히라가나 훈독, JLPT 등급 배지(N5–N1), 영어 뜻이 함께 표시됩니다.

## 빌드 방법

```bash
# 의존성 설치 (npm 패키지)
mkdir .kdata && cd .kdata
npm install @madcat/kanjivg kanjivg-js kanji kanjidic
cd ..

# 한자 데이터 추출 (kanji-data.json 생성)
node scripts/extract_kanji_data.js

# HTML 워크북 생성
python3 scripts/build_hanja_html.py
python3 scripts/build_kyoiku_workbook.py
python3 scripts/build_expansion_workbook.py
```

## 데이터 출처

- **획 데이터**: [KanjiVG](https://kanjivg.tagaini.net/) (CC BY-SA 3.0)
- **한자 메타데이터**: [kanji](https://www.npmjs.com/package/kanji), [kanjidic](https://www.npmjs.com/package/kanjidic) npm 패키지

## 기술 노트

부수 식별은 `kanjidic`의 `radicalNumber`(Nelson 분류)와 KanjiVG의 `kvg:element` 속성을 매칭합니다. 좌/우 양쪽에 쓰이는 阝(邑/阜)는 `kvg:position`으로 구분합니다. 변형 부수(亻=人, 氵=水, 扌=手, 灬=火 등)는 `VARIANTS` 테이블에서 정의되어 있습니다.

## 라이센스

코드 MIT, 데이터(KanjiVG) CC BY-SA 3.0.
