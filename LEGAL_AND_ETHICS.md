# Legal and ethical framework

This is not legal advice. It describes the rules this project follows to study games that still belong to someone, and the way it seeks contact with the people who made them.

## What is never committed

The games studied here are protected works, whatever their age and commercial status. Repositories following this protocol never contain:

- disk or tape images;
- files extracted from them;
- memory images, snapshots or any other binary copy of the game;
- complete disassembly listings, which reproduce the code;
- graphics, screenshots, room or sprite renders;
- music renders (audio files), transcriptions (scores, MIDI, MusicXML) or extracted sound data;
- interactive pages that embed game data.

The `.gitignore` files exclude the usual extensions, but the rule applies whatever the extension. Before making a repository public, check the full list of tracked files (`git ls-files`) and the history.

## What is committed

The repositories contain the following:

- original code: extractors, emulation harnesses, models, verification scripts, generators;
- documentation written by the contributors;
- checksums (SHA-256) of the expected inputs and intermediate images.

Documentation may quote addresses, short byte sequences and individual values (a table entry, a speed, a colour number) where they are needed to explain or verify a mechanism. It does not reproduce tables, texts or code at length.

Each user regenerates everything else locally from a copy they obtained themselves. The checksums let them confirm they hold the same release without anyone distributing it.

## Third-party software

The Z80 core comes from SkoolKit (Richard Dymond, GPL-3.0). It is not copied into this repository. `cpcarch.cpcsim` reads the installed SkoolKit source at run time and lifts its ZX Spectrum ROM write protection. The code here is MIT-licensed, which is compatible with the GPL. Anyone redistributing a bundle that includes SkoolKit must respect its licence.

## Credit and accuracy

Name the authors of the game in every repository: programmer, graphic artist, musician, publisher. They are usually listed on the title screen or in the manual. Name the authors of conversions too, and say clearly which parts of what you describe are theirs. Distinguish verified facts from inferences. Disclose the use of AI assistants.

## Contacting creators and rights holders

The best outcome of this kind of work is to put it in front of the people who made the game. They can correct what was misread, add what no binary can tell (how they worked, which tools they used, what was cut), and sometimes allow more to be shared. Proceed as follows:

1. **Identify the people.** Start from the credits on the title screen and in the manual. Then look up current interviews, personal sites and professional profiles. Many developers of the 1980s are still active and approachable.
2. **Identify the rights holders.** Publishers were sold, merged or closed. Rights may have passed to another company, been bought by a collector of back catalogues, or returned to the authors. Do not guess: document what you find, with sources, in the game repository.
3. **Write first, publish later.** Before making a repository public, consider sending the authors a short, factual message: what was studied, the fact that no game material is distributed, a link to the private repository or to a summary, and an open question or two they alone can answer. Respect silence and refusals.
4. **Record contacts.** Keep a `CONTACTS.md` in the game repository with dates, who was contacted, how, and the answer, without publishing personal contact details.

A template message:

> Dear …,
>
> I am studying *[game]*, which you [programmed / drew / composed] for [publisher] in [year], as part of a documentation project on Amstrad CPC games. The work explains how the game's [movement, sound driver, ending…] work, and checks every explanation against the original code running in an emulator. It does not distribute the game or any of its graphics, music or code: readers must use their own copy.
>
> A summary is here: [link]. I would be glad to know whether you have any objection to its publication. If you have a moment, I would also be very interested in [one or two precise questions: tools used, development machine, a design choice].
>
> With thanks for the game, …
