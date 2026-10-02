"""Store one sheet's readings in chars.json.

    python tools/apply_sheet.py <sheet number> <readings.txt>

readings.txt has one line per sheet row (20 characters; the last row may be
shorter). Optionally, a line '#flags' followed by 'row,col' lines marks
uncertain readings, which also go in low-confidence.json."""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s = int(sys.argv[1])
lines = open(sys.argv[2], encoding="utf-8").read().split("\n")
cut = lines.index("#flags") if "#flags" in lines else len(lines)
rows = [l for l in lines[:cut] if l]
flags = {tuple(map(int, l.split(","))) for l in lines[cut + 1:] if l.strip()}
order = json.load(open(os.path.join(ROOT, "sheets", "order.json")))
path, low_path = os.path.join(ROOT, "chars.json"), os.path.join(ROOT, "low-confidence.json")
known = json.load(open(path, encoding="utf-8"))
low = json.load(open(low_path, encoding="utf-8")) if os.path.exists(low_path) else {}
for r, row in enumerate(rows):
    assert len(row) == 20 or r == len(rows) - 1, f"row {r} has {len(row)} characters"
    for c, ch in enumerate(row):
        k = order[s * 200 + r * 20 + c]
        known[k] = ch
        if (r, c) in flags:
            low[k] = ch
json.dump(known, open(path, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=0)
json.dump(low, open(low_path, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=0)
print(len(known), "characters known,", len(low), "low-confidence")
