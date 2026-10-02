"""Dongwu Senlin (iQue) script extractor.

Reads your own decrypted ROM, unpacks the message files (raw DEFLATE), and
writes every message with its control codes as tags to script.txt, next to
this file. Characters are looked up in chars.json (character code ->
character); any missing from it are written as [#1234] or [b16].

    python extract.py "path/to/Dongwu Senlin (China).z64"
"""
import json, os, struct, sys, zlib, collections

HERE = os.path.dirname(os.path.abspath(__file__))
FILE_TABLE = 0x21D80
MSG_DATA, MSG_INDEX = 1883, 1884  # file numbers in the ROM's file table

# Control codes: 0x7F <code> <args>. Sizes (including the 7F and code byte)
# and names from the GameCube decompilation's mFont_cont_info_tbl; every
# message parses to its exact end with these.
CODES = [
    (2, "end"), (2, "continue"), (2, "clear"), (3, "pause"), (2, "button"),
    (5, "color"), (2, "can_cancel"), (2, "no_cancel"), (5, "demo_player"),
    (5, "demo_npc0"), (5, "demo_npc1"), (5, "demo_npc2"), (5, "demo_quest"),
    (2, "select_window"), (4, "next_f"), (4, "next_0"), (4, "next_1"),
    (4, "next_2"), (4, "next_3"), (6, "next_random2"), (8, "next_random3"),
    (10, "next_random4"), (6, "choices2"), (8, "choices3"), (10, "choices4"),
    (2, "force_next"), (2, "player_name"), (2, "talk_name"), (2, "catchphrase"),
    (2, "year"), (2, "month"), (2, "weekday"), (2, "day"), (2, "hour"),
    (2, "minute"), (2, "second"),
    *[(2, f"free{i}") for i in range(10)],
    (2, "determination"), (2, "town_name"), (2, "random_number"),
    *[(2, f"item{i}") for i in range(5)],
    *[(2, f"free{i}") for i in range(10, 20)],
    (2, "mail"),
    *[(2, f"destiny{i}") for i in range(10)],
    (2, "mood_normal"), (2, "mood_angry"), (2, "mood_sad"), (2, "mood_fun"),
    (2, "mood_sleepy"), (6, "color_chars"), (3, "sound_cut"), (3, "line_offset"),
    (3, "line_type"), (3, "char_scale"), (2, "button2"), (4, "bgm_make"),
    (4, "bgm_delete"), (3, "time_end"), (3, "sound_sys"), (3, "line_scale"),
    (2, "sound_no_page"), (2, "voice_on"), (2, "voice_off"), (2, "select_no_b"),
    (2, "give_open"), (2, "give_close"), (2, "mood_gloomy"),
    (2, "select_no_b_close"), (6, "next_random_section"),
]
# Codes past the named ones still need a size: the GameCube table's tail.
EXTRA_SIZES = [3, 3, 4, 3, 2, 2, 6, 2, 2, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 4, 4, 12, 14]


def code_info(c):
    if c < len(CODES):
        return CODES[c]
    k = c - len(CODES)
    return (EXTRA_SIZES[k] if k < len(EXTRA_SIZES) else 2), f"code{c:02x}"


def read_file(rom, n):
    vs, ve, ps, pe = struct.unpack(">4I", rom[FILE_TABLE + 16 * n:FILE_TABLE + 16 * n + 16])
    return zlib.decompress(rom[ps:pe], -15) if pe else rom[ps:ps + ve - vs]


def main(rom_path):
    rom = open(rom_path, "rb").read()
    data, index = read_file(rom, MSG_DATA), read_file(rom, MSG_INDEX)
    ends = struct.unpack(f">{len(index) // 4}I", index)
    table_path = os.path.join(HERE, "chars.json")
    chars = json.load(open(table_path, encoding="utf-8")) if os.path.exists(table_path) else {}
    used = collections.Counter()
    out = []
    for m in range(1, len(ends)):
        i, e, s = ends[m - 1], ends[m], []
        while i < e:
            b = data[i]
            if b == 0x7F:
                size, name = code_info(data[i + 1])
                args = data[i + 2:i + size]
                if name != "end":
                    s.append("{" + name + (" " + args.hex() if args else "") + "}")
                i += size
            elif b == 0x7D:
                s.append("\n"); i += 1
            elif b >= 0x80:
                g = (data[i + 1] << 7) | (b & 0x7F); used[g] += 1
                s.append(chars.get(str(g), f"[#{g}]")); i += 2
            else:
                g = f"b{b:02x}"; used[g] += 1
                s.append(chars.get(g, f"[{g}]")); i += 1
        out.append(f"=== {m - 1:05d}\n{''.join(s)}\n")
    with open(os.path.join(HERE, "script.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.writelines(out)
    with open(os.path.join(HERE, "glyphs-used.txt"), "w", encoding="utf-8", newline="\n") as f:
        for g, n in used.most_common():
            f.write(f"{g}\t{n}\t{chars.get(str(g), '')}\n")
    known = sum(n for g, n in used.items() if str(g) in chars)
    print(f"{len(ends) - 1} messages, {len(used)} distinct characters, "
          f"{known / sum(used.values()):.1%} of text decoded")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python extract.py <your own Dongwu Senlin ROM (.z64)>")
    main(sys.argv[1])
