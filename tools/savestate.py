"""Pull RAM, the loaded messages and the on-screen frame out of an ares save state.

    python tools/savestate.py <rom.z64> <state file>

Prints the numbers of the messages found in RAM and saves the frame as
<state file>.png, so text on screen can be matched against script.txt.
Needs Pillow. Tested with ares v134 states."""
import struct, sys
from PIL import Image
from common import read_file

rom = open(sys.argv[1], "rb").read()
st = open(sys.argv[2], "rb").read()
# ares stores RDRAM with each 32-bit word byte-reversed; find it by the boot code.
boot = read_file(rom, 1)
probe = b"".join(boot[0x100 + j:0x104 + j][::-1] for j in range(0, 32, 4))
base = st.find(probe) - 0x100 - 0x460
raw = st[base:base + 0x800000]
ram = bytearray(len(raw) // 4 * 4)
for i in range(0, len(ram), 4):
    ram[i:i + 4] = raw[i:i + 4][::-1]
ram = bytes(ram)
data, index = read_file(rom, 1883), read_file(rom, 1884)
ends = struct.unpack(f">{len(index) // 4}I", index)
found = [m - 1 for m in range(1, len(ends))
         if ends[m] - ends[m - 1] >= 12 and data[ends[m - 1]:ends[m - 1] + min(24, ends[m] - ends[m - 1])] in ram]
print("messages in RAM:", found)
# The game's two 320x240 RGBA5551 framebuffers sit around RAM 0x3A0000.
top, rows = 0x3A0000, (0x3E0000 - 0x3A0000) // 640
img = Image.new("RGB", (320, rows))
px = img.load()
for y in range(rows):
    for x in range(320):
        v = int.from_bytes(ram[top + y * 640 + x * 2:top + y * 640 + x * 2 + 2], "big")
        px[x, y] = ((v >> 11 & 31) * 8, (v >> 6 & 31) * 8, (v >> 1 & 31) * 8)
img.save(sys.argv[2] + ".png")
print("frame saved to", sys.argv[2] + ".png")
