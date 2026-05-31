// Extract Korean 훈음 (hun-eum) for every character that appears in our
// kanji-game-data.json — both as a kanji itself and as a component.
// Output: char-huneum.json  (single map: { "馬": "말 마", "人": "사람 인", ... })

const fs = require('fs');
const path = require('path');
const hanjadict = require('@seyoungsong/hanjadict');

const DATA_PATH = path.join(__dirname, '..', 'kanji-game-data.json');
const OUT = path.join(__dirname, '..', 'char-huneum.json');

// Variant radical forms → canonical char (so we can look up 亻 via 人)
const VARIANT_TO_CANONICAL = {
  '亻': '人', '⺅': '人',
  '氵': '水', '氺': '水',
  '扌': '手',
  '忄': '心', '⺗': '心',
  '灬': '火',
  '犭': '犬',
  '衤': '衣',
  '⺝': '肉',
  '艹': '艸', '⺾': '艸', '⺿': '艸',
  '辶': '辵', '⻌': '辵',
  '讠': '言',
  '釒': '金',
  '纟': '糸',
  '飠': '食',
  '礻': '示',
  '⻁': '虍',
  '⺮': '竹',
  '罒': '网', '⺲': '网',
};

function firstReading(s) {
  if (!s) return '';
  return s.split(',')[0].trim();
}

function lookup(ch) {
  let r = hanjadict.lookup(ch);
  if (!r && VARIANT_TO_CANONICAL[ch]) {
    r = hanjadict.lookup(VARIANT_TO_CANONICAL[ch]);
  }
  return firstReading(r) || '';
}

const game = JSON.parse(fs.readFileSync(DATA_PATH, 'utf-8'));
const chars = new Set();
for (const k of game) {
  chars.add(k.ch);
  for (const c of k.components) {
    chars.add(c.element);
    if (c.original) chars.add(c.original);
  }
}

const map = {};
let found = 0;
for (const ch of chars) {
  const r = lookup(ch);
  if (r) { map[ch] = r; found++; }
}

fs.writeFileSync(OUT, JSON.stringify(map, null, 0), 'utf-8');
console.log(`Wrote ${OUT}: ${found}/${chars.size} chars have huneum`);
// Show samples
console.log('Samples:');
for (const ch of ['人','亻','馬','水','氵','心','忄','木','休','寺','介','思','一','亅','厶']) {
  console.log(' ', ch, '→', map[ch] || '(none)');
}
