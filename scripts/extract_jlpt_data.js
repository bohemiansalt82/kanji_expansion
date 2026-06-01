// Extract all JLPT kanji (N5→N1) with reading, meaning, Korean (Hangul + 훈음)
const fs = require('fs');
const path = require('path');
const kanji = require('kanji');
const kanjidic = require('kanjidic');
const { default: hanja } = require('hanja');
const hanjadict = require('@seyoungsong/hanjadict');

// Re-use the same modern override + cleaning logic as extract_huneum.js
const MODERN_HUNEUM = JSON.parse(fs.readFileSync(
  path.join(__dirname, 'modern-huneum.json'), 'utf-8'
));
function cleanHuneum(s) {
  if (!s) return '';
  let r = s.split(',')[0].trim();
  r = r.replace(/\s*\([^)]*\)\s*/g, '').trim();
  if (r.includes('/')) {
    const parts = r.split('/').map(x => x.trim()).filter(Boolean);
    r = parts[parts.length - 1] || parts[0];
  }
  return r;
}
function huneumOf(ch) {
  if (MODERN_HUNEUM[ch]) return MODERN_HUNEUM[ch];
  return cleanHuneum(hanjadict.lookup(ch)) || '';
}

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
    // Full Korean 훈음 (e.g. "모일 사") — falls back to phonetic only if not found
    let korean = huneumOf(ch);
    if (!korean) {
      try {
        const h = hanja.translate(ch, 'SUBSTITUTION');
        if (h && h !== ch) korean = h;
      } catch (e) {}
    }
    // Combined reading: kun + on (on converted to hiragana), comma-separated
    const kunPart = kun.length ? cleanReading(kun[0]) : '';
    const onPart  = on.length  ? toHiragana(on[0])     : '';
    const readingFull = [kunPart, onPart].filter(Boolean).join('・');
    // Multiple English meanings (top 3) joined by ', '
    const meaningFull = (dic.meaning || []).slice(0, 5).join(', ');
    result.push({
      ch,
      code: unicodeHex(ch),
      jlpt: lvl.toUpperCase(),
      reading: readingFull || reading,   // kun・on (fallback to old single reading)
      meaning: meaningFull || meaning,   // top-3 meanings
      korean,
    });
  }
}

const outPath = path.join(__dirname, '..', 'jlpt-data.json');
fs.writeFileSync(outPath, JSON.stringify(result, null, 2), 'utf-8');
console.log('Wrote', outPath, '—', result.length, 'kanji');
const counts = {};
for (const k of result) counts[k.jlpt] = (counts[k.jlpt] || 0) + 1;
console.log('Counts:', counts);
