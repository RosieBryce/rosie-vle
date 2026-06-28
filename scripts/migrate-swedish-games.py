"""
Migrate Swedish games from Documents/Swedish 🫎/Tools/ to rosie-vle/swedish/games/
Steps per file:
  1. Copy HTML
  2. Fix data path: ../Words/flashcards.js → ../flashcards.js
  3. Apply light-mode token swap (dark Nord palette → paper-and-peaches)
  4. Swap nav: add "← Swedish" back link (inject after <body>)
  5. Add XP wiring (engine.js + sync.js scripts + addXP call at game end)
Also copies flashcards.js to rosie-vle/swedish/flashcards.js
"""

import os, re, shutil

SRC_TOOLS  = r"C:\Users\DELL\Documents\Swedish 🫎\Tools"
SRC_WORDS  = r"C:\Users\DELL\Documents\Swedish 🫎\Words"
DEST_GAMES = r"C:\Users\DELL\Documents\rosie-vle\swedish\games"
DEST_SV    = r"C:\Users\DELL\Documents\rosie-vle\swedish"
VLE_ROOT   = r"C:\Users\DELL\Documents\rosie-vle"

GAMES = [
    "daily-challenge.html",
    "quiz.html",
    "speed-round.html",
    "matching.html",
    "cloze.html",
    "hangman.html",
    "en-eller-ett.html",
    "conjugation.html",
    "adjective-agreement.html",
    "plurals.html",
    "word-order.html",
]

# Dark Nord tokens → light paper-and-peaches
COLOUR_MAP = {
    "--bg: #2e3440":    "--bg:#faf6f0",
    "--bg:#2e3440":     "--bg:#faf6f0",
    "--surface: #3b4252": "--surface:#ffffff",
    "--surface:#3b4252":  "--surface:#ffffff",
    "--surface2: #434c5e": "--surface2:#f2ece2",
    "--surface2:#434c5e":  "--surface2:#f2ece2",
    "--border: #4c566a": "--border:#e8ddd0",
    "--border:#4c566a":  "--border:#e8ddd0",
    "--text: #eceff4":  "--text:#2c1f12",
    "--text:#eceff4":   "--text:#2c1f12",
    "--muted: #d8dee9": "--muted:#8a7a68",
    "--muted:#d8dee9":  "--muted:#8a7a68",
    "--blue: #88c0d0":  "--blue:#b85430",
    "--blue:#88c0d0":   "--blue:#b85430",
    "--green: #a3be8c": "--green:#3d6e30",
    "--green:#a3be8c":  "--green:#3d6e30",
    "--red: #bf616a":   "--red:#b03428",
    "--red:#bf616a":    "--red:#b03428",
    "--yellow: #ebcb8b": "--yellow:#a06820",
    "--yellow:#ebcb8b":  "--yellow:#a06820",
    # Hardcoded hex values used inline
    "#2e3440": "#faf6f0",
    "#3b4252": "#ffffff",
    "#434c5e": "#f2ece2",
    "#4c566a": "#e8ddd0",
    "#eceff4": "#2c1f12",
    "#d8dee9": "#8a7a68",
    "#88c0d0": "#b85430",
    "#a3be8c": "#3d6e30",
    "#bf616a": "#b03428",
    "#ebcb8b": "#a06820",
}

NAV_SNIPPET = '''\n<nav style="background:var(--surface);border-bottom:1px solid var(--border);
  padding:0 1.25rem;height:48px;display:flex;align-items:center;gap:1rem;
  position:sticky;top:0;z-index:100;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <a href="../index.html" style="font-weight:700;font-size:.875rem;color:var(--text);text-decoration:none;">
    🫎 Swedish
  </a>
  <span style="color:var(--border)">›</span>
  <span style="font-size:.875rem;color:var(--muted)">GAME_NAME</span>
</nav>\n'''

XP_SCRIPTS = '''\n<script src="../../domains.js"></script>
<script src="../../sr/engine.js"></script>
<script src="../../sync.js"></script>
<script>
function swAddXP(amount) {
  if (amount <= 0) return;
  if (typeof engine !== 'undefined') engine.addXP(amount, 'swedish');
  if (typeof sync   !== 'undefined' && sync.isConfigured()) sync.push().catch(function(){});
  // Toast
  var el = document.getElementById('xp-toast-sw');
  if (!el) {
    el = document.createElement('div');
    el.id = 'xp-toast-sw';
    el.style.cssText = 'position:fixed;bottom:1.5rem;right:1rem;background:#b85430;color:#fff;'
      + 'padding:.45rem .9rem;border-radius:8px;font-size:.85rem;font-weight:700;'
      + 'opacity:0;transition:opacity .25s;pointer-events:none;z-index:9999;';
    document.body.appendChild(el);
  }
  el.textContent = '+' + amount + ' XP';
  el.style.opacity = '1';
  setTimeout(function() { el.style.opacity = '0'; }, 2200);
}
</script>\n'''

def game_display_name(filename):
    names = {
        "daily-challenge.html": "Daily Challenge",
        "quiz.html":            "Quiz",
        "speed-round.html":     "Speed Round",
        "matching.html":        "Matching",
        "cloze.html":           "Cloze",
        "hangman.html":         "Hangman",
        "en-eller-ett.html":    "En eller ett?",
        "conjugation.html":     "Conjugation",
        "adjective-agreement.html": "Adjective Agreement",
        "plurals.html":         "Plurals",
        "word-order.html":      "Word Order",
    }
    return names.get(filename, filename)

os.makedirs(DEST_GAMES, exist_ok=True)

# ── 1. Copy flashcards.js ─────────────────────────────────────
src_fc = os.path.join(SRC_WORDS, "flashcards.js")
dst_fc = os.path.join(DEST_SV,   "flashcards.js")
shutil.copy2(src_fc, dst_fc)
print(f"  copied: flashcards.js ({os.path.getsize(dst_fc)//1024}KB)")

# ── 2. Process each game ──────────────────────────────────────
for game in GAMES:
    src = os.path.join(SRC_TOOLS, game)
    dst = os.path.join(DEST_GAMES, game)
    if not os.path.exists(src):
        print(f"  MISSING: {game}")
        continue

    html = open(src, encoding='utf-8').read()

    # Fix data path
    html = html.replace('../Words/flashcards.js', '../flashcards.js')

    # Apply colour map (longer strings first to avoid partial matches)
    for old, new in sorted(COLOUR_MAP.items(), key=lambda x: -len(x[0])):
        html = html.replace(old, new)

    # Inject nav after <body>
    nav = NAV_SNIPPET.replace('GAME_NAME', game_display_name(game))
    html = re.sub(r'(<body[^>]*>)', r'\1' + nav, html, count=1)

    # Inject XP scripts before </body>
    html = html.replace('</body>', XP_SCRIPTS + '</body>', 1)

    with open(dst, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"  migrated: {game}")

print("\nDone. Games are in rosie-vle/swedish/games/")
print("Note: swAddXP(n) is available in each game — wire it to score events as needed.")
