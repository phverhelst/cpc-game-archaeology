"""A Z80 simulator for the Amstrad CPC, built at import time from SkoolKit's simulator.

SkoolKit (https://skoolkit.ca, Richard Dymond, GPL-3.0) simulates the ZX Spectrum, whose first 16 KB are ROM:
its simulator refuses writes below &4000. On a CPC with the ROMs paged out, that memory is RAM. Rather than
ship a modified copy of a GPL file, this module reads the installed `skoolkit.simulator` source, lifts the
write protection (every `if <addr> > 0x3FFF:` guard becomes `if True:`), and executes the result here.

Tested with SkoolKit 10.2. If a future version changes the guards, the count check below fails loudly.
Register indices (SkoolKit convention): A=0 F=1 B=2 C=3 D=4 E=5 H=6 L=7 IXh=8 IXl=9 IYh=10 IYl=11 SP=12
I=13 R=14, alternate set from 15, PC=24, T-states=25, IFF=26, IM=27.
"""
import inspect, re
import skoolkit.simulator as _src

_code = inspect.getsource(_src)
_code, _n = re.subn(r"if (\w+) > 0x3FFF:", "if True:", _code)
EXPECTED_PATCHES = 32
if _n != EXPECTED_PATCHES:
    raise ImportError("cpcsim: expected %d ROM guards in skoolkit.simulator, found %d "
                      "(SkoolKit version %s untested)" % (EXPECTED_PATCHES, _n, getattr(_src, "__version__", "?")))
exec(compile(_code, "<cpcsim from skoolkit.simulator>", "exec"), globals())
