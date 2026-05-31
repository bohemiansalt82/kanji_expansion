// Extract Kyoiku Kanji data: grade, kana reading, JLPT, English meaning, radical
const fs = require('fs');
const path = require('path');
const kanji = require('kanji');
const kanjidic = require('kanjidic');

function toHiragana(s) {
  if (!s) return '';
  return s.replace(/[ァ-ヶ]/g, c =>
    String.fromCharCode(c.charCodeAt(0) - 0x60)
  );
}
function cleanReading(r) {
  if (!r) return '';
  return r.replace(/[.\-]/g, '');
}

const jlptMap = new Map();
for (const lvl of ['n5', 'n4', 'n3', 'n2', 'n1']) {
  for (const ch of kanji.jlpt[lvl]()) {
    if (!jlptMap.has(ch)) jlptMap.set(ch, lvl.toUpperCase());
  }
}

function unicodeHex(ch) {
  return ch.codePointAt(0).toString(16).padStart(5, '0');
}

const result = [];
for (let g = 1; g <= 6; g++) {
  const list = kanji.grade['g0' + g]();
  for (const ch of list) {
    const dic = kanjidic.lookup(ch) || {};
    const kun = (dic.kunyomi || []).filter(Boolean);
    const on = (dic.onyomi || []).filter(Boolean);
    let reading = '';
    if (kun.length) reading = cleanReading(kun[0]);
    else if (on.length) reading = toHiragana(on[0]);
    const meanings = dic.meaning || [];
    const meaning = meanings.length ? meanings[0] : '';
    result.push({
      ch,
      code: unicodeHex(ch),
      grade: g,
      reading,
      jlpt: jlptMap.get(ch) || '',
      meaning,
      radical: dic.radicalNumber || null,
      strokes: (dic.strokeCount && dic.strokeCount[0]) || null,
    });
  }
}

const outPath = path.join(__dirname, '..', 'kanji-data.json');
fs.writeFileSync(outPath, JSON.stringify(result, null, 2), 'utf-8');
console.log('Wrote', outPath, '—', result.length, 'kanji');
