"""Linear Z80 disassembly of a memory range (SkoolKit's disassembler). dis(mem, lo, hi) -> list of lines."""
import json,sys
from types import SimpleNamespace
from skoolkit.disassembler import Disassembler
class I:
    def __init__(s,a,o,b): s.a,s.o,s.b=a,o,b
def dis(mem,lo,hi):
    D=Disassembler(mem,SimpleNamespace(asm_hex=True,asm_lower=False,defb_size=8,defm_size=64,defw_size=8,handle_rst=False,imaker=I,opcodes="",wrap=False))
    return ["%04X  %-22s %s"%(i.a,i.o," ".join("%02X"%b for b in i.b)) for i in D.disassemble(lo,hi,'h')]
if __name__=="__main__":
    d=json.load(open(sys.argv[1])); mem=d['mem']; R=d['regs']
    print("PC=&%04X SP=&%04X"%(R[24],R[12]))
    for a in sys.argv[2:]:
        lo,hi=[int(x,16) for x in a.split('-')]
        print("\n".join(dis(mem,lo,hi))); print('---')
