"""Read Amstrad CPC disk images (.DSK, standard and extended) and the AMSDOS files on them.

    python3 -m cpcarch.dsk image.dsk                 list the catalogue
    python3 -m cpcarch.dsk image.dsk NAME.EXT out    extract one file (AMSDOS header removed)

Supports the DATA (sectors &C1-&C9) and SYSTEM (sectors &41-&49, two reserved tracks) formats, 1 KB blocks,
single-sided images. Copy-protected or non-AMSDOS disks are out of scope: use a dedicated tool for those.
"""
import struct, sys


class Disk:
    def __init__(self, data):
        sig = data[:34]
        self.extended = sig.startswith(b"EXTENDED")
        if not (self.extended or sig.startswith(b"MV - CPC")):
            raise ValueError("not a CPC disk image")
        self.tracks, self.sides = data[0x30], data[0x31]
        if self.extended:
            sizes = [data[0x34 + i] * 256 for i in range(self.tracks * self.sides)]
        else:
            sizes = [struct.unpack_from("<H", data, 0x32)[0]] * (self.tracks * self.sides)
        self.sectors = {}                       # (track, side, id) -> bytes
        pos = 0x100
        for t in range(self.tracks * self.sides):
            if sizes[t] == 0:
                continue
            ti = data[pos:pos + sizes[t]]
            if not ti.startswith(b"Track-Info"):
                raise ValueError("bad track header at %d" % pos)
            track, side, nsec = ti[0x10], ti[0x11], ti[0x15]
            off = 0x100
            for s in range(nsec):
                c, h, r, n, st1, st2, length = struct.unpack_from("<BBBBBBH", ti, 0x18 + 8 * s)
                if not self.extended:
                    length = 128 << n
                self.sectors[(track, side, r)] = ti[off:off + length]
                off += length
            pos += sizes[t]
        ids = {r for (_, _, r) in self.sectors}
        self.first = 0xC1 if 0xC1 in ids else 0x41
        self.reserved = 0 if self.first == 0xC1 else 2

    def logical(self, n):
        """Logical 512-byte sector n of the AMSDOS data area."""
        t, s = divmod(n, 9)
        return self.sectors[(t + self.reserved, 0, self.first + s)]

    def block(self, b):
        return self.logical(2 * b) + self.logical(2 * b + 1)

    def catalogue(self):
        d = self.block(0) + self.block(1)
        files = {}
        for i in range(64):
            e = d[32 * i:32 * i + 32]
            if e[0] == 0xE5:
                continue
            name = bytes(c & 0x7F for c in e[1:9]).decode("ascii").rstrip()
            ext = bytes(c & 0x7F for c in e[9:12]).decode("ascii").rstrip()
            key = (e[0], name + "." + ext)
            files.setdefault(key, []).append((e[12], e[15], [b for b in e[16:32] if b]))
        out = {}
        for (user, fname), extents in files.items():
            extents.sort()
            blocks = [b for ext in extents for b in ext[2]]
            records = sum(ext[1] for ext in extents)
            out[fname] = dict(user=user, blocks=blocks, records=records)
        return out

    def read(self, fname):
        """File contents; the 128-byte AMSDOS header, if present and valid, is removed."""
        e = self.catalogue()[fname]
        raw = b"".join(self.block(b) for b in e["blocks"])[:e["records"] * 128]
        h = raw[:128]
        if len(raw) >= 128 and sum(h[:67]) & 0xFFFF == struct.unpack_from("<H", h, 67)[0]:
            length = struct.unpack_from("<H", h, 24)[0] | (h[66] << 16)
            return raw[128:128 + length], dict(type=h[18], load=struct.unpack_from("<H", h, 21)[0],
                                              exec=struct.unpack_from("<H", h, 26)[0], length=length)
        return raw, None


if __name__ == "__main__":
    disk = Disk(open(sys.argv[1], "rb").read())
    if len(sys.argv) == 2:
        for name, e in sorted(disk.catalogue().items()):
            data, hdr = disk.read(name)
            print("%-12s %6d bytes %s" % (name, len(data), "" if hdr is None else
                  "type %d load &%04X exec &%04X" % (hdr["type"], hdr["load"], hdr["exec"])))
    else:
        data, hdr = disk.read(sys.argv[2])
        open(sys.argv[3], "wb").write(data)
        print("wrote", sys.argv[3], len(data), "bytes")
