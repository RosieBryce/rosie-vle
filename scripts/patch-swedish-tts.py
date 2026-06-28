"""
Add Swedish TTS "Hear it" button to migrated Swedish games.
Each game has a different structure — patches are targeted per file.
"""

import os, re

GAMES = r"C:\Users\DELL\Documents\rosie-vle\swedish\games"

# ── Shared helper to inject into each file ────────────────────
# Replaces the closing </script> of the already-injected XP block
# (which ends with the toast code) to add swSpeak() too.

SPEAK_FN = """\
function swSpeak(text) {
  if (!text || !('speechSynthesis' in window)) return;
  speechSynthesis.cancel();
  var u = new SpeechSynthesisUtterance(text.trim());
  u.lang = 'sv-SE';
  speechSynthesis.speak(u);
}
"""

BTN_STYLE = """\
.btn-hear {
  background:none; border:1px solid var(--border); border-radius:8px;
  color:var(--muted); font-size:.8rem; padding:.3rem .75rem; cursor:pointer;
  display:inline-flex; align-items:center; gap:.3rem;
  transition:border-color .15s, color .15s; margin-top:.5rem;
}
.btn-hear:hover { border-color:var(--blue); color:var(--blue); }
"""

def inject_speak_fn(html):
    """Add swSpeak() inside the already-injected XP script block."""
    marker = "function swAddXP(amount) {"
    if marker in html and "swSpeak" not in html:
        html = html.replace(marker, SPEAK_FN + "\n" + marker, 1)
    return html

def inject_btn_style(html):
    """Add .btn-hear CSS before </style> of the first style block."""
    if ".btn-hear" not in html:
        html = html.replace("</style>", BTN_STYLE + "</style>", 1)
    return html

def patch(filename, fn):
    path = os.path.join(GAMES, filename)
    html = open(path, encoding="utf-8").read()
    original = html
    html = inject_speak_fn(html)
    html = inject_btn_style(html)
    html = fn(html)
    if html != original:
        open(path, "w", encoding="utf-8").write(html)
        print(f"  patched: {filename}")
    else:
        print(f"  no change: {filename}")

# ── daily-challenge ───────────────────────────────────────────
# Swedish word in <div class="swedish" id="sw"></div>
# Set via: document.getElementById('sw').textContent = c.swedish
def patch_daily(html):
    # Add Hear it button after the #sw div
    html = html.replace(
        '<div class="swedish" id="sw"></div>',
        '<div class="swedish" id="sw"></div>\n'
        '<button class="btn-hear" id="btn-hear" onclick="swSpeak(document.getElementById(\'sw\').textContent)">🔊 Hear it</button>'
    )
    # Auto-speak when card is shown (line: document.getElementById('sw').textContent = c.swedish)
    html = html.replace(
        "document.getElementById('sw').textContent = c.swedish;",
        "document.getElementById('sw').textContent = c.swedish;\n  swSpeak(c.swedish);"
    )
    return html

patch("daily-challenge.html", patch_daily)

# ── speed-round ───────────────────────────────────────────────
# Same #sw / .swedish pattern but in a timed game — button only (no auto-speak)
def patch_speed(html):
    html = html.replace(
        '<div class="swedish" id="sw"></div>',
        '<div class="swedish" id="sw"></div>\n'
        '<button class="btn-hear" onclick="swSpeak(document.getElementById(\'sw\').textContent)">🔊 Hear it</button>'
    )
    return html

patch("speed-round.html", patch_speed)

# ── quiz ──────────────────────────────────────────────────────
# Swedish shown in #prompt when curDir === 'sv-en' only.
# Button should only be visible when direction is sv-en.
def patch_quiz(html):
    # Add button after #prompt div
    html = html.replace(
        '<div class="prompt" id="prompt"></div>',
        '<div class="prompt" id="prompt"></div>\n'
        '<button class="btn-hear" id="btn-hear" '
        'onclick="swSpeak(document.getElementById(\'prompt\').textContent)">🔊 Hear it</button>'
    )
    # Show/hide button depending on direction — find where nextCard sets the prompt
    # Pattern: document.getElementById('prompt').textContent = curDir === 'sv-en' ? c.swedish : core(c.english);
    old_prompt = "document.getElementById('prompt').textContent = curDir === 'sv-en' ? c.swedish : core(c.english);"
    new_prompt = (
        "document.getElementById('prompt').textContent = curDir === 'sv-en' ? c.swedish : core(c.english);\n"
        "  var bh = document.getElementById('btn-hear');\n"
        "  if (bh) { bh.style.display = curDir === 'sv-en' ? 'inline-flex' : 'none'; }"
    )
    html = html.replace(old_prompt, new_prompt)
    return html

patch("quiz.html", patch_quiz)

# ── en-eller-ett ──────────────────────────────────────────────
# Swedish noun in <div class="word" id="word"></div>
# Set via: document.getElementById('word').textContent=n.sv
def patch_en_ett(html):
    html = html.replace(
        '<div class="word" id="word"></div>',
        '<div class="word" id="word"></div>\n'
        '<button class="btn-hear" onclick="swSpeak(document.getElementById(\'word\').textContent)">🔊 Hear it</button>'
    )
    # Auto-speak on each word
    html = html.replace(
        "document.getElementById('word').textContent=n.sv;",
        "document.getElementById('word').textContent=n.sv;\n  swSpeak(n.sv);"
    )
    return html

patch("en-eller-ett.html", patch_en_ett)

# ── hangman ───────────────────────────────────────────────────
# Word is in `target` variable, only reveal at game end.
# Find where game ends (won or lost) and speak the answer.
# Won: "won = [...target]..." → after this, speak
# Lost: look for the "lose" path — wrong >= MAX_WRONG
def patch_hangman(html):
    # Add button to the game-over area — but since it's letter boxes, we inject
    # swSpeak(targetWord) at the point where the full word is revealed.
    # Find: const won = [...target].filter... every...
    # After win/loss determined, call swSpeak.
    # The function that handles end state renders the board with all letters shown.
    # Simplest: after `gameOver = true`, speak.
    html = html.replace(
        "gameOver=true;",
        "gameOver=true; swSpeak(target);",
        1  # only the first occurrence (game-over set)
    )
    return html

patch("hangman.html", patch_hangman)

# ── matching ──────────────────────────────────────────────────
# Swedish items are divs in left column. Each has onclick="pick(...)".
# Speak when a Swedish-side item is clicked.
# The items are created with: div.textContent = item.text, side:'sv'
# onclick="pick(${item.id}, '${item.side}')"
def patch_matching(html):
    # In pick() function, when side === 'sv', speak the text
    # Find pick function: function pick(id, side) {
    old_pick = "function pick(id, side) {"
    new_pick = (
        "function pick(id, side) {\n"
        "  if (side === 'sv') {\n"
        "    var el = document.querySelector('[data-id=\"'+id+'\"][data-side=\"sv\"]');\n"
        "    if (el) swSpeak(el.textContent);\n"
        "  }"
    )
    html = html.replace(old_pick, new_pick, 1)
    # Also add data-id and data-side to the item divs so we can find them
    # The items are rendered with: div.onclick = () => pick(item.id, item.side)
    # And: div.textContent = item.text
    # Replace the item creation to add data attributes
    old_item = "  div.textContent = item.text;"
    new_item = (
        "  div.textContent = item.text;\n"
        "  div.dataset.id = item.id;\n"
        "  div.dataset.side = item.side;"
    )
    html = html.replace(old_item, new_item, 1)
    return html

patch("matching.html", patch_matching)

# ── Grammar games — speak the prompt word ────────────────────

# conjugation: shows Swedish verb to conjugate
# Look for the element that displays the verb
def patch_conjugation(html):
    # Read to find pattern
    if '#verb' in html or 'id="verb"' in html:
        html = re.sub(
            r'(document\.getElementById\(["\']verb["\']\)\.textContent\s*=\s*)([^;]+);',
            lambda m: m.group(0) + '\n  swSpeak(' + m.group(2).strip() + ');',
            html, count=1
        )
    return html

patch("conjugation.html", patch_conjugation)

# plurals: shows Swedish singular noun
def patch_plurals(html):
    if 'id="singular"' in html or '#singular' in html:
        html = re.sub(
            r'(document\.getElementById\(["\']singular["\']\)\.textContent\s*=\s*)([^;]+);',
            lambda m: m.group(0) + '\n  swSpeak(' + m.group(2).strip() + ');',
            html, count=1
        )
    return html

patch("plurals.html", patch_plurals)

# adjective-agreement: shows Swedish noun phrase
def patch_adj(html):
    # Similar pattern — speak whatever the prompt word is
    return html  # skip — complex enough to handle manually if needed

patch("adjective-agreement.html", patch_adj)

# word-order: tiles to arrange — skip (speaking each tile would be odd)
# cloze: passage-based — skip

print("\nDone.")
