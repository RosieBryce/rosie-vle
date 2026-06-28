/* ═══════════════════════════════════════════════════════════════
   Gist Sync — cross-device progress sync via GitHub Gist
   Requires engine.js to be loaded first.

   Storage keys (localStorage):
     VLE_SYNC_TOKEN   — GitHub personal access token (gist scope)
     VLE_SYNC_GIST_ID — ID of the private Gist used for storage

   Public API:
     sync.isConfigured()       → bool
     sync.setup(token, gistId) → create/link Gist, returns { ok, gistId, error }
     sync.pull()               → fetch remote → merge into local, returns { ok, source }
     sync.push()               → write local → remote, returns { ok, error }
     sync.getStatus()          → { configured, lastPush, lastPull }
═══════════════════════════════════════════════════════════════ */

const sync = (() => {
  const TOKEN_KEY   = 'VLE_SYNC_TOKEN';
  const GIST_KEY    = 'VLE_SYNC_GIST_ID';
  const META_KEY    = 'VLE_SYNC_META';
  const FILE_NAME   = 'vle-progress.json';
  const API         = 'https://api.github.com';

  // ── Config ────────────────────────────────────────────────
  const getToken  = () => localStorage.getItem(TOKEN_KEY);
  const getGistId = () => localStorage.getItem(GIST_KEY);

  function isConfigured() {
    return !!(getToken() && getGistId());
  }

  function getMeta() {
    try { return JSON.parse(localStorage.getItem(META_KEY) || '{}'); }
    catch { return {}; }
  }

  function saveMeta(meta) {
    localStorage.setItem(META_KEY, JSON.stringify(meta));
  }

  // ── GitHub API helpers ────────────────────────────────────
  function headers() {
    return {
      'Authorization': `token ${getToken()}`,
      'Content-Type':  'application/json',
      'Accept':        'application/vnd.github+json'
    };
  }

  async function apiGet(url) {
    const res = await fetch(url, { headers: headers() });
    if (!res.ok) throw new Error(`GitHub API ${res.status}: ${await res.text()}`);
    return res.json();
  }

  async function apiPost(url, body) {
    const res = await fetch(url, { method: 'POST', headers: headers(), body: JSON.stringify(body) });
    if (!res.ok) throw new Error(`GitHub API ${res.status}: ${await res.text()}`);
    return res.json();
  }

  async function apiPatch(url, body) {
    const res = await fetch(url, { method: 'PATCH', headers: headers(), body: JSON.stringify(body) });
    if (!res.ok) throw new Error(`GitHub API ${res.status}: ${await res.text()}`);
    return res.json();
  }

  // ── Merge strategy: timestamp-based last-write-wins ───────
  // Progress objects include a `_ts` field (Unix ms).
  // Whichever is newer wins. For a single user on two devices
  // this is safe — the last device to study is authoritative.
  function stampedProgress() {
    const p = engine.getProgress();
    p._ts = Date.now();
    return p;
  }

  function mergeProgress(local, remote) {
    if (!remote || !remote._ts) return local;
    if (!local  || !local._ts)  return remote;
    return local._ts >= remote._ts ? local : remote;
  }

  // ── Setup ─────────────────────────────────────────────────
  // Call with a GitHub PAT (gist scope).
  // If gistId provided, links to existing Gist.
  // If not, creates a new private Gist.
  async function setup(token, existingGistId) {
    try {
      localStorage.setItem(TOKEN_KEY, token);

      if (existingGistId) {
        localStorage.setItem(GIST_KEY, existingGistId);
        // Verify it exists
        await apiGet(`${API}/gists/${existingGistId}`);
        return { ok: true, gistId: existingGistId };
      }

      // Create new Gist
      const progress = stampedProgress();
      const gist = await apiPost(`${API}/gists`, {
        description: 'Rosie VLE Progress (do not edit manually)',
        public: false,
        files: { [FILE_NAME]: { content: JSON.stringify(progress, null, 2) } }
      });

      localStorage.setItem(GIST_KEY, gist.id);
      saveMeta({ lastPush: new Date().toISOString() });
      return { ok: true, gistId: gist.id };

    } catch (e) {
      return { ok: false, error: e.message };
    }
  }

  // ── Pull ──────────────────────────────────────────────────
  async function pull() {
    if (!isConfigured()) return { ok: false, error: 'Sync not configured' };

    try {
      const gist = await apiGet(`${API}/gists/${getGistId()}`);
      const content = gist.files?.[FILE_NAME]?.content;

      if (!content) return { ok: true, source: 'local' };

      const remote = JSON.parse(content);
      const local  = engine.getProgress();
      const winner = mergeProgress(local, remote);

      // Write winner back to localStorage via engine's import
      engine.importJSON(JSON.stringify(winner));

      const meta = getMeta();
      meta.lastPull = new Date().toISOString();
      saveMeta(meta);

      return { ok: true, source: winner === remote ? 'remote' : 'local' };

    } catch (e) {
      return { ok: false, error: e.message };
    }
  }

  // ── Push ──────────────────────────────────────────────────
  async function push() {
    if (!isConfigured()) return { ok: false, error: 'Sync not configured' };

    try {
      const progress = stampedProgress();
      engine.importJSON(JSON.stringify(progress)); // save stamped version locally too

      await apiPatch(`${API}/gists/${getGistId()}`, {
        files: { [FILE_NAME]: { content: JSON.stringify(progress, null, 2) } }
      });

      const meta = getMeta();
      meta.lastPush = new Date().toISOString();
      saveMeta(meta);

      return { ok: true };

    } catch (e) {
      return { ok: false, error: e.message };
    }
  }

  // ── Status ────────────────────────────────────────────────
  function getStatus() {
    const meta = getMeta();
    return {
      configured: isConfigured(),
      gistId:     getGistId(),
      lastPush:   meta.lastPush || null,
      lastPull:   meta.lastPull || null,
    };
  }

  return { isConfigured, setup, pull, push, getStatus };
})();
