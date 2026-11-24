# Contributing

Contributions are welcome: new tools, fixes, a game studied with this protocol, translations, corrections of fact. A few rules keep the work trustworthy and legal.

**No game material.** Never commit a disk or tape image, a memory image, a disassembly listing, graphics, music, or a page that embeds game data. See `LEGAL_AND_ETHICS.md`. Pull requests that contain such material will be closed, and the history rewritten if necessary.

**Verified claims.** A finding about how a game works comes with the means to check it: a model, a harness that compares it with the original code in the emulator, and the figures of that comparison (scenarios, turns, differences). Observations that are not yet verified are welcome too, labelled as such.

**Reproducibility.** Any generated file must be produced by a script in the repository, from the user's own copy of the game, with its input checked by SHA-256.

**Name the release.** Say which release of a game you studied (original tape, budget re-release, disk conversion, by whom) and give its hash.

**Language.** Documentation is written in English. The Antiriad study was carried out in French, and its code still has French identifiers and comments; translating them is a welcome contribution, provided every verification still passes afterwards.

**Wanted.**
- Tape image (CDT/TZX) support, with a loader runner able to feed the tape signal to the emulated machine.
- Copy-protected disk formats.
- The AY hardware envelope in `cpcarch.ay`.
- Accurate CPC instruction timing (Gate Array wait states) in the emulator.
- Studies of other games.
- Contacts with the original authors (see `LEGAL_AND_ETHICS.md`).

To propose a new game study, open an issue first with the game, the release and what you intend to look at.
