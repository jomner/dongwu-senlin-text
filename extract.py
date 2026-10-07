"""Dongwu Senlin (iQue) text extractor.

Reads your own decrypted ROM, unpacks its text files (raw DEFLATE), and
writes all of its text, control codes as tags, next to this file:

    script.txt   the messages (the dialogue)
    answers.txt  the choice answers
    letters.txt  the letters: bodies, greetings and sign-offs
    names.txt    the villager names
    strings.txt  the short string table (names, words, catchphrases)
    items.txt    the item names, in the file's order

Characters are looked up in chars.json (character code -> character); any
missing from it are written as [#1234] or [b16].

    python extract.py "path/to/Dongwu Senlin (China).z64"
"""
import json, os, struct, sys, zlib, collections

HERE = os.path.dirname(os.path.abspath(__file__))
FILE_TABLE = 0x21D80
# File numbers in the ROM's file table: text data, then the index of where each entry ends.
MSG_DATA, MSG_INDEX = 1883, 1884
ANSWERS = (1885, 1886)
LETTERS = (("body", 1887, 1888), ("greeting", 1889, 1890), ("sign-off", 1891, 1892))
STRINGS = (1893, 1894)
NAMES, NAME_HEADER, NAME_SIZE = 1914, 8, 6  # 3 characters each, padded with spaces
ITEMS, ITEM_HEADER, ITEM_SIZE = 2225, 8, 10  # 5 characters each, padded; zeros between tables

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


def decode(data, i, e, chars, used):
    """One entry, data[i:e] -> its text, control codes as tags."""
    s = []
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
    return "".join(s)


def table(rom, data_file, index_file, chars, used):
    """A table whose index gives each entry's end, the first starting at 0."""
    data, index = read_file(rom, data_file), read_file(rom, index_file)
    ends = (0,) + struct.unpack(f">{len(index) // 4}I", index)
    return [decode(data, ends[n], ends[n + 1], chars, used) for n in range(len(ends) - 1)]


def write(name, entries):
    with open(os.path.join(HERE, name), "w", encoding="utf-8", newline="\n") as f:
        f.writelines(f"=== {label}\n{text}\n" for label, text in entries)


def main(rom_path):
    rom = open(rom_path, "rb").read()
    table_path = os.path.join(HERE, "chars.json")
    chars = json.load(open(table_path, encoding="utf-8")) if os.path.exists(table_path) else {}
    used = collections.Counter()

    # The messages: their index's first entry is where the first one starts.
    data, index = read_file(rom, MSG_DATA), read_file(rom, MSG_INDEX)
    ends = struct.unpack(f">{len(index) // 4}I", index)
    messages = [decode(data, ends[m - 1], ends[m], chars, used) for m in range(1, len(ends))]
    write("script.txt", ((f"{m:05d}", text) for m, text in enumerate(messages)))

    answers = table(rom, *ANSWERS, chars, used)
    write("answers.txt", ((f"{n:04d}", text) for n, text in enumerate(answers)))

    letters = []
    for part, data_file, index_file in LETTERS:
        letters += [(f"{part} {n:03d}", text) for n, text in enumerate(table(rom, data_file, index_file, chars, used))]
    write("letters.txt", letters)

    strings = table(rom, *STRINGS, chars, used)
    write("strings.txt", ((f"{n:04d}", text) for n, text in enumerate(strings)))

    data = read_file(rom, NAMES)
    names = [decode(data, at, at + NAME_SIZE, chars, used).rstrip(" ")
             for at in range(NAME_HEADER, len(data) - NAME_SIZE + 1, NAME_SIZE)]
    write("names.txt", ((f"{n:03d}", text) for n, text in enumerate(names)))

    # Item names: numbered through the whole file. (A table ending on a 4-byte boundary has no padding after it,
    # so where one table ends and the next begins can't be read from the file alone.)
    data, items, at = read_file(rom, ITEMS), [], ITEM_HEADER
    while at + ITEM_SIZE <= len(data):
        if data[at] == 0:  # padding before the next table
            at += 1
            continue
        items.append(decode(data, at, at + ITEM_SIZE, chars, used).rstrip(" "))
        at += ITEM_SIZE
    write("items.txt", ((f"{n:04d}", text) for n, text in enumerate(items)))

    with open(os.path.join(HERE, "glyphs-used.txt"), "w", encoding="utf-8", newline="\n") as f:
        for g, n in used.most_common():
            f.write(f"{g}\t{n}\t{chars.get(str(g), '')}\n")
    known = sum(n for g, n in used.items() if str(g) in chars)
    print(f"{len(messages)} messages, {len(answers)} answers, {len(letters)} letter parts, {len(strings)} strings, "
          f"{len(names)} names, {len(items)} items; {len(used)} distinct characters, "
          f"{known / sum(used.values()):.1%} of text decoded")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python extract.py <your own Dongwu Senlin ROM (.z64)>")
    main(sys.argv[1])
