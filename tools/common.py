"""Shared helpers: the ROM's file table, the font, and character codes."""
import struct, zlib

FILE_TABLE = 0x21D80
FONT_FILE, FONT_OFFSET = 1882, 0x128  # 4-bit sheet, 192 px wide, 12x12 glyphs


def read_file(rom, n):
    vs, ve, ps, pe = struct.unpack(">4I", rom[FILE_TABLE + 16 * n:FILE_TABLE + 16 * n + 16])
    return zlib.decompress(rom[ps:pe], -15) if pe else rom[ps:ps + ve - vs]


def glyphs(rom):
    """Every glyph in the font as a list of 12 rows of 12 booleans (ink or not)."""
    data = read_file(rom, FONT_FILE)[FONT_OFFSET:]
    rows = len(data) // 1152
    out = []
    for r in range(rows):
        strip = data[r * 1152:(r + 1) * 1152]
        for c in range(16):
            g = []
            for y in range(12):
                line = strip[y * 96 + c * 6:y * 96 + c * 6 + 6]
                g.append([bool((b >> 4) if x % 2 == 0 else (b & 15)) for b in line for x in (0, 1)])
            out.append(g)
    return out


def glyph_number(code):
    """chars.json key ("b41" for one-byte code 0x41, "673" for a two-byte character) -> glyph number."""
    return int(code[1:], 16) if code.startswith("b") else int(code) + 128
