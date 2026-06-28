"""
Patch IBM game HTML files to wire XP into the engine.

Changes per file:
  1. Add engine.js + sync.js + domains.js script tags after shared.js
  2. Inject showXPToast() helper + awardGameXP() at top of showResults()
     — toast floats over the results screen, no innerHTML surgery needed

Run from rosie-vle/ root:
  python scripts/patch-ibm-games-xp.py
"""

import os, re

GAMES_DIR = r"ibm\games"

GAMES = [
    ("c03-quiz.html",        "score * 5"),
    ("c04-quiz.html",        "score * 5"),
    ("c03-flashcards.html",  "gotIt * 10 + nearly * 5"),
    ("c04-flashcards.html",  "gotIt * 10 + nearly * 5"),
    ("c03-odd-one-out.html", "correct * 4"),
    ("c04-odd-one-out.html", "correct * 4"),
    ("c03-true-false.html",  "correct * 3"),
    ("c04-true-false.html",  "correct * 3"),
]

OLD_SCRIPT_TAG = '  <script src="../shared.js"></script>'
NEW_SCRIPT_TAGS = '''\
  <script src="../shared.js"></script>
  <script src="../../domains.js"></script>
  <script src="../../sr/engine.js"></script>
  <script src="../../sync.js"></script>
  <style>
    #xp-toast { position:fixed; bottom:1.5rem; right:1.5rem; z-index:999;
      background:#d29922; color:#0d1117; font-size:.85rem; font-weight:700;
      padding:.5rem 1rem; border-radius:99px; opacity:0; pointer-events:none;
      transition:opacity .3s ease; }
    #xp-toast.show { opacity:1; }
  </style>'''

XP_TOAST_HELPER = '''\
// ── XP toast ──────────────────────────────────────────────
function showXPToast(xp) {
  var el = document.getElementById('xp-toast');
  if (!el) { el = document.createElement('div'); el.id = 'xp-toast'; document.body.appendChild(el); }
  el.textContent = '+' + xp + ' XP';
  el.classList.add('show');
  setTimeout(function() { el.classList.remove('show'); }, 2200);
}
'''

def patch_file(fname, xp_expr):
    fpath = os.path.join(GAMES_DIR, fname)
    html  = open(fpath, encoding='utf-8').read()

    # Idempotent
    if 'engine.js' in html:
        print(f"  {fname}: already patched, skipping")
        return

    # 1. Add script + style tags
    html = html.replace(OLD_SCRIPT_TAG, NEW_SCRIPT_TAGS, 1)

    # 2. Add toast helper before showResults
    html = html.replace(
        'function showResults() {',
        XP_TOAST_HELPER + 'function showResults() {',
        1
    )

    # 3. Inject XP award + toast call at TOP of showResults body
    xp_block = f"""\
function showResults() {{
  // ── XP award ──
  var _xp = {xp_expr};
  if (_xp > 0 && typeof engine !== 'undefined') {{
    engine.addXP(_xp, 'ibm');
    showXPToast(_xp);
    if (typeof sync !== 'undefined' && sync.isConfigured()) {{
      sync.push().catch(function(){{}});
    }}
  }}
"""
    # Replace only the first occurrence of 'function showResults() {'
    # after the helper was inserted (which became 'function showResults() {\n')
    html = html.replace(
        XP_TOAST_HELPER + 'function showResults() {\n',
        XP_TOAST_HELPER + xp_block,
        1
    )

    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"  {fname}: patched (+XP: {xp_expr})")

print("Patching IBM game files...")
for fname, xp_expr in GAMES:
    patch_file(fname, xp_expr)
print("Done.")
