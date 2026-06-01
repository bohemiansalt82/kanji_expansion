// Extract Korean 훈음 (hun-eum) for every character that appears in our
// kanji-game-data.json — both as a kanji itself and as a component.
// Output: char-huneum.json  (single map: { "馬": "말 마", "人": "사람 인", ... })

const fs = require('fs');
const path = require('path');
const hanjadict = require('@seyoungsong/hanjadict');

const DATA_PATH = path.join(__dirname, '..', 'kanji-game-data.json');
const OUT = path.join(__dirname, '..', 'char-huneum.json');

// Modern Korean overrides — hanjadict gives the ancient/etymological huneum
// for some characters (e.g. 社 → "토지신 사") that no modern learner uses.
// This table provides the commonly-known modern Korean reading instead.
const MODERN_HUNEUM = {
  '社':'모일 사',     // hanjadict: 토지신 사
  '式':'법 식',
  '院':'집 원',
  '党':'무리 당',
  '党':'무리 당',
  '区':'구분할 구',
  '元':'으뜸 원',
  '台':'대 대',
  '号':'이름 호',
  '広':'넓을 광',
  '当':'마땅할 당',
  '帰':'돌아갈 귀',
  '残':'남을 잔',
  '実':'열매 실',
  '対':'대할 대',
  '帯':'띠 대',
  '尽':'다할 진',
  '従':'좇을 종',
  '徳':'덕 덕',
  '済':'건널 제',
  '労':'일할 로',
  '営':'경영할 영',
  '巻':'책 권',
  '関':'관계할 관',
  '勧':'권할 권',
  '担':'멜 담',
  '挙':'들 거',
  '楽':'즐길 락',
  '権':'권세 권',
  '欧':'유럽 구',
  '歴':'지낼 력',
  '残':'남을 잔',
  '湿':'젖을 습',
  '焼':'사를 소',
  '営':'경영할 영',
  '献':'드릴 헌',
  '献':'드릴 헌',
  '画':'그림 화',
  '番':'차례 번',
  '発':'필 발',
  '皇':'임금 황',
  '禅':'고요할 선',
  '稼':'심을 가',
  '穏':'편안할 온',
  '突':'갑자기 돌',
  '窓':'창 창',
  '糸':'실 사',
  '緑':'푸를 록',
  '緒':'실마리 서',
  '罪':'허물 죄',
  '群':'무리 군',
  '聖':'성스러울 성',
  '能':'능할 능',
  '臓':'오장 장',
  '舗':'가게 포',
  '芸':'재주 예',
  '苦':'쓸 고',
  '草':'풀 초',
  '蔵':'감출 장',
  '行':'다닐 행',
  '装':'꾸밀 장',
  '裁':'마를 재',
  '製':'지을 제',
  '覚':'깨달을 각',
  '観':'볼 관',
  '誉':'기릴 예',
  '読':'읽을 독',
  '謝':'사례할 사',
  '譲':'사양할 양',
  '豊':'풍성할 풍',
  '質':'바탕 질',
  '購':'살 구',
  '転':'구를 전',
  '辞':'말씀 사',
  '農':'농사 농',
  '述':'펼 술',
  '進':'나아갈 진',
  '逐':'쫓을 축',
  '逓':'갈마들 체',
  '達':'통달할 달',
  '違':'어긋날 위',
  '遷':'옮길 천',
  '選':'가릴 선',
  '郵':'우편 우',
  '都':'도읍 도',
  '酸':'실 산',
  '醸':'술 빚을 양',
  '釈':'풀 석',
  '銭':'돈 전',
  '鋳':'쇠 부어 만들 주',
  '錠':'덩이 정',
  '鎌':'낫 겸',
  '鎮':'진정할 진',
  '鏡':'거울 경',
  '門':'문 문',
  '陥':'빠질 함',
  '陳':'베풀 진',
  '険':'험할 험',
  '陽':'볕 양',
  '随':'따를 수',
  '隔':'사이 뜰 격',
  '険':'험할 험',
  '雄':'수컷 웅',
  '雪':'눈 설',
  '雲':'구름 운',
  '霊':'신령 영',
  '青':'푸를 청',
  '静':'고요할 정',
  '面':'낯 면',
  '韓':'한국 한',
  '頭':'머리 두',
  '顕':'나타날 현',
  '類':'무리 류',
  '飯':'밥 반',
  '養':'기를 양',
  '香':'향기 향',
  '駐':'머무를 주',
  '騒':'떠들 소',
  '騰':'오를 등',
  '驚':'놀랄 경',
  '骨':'뼈 골',
  '髪':'터럭 발',
  '鬼':'귀신 귀',
  '鳴':'울 명',
  '鶴':'학 학',
  '黒':'검을 흑',
};

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

function cleanReading(s) {
  if (!s) return '';
  // Take only the first comma-separated reading
  let r = s.split(',')[0].trim();
  // Strip parenthetical alternations: "여자 녀(여)" → "여자 녀"
  r = r.replace(/\s*\([^)]*\)\s*/g, '').trim();
  // For slash alternations, keep the first: "클 대/큰 대" → "큰 대" (later) — actually take last as it's usually the modern form
  if (r.includes('/')) {
    const parts = r.split('/').map(s => s.trim()).filter(Boolean);
    // Heuristic: prefer the part that uses 큰/작은 modern forms over 클/작을
    r = parts[parts.length - 1] || parts[0];
  }
  return r;
}

function lookup(ch) {
  // Modern overrides take priority
  if (MODERN_HUNEUM[ch]) return MODERN_HUNEUM[ch];
  let r = hanjadict.lookup(ch);
  if (!r && VARIANT_TO_CANONICAL[ch]) {
    r = hanjadict.lookup(VARIANT_TO_CANONICAL[ch]);
  }
  return cleanReading(r) || '';
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
for (const ch of ['人','亻','馬','水','氵','心','忄','木','休','寺','介','思','一','亅','厶','社','女','大','行','寺','母']) {
  console.log(' ', ch, '→', map[ch] || '(none)');
}
