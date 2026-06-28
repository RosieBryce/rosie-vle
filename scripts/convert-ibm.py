"""
Convert IBM Anki cards + VLE game flashcards → data/decks/ibm.json

Sources:
  1. IBM Courses/Anki Flashcards/**/*.md  — cloze cards (~~hidden~~)
  2. rosie-vle/ibm/games/*-flashcards.html — Q&A cards (richer conceptual content)

Cloze card format:
  Front: text with ~~word~~ replaced by [...]
  Back:  full text with ~~word~~ shown in **bold**

Q&A card format:
  Front: question text
  Back:  answer text

Run from rosie-vle/ root:
  python scripts/convert-ibm.py
"""

import os, re, json

ANKI_ROOT  = r"C:\Users\DELL\Documents\IBM Courses\Anki Flashcards"
GAMES_ROOT = r"ibm\games"
OUTPUT     = r"data\decks\ibm.json"

# Map folder names → course IDs
COURSE_MAP = {
    "ML with Python":                  "c01",
    "Deep Learning with Keras":        "c02",
    "Deep Learning with Keras and TF": "c03",
}

cards = []
skipped = 0

# ── 1. Anki cloze cards ──────────────────────────────────────
def strip_frontmatter(text):
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()
    return text.strip()

def cloze_to_front(text):
    """Replace ~~hidden~~ with [...]"""
    return re.sub(r'~~(.+?)~~', '[...]', text, flags=re.DOTALL).strip()

def cloze_to_back(text):
    """Replace ~~hidden~~ with **hidden** for reveal"""
    return re.sub(r'~~(.+?)~~', r'**\1**', text, flags=re.DOTALL).strip()

def make_id(course_id, filepath):
    fname = os.path.splitext(os.path.basename(filepath))[0]
    fname = re.sub(r'[^\w\s\-]', '', fname).strip().replace(' ', '-').lower()
    return f"{course_id}-{fname}"

for course_name, course_id in COURSE_MAP.items():
    course_dir = os.path.join(ANKI_ROOT, course_name)
    if not os.path.isdir(course_dir):
        print(f"  MISSING: {course_dir}")
        continue

    for root, dirs, files in os.walk(course_dir):
        # module name from subfolder
        rel = os.path.relpath(root, course_dir)
        module = rel if rel != '.' else 'general'

        for fname in sorted(files):
            if not fname.endswith('.md'):
                continue
            fpath = os.path.join(root, fname)
            try:
                raw = open(fpath, encoding='utf-8').read()
            except Exception as e:
                print(f"  SKIP (read error): {fpath} — {e}")
                skipped += 1
                continue

            text = strip_frontmatter(raw)
            if not text or '~~' not in text:
                # Plain card with no cloze — treat whole thing as back, filename as front hint
                front = os.path.splitext(fname)[0].replace('-', ' ')
                back  = text
            else:
                front = cloze_to_front(text)
                back  = cloze_to_back(text)

            if not front or not back:
                skipped += 1
                continue

            cards.append({
                "id":     make_id(course_id, fpath),
                "front":  front,
                "back":   back,
                "domain": "ibm",
                "course": course_id,
                "module": module,
                "audio":  False,
                "type":   "cloze"
            })

print(f"Anki cards converted: {len(cards)}")

# ── 2. Game Q&A flashcards ───────────────────────────────────
def extract_game_cards(html_path, course_id):
    """Pull CARDS array from a *-flashcards.html file."""
    try:
        html = open(html_path, encoding='utf-8').read()
    except Exception as e:
        print(f"  SKIP (read error): {html_path} — {e}")
        return []

    # Find the CARDS = [ ... ]; block
    m = re.search(r'const CARDS\s*=\s*(\[.*?\]);', html, re.DOTALL)
    if not m:
        print(f"  SKIP (no CARDS array): {html_path}")
        return []

    raw_array = m.group(1)

    # Extract individual {q:..., a:...} objects
    pattern = re.compile(
        r'\{\s*q\s*:\s*"((?:[^"\\]|\\.)*)"\s*,\s*a\s*:\s*"((?:[^"\\]|\\.)*)"',
        re.DOTALL
    )

    extracted = []
    for i, match in enumerate(pattern.finditer(raw_array)):
        q = match.group(1).replace('\\"', '"').replace('\\n', '\n').replace('\\\\', '\\')
        a = match.group(2).replace('\\"', '"').replace('\\n', '\n').replace('\\\\', '\\')
        card_id = f"{course_id}-game-{i+1:02d}"
        extracted.append({
            "id":     card_id,
            "front":  q.strip(),
            "back":   a.strip(),
            "domain": "ibm",
            "course": course_id,
            "module": "game-flashcards",
            "audio":  False,
            "type":   "qa"
        })
    return extracted

game_total = 0
for fname in sorted(os.listdir(GAMES_ROOT)):
    if not fname.endswith('-flashcards.html'):
        continue
    course_id = fname.replace('-flashcards.html', '')  # e.g. 'c03'
    path = os.path.join(GAMES_ROOT, fname)
    game_cards = extract_game_cards(path, course_id)
    print(f"  {fname}: {len(game_cards)} Q&A cards")
    cards.extend(game_cards)
    game_total += len(game_cards)

print(f"Game Q&A cards converted: {game_total}")

# ── Deduplicate IDs ──────────────────────────────────────────
seen = {}
deduped = []
for card in cards:
    cid = card['id']
    if cid in seen:
        seen[cid] += 1
        card['id'] = f"{cid}-{seen[cid]}"
    else:
        seen[cid] = 0
    deduped.append(card)

# ── Write output ─────────────────────────────────────────────
os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
with open(OUTPUT, 'w', encoding='utf-8') as f:
    json.dump(deduped, f, ensure_ascii=False, indent=2)

print(f"\nDone. {len(deduped)} total IBM cards → {OUTPUT}")
if skipped:
    print(f"Skipped: {skipped} files")
