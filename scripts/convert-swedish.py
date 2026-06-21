"""
Convert Swedish 🫎/Flashcards/*.md (Yanki format) → data/decks/swedish.json

Card format:
    [Swedish term]

    ---

    [English translation]

Skips Archive/ subfolder. Skips malformed files.
Run from rosie-vle/ root:
    python scripts/convert-swedish.py
"""

import os, json, re, unicodedata

SOURCE = r"C:\Users\DELL\Documents\Swedish 🫎\Flashcards"
OUTPUT = r"data\decks\swedish.json"

def make_id(filename):
    """Kebab-case ID from filename (strip .md, normalise)"""
    name = filename[:-3]  # strip .md
    # normalise unicode, keep letters/digits/spaces/hyphens/dots/parentheses
    name = unicodedata.normalize("NFC", name)
    name = re.sub(r"[^\w\s\-\.\(\)åäöÅÄÖ]", "", name)
    name = name.strip().replace(" ", "-").lower()
    return name

cards = []
skipped = 0

for fname in sorted(os.listdir(SOURCE)):
    if not fname.endswith(".md"):
        continue

    filepath = os.path.join(SOURCE, fname)

    # skip directories (Archive/)
    if os.path.isdir(filepath):
        continue

    try:
        raw = open(filepath, encoding="utf-8").read()
    except Exception as e:
        print(f"  SKIP (read error): {fname} — {e}")
        skipped += 1
        continue

    # strip YAML frontmatter if present (Yanki adds noteId on sync)
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) >= 3:
            raw = parts[2].strip()

    # split on --- separator
    parts = re.split(r"\n---\n", raw, maxsplit=1)
    if len(parts) != 2:
        print(f"  SKIP (no separator): {fname}")
        skipped += 1
        continue

    front = parts[0].strip()
    back  = parts[1].strip()

    if not front or not back:
        print(f"  SKIP (empty side): {fname}")
        skipped += 1
        continue

    cards.append({
        "id":     make_id(fname),
        "front":  front,
        "back":   back,
        "domain": "swedish",
        "audio":  True
    })

# deduplicate IDs (e.g. "annorlunda.md" and "annorlunda (2).md")
seen = {}
deduped = []
for card in cards:
    cid = card["id"]
    if cid in seen:
        seen[cid] += 1
        card["id"] = f"{cid}-{seen[cid]}"
    else:
        seen[cid] = 0
    deduped.append(card)

os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(deduped, f, ensure_ascii=False, indent=2)

print(f"\nDone. {len(deduped)} cards written to {OUTPUT}")
if skipped:
    print(f"Skipped: {skipped} files")
