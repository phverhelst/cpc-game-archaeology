"""Template extractor: from the user's own disk image to build/, every step checked by SHA-256.

Copy into a game repository, fill in the constants, and add the snapshots your study needs.
"""
import hashlib, os, sys
from cpcarch.dsk import Disk
from cpcarch.loader import run_loader

ICI = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(ICI, "build")
DISK_SHA256 = "..."          # the release studied
FILE = "GAME.BAS"            # the file the loader starts from
LOAD, START, ENTRY = 0x0170, 0x0190, 0x0000
EXPECTED = {"game_entry.bin": "..."}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def check(name, data):
    ok = sha(data) == EXPECTED.get(name, sha(data))
    print("%-20s %s" % (name, "ok" if ok else "DIFFERENT RELEASE? sha256 " + sha(data)))
    return ok


if __name__ == "__main__":
    image = open(sys.argv[1], "rb").read()
    if sha(image) != DISK_SHA256:
        print("warning: this disk image is not the release studied; results may differ")
    os.makedirs(BUILD, exist_ok=True)
    data, header = Disk(image).read(FILE)
    mem, regs, log = run_loader(data, LOAD, START, ENTRY)
    check("game_entry.bin", mem)
    open(os.path.join(BUILD, "game_entry.bin"), "wb").write(mem)
