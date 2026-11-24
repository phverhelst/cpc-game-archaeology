# A protocol for the verified reverse engineering of Amstrad CPC games

This protocol describes how to take an Amstrad CPC game apart, understand it subsystem by subsystem, and prove that the understanding is correct. It grew out of the study of *The Sacred Armour of Antiriad* (Palace Software, 1986), published in the companion repository `cpc-game-archaeology-antiriad`, and every step below points to what was done there. It is a first version: it describes what worked on one game and is meant to be refined on others.

## Principles

The game's binary is the only source of truth. Magazine articles, memories, other versions of the game and our own intuitions are leads, never evidence. A claim about how the game works is accepted when a model written from that claim reproduces the game's behaviour, checked byte for byte against the original code running in an emulator.

The stance is that of a museum curator, not a modder. Bugs and oddities of the original are documented and reproduced, never fixed in the model. In Antiriad, a sound routine writes past its table and silently erases three instruments for the rest of the game; the model does the same, and the documentation explains it.

Nothing that belongs to the rights holders is distributed. Repositories contain code, documentation and checksums. Every game file, memory image, disassembly, graphic, score or recording is regenerated locally from the user's own copy by an extractor. See `LEGAL_AND_ETHICS.md`.

Everything is reproducible. A newcomer with the same disk image must be able to run one command and get the same files and the same verification results.

## Phase 1: identify the release

Record which release you have: format (tape or disk), publisher, year, language, and above all whether it is an original or a conversion. Compute its SHA-256 and publish the hash, not the file. This matters more than it seems. The Antiriad disk studied here is a 2013 tape-to-disk conversion by CNGSoft: its loader, its opening logo and the curtain effect that reveals the loading screen are CNGSoft's work, not Palace's. Only the game code proper, from &5400 on, is from 1986. Any finding about the loading sequence must say which release it describes.

## Phase 2: extract the files

`python3 -m cpcarch.dsk image.dsk` lists the AMSDOS catalogue and `python3 -m cpcarch.dsk image.dsk NAME.EXT out` extracts a file, AMSDOS header removed. Standard and extended DSK images in DATA or SYSTEM format are supported. Copy-protected disks and tape images (CDT/TZX) are not supported yet: contributions are welcome.

## Phase 3: reach the game's entry point

Rather than reimplementing a loader's decompressor, run it. `cpcarch.loader.run_loader` executes the loader in SkoolKit's Z80 core (made CPC-compatible by `cpcarch.cpcsim`), answers firmware calls with a simple return, skips HALT and simulates VSYNC, and stops when the program counter reaches the entry point you name. The result is a 64 KB memory image of the game ready to start. For Antiriad, the loader writes its own `LDIR / RET` at &0030, copies 41 KB down to &0200 and returns to &5400.

From this image, `python3 -m cpcarch.sna` writes a `.SNA` snapshot that a real emulator (WinAPE, CPCEC, Caprice) can open, which is useful to look at the game while reading its code. `cpcarch.emu.CPC` runs the game itself in Python, with 300 Hz interrupts, palette and mode changes per interrupt slot, keyboard matrix and screenshots: slow, but deterministic and scriptable.

## Phase 4: draw the first map

Disassemble recursively from the entry point, the interrupt handler and any other entry you find (`cpcarch.rdis`). Then build a memory map: where the code is, where the data are, where the screen is, which variables live where. Locate the main loop, the interrupt handler and what it does at each of its six slots per frame, the screen layout (mode, palette changes, split screens), the keyboard reading. Render screens from the emulator to see what each region of memory becomes.

At this stage the useful output is a short document listing addresses with one sentence each. In Antiriad: main loop at &54FA, interrupt at &6EF2, eight object slots of 19 bytes at &B400, a state table at &922A, movement scripts at &97F8, a sound driver at &755E called at 100 Hz.

## Phase 5: one subsystem at a time, model and verify

Choose a subsystem: player movement, the object animator, collisions, enemy scripts, the status panel, the sound driver. For each one, the cycle is the same.

First, transcribe the routine into Python, close to the code: same variables, same order of operations, same 8-bit arithmetic, with the original address in a comment on each function. Do not improve or simplify it yet.

Then build a verification harness. Run the real game in the emulator through a scripted scenario (keys pressed for a given number of frames). At the routine's entry, take a copy of memory; at its exit, take another. Apply the model to the first copy and compare the result with the second, over all the memory the routine may touch. Report differences by name ("object 2 +07", "panel line 140 column 12"), not by address alone.

Two checks are needed. The step-by-step check resynchronises the model on the game at every call and finds local mistakes. The continuous check lets the model run alone from the same starting point, without resynchronising, and finds drifts that only accumulate over time. Antiriad's object model was accepted after 24 scenarios and 5 262 turns matched in both modes, plus the player's death, the beam weapon and the complete ending.

Expect the following difficulties, all met in Antiriad:

- **Interrupts in the middle of the routine.** An interrupt that fires during the routine can change memory the model does not expect. If you cannot tell when it fired, try the model with the interrupt's effect before and after, and keep the version that matches.
- **Volatile memory.** Some memory is meant to differ: the stack, the sound driver's state, or a part of the screen that displays raw memory (Antiriad's panel has one). Exclude it explicitly and say why.
- **Raw Z80 timing.** SkoolKit counts raw Z80 T-states, but the CPC's Gate Array stretches every instruction to a multiple of 4 T-states (1 µs). Logic is unaffected; anything timed to the raster (colour changes during the frame) must be modelled in CPC microseconds.
- **Firmware conventions.** With the firmware intercepted, registers that the firmware normally maintains hold zero. The CPC firmware keeps the Gate Array port and mode in BC', for instance, so code that relies on it writes to a different port in the emulator.
- **Hidden randomness.** Games often read the Z80's R register for randomness. A deterministic emulator always draws the same value, which can hide a whole branch of the game. Antiriad picks its starting room from bit 0 of R, and the emulator always chose the same room until the branch was found in the code and forced.
- **Self-modifying code.** Read the routine as it is in memory at the time of the call, not as it was when the game started.

## Phase 6: extract the data into neutral formats

Once a routine is understood, the data it reads can be extracted: movement tables, room descriptions, object lists, enemy scripts, music. Write them as JSON or plain binary with a documented layout, generated locally by a script and never committed. These files serve other languages, ports and tools.

## Phase 7: ports and sandboxes

A model in Python can be ported to JavaScript and turned into an interactive page (a sandbox) where the player can be moved and the internal values watched. The port is verified against the Python model in its turn: in Antiriad, by comparing MD5 hashes of the full 64 KB memory after 320 turns from 26 starting points. Pages are built from templates by a script, because they embed game data and must not be committed.

## Phase 8: document

Each subsystem gets a document in prose: what it does, how (with addresses), the figures that characterise it (heights, durations, counts), what the verification covered, and what remains outside the model. A project-state document summarises findings for whoever resumes the work. Distinguish clearly what was verified, what was observed and what is inferred.

## Repository layout for a game

A game repository following this protocol contains:

- **`README.md`**: what the game is, which release was studied (with its SHA-256), how to extract, what was found.
- **`checksums.sha256`**: hashes of the expected input file and of every intermediate memory image, so that a user knows whether their copy is the same release.
- **`extract.py`**: from the user's disk image to `build/` (game files, memory images), checking every hash.
- **`make_all.py`** (or an equivalent): regenerates every product and runs every verification.
- **One folder per subsystem**, each with its model, its verification harness and its document.
- **`.gitignore`**, excluding `build/` and every generated file.

`templates/` contains starting points for these files.

## Working with an AI assistant

The Antiriad study was carried out by a person directing an AI assistant (Claude, by Anthropic), which wrote most of the code and documentation. This protocol is what made that collaboration trustworthy. Every claim had to pass an automated comparison with the original code, and the assistant's own mistakes surfaced the same way as anyone else's: a wrong reading of a sound command, a misplaced test, a timeout. Whoever uses an assistant should say so, and should keep verification, not plausibility, as the criterion of truth.
