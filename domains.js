/* ═══════════════════════════════════════════════════════════════
   Domain Registry
   Add a new object here to register a new learning domain.
   Change status to "snoozed" to hide a domain from the queue.
═══════════════════════════════════════════════════════════════ */

const DOMAINS = [
  {
    id:       'ibm',
    name:     'IBM AI Engineering',
    icon:     '🤖',
    status:   'active',       // 'active' | 'snoozed' | 'done'
    color:    '#2563eb',
    deadline: '2026-09-01',
    prize:    'Nintendo Switch 2 + Pokopia',
    deck:     'data/decks/ibm.json',
    hub:      'ibm/index.html',
    audio:    false,
    newPerDay: 10
  },
  {
    id:        'swedish',
    name:      'Swedish',
    icon:      '🫎',
    status:    'active',
    color:     '#16a34a',
    deck:      'data/decks/swedish.json',
    hub:       'swedish/index.html',
    audio:     true,
    audioLang: 'sv-SE',
    newPerDay: 20
  }
];
