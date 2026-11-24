"""Write a CPC .SNA (v2) snapshot of a 64 KB memory image, to open it in a real emulator.

Usage: python3 -m cpcarch.sna memory.bin out.sna [PC] [SP]   (hex, default 5400 BFF0)
The palette, mode and CRTC values below are those Antiriad sets at start-up; adjust them for another game.
"""
import sys
mem = open(sys.argv[1], 'rb').read(); out = sys.argv[2]
h = bytearray(256)
h[0:8] = b"MV - SNA"; h[0x10] = 2
PC = int(sys.argv[3], 16) if len(sys.argv) > 3 else 0x5400
SP = int(sys.argv[4], 16) if len(sys.argv) > 4 else 0xBFF0
h[0x21], h[0x22] = SP & 255, SP >> 8
h[0x23], h[0x24] = PC & 255, PC >> 8
h[0x25] = 1                                   # IM 1, interrupts disabled (the game enables them itself)
pal = [0x14, 0x0B, 0x00, 0x03, 0x14, 0x17, 0x13, 0x04, 0x14, 0x07, 0x03, 0x18, 0x14, 0x14, 0x14, 0x14, 0x14]
h[0x2E] = 0
h[0x2F:0x40] = bytes(pal)
h[0x40] = 0x8C                                # mode 0, lower and upper ROM disabled
h[0x41] = 0
crtc = [63, 40, 46, 0x8E, 38, 0, 25, 30, 0, 7, 0, 0, 0x30, 0, 0, 0, 0, 0]
h[0x42] = 0; h[0x43:0x55] = bytes(crtc)
h[0x55] = 0; h[0x59] = 0x82
h[0x5A] = 0; h[0x5B + 7] = 0x3F
h[0x6B], h[0x6C] = 64, 0
h[0x6D] = 2                                   # CPC 6128
open(out, 'wb').write(bytes(h) + mem[:65536])
print("written", out, len(h) + 65536)
