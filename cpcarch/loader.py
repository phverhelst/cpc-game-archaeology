"""Run a CPC loader in the Z80 simulator until it jumps to the game's entry point.

Many disk conversions and tape loaders decompress and relocate the game, then jump to it. Running the loader
is usually simpler and safer than reimplementing its unpacker. The firmware is not emulated: every call into
the jumpblock (&B900-&BDFF) returns at once, KM_WAIT_CHAR/KEY answer "space", HALT is skipped (no interrupts)
and VSYNC (PPI port B, bit 0) is simulated as high during the first 8 lines of each 79 872 T-state frame.
That is enough for simple loaders; anything that reads the tape, the FDC or depends on firmware state needs more.

    from cpcarch.loader import run_loader
    mem, regs, log = run_loader(data, load=0x170, start=0x190, entry=0x5400)

`log` records CRTC register writes, firmware calls and the T-state at which chosen addresses were first reached.
"""
from .cpcsim import Simulator

FRAME = 79872
VSYNC = 8 * 256


def run_loader(data, load, start, entry, sp=0xBFF0, max_steps=60_000_000, marks=(), on_step=None):
    mem = [0] * 65536
    mem[load:load + len(data)] = list(data)
    log = {"crtc": {}, "firmware": [], "marks": {}}
    sel = [0]

    class Tracer:
        def write_port(self, r, port, v, *a):
            hi = port >> 8
            if hi == 0xBC:
                sel[0] = v
            elif hi == 0xBD:
                log["crtc"][sel[0]] = v

        def read_port(self, r, port, *a):
            if port >> 8 == 0xF5:
                return 0xFE | (1 if r[25] % FRAME < VSYNC else 0)
            return 0xFF

    sim = Simulator(mem, {"PC": start, "SP": sp})
    sim.set_tracer(Tracer())
    R = sim.registers
    steps = 0
    while steps < max_steps:
        pc = R[24]
        if pc in marks and pc not in log["marks"]:
            log["marks"][pc] = R[25]
        if on_step:
            on_step(pc, R, mem)
        if 0xB900 <= pc <= 0xBDFF:
            log["firmware"].append((pc, R[0], R[2] << 8 | R[3]))
            if pc in (0xBB06, 0xBB18):
                R[0] = 0x20
            s = R[12]
            R[24] = mem[s] | mem[(s + 1) & 0xFFFF] << 8
            R[12] = (s + 2) & 0xFFFF
            continue
        if mem[pc] == 0x76:
            R[24] = (pc + 1) & 0xFFFF; steps += 1; continue
        sim.run(); steps += 1
        if R[24] == entry and steps > 1:
            return bytes(mem), list(R), log
    raise RuntimeError("entry point &%04X not reached after %d steps" % (entry, steps))
