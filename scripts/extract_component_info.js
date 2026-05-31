// Generate component-info.json — one entry per unique kvg:element across all
// 2,136 JLPT kanji, with Japanese readings, Korean hun-eum, English meaning,
// and per-JLPT frequency stats. Used by the admin page to let the user pick
// emojis with full context.

const fs = require('fs');
const path = require('path');
const kanjidic = require('kanjidic');
const hanjadict = require('@seyoungsong/hanjadict');

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
  '⻖': '阜',
  '⻏': '邑',
  '⻊': '足',
};

function toHiragana(s) {
  if (!s) return '';
  return s.replace(/[ァ-ヶ]/g, c => String.fromCharCode(c.charCodeAt(0) - 0x60));
}
function cleanReading(r) { return (r || '').replace(/[.\-]/g, ''); }
function firstHuneum(s) { return (s || '').split(',')[0].trim(); }

const GAME_DATA = JSON.parse(
  fs.readFileSync(path.join(__dirname, '..', 'kanji-game-data.json'), 'utf-8')
);

// Build component → { freq by jlpt, total }
const stats = {};
for (const k of GAME_DATA) {
  const seen = new Set();
  for (const c of k.components) {
    const e = c.element;
    if (seen.has(e)) continue;
    seen.add(e);
    if (!stats[e]) stats[e] = { byLevel: {N5:0,N4:0,N3:0,N2:0,N1:0}, total: 0 };
    stats[e].byLevel[k.jlpt]++;
    stats[e].total++;
  }
}

const result = {};
for (const elem of Object.keys(stats)) {
  const canonical = VARIANT_TO_CANONICAL[elem] || elem;
  const dic = kanjidic.lookup(canonical) || {};
  const kun = (dic.kunyomi || []).filter(Boolean).map(cleanReading);
  const on  = (dic.onyomi  || []).filter(Boolean).map(toHiragana);
  const meanings = dic.meaning || [];
  let huneum = firstHuneum(hanjadict.lookup(elem));
  if (!huneum && canonical !== elem) huneum = firstHuneum(hanjadict.lookup(canonical));
  result[elem] = {
    canonical: canonical !== elem ? canonical : '',
    kun,
    on,
    meanings: meanings.slice(0, 4),
    huneum: huneum || '',
    freq: stats[elem].byLevel,
    total: stats[elem].total,
  };
}

const outPath = path.join(__dirname, '..', 'component-info.json');
fs.writeFileSync(outPath, JSON.stringify(result, null, 0), 'utf-8');
console.log(`Wrote ${outPath}: ${Object.keys(result).length} components`);
console.log('Samples:');
for (const e of ['人','亻','馬','水','氵','心','忄','十','一','大','八','立','戈']) {
  const r = result[e];
  if (r) console.log(' ', e, JSON.stringify(r));
}
