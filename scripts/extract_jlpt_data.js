// Extract all JLPT kanji (N5→N1) with reading, meaning
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
function unicodeHex(ch) {
  return ch.codePointAt(0).toString(16).padStart(5, '0');
}

const seen = new Set();
const result = [];
for (const lvl of ['n5','n4','n3','n2','n1']) {
  for (const ch of kanji.jlpt[lvl]()) {
    if (seen.has(ch)) continue;
    seen.add(ch);
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
      jlpt: lvl.toUpperCase(),
      reading,
      meaning,
    });
  }
}

const outPath = path.join(__dirname, '..', 'jlpt-data.json');
fs.writeFileSync(outPath, JSON.stringify(result, null, 2), 'utf-8');
console.log('Wrote', outPath, '—', result.length, 'kanji');
const counts = {};
for (const k of result) counts[k.jlpt] = (counts[k.jlpt] || 0) + 1;
console.log('Counts:', counts);
