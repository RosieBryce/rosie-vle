/* ═══════════════════════════════════════════════════════════════
   SR Engine — SM-2 algorithm
   Storage key: VLE_PROGRESS (localStorage)

   Public API:
     engine.getProgress()             → full progress object
     engine.getDueCards(deck, domain) → cards due today + new cards
     engine.review(cardId, quality)   → update card after review (quality: 1|3|5)
     engine.addXP(amount, domainId)   → award XP
     engine.getStreak()               → { global, byDomain }
     engine.exportJSON()              → JSON string for backup/sync
     engine.importJSON(str)           → restore from JSON string
═══════════════════════════════════════════════════════════════ */

const engine = (() => {
  const STORAGE_KEY = 'VLE_PROGRESS';
  const DEFAULT_EASE = 2.5;
  const MIN_EASE = 1.3;

  // ── Helpers ────────────────────────────────────────────────
  function today() {
    return new Date().toISOString().slice(0, 10); // 'YYYY-MM-DD'
  }

  function addDays(dateStr, n) {
    const d = new Date(dateStr);
    d.setDate(d.getDate() + n);
    return d.toISOString().slice(0, 10);
  }

  function daysBetween(a, b) {
    return Math.round((new Date(b) - new Date(a)) / 86400000);
  }

  // ── Storage ────────────────────────────────────────────────
  function load() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : freshProgress();
    } catch {
      return freshProgress();
    }
  }

  function save(progress) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(progress));
  }

  function freshProgress() {
    return {
      xp:        0,
      lastStudy: null,
      streak:    0,
      domains:   {},
      sr:        {}        // cardId → { interval, ease, reps, due }
    };
  }

  function ensureDomain(progress, domainId) {
    if (!progress.domains[domainId]) {
      progress.domains[domainId] = { xp: 0, streak: 0, lastStudy: null, cardsReviewed: 0 };
    }
  }

  // ── SM-2 core ──────────────────────────────────────────────
  function sm2Update(card, quality) {
    // quality: 5 = Got it, 3 = Nearly, 1 = Missed
    let { interval = 0, ease = DEFAULT_EASE, reps = 0 } = card;

    if (quality >= 3) {
      if (reps === 0)      interval = 1;
      else if (reps === 1) interval = 6;
      else                 interval = Math.round(interval * ease);
      ease = ease + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02));
      ease = Math.max(MIN_EASE, ease);
      reps += 1;
    } else {
      reps = 0;
      interval = 1;
    }

    return { interval, ease: Math.round(ease * 1000) / 1000, reps, due: addDays(today(), interval) };
  }

  // ── Public API ─────────────────────────────────────────────
  function getProgress() {
    return load();
  }

  function getDueCards(deck, domain, maxNew = 20) {
    const progress = load();
    const t = today();
    const due   = [];
    const fresh = [];

    for (const card of deck) {
      const state = progress.sr[card.id];
      if (!state) {
        fresh.push(card);
      } else if (state.due <= t) {
        due.push({ ...card, _srState: state });
      }
    }

    // Shuffle fresh cards, take up to maxNew
    const shuffled = fresh.sort(() => Math.random() - 0.5).slice(0, maxNew);

    return { due, fresh: shuffled, total: due.length + shuffled.length };
  }

  function review(cardId, quality, domainId) {
    const progress = load();
    ensureDomain(progress, domainId);

    const existing = progress.sr[cardId] || { interval: 0, ease: DEFAULT_EASE, reps: 0 };
    const updated  = sm2Update(existing, quality);
    progress.sr[cardId] = updated;

    // XP
    const xpMap = { 5: 10, 3: 5, 1: 2 };
    const xpGain = xpMap[quality] || 2;
    progress.xp += xpGain;
    progress.domains[domainId].xp += xpGain;
    progress.domains[domainId].cardsReviewed += 1;

    // Streak
    const t = today();
    if (progress.lastStudy !== t) {
      const yesterday = addDays(t, -1);
      progress.streak = (progress.lastStudy === yesterday) ? progress.streak + 1 : 1;
      progress.lastStudy = t;
    }
    const dom = progress.domains[domainId];
    if (dom.lastStudy !== t) {
      const yesterday = addDays(t, -1);
      dom.streak = (dom.lastStudy === yesterday) ? dom.streak + 1 : 1;
      dom.lastStudy = t;
    }

    save(progress);
    return { xpGain, newState: updated };
  }

  function addXP(amount, domainId) {
    const progress = load();
    progress.xp += amount;
    if (domainId) {
      ensureDomain(progress, domainId);
      progress.domains[domainId].xp += amount;
    }
    save(progress);
  }

  function getStreak() {
    const p = load();
    return { global: p.streak || 0, byDomain: Object.fromEntries(
      Object.entries(p.domains).map(([k, v]) => [k, v.streak || 0])
    )};
  }

  function exportJSON() {
    return JSON.stringify(load(), null, 2);
  }

  function importJSON(str) {
    try {
      const data = JSON.parse(str);
      save(data);
      return true;
    } catch {
      return false;
    }
  }

  return { getProgress, getDueCards, review, addXP, getStreak, exportJSON, importJSON };
})();
