"""Minimal Amstrad CPC emulation around the SkoolKit Z80 core: 300 Hz IM1 interrupts, Gate Array palette/mode,
PPI/PSG keyboard matrix, VSYNC on PPI port B. Enough to let a game run from a snapshot and take screenshots."""
from .cpcsim import Simulator
from .cpcgfx import HW, screen

FRAME = 79872           # T-states per 50 Hz frame (4 MHz)
INT_EVERY = FRAME // 6  # 300 Hz

class CPC:
    def __init__(self, mem, pc, sp):
        self.mem = list(mem)
        self.sim = Simulator(self.mem, {"PC": pc, "SP": sp})
        self.R = self.sim.registers
        self.R[27] = 1                       # IM 1
        self.pen = 0
        self.pal = [0x14] * 17               # 16 pens + border (hardware colour numbers)
        self.mode = 0
        self.psg_reg = 0
        self.ppi_c = 0
        self.keys = set()                    # pressed (row, bit)
        self.next_int = INT_EVERY
        self.crtc_reg = 0
        self.crtc = {}
        self.sim.set_tracer(self)
        self.steps = 0
        self.slot_pal = [list(self.pal) for _ in range(6)]
        self.slot_mode = [0] * 6

    # ---- ports
    def write_port(self, registers, port, value, *a):
        hi = port >> 8
        if not port & 0x8000 and (port & 0x4000):          # Gate Array (&7Fxx)
            f = value >> 6
            if f == 0:
                self.pen = 16 if value & 0x10 else value & 15
            elif f == 1:
                self.pal[self.pen] = value & 31
            elif f == 2:
                self.mode = value & 3
                if value & 0x10:
                    pass
        if not port & 0x4000:                             # CRTC (&BCxx / &BDxx)
            if (hi & 3) == 0:
                self.crtc_reg = value & 31
            elif (hi & 3) == 1:
                self.crtc[self.crtc_reg] = value
        if not port & 0x0800:                             # PPI (&F4xx-&F7xx)
            p = (hi >> 0) & 3
            if p == 0:
                self.psg_data = value
            elif p == 2:
                self.ppi_c = value
            elif p == 3 and value & 0x80:                 # mode set: the 8255 clears its output latches
                self.ppi_c = 0
            elif p == 3 and not value & 0x80:             # bit set/reset on port C
                bit = (value >> 1) & 7
                if value & 1: self.ppi_c |= 1 << bit
                else: self.ppi_c &= ~(1 << bit)

    def read_port(self, registers, port, *a):
        hi = port >> 8
        if not port & 0x0800:
            p = hi & 3
            if p == 2:
                return self.ppi_c
            if p == 1:                                    # port B: VSYNC in bit 0
                return 0xFE | (1 if registers[25] % FRAME < 1024 else 0)
            if p == 0:                                    # port A: PSG register 14 = keyboard row
                row = self.ppi_c & 15
                v = 0xFF
                for (r, b) in self.keys:
                    if r == row: v &= ~(1 << b)
                return v
        return 0xFF

    # ---- run
    def run(self, nsteps):
        R, mem, sim = self.R, self.mem, self.sim
        for _ in range(nsteps):
            pc = R[24]
            if mem[pc] == 0x76:                           # HALT: jump to the next interrupt
                R[25] = max(R[25], self.next_int)
                R[24] = (pc + 1) & 0xFFFF
            else:
                sim.run()
            self.steps += 1
            if R[25] >= self.next_int:
                k = (self.next_int // INT_EVERY) % 6
                self.slot_pal[(k - 1) % 6] = list(self.pal)     # palette that was in force during the slot
                self.slot_mode[(k - 1) % 6] = self.mode
                self.next_int += INT_EVERY
                if R[26]:
                    sim.accept_interrupt(R, mem, pc)

    def shot_raster(self, path, scale=2):
        """Each display line uses the palette of its interrupt slot (display line 0 is ~70 lines after interrupt 0)."""
        from PIL import Image
        from .cpcgfx import px0
        base = ((self.crtc.get(12, 0x30) & 0x30) << 10)
        img = Image.new('RGB', (320, 200))
        for y in range(200):
            slot = ((y + 70) // 52) % 6
            pal = [HW[c & 31] for c in self.slot_pal[slot][:16]]
            mode = self.slot_mode[slot]
            for x in range(80):
                b = self.mem[(base + (y % 8) * 0x800 + (y // 8) * 80 + x) & 0xFFFF]
                if mode == 1:
                    for i in range(4):
                        p = ((b >> (7 - i)) & 1) | (((b >> (3 - i)) & 1) << 1)
                        img.putpixel((x * 4 + i, y), pal[p])
                else:
                    for k, p in enumerate(px0(b)):
                        img.putpixel((x * 4 + k * 2, y), pal[p]); img.putpixel((x * 4 + k * 2 + 1, y), pal[p])
        img.resize((320 * scale // 2 * 2, 200 * scale)).save(path)

    def shot(self, path, scale=2):
        pal = [HW[c & 31] for c in self.pal[:16]]
        base = ((self.crtc.get(12, 0x30) & 0x30) << 10)
        img = screen(self.mem, pal, base=base)
        img = img.resize((img.width * scale // 2 * 1, img.height * scale))
        img.save(path)

# CPC keyboard matrix (row, bit)
KEY = {"space": (5, 7), "fire": (9, 4), "joy_up": (9, 0), "joy_down": (9, 1), "joy_left": (9, 2), "joy_right": (9, 3),
       "fire2": (9, 5), "return": (2, 2), "1": (8, 0), "q": (8, 3), "a": (8, 5), "o": (4, 2), "p": (3, 3), "enter": (0, 6)}
