# Dòngwù Sēnlín text

Tools and a character table for reading the Chinese text of **动物森林 (Dòngwù Sēnlín)**, the 2006 iQue Player release of Animal Forest, from your own copy of the game.

This repository holds no game data: no ROM, no script, no font. Run the extractor on your own dump to produce the script.

## Use

```
python extract.py "path/to/Dongwu Senlin (China).z64"
```

It writes `script.txt`: all 11,791 messages by number, in Chinese, with the game's control codes as tags (`{player_name}`, `{choices2 …}`, `{color 969696}`, `{pause 08}`). Needs Python 3, no packages. The ROM must be decrypted (a big-endian `.z64`).

## Files

- `extract.py` — the extractor.
- `chars.json` — character code → character, for all 2,670 characters the script uses.
- `low-confidence.json` — the 380 readings in `chars.json` that are less certain: kana (likely leftovers from the Japanese original), bold Latin letters and digits, and characters the font holds twice in near-identical forms.

## How the text is stored

- **Files.** The file table is at ROM `0x21D80` (16 bytes per file: VROM start/end, ROM start/end, as in Ocarina of Time). Compressed files are raw DEFLATE, not Yaz0 as on the N64.
- **Messages.** File 1883 is the message data; file 1884 indexes it, as big-endian 32-bit end offsets.
- **Characters.**
  - `7D` — new line.
  - `7F xx …` — control code `xx`, followed by its arguments. Sizes and meanings match the GameCube Animal Crossing's control codes (`mFont_cont_info_tbl` in ac-decomp); every message parses to its exact end with them.
  - `00`–`7C` — one-byte character: glyph number = the byte.
  - `80`–`FF` then a second byte — two-byte character: glyph number = `(second << 7 | (first & 0x7F)) + 128`.
- **Font.** File 1882, from offset `0x128`: one 4-bit intensity sheet 192 pixels wide, 12×12 glyphs, 16 per row (1,152 bytes per row of glyphs), 7,056 slots. The game copies a glyph into its text cache with the routine at `0x80073E68`. The glyphs are in the game's own order, not GB2312, so the table was made by reading each glyph.

## How the table was made

The glyph-number rule was confirmed against text drawn on screen in emulator save states. Every glyph the script uses was then read by eye, most frequent first, and checked in context. Corrections are welcome.

## Credits

- [zeldaret/af](https://github.com/zeldaret/af) — the Animal Forest decompilation (ROM layout).
- [ACreTeam/ac-decomp](https://github.com/ACreTeam/ac-decomp) — the GameCube Animal Crossing decompilation (control codes).
- [zeldaret/oot](https://github.com/zeldaret/oot) — its iQue Chinese work showed how the iQue team stored text.

Dòngwù Sēnlín © Nintendo / iQue. This is an unofficial project, not affiliated with either.
