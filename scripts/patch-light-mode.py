"""
Swap dark-mode tokens for paper-and-peaches light mode
in standalone pages (index.html, sr/queue.html, sync-setup.html)
and update hardcoded hex colours.
"""
import os, re

ROOT = r"C:\Users\DELL\Documents\rosie-vle"

DARK_TOKENS = """\
      --bg:#0d1117; --surface:#161b22; --surface2:#21262d;
      --border:#30363d; --text:#e6edf3; --muted:#8b949e;
      --green:#3fb950; --green-bg:rgba(63,185,80,.12);
      --blue:#58a6ff;  --blue-bg:rgba(88,166,255,.10);
      --yellow:#d29922; --yellow-bg:rgba(210,153,34,.12);
      --red:#f85149;   --red-bg:rgba(248,81,73,.12);
      --purple:#bc8cff; --purple-bg:rgba(188,140,255,.12);"""

LIGHT_TOKENS = """\
      --bg:#faf6f0; --surface:#ffffff; --surface2:#f2ece2;
      --border:#e8ddd0; --text:#2c1f12; --muted:#8a7a68;
      --green:#3d6e30; --green-bg:rgba(61,110,48,.1);
      --blue:#b85430;  --blue-bg:rgba(184,84,48,.1);
      --yellow:#a06820; --yellow-bg:rgba(160,104,32,.1);
      --red:#b03428;   --red-bg:rgba(176,52,40,.1);
      --purple:#7048a0; --purple-bg:rgba(112,72,160,.1);"""

# Hardcoded colours that appear inline and need swapping
COLOUR_MAP = {
    # backgrounds
    "#0d1117": "#faf6f0",
    # surface
    "#161b22": "#ffffff",
    "#21262d": "#f2ece2",
    # border
    "#30363d": "#e8ddd0",
    # text
    "#e6edf3": "#2c1f12",
    # muted
    "#8b949e": "#8a7a68",
    # green
    "#3fb950": "#3d6e30",
    # blue/peach
    "#58a6ff": "#b85430",
    # yellow
    "#d29922": "#a06820",
    # red
    "#f85149": "#b03428",
    # purple
    "#bc8cff": "#7048a0",
    # XP bar gradient
    "linear-gradient(90deg,#bc8cff,#58a6ff)": "linear-gradient(90deg,#e09060,#b85430)",
    # toast (in game files)
    "background:#d29922; color:#0d1117": "background:#b85430; color:#ffffff",
}

STANDALONE = [
    r"index.html",
    r"sr\queue.html",
    r"sync-setup.html",
]

GAME_FILES = [os.path.join(ROOT, "ibm", "games", f) for f in [
    "c03-quiz.html","c04-quiz.html",
    "c03-flashcards.html","c04-flashcards.html",
    "c03-odd-one-out.html","c04-odd-one-out.html",
    "c03-true-false.html","c04-true-false.html",
]]

def patch(fpath):
    html = open(fpath, encoding='utf-8').read()
    original = html

    # Swap token block (standalone pages only)
    if DARK_TOKENS in html:
        html = html.replace(DARK_TOKENS, LIGHT_TOKENS, 1)

    # Swap hardcoded colours everywhere
    for old, new in COLOUR_MAP.items():
        html = html.replace(old, new)

    if html != original:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  patched: {os.path.relpath(fpath, ROOT)}")
    else:
        print(f"  no change: {os.path.relpath(fpath, ROOT)}")

print("Applying light mode...")
for rel in STANDALONE:
    patch(os.path.join(ROOT, rel))
for fpath in GAME_FILES:
    patch(fpath)
print("Done.")
