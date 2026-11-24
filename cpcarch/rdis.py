"""Recursive-descent disassembly of a 64K CPC snapshot from given entry points."""
import sys, re, json
from types import SimpleNamespace
from skoolkit.disassembler import Disassembler

class Ins:
    def __init__(s, a, o, b): s.address, s.operation, s.bytes = a, o, b

def analyse(mem, entries, lo=0x0000, hi=0x10000, names=None):
    dis = Disassembler(list(mem), SimpleNamespace(asm_hex=True, asm_lower=False, defb_size=8, defm_size=64,
                                                  defw_size=8, handle_rst=False, imaker=Ins, opcodes="", wrap=False))
    code, labels, calls, xrefs = {}, set(entries), {}, {}
    todo = list(entries)
    while todo:
        a = todo.pop()
        while lo <= a < hi and a not in code:
            ins = dis.disassemble(a, a + 1, "h")[0]
            code[a] = ins
            op = ins.operation
            m = re.match(r"(JP|JR|CALL|DJNZ|RST)\s+(?:(NZ|Z|NC|C|PO|PE|P|M),)?\$([0-9A-F]{2,4})$", op)
            if m:
                t = int(m.group(3), 16)
                labels.add(t)
                xrefs.setdefault(t, []).append(a)
                if m.group(1) == "CALL":
                    calls[t] = calls.get(t, 0) + 1
                if lo <= t < hi:
                    todo.append(t)
                if m.group(1) in ("JP", "JR") and not m.group(2):
                    break
            if op in ("RET", "RETI", "RETN") or op.startswith("JP (") or op == "HALT" and False:
                break
            a += len(ins.bytes)
    return code, labels, calls, xrefs

def emit(mem, code, labels, lo, hi, names=None, comments=None):
    names = names or {}
    comments = comments or {}
    nm = lambda t: names.get(t, "L%04X" % t)
    def fmt(op):
        return re.sub(r"\$([0-9A-F]{4})", lambda m: nm(int(m.group(1), 16)) if int(m.group(1), 16) in labels or int(m.group(1), 16) in names else "&" + m.group(1), op).replace("$", "&")
    out = []
    a = lo
    while a < hi:
        if a in labels or a in names:
            out.append("")
            if a in comments: out.append("; " + comments[a])
            out.append(nm(a) + ":")
        if a in code:
            ins = code[a]
            out.append("        %-32s; %04X  %s" % (fmt(ins.operation), a, " ".join("%02X" % b for b in ins.bytes)))
            a += len(ins.bytes)
        else:
            s = a; data = []
            while a < hi and a not in code and (a == s or (a not in labels and a not in names)) and len(data) < 16:
                data.append(mem[a]); a += 1
            if all(v == data[0] for v in data) and len(data) == 16:
                # compress runs
                while a < hi and a not in code and a not in labels and mem[a] == data[0]:
                    a += 1
                out.append("        DEFS %d,&%02X%s; %04X" % (a - s, data[0], " " * 20, s))
            else:
                txt = "".join(chr(b) if 32 <= b < 127 else "." for b in data)
                out.append("        DEFB %-40s; %04X  %s" % (",".join("&%02X" % b for b in data[:8]) + ("..." if len(data) > 8 else ""), s, txt))
    return "\n".join(out)

if __name__ == "__main__":
    mem = open(sys.argv[1], "rb").read()
    entries = [int(x, 16) for x in sys.argv[2].split(",")]
    code, labels, calls, xrefs = analyse(mem, entries)
    lo_c = min(code); hi_c = max(code)
    print("code bytes", sum(len(i.bytes) for i in code.values()), "range &%04X-&%04X" % (lo_c, hi_c), "routines", len(calls))
    firm = sorted((k, v) for k, v in calls.items() if k >= 0xB900)
    print("firmware/high calls:", ["&%04X x%d" % kv for kv in firm])
    print("most called:", ["&%04X x%d" % kv for kv in sorted(calls.items(), key=lambda kv: -kv[1])[:20]])
    open(sys.argv[3], "w").write(emit(mem, code, labels, 0x0000, 0x10000))
