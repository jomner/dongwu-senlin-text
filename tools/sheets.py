"""Draw the characters chars.json doesn't have yet, most frequent first, as reading sheets.

    python tools/sheets.py <rom.z64>

Run extract.py first (it writes glyphs-used.txt). Writes sheets/sheetNN.png (20 per
row, 10 rows) and sheets/order.json, which apply_sheet.py uses. Needs Pillow."""
import json, os, sys
from PIL import Image, ImageDraw
from common import glyphs, glyph_number

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLS, ROWS, SCALE = 20, 10, 4
rom = open(sys.argv[1], "rb").read()
G = glyphs(rom)
known = json.load(open(os.path.join(ROOT, "chars.json"), encoding="utf-8"))
used = [l.split("\t")[0] for l in open(os.path.join(ROOT, "glyphs-used.txt"), encoding="utf-8")]
todo = [k for k in used if k not in known]
os.makedirs(os.path.join(ROOT, "sheets"), exist_ok=True)
json.dump(todo, open(os.path.join(ROOT, "sheets", "order.json"), "w"))
cell = 12 * SCALE + 8
for s in range(0, len(todo), COLS * ROWS):
    im = Image.new("L", (COLS * cell + 40, ROWS * cell), 255)
    dr = ImageDraw.Draw(im)
    for i, k in enumerate(todo[s:s + COLS * ROWS]):
        r, c = divmod(i, COLS)
        g = G[glyph_number(k)]
        for y in range(12):
            for x in range(12):
                if g[y][x]:
                    x0, y0 = 40 + c * cell + 4 + x * SCALE, r * cell + 4 + y * SCALE
                    dr.rectangle([x0, y0, x0 + SCALE - 1, y0 + SCALE - 1], fill=0)
        if c == 0:
            dr.text((4, r * cell + 20), str(r), fill=0)
    for c in range(COLS + 1):
        dr.line([(40 + c * cell, 0), (40 + c * cell, ROWS * cell)], fill=180)
    for r in range(ROWS + 1):
        dr.line([(40, r * cell), (40 + COLS * cell, r * cell)], fill=180)
    im.save(os.path.join(ROOT, "sheets", f"sheet{s // (COLS * ROWS):02d}.png"))
print(len(todo), "characters to read")
