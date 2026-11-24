# cpc-game-archaeology

A protocol and a small toolkit for the verified reverse engineering of Amstrad CPC games: understanding how a 1980s game works, subsystem by subsystem, and proving each explanation by checking it against the original code running in an emulator.

The approach is that of a museum curator. The game's binary is the only source of truth. Its bugs are documented, not fixed. No game material is distributed: each user regenerates everything from their own copy.

## Contents

| | |
|---|---|
| `PROTOCOL.md` | The method, phase by phase, with the pitfalls met on a first game |
| `LEGAL_AND_ETHICS.md` | What is never committed, credit, and how to contact authors and rights holders |
| `DEVELOPMENT_PLAN.md` | The other way round: how a game like this could be designed and planned, step by step |
| `CONTRIBUTING.md` | How to contribute, and what is wanted |
| `cpcarch/` | The toolkit (Python) |
| `templates/` | Starting points for a game repository |

## The toolkit

| Module | Purpose |
|---|---|
| `cpcarch.dsk` | Read DSK images (standard and extended) and extract AMSDOS files |
| `cpcarch.loader` | Run a loader in the Z80 simulator until it jumps to the game, with the firmware intercepted |
| `cpcarch.cpcsim` | SkoolKit's Z80 simulator with the ZX Spectrum ROM protection lifted, built at import time |
| `cpcarch.emu` | A minimal CPC: 300 Hz interrupts, Gate Array palette and mode per interrupt slot, keyboard matrix, VSYNC, screenshots |
| `cpcarch.rdis`, `cpcarch.zdis` | Recursive and linear disassembly |
| `cpcarch.cpcgfx` | Hardware and firmware palettes, mode 0 pixel decoding, screen rendering |
| `cpcarch.ay` | A simplified AY-3-8912 renderer (tone, noise, mixer, volume; no hardware envelope) |
| `cpcarch.sna` | Write a `.SNA` snapshot from a memory image, for real emulators |

Installation: Python 3.9 or later, then `pip install -e .` from this folder. This installs SkoolKit 10.2, NumPy, Pillow and SciPy. Some game studies also use `ffmpeg` (video, audio), `rsvg-convert` (score engraving) and Node.js (verification of JavaScript ports).

## Games studied

| Game | Repository | Status |
|---|---|---|
| *The Sacred Armour of Antiriad* (Palace Software, 1986) | `cpc-game-archaeology-antiriad` | Movement, objects and enemies, rooms, status panel, sound driver and music, ending, loader of the CNGSoft disk conversion: modelled and verified; playable sandbox |

## How this was made

The protocol and the toolkit came out of a study carried out in 2026 by Philippe Verhelst, directing an AI assistant (Claude, by Anthropic), which wrote most of the code and documentation. Every finding was accepted only after an automated comparison with the original code. See the end of `PROTOCOL.md`.

## Licence

Code: MIT (`LICENSE`). Documentation: CC BY 4.0 (`LICENSE-docs.md`). SkoolKit, used as a dependency, is GPL-3.0 and is not included.
