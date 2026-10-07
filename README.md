# Dòngwù Sēnlín text

Tools and a character table for reading the Chinese text of **动物森林 (Dòngwù Sēnlín)**, the 2006 iQue Player release of Animal Forest, from your own copy of the game.

This repository holds no game data: no ROM, no script, no font. Run the extractor on your own dump to produce the script.

## Use

```
python extract.py "path/to/Dongwu Senlin (China).z64"
```

It writes all of the game's text, in Chinese, with its control codes as tags (`{player_name}`, `{choices2 …}`, `{color 969696}`, `{pause 08}`), each entry under its number:

- `script.txt` — the 11,791 messages (the dialogue).
- `answers.txt` — the 460 choice answers.
- `letters.txt` — the letters: 564 bodies, greetings and sign-offs each.
- `strings.txt` — the 1,564 entries of the short string table (names, words, catchphrases, the staff credits).
- `names.txt` — the 220 villager names.
- `items.txt` — the 4,544 item names, in the file's order.

Needs Python 3, no packages. The ROM must be decrypted (a big-endian `.z64`).

## Files

- `extract.py` — the extractor.
- `chars.json` — character code → character, for all 3,026 characters the game's text uses.
- `low-confidence.json` — the readings in `chars.json` that are still best guesses (see below).
- `tools/` — what the table was made with (Python 3 and Pillow):
  - `sheets.py <rom>` draws the characters `chars.json` lacks, most frequent first, as numbered sheets of the game's own glyphs.
  - `apply_sheet.py <n> <readings.txt>` stores one sheet's readings.
  - `savestate.py <rom> <state>` reads an [ares](https://ares-emu.net) save state: which messages are in RAM, and the frame on screen. Use it to check readings against the game.
  - `common.py` holds the ROM's file table, the font and the code → glyph rule.

## How the text is stored

- **Files.** The file table is at ROM `0x21D80` (16 bytes per file: VROM start/end, ROM start/end, as in Ocarina of Time). Compressed files are raw DEFLATE, not Yaz0 as on the N64.
- **Messages.** File 1883 is the message data; file 1884 indexes it, as big-endian 32-bit end offsets.
- **The rest of the text,** in the same encoding: choice answers (1885/1886), letters (bodies 1887/1888, greetings
  1889/1890, sign-offs 1891/1892), the short string table (1893/1894: names, words, catchphrases), each indexed by
  end offsets from 0; villager names (1914: an 8-byte header, then 6 bytes per name); item names (2225: an 8-byte
  header, then 10 bytes per name, padded with spaces, in the N64's item tables, zeros between some of them).
- **Characters.**
  - `7D` — new line.
  - `7F xx …` — control code `xx`, followed by its arguments. Sizes and meanings match the GameCube Animal Crossing's control codes (`mFont_cont_info_tbl` in ac-decomp); every message parses to its exact end with them.
  - `00`–`7C` — one-byte character: glyph number = the byte.
  - `80`–`FF` then a second byte — two-byte character: glyph number = `(second << 7 | (first & 0x7F)) + 128`.
- **Font.** File 1882, from offset `0x128`: one 4-bit intensity sheet 192 pixels wide, 12×12 glyphs, 16 per row (1,152 bytes per row of glyphs), 7,056 slots. The game copies a glyph into its text cache with the routine at `0x80073E68`. The glyphs are in the game's own order, not GB2312, so the table was made by reading each glyph.

## Notes on the text

- About 380 messages (including the first ones, #0–4) are mostly Japanese: text the Chinese release left untranslated, likely unused or debug messages. So are about 290 entries of the string table (most of them 156–355) and five answers.
- The string table ends with the staff credits, in full-width Latin letters.
- `．` mostly appears between pause codes: dots that appear one by one, the game's dramatic "…".
- Some Chinese on screen is drawn as pictures rather than text (the title logo, signs, some menu labels), so it isn't in the script.

## How sure the readings are

Every character the game's text uses has a reading (3,026 in all), so the extracted text has no gaps. All are confirmed by the words they form in context. A second pass over the 173 that were once best guesses (sound words, kana and Latin letters from the untranslated Japanese messages, rare characters) corrected 21 of them, among them 罐 in 空罐子 and 逵 in 李逵. A blank glyph read as □ is now a full-width space.

The last six best guesses, found only in villager names and catchphrases, were checked pixel by pixel against the candidates and kept, so `low-confidence.json` is now empty. The last 19, found only in the string table's untranslated Japanese and its credits, are kana confirmed by the words they spell (ヨーデル, ソナタ, メゾネット, ファンブル), full-width letters confirmed by the names (Ｔａｋａｓｈｉ Ｔｅｚｕｋａ), and 鼹, told from 鼬 by its shape. Corrections are welcome (`tools/savestate.py` shows a glyph on screen).

## Not yet covered

- Chinese drawn as pictures (the title logo, signs, some menu labels).

## How the table was made

The glyph-number rule was confirmed against text drawn on screen in emulator save states. Every glyph the script uses was then read by eye, most frequent first, and checked in context. Corrections are welcome.

## Credits

- [zeldaret/af](https://github.com/zeldaret/af) — the Animal Forest decompilation (ROM layout).
- [ACreTeam/ac-decomp](https://github.com/ACreTeam/ac-decomp) — the GameCube Animal Crossing decompilation (control codes).
- [zeldaret/oot](https://github.com/zeldaret/oot) — its iQue Chinese work showed how the iQue team stored text.

Dòngwù Sēnlín © Nintendo / iQue. This is an unofficial project, not affiliated with either.

## Licence

The code and `chars.json` are under the MIT licence (see `LICENSE`). It covers this project only, not the game or its text.
